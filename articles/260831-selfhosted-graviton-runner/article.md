---
title: "GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた"
status: draft
published_at: null
verified_at: 2026-09-04
article_type: case-study
level: intermediate
topics:
  - github-actions
  - aws
  - ci
  - self-hosted-runner
  - individual-development
domains:
  - devops
  - infra
languages: []
technologies:
  - GitHub Actions
  - AWS EC2
  - AWS Graviton
  - Amazon Linux 2023
  - Terraform
portfolio_signals:
  - automation
  - infrastructure
  - ci
source_repositories:
  - ivRooom/ivrm-web
source_refs:
  - repository: ivRooom/ivrm-web
    commit: 6046e04715550d5f989fc9208ba1bcfd00f15d9d
  - repository: ivRooom/ivrm-web
    commit: 3f019f6cd6ff57964f1959f7037f4ca4942a62a3
published:
  qiita: null
  zenn: null
  note: null
---

# GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた

ある日、Pull RequestのCIが全部落ちるようになりました。

テストが失敗したわけではありません。ログを開くと、ジョブがステップに入る前に、3〜4秒で終わっています。`runner_id` が `0` で、実行されたステップの配列が空でした。

最初は一時的な障害かと思って再実行しましたが、何度やっても同じでした。

そのうち、`main` のbranch protectionを設定しようとしたAPIが `403` を返しました。メッセージは「GitHub Proにアップグレードするか、このrepositoryをpublicにしてください」。

これで話がつながりました。private repositoryのGitHub Actions無料枠、正確にはspending limitを使い切っていて、hosted runnerがジョブを割り当てる前に弾いていたわけです。

このrepositoryは個人開発の中では規模が大きめで、テスト・型チェック・Lint・ビルド・TerraformのvalidateまでCIで回しています。ここが動かないと、開いているPRが「レビューできない」状態でただ積み上がっていきます。

## 選択肢を並べてみる

CIを動かす場所を用意する方法は、思ったよりいくつもありました。ざっと検討したものを並べてみます。

一番手軽なのは、GitHub Proにして課金してしまうことです。月4ドルで、private repositoryのActions無料枠が2,000分から3,000分に増えます。それを超えた分はLinuxで1分0.006ドル（2026年1月の値下げ後のレート）。CIの構成を何も変えなくていいのは魅力ですが、うちのCIは型チェック・テスト・Lint・複数のNext.jsビルド・OpenNextバンドル・Terraform validateまで回していて、1 runで十数分かかります。PRを普通に開いていくだけで3,000分はそれなりに現実味があり、そうなると使った分だけ請求が伸びる変動費になってしまいます。Proにはせず、spending limitだけ上げてpay-as-you-goで溢れた分を払う、という手もありますが、これも実質同じで青天井の変動費という点が気になりました。

repositoryをpublicにすれば、hosted runnerは無制限で無料になります。これはかなり効くんですが、このプロジェクトはpublicにできない都合があるので、最初から選択肢に入りませんでした。

手元のマシンや、常時起動のPCにrunnerを置くという手もあります。コストはゼロに近い。でも自分の開発機だと、CIが走っている間うるさいし重いし、電源を切ったらCIも止まってしまいます。専用の常時起動マシンは持っていないので、これも見送りました。

最終的に選んだのは、AWSにCI専用のインスタンスを立てることでした。他のサービスをすでにAWSに載せているので、運用の土地勘があります。CI専用に1台足すだけなら、既存の請求に数百円乗る程度で済みます。

ざっくり並べるとこんな感じです（月額はうちのCI量・東京リージョンでの概算で、正確な数字ではありません）。

| 方法 | 月額の目安 | 立てる手数 | 保守 | 備考 |
|---|---|---|---|---|
| GitHub Pro / 従量課金 | 4ドル〜（超過分は従量） | ほぼゼロ | ゼロ | CIが増えると変動費が伸びる |
| repositoryをpublicにする | 無料 | ゼロ | ゼロ | 今回は不可 |
| 手元 / 常時PC | ほぼ無料 | 小 | 中（電源・OS） | マシンを占有される |
| AWS 常時spot 1台 | 約¥1,400 | 中〜大 | 中 | 直列・spot中断で消失（この記事の構成） |
| AWS scale-to-zero | 約¥300〜700 | 大 | 中 | ジョブ実行時だけ課金（→ 次の構成） |

