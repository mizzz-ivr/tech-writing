---
title: "CI runnerをscale-to-zeroに移したら、2GBの壁とTerraformのdesired stateにハマった"
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

# CI runnerをscale-to-zeroに移したら、2GBの壁とTerraformのdesired stateにハマった

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

設計図の上では、かなりきれいでした。

ジョブが来たら起きる。
ジョブが終わったら消える。
アイドル時は0台。

ところが実際に移してみると、問題になったのは「EC2を起動する仕組み」そのものより、**以前のrunnerが暗黙に持っていた運用条件**と、**Terraformがどのconfigurationを正解として見るか**でした。

この記事では、その2つに絞って書きます。

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

ネットワークは、個人開発のコストを考えてNAT Gatewayを置かない構成です。runnerにはpublic IPv4を付けますが、Security Groupはinboundを許可せず、外へ出る通信だけにしています。

GitHub Appの`workflow_job` webhookを入口に、API Gateway、Lambda、EventBridge、SQSを経てEC2 Spotを起動します。runnerはephemeralなので、仕事が終わればそのインスタンスごと消えます。

ここまでは、想定どおりでした。

## 1つ目の壁 — 2GBのrunnerは、きれいなエラーを残してくれない

新しいrunnerが起動し、GitHubへ登録され、ジョブも取り始めました。

ところが、重いCIだけが途中で落ちます。

あるジョブはOpenNextのbundle build付近でrunner自体が消え、GitHub Actions上ではstepが`null`のまま。十分なエラーログも残りませんでした。

別のDocker buildでは、`next build`が`Running TypeScript ...`あたりで`exit 255`。

一方で、Next.js buildを含まない軽いDocker検証は同じrunnerで通る。

共通点を並べていくと、原因はメモリに寄っていきました。

当時使っていた`t4g.small`は2GB RAMです。

2GBでも、checkoutして軽いscriptを実行するだけなら十分です。
でもNext.js、OpenNext、Docker buildのように複数のprocessがメモリを使うCIでは、突然厳しくなる。

さらに移行前のrunnerには、実運用の中で追加された8GBのswapがありました。

新しい構成ではprovisioningの仕組み自体をTerraform moduleへ置き換えたため、このような**後から足されたruntime tuningは、明示的に移さない限り新しいrunnerには存在しません。**

ここが一番大きなポイントでした。

**IaCへ移行しても、既存環境の運用知識まで自動的にIaCへ変換されるわけではない。**

machine imageやinstance typeだけを見て「同じようなEC2を作った」と考えると、以前の環境を実用に耐えさせていた設定が抜けることがあります。

対策として、user-dataで8GBのswapfileを用意しました。

```bash
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

さらにinstanceのfloorを`t4g.medium`の4GBへ上げました。現在はSpot capacityの候補として`t4g.medium`と`t4g.large`を渡しています。

ここは少し紛らわしいところです。

`t4g.large`は「OOMしたら大きなinstanceで自動retryする」ためではありません。jobの重さを見てinstance typeを選んでいるわけでもありません。

現在の構成では`instance_allocation_strategy`を明示しておらず、module既定の`lowest-price`です。`t4g.large`はSpot capacityの選択肢を広げるための候補で、swapはどちらでも8GB固定です。

修正後、重いCIも通るようになりました。

ここで残ったのは、「2GBでは足りなかった」という話だけではありません。

**移行前に確認すべきなのはinstance specだけではなく、そのmachineが本番運用の中で獲得した設定まで含めた“実際のruntime”である。**

## 2つ目の壁 — Terraformのstateがあっても、branchごとの「正解」は1つではない

OOM対策と並行して、infra側では複数の変更を進めていました。

たとえば、こんな2つです。

- 新しいrunnerのruntime設定を改善する変更
- 古いrunnerをTerraform管理から外す変更

どちらも未マージのPRとして存在し、同じ`main`から分岐しているとします。

このとき注意が必要なのが、**それぞれのbranchから順番に`terraform apply`すること**です。

1本目のbranchをapplyすると、そのbranchが持つconfigurationへAWSが収束します。

次に2本目のbranchへ切り替えてapplyすると、Terraformは当然、今checkoutされている2本目のconfigurationをdesired stateとして扱います。

もし2本目のbranchに1本目の変更が入っていなければ、Terraformから見ればそれは「存在すべき変更」ではありません。

結果として、1本目で入れた変更が2本目のapplyで戻ることがあります。

```text
main
 ├─ PR A: runner runtime改善
 └─ PR B: old runner decommission

