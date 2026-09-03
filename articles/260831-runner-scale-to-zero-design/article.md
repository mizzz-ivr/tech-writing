---
title: "常時起動のCI runnerをephemeral scale-to-zeroに移す設計と、その途中で全部踏んだ話"
status: draft
published_at: null
verified_at: 2026-09-04
article_type: design-decision
level: intermediate
topics:
  - github-actions
  - aws
  - terraform
  - ci
  - self-hosted-runner
domains:
  - devops
  - infra
languages: []
technologies:
  - GitHub Actions
  - AWS EC2
  - AWS Lambda
  - Terraform
  - github-aws-runners
portfolio_signals:
  - architecture
  - infrastructure
  - cost-optimization
source_repositories:
  - ivRooom/ivrm-web
source_refs:
  - repository: ivRooom/ivrm-web
    commit: 1b3c2d9bcc9a3a089ebd534278e8d0939b8776ab
published:
  qiita: null
  zenn: null
  note: null
---

# 常時起動のCI runnerをephemeral scale-to-zeroに移す設計と、その途中で全部踏んだ話

個人開発の private repository で、GitHub Actions の無料枠が尽きたので AWS にセルフホストの runner を立てた、という話を[別の記事](https://github.com/mizzz-ivr/tech-writing)で書きました。そのときの構成は「ARM64 の spot インスタンスを1台、24/7 で起動しっぱなし」というものです。

これはこれで動いていたのですが、弱点が2つありました。

1つは、**runner が1台しかないのでジョブが直列**になること。rebase した9本のブランチをまとめて push したら、CI が7本待ち行列になりました。

もう1つは、この spot インスタンスが `one-time` リクエストで、AWS に回収されると `terminate` されて消えること。自動で立て直す仕組みを入れていなかったので、落ちたら手で起動する前提でした。

なので「ジョブが来たときだけ EC2 を起動して、1ジョブで捨てる」構成に移すことにしました。アイドル時は0台。いわゆる scale-to-zero です。

この記事は、その移行で決めたことと、移行の途中で踏んだ穴の記録です。手順書ではなく、なぜその選択をしたか・何を見落としたかの方に寄せています。

## 前提: 何を作っているか

`ivrm.jp` という個人サイトのモノレポで、Next.js アプリが複数、Cloudflare Worker が複数、共有パッケージがいくつか、という構成です。CI では型チェック・テスト・Lint・複数の Next.js ビルド・OpenNext バンドル・Terraform の validate・Docker イメージのビルド検証まで回しています。

runner は `ivrm-web` だけでなく、別リポジトリ（`ivrm-platform`）の CI からも使いたい、という要件も途中で出てきました。

## module をどれにするか

webhook 駆動の ephemeral runner を Terraform で組むなら、事実上の定番は `philips-labs/terraform-aws-github-runner` です。API Gateway + Lambda + SQS + EC2 spot で、`workflow_job` の webhook をきっかけに runner を起こす、というやつ。

ただ、調べたら **philips-labs のリポジトリは 2026-01 にアーカイブされていて read-only、v6.1.0 で更新が止まっていました**。Lambda の依存パッケージの脆弱性修正が今後入らない、というのは個人開発でも避けたい。

後継として `github-aws-runners/terraform-aws-github-runner` という org に移っていて、こちらは活発にメンテされていました（この記事の時点で v7.11）。アーキテクチャは同じで、v7 で一部の変数名が v6 と変わっている、くらいの違い。こちらを採用しました。

元々のプランには philips-labs と書いていたので、この乗り換えは「元の指示と違う判断」になります。こういうのは勝手に決めず、理由を添えて確認を取ってから進めました。

## 設計で決めたこと

### ネットワーク: NAT を置かない

runner の EC2 は GitHub API に outbound で到達できる必要があります。普通は private subnet + NAT Gateway ですが、NAT Gateway は東京リージョンで月4,000円くらいかかる。予算が月5,000円のプロジェクトでこれは重い。

既存の VPC を見たら、subnet が2つとも Internet Gateway にルートされていて（`MapPublicIpOnLaunch` は false）、NAT はありませんでした。なので runner に public IP を振る方針にしました。module の `associate_public_ipv4_address = true` です。scale-up Lambda 自体は VPC 外で動くので、そちらは何もしなくていい。

セキュリティ的には、runner の Security Group は inbound 全拒否・egress のみ。public IP はあるけど誰も入ってこれない。

### アーキテクチャ（v7 の既定は EventBridge 経由）

plan を見て気づいたのですが、v7 の webhook は EventBridge を挟む構成が既定になっていました。

```
GitHub App の workflow_job webhook
  → API Gateway (HTTP API)
  → Lambda: webhook（HMAC 検証）
  → EventBridge bus
  → Lambda: dispatcher
  → SQS
  → Lambda: scale-up（EC2 spot を RunInstances、JIT config で登録）
  → EC2 が1ジョブ実行して自己終了
  → Lambda: scale-down（cron */5 で idle/orphan を掃除）
```

部品は増えますが、機能は philips-labs 時代と同じ。これはそのまま受け入れました。

### enable_job_queued_check という安全弁

`enable_job_queued_check = true` にすると、scale-up Lambda が EC2 を起こす前に GitHub API を叩いて「そのジョブがまだ `queued` か」を確認します。

これが移行期間中に効きました。旧 runner（常時起動）と新 runner（webhook 駆動）を併存させていたとき、旧 runner が3秒でジョブを取る → scale-up Lambda が30秒後に処理を始める頃には `in_progress` → 「もう実行中だから EC2 は起こさない」とスキップ。ログには `No runner will be created, job is not queued.` と出ます。

冷えた EC2 を起こすのに1〜2分かかる ephemeral 構成は、常時起動の runner と競争すると必ず負けます。でもそれは「無駄なインスタンスを立てない」という正しい挙動でもある。移行の順番を「新を先に検証 → 旧を落とす」にしていたので、旧を落とすまで新はほとんど仕事をしませんでした。

### repo をまたぐ

`REPOSITORY_ALLOW_LIST` を空にして、GitHub App を `ivrm-web` と `ivrm-platform` の両方にインストールしました。App レベルの webhook にしておくと、どちらのリポジトリの `workflow_job` も同じ Lambda に届き、scale-up が webhook の `repository` を見てそのリポジトリ scope で runner を登録します。`ivrm-platform` 側に固有の Terraform は要りませんでした。

## 踏んだ穴

ここからが本題かもしれません。

### 穴1: instance profile の名前衝突

`terraform apply` が最後の1リソースで止まりました。

```
Error: creating IAM Instance Profile (ivrm-ci-runner-profile):
  409 EntityAlreadyExists
```

module は runner の instance profile を `${prefix}-runner-profile` という名前で作ります。`prefix` を `ivrm-ci` にしていたので `ivrm-ci-runner-profile`。ところがこれは、旧 runner（Terraform に import 済み）の instance profile と完全に同じ名前でした。他のリソースはランダムな suffix 付きで衝突を回避していたのに、instance profile だけ決め打ちだった。

`prefix` を `ivrm-ghr` に変えて解決。ラベルは `prefix` 由来ではない（`self-hosted,linux,arm64,ci-runner`）ので、ワークフローの `runs-on` はそのまま。作りかけの85リソースは作り直しになりましたが、まだ何も動いていない状態だったので実害なし。

### 穴2: OOM

新 runner でジョブが走るようになったら、重い CI ジョブが落ちるようになりました。

- `ci.yml` の Quality Checks: OpenNext のバンドルビルドのステップで runner が突然死（ステップが `null`、ログなし）
- Docker イメージ検証: `docker build` の中の `next build` が「Running TypeScript ...」で exit 255

`t4g.small` は 2GB RAM です。Next.js/OpenNext のビルドを何回も連続で回すには足りない。実は旧 runner（Phase 1）は同じ理由で 8GB の swapfile を積んでいて、それで耐えていました。Terraform 化するときに、その swap 設定を module の user-data に持ってくるのを忘れていた。

対して、`aws-api-runtime.yml` の Docker ビルド（`next build` を含まない）は `t4g.small` で通っていました。犯人がハッキリした。

`userdata_post_install` に swapfile を戻し、ついでにインスタンスタイプを `t4g.medium`（4GB）を floor にしました。scale-to-zero なのでジョブ実行時だけの課金で、月数百円の差。

### 穴3: 未マージのブランチを2本、それぞれから apply した

これは設計というより手順のミスです。

swap 修正の PR と、旧 runner を Terraform から外す decommission の PR が、両方とも未マージで存在していました。両方とも「同じ `main` から分岐した別ファイルの変更」です。

私はこれを、swap ブランチから apply → decommission ブランチから apply、と順にやりました。すると2本目の apply が1本目の変更を巻き戻しました。decommission ブランチには swap 前の `phase2.tf` が入っているので、それが state に書き戻されたわけです。

しかもこの間に、decommission ブランチには旧 runner の import 定義がまだ残っていて、それが「terminated 済みのインスタンスを import しようとして見つからない → 設定に合わせて新規作成」を実行し、**runner bootstrap の無い空の EC2 を1台作りました**。#280 で自分が指摘していた「one-time spot は消えると復旧しない」の穴を、Terraform 経由で踏み直した形。

正解は「関連する infra の PR は全部 `main` にマージしてから、`main` で1回だけ apply する」でした。次からそうします。

### 穴4（外部要因）: 移行の最中に旧 runner がスポット回収された

移行の soak 中に、旧 runner の spot インスタンスが AWS に回収されて terminated になりました（`Server.SpotInstanceTermination`）。one-time spot のリスクがそのまま出た。

これは幸い、その時点で新 runner が `ivrm-web` と `ivrm-platform` の両方の CI を処理できるようになっていたので、CI は止まりませんでした。むしろ「旧を手で落とす」という cutover のステップが不要になった。結果オーライですが、狙ってやったわけではないです。

## 今の状態

`main` の CI は全部 self-hosted の ephemeral runner（`t4g.medium` + swap）で緑になっています。ジョブが来ると EC2 が1台起きて、1ジョブ実行して、自己終了。アイドル時は0台。

その後、EC2 Fleet に渡すインスタンスタイプを `t4g.medium` 単体から `["t4g.medium", "t4g.large"]` の2種類に増やしました（#293）。ある日 spot 在庫が偏って13台中13台が同じAZに集中したのを見て、`instance_allocation_strategy` を module デフォルトの `lowest-price`（一番安いプールに全部乗せる）から `price-capacity-optimized`（在庫が厚いプールも考慮する）に変えたのに合わせての対応です。**これはジョブの大きさで instance type を選んでいるわけではありません**。どのジョブが来ても同じ2択のプールから spot 在庫の厚い方が選ばれるだけで、OOM時の自動リトライでもない。Swap も常に8GB固定です。

コストは、常時起動のときが月1,400円くらい（spot + gp3）。今は EC2 がジョブ実行時だけなので、月300〜700円くらいの見込み（`t4g.medium` にした分、当初見積りの100〜350円から少し上がった）。

`ivrm-platform` の方は、そのリポジトリに runner を1台も登録していなかったのが元の詰まりでした。App が両方にインストールされていて `REPOSITORY_ALLOW_LIST` が空なら、`workflow_job` を1回発火させるだけで scale-up がそのリポジトリ用の runner を動的に登録する。追加の Terraform は書いていません。

## まだ気にしていること

- `t4g.medium` + swap でも、CI ジョブがまとめて来たら遅くなるはず。並列度（`runners_maximum_count`）と spot 在庫の兼ね合いは、実運用のデータが溜まってから見直す。
- module 内部の `inline_policy is deprecated` 警告が90個以上出ている。動作には影響しないけど、module の更新で直るのを待っている状態。
- ephemeral runner が terminate した後、GitHub 側の runner エントリが offline のまましばらく残る。module の housekeeper Lambda が掃除するはずだけど、挙動を追い切れていない。

## 今のところの結論

「常時起動 → scale-to-zero」は、コストとスケールの両方で正しい方向でした。ただ、移行そのものは思ったより穴が多かった。特に「未マージの infra ブランチを個別に apply しない」は、頭では分かっていても手が先に動いてしまった。

module を選ぶときにアーカイブ状態を確認する、既存リソースとの名前衝突を plan で見る、2GB のマシンで何をビルドするか現実的に見積もる。どれも当たり前ですが、当たり前を1個ずつ飛ばした結果の記録です。

少なくともこのプロジェクトでは、この構成で続けます。