決め手になったのは、**セルフホストrunnerの実行時間はGitHubの分数課金に含まれない**（＝走らせるマシンのコストだけで済む）という点でした。しかも今回の `runner_id=0` 問題そのものも、hosted runnerを使わなくなれば消えます。

> 補足（2026-09-04確認）: GitHub-hosted runnerは2026年1月1日に最大39%値下げされました。一方、2026年3月1日から予定されていたprivate repository上のself-hosted runnerへの1分0.002ドルのGitHub Actions cloud platform chargeは、GitHubが導入前に延期しています。2026年9月4日時点の公式Docsでも、self-hosted runnerではbillable minutesが発生しないと案内されています。したがって、この記事では現在も「self-hosted runnerの実行時間はGitHubの分数課金に含まれない」前提で記載しています。参考: [GitHub Actions pricing update](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/) / [Viewing job execution time](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-job-execution-time)

「立てる手数」と「保守」を安く見せていますが、実際にはGitHub App、IAM、Security Group、ephemeralのループ、ワークフローの段階移行と、決めることがそれなりにあります（この後の節がだいたいその話です）。それでも、変動費を増やさずにCIを自分の手元に戻せるなら、個人開発の運用としては引き合うと判断しました。

## なぜGraviton（ARM64）にしたか

インスタンスタイプは `t4g.small` にしました。ARM64のGravitonです。

理由は主に2つあります。

1つは、このrepositoryのデプロイ用ワークフローが `linux/arm64` のコンテナイメージをビルドしていること。x86のrunnerでARMイメージを作ると `docker/setup-qemu-action` でエミュレーションが必要になりますが、runner自体がARMならネイティブでビルドできます。速いし、安定します。

もう1つは単純に、同じくらいのスペックならGravitonの方が安いこと。

OSはAmazon Linux 2023。メモリが2GBしかないので、8GBのswapファイルを足してあります。CIでpnpm installとNext.jsのビルドを回すと、swapなしだと厳しい場面がありました。

## ephemeral runnerにする

セルフホストrunnerで一番気にしていたのは、ジョブ間で状態が残ることでした。

前のジョブが置いていったキャッシュや、うっかり残った認証情報を次のジョブが拾う、みたいなことは避けたい。特にデプロイ系のジョブが同じマシンで動くので。

なので **ephemeral runner**（1ジョブ実行したら登録解除して破棄）にしました。

やっていることはシンプルで、systemdのサービスがこのループを回しているだけです。

1. GitHub Appの秘密鍵から短命のインストールトークンを作る
2. そのトークンで、repositoryのrunner登録トークンを取得する
3. `config.sh --ephemeral --replace` で登録する
4. `run.sh` で1ジョブ待ち受ける
5. ジョブが終わったら登録解除して、1に戻る

ポイントは、**staticなPersonal Access Tokenを置きっぱなしにしていない**ことです。GitHub Appを使うと、その場で短命トークンを発行できます。App IDとinstallation ID、秘密鍵はAWSのParameter Store（SecureString）に入れて、runnerのIAMロールから読めるようにしてあります。

runnerのIAMロールにデプロイ権限は持たせていません。デプロイするジョブは、これまで通り `configure-aws-credentials` のOIDCでワークフローごとのロールをassumeします。セルフホストrunner上でもOIDCはそのまま動きました。

## ワークフローの移行は一気にやらない

`runs-on` の変更自体は1行です。

```yaml
# before
runs-on: ubuntu-latest

# after
runs-on: [self-hosted, linux, ARM64, ci-runner]
```

ただ、16個くらいあるワークフローを全部いっぺんに切り替えるのはやめました。

まず、CIが詰まって困っていたコア部分（テストとLintを回すジョブ、Terraformのvalidate）だけをセルフホストに向けて、実際に緑になるのを確認しました。残りは順番に、PRを分けて移しています。

デプロイ系（ARMイメージのビルドを含むもの）は、移すときに `docker/setup-qemu-action` のステップを一緒に消せます。runnerがARMなので、もうエミュレーションは要りません。

## 立てたあとに踏んだ小さな穴

