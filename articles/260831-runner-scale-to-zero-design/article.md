---
title: "CI runnerをscale-to-zeroにしたかっただけなのに、名前衝突・OOM・Terraformの巻き戻しを全部踏んだ"
status: draft
published_at: null
verified_at: 2026-09-04
article_type: case-study
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
  - repository: ivRooom/ivrm-web
    commit: 1a6f2e5e67dd67ca41f3e7951dd53e5f22307b46
published:
  qiita: null
  zenn: null
  note: null
---

# CI runnerをscale-to-zeroにしたかっただけなのに、名前衝突・OOM・Terraformの巻き戻しを全部踏んだ

最初に消したかったのは、月に千円ちょっとの待機コストでした。

ジョブがないなら、EC2も寝ていてほしい。
ジョブが来たら起きて、1つ仕事をしたら消える。

それだけの構成にしたかった。

前回、private repositoryのGitHub Actions無料枠が尽きたのをきっかけに、AWSへARM64のself-hosted runnerを立てました。

その話は[GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた](https://qiita.com/mizzz-ivr/items/e4c663c7f5d3f82fd0a9)にまとめています。

最初のrunnerは、GravitonのSpotインスタンスを1台、24時間起動しておく構成でした。

CIは戻りました。
でも、runnerは1台なのでジョブは直列です。複数のbranchをまとめてpushすると、後ろに待ち行列が伸びていく。

しかもone-timeのSpotなので、AWSに回収されればそのまま消えます。自動で次を立てる仕組みもありませんでした。

だったら、常時起動をやめればいい。

そうして始めたのが、webhook駆動のephemeral runnerへの移行でした。

ところが、最初の`terraform apply`は名前で止まりました。
次にrunnerは、ログも残さず消えました。
ようやく直したswapは、別branchからの`apply`で消えました。

EC2を眠らせたかっただけなのに。
気づけば、Terraformのstateとbranchの扱いまで含めて、かなり良い教材ができていました。

この記事は、その記録です。

## 作りたかったものは単純だった

目標はこれです。

```text
GitHub workflow_job=queued
  ↓
Webhook
  ↓
Lambda / Queue
  ↓
必要なときだけEC2 Spotを起動
  ↓
1 jobだけ実行
  ↓
runnerごと終了

idle時: 0台
```

自前で全部組むのではなく、Terraform moduleを使うことにしました。

候補にしていた`philips-labs/terraform-aws-github-runner`を確認すると、repositoryはarchive済みでした。そこで、現在メンテされている後継の`github-aws-runners/terraform-aws-github-runner`へ切り替えました。2026年9月4日時点で利用しているのはv7.11系です。

ネットワークも、個人開発のコストを考えてNAT Gatewayは置いていません。runnerにはpublic IPv4を付けますが、Security Groupはinboundを許可せず、外へ出る通信だけにしています。

GitHub Appの`workflow_job` webhookを入口に、API Gateway、Lambda、EventBridge、SQSを経てEC2 Spotを起動します。runnerはephemeralなので、仕事が終わればそのインスタンスごと消えます。

設計だけを見ると、きれいでした。

ここから、順番に壊れます。

## 1つ目の穴 — 最後の1リソースで、名前がぶつかった

最初の`terraform apply`は、ほとんど最後まで進みました。

そして、最後の方で止まりました。

```text
Error: creating IAM Instance Profile (ivrm-ci-runner-profile):
  409 EntityAlreadyExists
```

新しいmoduleは、runner用のinstance profileを`${prefix}-runner-profile`という名前で作ります。

最初は`prefix = "ivrm-ci"`にしていました。
すると生成される名前は`ivrm-ci-runner-profile`。

問題は、その名前を**旧runnerがすでに使っていた**ことでした。

他のAWSリソースにはランダムsuffixが付いていて衝突しないものも多かったので、少し油断していました。instance profileは違った。名前がそのまま、過去と現在をぶつけてきました。

対応は単純で、新しいrunner群のnamespaceを分けました。

```hcl
prefix = "ivrm-ghr"
```

runnerのlabelはprefixとは別なので、GitHub Actions側の`runs-on`を変える必要はありません。

この時点では、まだ新runnerで本番のCIを動かしていなかったので実害はほぼありませんでした。

ただ、ここで1つ目の教訓が残りました。

**名前はただの名前ではなく、移行境界そのものになる。**

新旧を並べるなら、IAMも含めてnamespaceを先に分けておくべきでした。

## 2つ目の穴 — runnerが、何も言わずに消えた

名前衝突を直して、新しいrunnerが起動するようになりました。

Webhookが届く。
EC2が起きる。
GitHubにrunnerが登録される。
ジョブも取り始める。

ここまでは良かった。

ところが、重いCIだけが途中で落ちます。

あるジョブはOpenNextのbundle build付近でrunner自体が消え、GitHub Actions上ではstepが`null`のまま。十分なエラーログも残りませんでした。

別のDocker buildでは、`next build`が`Running TypeScript ...`あたりで`exit 255`。

一方で、Next.js buildを含まない軽いDocker検証は同じrunnerで通る。

共通点を並べていくと、原因はメモリに寄っていきました。

使っていた`t4g.small`は2GB RAM。

そして、ここで一番痛かった事実に気づきます。

**旧runnerには8GBのswapを入れていたのに、新runnerへ移植するのを忘れていました。**

古い構成では、2GBだけでは厳しいことをすでに知っていた。
一度踏んだ穴だった。

それなのに、Terraform moduleへ移すときに「EC2をどう作るか」へ意識が寄りすぎて、「そのEC2を実用に耐えさせていた設定」を落としていました。

移行で失われるのは、コードだけではありません。
運用の中で後から足した小さな補強ほど、きれいな再構築のときに消えやすい。

対策として、user-dataに8GBのswapfileを戻しました。

```bash
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

さらにinstance floorを`t4g.medium`の4GBへ上げました。現在はSpot capacityの選択肢として`t4g.medium`と`t4g.large`を渡しています。

ここは誤解しやすいのですが、`t4g.large`は「OOMしたら大きなinstanceで自動retryする」ためではありません。jobの重さでinstance typeを選んでいるわけでもありません。

現在の構成では`instance_allocation_strategy`を明示しておらず、module既定の`lowest-price`です。`t4g.large`はSpotのcapacityを広げるためのfallbackで、swapも常に8GB固定です。

修正後、重いCIは通るようになりました。

2つ目の教訓は、少し地味です。

**IaCへ移したからといって、過去の運用知識まで自動でIaCになるわけではない。**

## 3つ目の穴 — 直したはずのswapが消えた

OOM対策を入れて、これで落ち着くと思いました。

次に壊したのはAWSでもmoduleでもなく、自分の`terraform apply`の順番でした。

当時、infraには2本の未マージPRがありました。

- 新runnerへswapを追加するbranch
- 旧runnerをTerraform管理から外すdecommission branch

どちらも同じ`main`から分岐していました。

私は最初にswap側のbranchから`terraform apply`しました。

新runnerへswapが入る。
CIも改善する。

そのあと、decommission側のbranchへ切り替えて、もう一度`terraform apply`しました。

ここで、直したはずのものが消えました。

decommission branchが持っていた`phase2.tf`は、swap修正前の状態です。

Terraformから見れば当然です。
今checkoutされているconfigurationがdesired stateなのだから、それに合わせます。

1本目のbranchで入れた変更を、2本目のbranchが巻き戻しました。

さらに悪いことに、decommission側には旧runnerのimport定義がまだ残っていました。実体のEC2はすでにterminated済みです。

その状態からconfigurationへ合わせようとして、**runner bootstrapの入っていない空のEC2まで1台作りました。**

「Terraformならstateがあるから安全」ではありませんでした。

stateが覚えているのは、どのresourceを管理しているかです。
何を正しいconfigurationとするかは、今その手元にあるコードが決めます。

つまり、別々の未マージbranchから順番に`apply`するということは、AWSへ別々の「正解」を交互に渡していたことになります。

この事故以降、infraの適用ルールを変えました。

**関連する変更はreviewして`main`へ統合してから、`main`の1つの状態を1回だけapplyする。**

複数branchの差分をAWS上で合成しない。

コードレビューの境界と、infra適用の境界を分けない。

3つ目の教訓は、これが一番大きかったです。

## その途中で、旧runnerは本当に消えた

移行期間中は、旧runnerと新runnerをしばらく並べていました。

新しい方には`enable_job_queued_check = true`を入れていたので、旧runnerが先にジョブを取った場合、新runner側は「もうqueuedではない」と判断して無駄なEC2を起動しません。

安全に切り替えるための並走期間でした。

その最中、旧runnerのSpotインスタンスがAWSに回収されました。

`Server.SpotInstanceTermination`。

最初の記事を書いたときから分かっていた、one-time Spotの弱点がそのまま現実になりました。

ただ、その頃には新しいephemeral runnerがCIを処理できていました。

旧runnerは消えた。
でもCIは止まらなかった。

狙ったcutoverではありません。
結果オーライです。

それでも、ここでようやく「新しい方へ移れた」と実感しました。

## 今は、ジョブがないと誰もいない

現在のrunnerは、ジョブが来たときだけ起きます。

- webhook駆動
- ephemeral runner
- idle 0台
- ARM64 / Spot
- `t4g.medium` / `t4g.large`をcapacity候補として利用
- allocation strategyはmodule既定の`lowest-price`
- 8GB swap固定
- 1 jobで自己終了

常時起動のrunnerを置いていた頃は、何もしていない時間にもEC2がそこにいました。

今は、ジョブがなければ0台です。

最初に欲しかった状態には、ちゃんと辿り着きました。

ただし、そこまでに覚えたことは「scale-to-zeroの作り方」だけではありませんでした。

## 3つの穴から残ったルール

今回の移行で、今後のinfra作業に残したルールは3つです。

1. **新旧を並べるなら、resource名のnamespaceまで先に分ける**
2. **移行前のマシンに後付けした運用設定を、コード以外も含めて棚卸しする**
3. **未マージの複数infra branchから、それぞれ`apply`しない**

どれも、書いてしまえば当たり前です。

名前がぶつかるなら変える。
2GBで足りないなら増やす。
別branchに別のdesired stateがあるなら、先に統合する。

でも、事故が起きるときは「知らなかったこと」より、「知っていたのに境界を越えるとき落としたこと」の方が多い気がします。

旧runnerにはswapがあった。
one-time Spotが消えることも知っていた。
Terraformがconfigurationへ収束することも知っていた。

それでも全部踏みました。

だから今は、applyの前に見るものが少し増えました。

`plan`だけではなく、**どのbranchの、どのcommitの、どの運用前提をapplyしようとしているのか**を見るようになりました。

## まとめ

ジョブがないなら、EC2も寝ていてほしい。

その小さな理由から始めたscale-to-zero移行でした。

最初のapplyは名前で止まり、
動き始めたrunnerはメモリで倒れ、
直したswapは別branchのTerraformが消しました。

そして最後には、旧runnerまでSpot回収で本当に消えました。

今、ジョブがない時間のrunnerは0台です。

静かになったのはAWSの請求だけではなくて、applyするときの自分の手順も少しだけ、です。

次にinfraを触るときは、たぶんもう少し静かに進められると思います。