PR Aから apply
  ↓
AWS = Aのdesired state

PR Bから apply
  ↓
AWS = Bのdesired state
  ↓
Aにしか無い変更は消える可能性がある
```

これはTerraformが壊れたわけではありません。

むしろTerraformは、非常に正しく動いています。

stateが覚えているのは、「どのresourceを管理しているか」です。

**何を正しい状態とするかは、apply時点のconfigurationが決めます。**

だから、同じstateを共有するinfraで複数の未マージbranchを個別にapplyすると、AWS上でbranch同士をmergeしてくれるわけではありません。

別々のdesired stateを、順番に適用しているだけです。

さらにdecommissionのような変更では、すでに実体が無くなったresourceのconfigurationが別branchに残っていると、「消えているから作る」という収束が起きることもあります。

ここから、infraの適用ルールをシンプルにしました。

**同じstateへ影響する関連変更は、reviewして`main`へ統合してから、統合済みのconfigurationをapplyする。**

複数のbranchを、cloud上で合成しない。

コードのmerge boundaryと、infraのapply boundaryをできるだけ揃える。

これはTerraformに限らず、「Git上のbranch」と「外部に存在するmutableな環境」を一緒に扱うときにかなり重要だと思います。

## 移行中に、旧runnerは本当に消えた

移行期間中は、旧runnerと新runnerをしばらく並べていました。

新しい方には`enable_job_queued_check = true`を入れていたので、旧runnerが先にジョブを取った場合、新runner側は「もうqueuedではない」と判断して無駄なEC2を起動しません。

つまり、新旧を並行稼働させながら、新しい経路だけを少しずつ検証できる構成です。

その最中、旧runnerのSpotインスタンスがAWSに回収されました。

`Server.SpotInstanceTermination`。

one-time Spotを常時runnerとして使う弱点が、そのまま現実になりました。

ただ、その時点では新しいephemeral runnerがCIを処理できる状態になっていました。

旧runnerは消えた。
でもCIは止まらなかった。

この出来事で、scale-to-zero側へ切り替えられていることを実運用でも確認できました。

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

ただ、今回の移行で一番残ったのはscale-to-zeroの設定値ではありません。

## 移行で見るようになった2つの境界

1つ目は、**コードに書かれている構成と、実際に運用されているruntimeの境界**です。

instance typeが同じでも、swap、package、user-data、cache、filesystem、環境変数などが違えば、同じrunnerではありません。

2つ目は、**Git上のbranchと、Terraformが収束させるdesired stateの境界**です。

複数の未マージbranchは、Git上ではただの並行作業です。
でも同じcloud環境へapplyした瞬間、それぞれが「自分こそ正解」として外部状態を書き換えます。

この2つを意識するようになってから、infra移行の前に見るものが増えました。

- 旧環境に後付けされたruntime設定は何か
- 新環境でそれを再現する必要があるか
- 同じstateへ影響する未マージ変更が他にないか
- applyするcommitは、実際にProductionへ持っていきたい統合状態か
- rollbackするとき、どのconfigurationへ戻すのか

ジョブがないなら、EC2も寝ていてほしい。

その小さな理由から始めたscale-to-zero移行でした。

今、ジョブがない時間のrunnerは0台です。

そしてapplyするときは、以前より少しだけ「今どの正解をAWSへ渡そうとしているのか」を見るようになりました。