CIが数日止まっていた影響が、思わぬところに出ました。

Prettierのフォーマット崩れが、いくつかのbranchに混ざっていました。CIの「変更ファイルだけPrettierでチェックする」ステップが動いていなかったので、その間にマージ・rebaseされた差分をチェックできていなかったわけです。runnerを立てて古いbranchをrebaseしたら、まとめて表面化しました。

もう1つはWindows側の話です。作業マシンがWindowsで `core.autocrlf=true` なので、チェックアウトしたMarkdownがCRLFになります。ローカルで `prettier --check` すると、行末だけを理由に「フォーマットが違う」と言われます。中身は正しいのに、です。

これに何度か振り回されました。結局、コミット済みのblobを直接取り出して（`git show HEAD:path`）、LFのままチェックするのが確実でした。Linux上のCIは最初からLFなので、そこでは問題になりません。

## 今の状態と、まだ残っている課題

CIは動くようになりました。開いていたPRも順番に緑にできています。

ただ、今の構成には明確な弱点があります。

**runnerが1台で、ジョブが直列**です。rebaseした9本のbranchをまとめてpushしたら、7本のCIが1台のrunnerの後ろで待ち行列になりました。個人開発のペースなら普段は困りませんが、まとめて何かやると詰まります。

それと、このインスタンスはspotの `one-time` で、中断されると `terminate` されて消えます。自動で立て直す仕組みはまだ入れていません。落ちたら手で起動する前提です。

なので次は、**ジョブが来たときだけEC2を起動して、1ジョブで捨てる**構成に変えるつもりです。`workflow_job` のwebhookをきっかけにLambdaがrunnerを起動して、アイドル時は0台、というやつです。moduleは `github-aws-runners/terraform-aws-github-runner`（`philips-labs` がアーカイブされた後の後継）を使う予定で、設計とTerraformのドラフトまでは書きました。並列度もそこで解決できます。

コスト面では、常時起動のspot `t4g.small` が月1,000円弱（+ gp3のディスク）。scale-to-zeroにすると、ジョブ実行時間だけの課金になるので、月数百円まで下がる見込みです。

## Terraformに載せるときにハマったこと

runnerは最初、CIを早く復旧させたくてAWSのAPIから手で作りました。あとからTerraform管理に移すときは、`import` ブロックで取り込みました。

このとき、初回の `terraform apply` を「純粋なimportだけ・変更0件」にするのに少し手間がかかりました。

- spotの属性やAMI、user_dataは `ignore_changes` に入れる（これらは読み戻しが安定しなかったり、後で丸ごと作り直す予定だったりする）
- providerの `default_tags` は一旦付けず、リソースごとにライブと同じタグを明示する

これで `terraform plan` が「7 to import, 0 to add, 0 to change, 0 to destroy」になりました。タグの正規化は、importが通ったあとの別コミットに回しました。

余談ですが、`terraform validate` と `plan` がWindowsのローカルで動きませんでした。AWS providerのスキーマ取得（gRPC）でクラッシュします。`terraform fmt` と `providers lock` は動くので、validateとplanはAWS CloudShellで回しています。

## 今のところの結論

「無料枠が尽きた」という後ろ向きなきっかけでしたが、結果的にはCIの土台を一度見直すことになりました。

セルフホストrunnerは、立てるまでの手数はhosted runnerより多いです。GitHub App、IAM、SG、ephemeralのループ、ワークフローの段階移行と、決めることがそれなりにあります。

それでも、**変動費を増やさずにCIを自分の手元に戻せた**のは、個人開発の運用としては良かったと思っています。少なくともこのプロジェクトでは、この方向で続けます。

追記: その後、上で触れたscale-to-zero構成への移行を完了させました。今はジョブが来たときだけEC2が起動し、1ジョブ実行したら自己終了するので、常時起動はしていません（アイドル時は0台）。インスタンスタイプは `t4g.medium` と `t4g.large` をspotの在庫確保のために併記していますが、タスクの大きさで動的に選んでいるわけではなく、Swapも常に8GB固定です。

この移行で決めたことと踏んだ穴（instance profile の名前衝突、2GB マシンでの OOM、未マージの infra ブランチを個別に apply して壊した話）は、Zenn の別記事にまとめました。