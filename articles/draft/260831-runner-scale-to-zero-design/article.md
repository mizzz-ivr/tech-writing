---
title: "CI runnerを0台にしたかっただけなのに、2GBの壁とTerraformの「正解」にぶつかった"
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

# CI runnerを0台にしたかっただけなのに、2GBの壁とTerraformの「正解」にぶつかった

最初に消したかったのは、EC2の待機コストでした。

ところが、移行を始めて最初に消えたのはコストではなく、**runnerそのもの**でした。

OpenNextのbuild途中。

GitHub Actionsのstepは`null`のまま。

きれいなOOMログもない。

さっきまでジョブを処理していたrunnerが、途中でいなくなっている。

「scale-to-zeroにして、使わない時間のEC2を0台にする」

やりたかったことは、それだけでした。

でも実際に移してみると、問題になったのはscale-to-zeroの仕組みそのものではありませんでした。

見えていなかったのは、2つです。

**旧runnerが運用の中で身につけていたruntime設定。**

そして、**Terraformがapplyするときに見ている“正解”の範囲。**

この記事は、その2つにぶつかった話です。

前回、private repositoryのGitHub Actions無料枠が尽きたのをきっかけに、AWSへARM64のself-hosted runnerを立てました。

そのときの話は、こちらにまとめています。

[GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた](https://qiita.com/mizzz-ivr/items/e4c663c7f5d3f82fd0a9)

今回は、そのrunnerを「24時間そこにいる1台」から、「必要なときだけ現れるrunner」へ変えた続きです。

## 月千円ちょっとを消すはずだった

最初のrunnerは、GravitonのSpotインスタンスを1台、常時起動していました。

これでCIは戻りました。

ただ、しばらく使うと気になるところも出てきます。

runnerは1台なので、ジョブは基本的に直列です。

複数のbranchをまとめてpushすると、後ろに待ち行列が伸びる。

そしてone-timeのSpotなので、AWSに回収されればそのrunnerは終わりです。

自動で次の1台を立てる仕組みもありません。

何より、ジョブが1件もない時間にもEC2は起きています。

月額では大きな金額ではありません。

でも、使っていないのに起きている。

それが少し気持ち悪い。

ジョブがないなら、EC2も寝ていてほしい。

だったら、runnerを常駐させるのをやめればいい。

そうして、webhook駆動のephemeral runnerへ移行することにしました。

## 設計図は、かなりきれいだった

欲しかった構成は単純です。

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

ジョブが来たら起きる。

1つ仕事をする。

終わったら消える。

誰も仕事をしていなければ、0台。

かなり理想的です。

自前で全部を組むのではなく、Terraform moduleを使いました。

候補にしていた`philips-labs/terraform-aws-github-runner`はarchive済みだったため、現在メンテされている後継の`github-aws-runners/terraform-aws-github-runner`へ切り替えています。2026年9月4日時点で利用しているのはv7.11系です。

ネットワークは、個人開発のコストを考えてNAT Gatewayを置かない構成です。

runnerにはpublic IPv4を付けますが、Security Groupはinboundを許可しません。

GitHub Appの`workflow_job` webhookを入口に、API Gateway、Lambda、EventBridge、SQSを経てEC2 Spotを起動する。

runnerはephemeralなので、ジョブが終わればインスタンスごと消える。

Terraformのplanも通る。

runnerもGitHubへ登録される。

軽いジョブも動く。

ここまでは、かなり順調でした。

そして重いCIを流しました。

## 最初に消えたのは、待機コストではなくrunnerだった

OpenNextのbundle build付近で、runnerが消えました。

GitHub Actionsを見ると、途中のstepは`null`。

「OOM Killerが動きました」と親切に書かれているわけでもありません。

別のDocker buildでは、`next build`が`Running TypeScript ...`付近で`exit 255`。

一方で、Next.js buildを含まない軽いDocker検証は同じrunnerで通ります。

軽いものは通る。

重いものだけ落ちる。

しかも落ち方が、あまり親切ではない。

共通点を並べていくと、かなり怪しいものが1つありました。

`t4g.small`。

RAMは2GBです。

checkoutしてscriptを動かす程度なら、2GBでも十分です。

でもNext.js、OpenNext、Docker buildが重なると、一気に余裕がなくなります。

「じゃあ2GBが犯人か」

半分は正解でした。

半分は、違いました。

## 犯人は2GB。だけではなかった

移行前のrunnerには、8GBのswapがありました。

最初から設計書にきれいに書かれていた設定ではありません。

実際に運用し、重いbuildに当たり、必要になって追加されたruntime tuningです。

そして今回、runnerのprovisioning方法そのものをTerraform moduleへ置き換えました。

そこで何が起きたか。

**EC2は新しくなった。IaCも新しくなった。でも、以前のrunnerが運用の中で獲得した設定までは自動で引っ越してこなかった。**

これが今回のOOMで一番大きかったポイントです。

IaCへ移行したからといって、既存環境の運用知識まで勝手にIaCへ変換されるわけではありません。

instance typeだけ見れば、同じようなARM64のEC2です。

でも実際のrunnerは違いました。

旧runnerにはswapがある。

新runnerにはない。

見た目のspec表だけでは、その差が見えません。

対策として、user-dataで8GBのswapfileを作るようにしました。

```bash
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

さらにinstanceのfloorを`t4g.medium`の4GBへ上げました。

現在はSpot capacityの候補として`t4g.medium`と`t4g.large`を渡しています。

ここは誤解しやすいので補足します。

`t4g.large`は「OOMしたら自動的に大きいinstanceでretryする」ためのものではありません。

jobの重さを見てinstance typeを選択しているわけでもありません。

現在の構成では`instance_allocation_strategy`を明示しておらず、module既定の`lowest-price`です。

`t4g.large`はSpot capacityの候補を広げるために含めていて、swapはどちらでも8GB固定です。

修正後、重いCIも通るようになりました。

runnerは消えない。

buildも終わる。

これで解決。

……と思いました。

## 直った。と思った。

OOM対策と並行して、infra側では別の変更も進んでいました。

例えば、こんな2つです。

- runnerのruntime設定を改善する変更
- 古いrunnerをTerraform管理から外す変更

どちらも同じ`main`から分岐した未マージのbranchだったとします。

Gitの上では、ただの並行作業です。

PR AとPR B。

それぞれ別々にreviewして、最後にmergeすればいい。

ところが、TerraformにはGitHubのPRという概念はありません。

Terraformが見るのは、**今この瞬間にcheckoutされているconfiguration**です。

PR Aのbranchからapplyする。

AWSはAのdesired stateへ収束する。

次にPR Bのbranchからapplyする。

今度はBのconfigurationがdesired stateになる。

もしBにAの変更が入っていなければ、Terraformから見るとAだけに存在する設定は「現在の正解」ではありません。

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
Aにしか無い変更は戻る可能性がある
```

先に直した設定が、後のapplyで消える。

一瞬、「Terraformに戻された」という感覚になります。

でも、ここで大事なのは逆でした。

## Terraformは、何も間違えていなかった

Terraformは非常に忠実に動いていました。

stateが覚えているのは、管理しているresourceです。

**何を正しい状態とするかは、apply時点のconfigurationが決めます。**

PR AとPR BがGit上で兄弟branchだからといって、TerraformがAWS上でA+Bへmergeしてくれるわけではありません。

Aをapplyしたら、Aが正解。

Bをapplyしたら、Bが正解。

ただそれだけです。

さらにdecommissionのような変更では、実体がすでに消えていても、別branchのconfigurationにresource定義が残っていれば「存在するべきresource」として再作成されることもあります。

Terraformは過去の意図を読んではくれません。

GitHubのPR一覧も見ません。

人間が「この2つは最終的に両方入る予定」と思っていても、それはapply時点のconfigurationに入っていなければ存在しないのと同じです。

ここから、infraの適用ルールをかなり単純にしました。

**同じstateへ影響する関連変更は、reviewして`main`へ統合してから、統合済みconfigurationをapplyする。**

複数branchをcloud上で合成しない。

Gitのmerge boundaryと、infraのapply boundaryをできるだけ揃える。

仕組みとしては地味です。

でも、このルールを決めたことで「今AWSへ渡している正解はどのcommitなのか」がかなり分かりやすくなりました。

## そして、旧runnerが本当に消えた

移行期間中は、旧runnerと新runnerをしばらく並行稼働させていました。

いきなり旧runnerを止めるのではなく、新しい経路が実際にCIを処理できることを確認してから切り替えるためです。

新しい方には`enable_job_queued_check = true`を入れています。

旧runnerが先にジョブを取った場合、新runner側は「もうqueuedではない」と判断し、無駄なEC2を起動しません。

これで新旧を並べながら、少しずつ新しい経路を試せます。

そして、その移行中。

最後の確認は、こちらが用意したテストではなくAWS側から来ました。

旧runnerのSpotインスタンスが回収されました。

`Server.SpotInstanceTermination`。

one-time Spotを常時runnerとして使う弱点が、そのまま現実になりました。

以前なら、そこでrunnerがいなくなります。

次のrunnerは自動では立ちません。

でも、その時点では新しいephemeral runnerがCIを処理できる状態になっていました。

旧runnerは消えた。

CIは止まらなかった。

結果的に、かなり分かりやすいcutover確認になりました。

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

常時起動runnerを置いていた頃は、何もしていない時間にもEC2が1台いました。

今は、ジョブがなければ0台です。

最初に欲しかった状態には、ちゃんと辿り着きました。

ただ、終わってみると一番印象に残ったのは、scale-to-zeroの設定値ではありませんでした。

## 最後に残ったのは、2つの「見えない状態」だった

今回見落としかけたものは、どちらも画面上では見えにくいものでした。

1つ目は、**コードに書かれた構成と、実際に動いているruntimeの差**です。

instance typeが同じでも、swap、package、user-data、cache、filesystem、環境変数が違えば、実際には同じmachineではありません。

長く動いている環境ほど、運用の中で後付けされた知識があります。

IaC移行では、その“見えない差分”まで棚卸しする必要があります。

2つ目は、**Git上のbranchと、Terraformが収束させるdesired stateの差**です。

GitではPR AとPR Bを並行して持てます。

でも同じcloud環境へapplyした瞬間、それぞれのbranchは「自分が正解」として外部状態を書き換えます。

だからinfra移行の前に、今はこのあたりを見るようになりました。

- 旧環境に後付けされたruntime設定は何か
- 新環境でそれを再現する必要があるか
- 同じstateへ影響する未マージ変更が他にないか
- applyするcommitは、本当にProductionへ持っていきたい統合状態か
- rollbackするとき、どのconfigurationへ戻すのか

最初に消したかったのは、月に千円ちょっとの待機コストでした。

途中でrunnerが消えました。

直したruntime設定も、別のdesired stateから見れば消える可能性がありました。

そして最後には、常時起動していたrunnerそのものが本当にいなくなりました。

今、ジョブがない時間のrunnerは0台です。

EC2は寝ています。

代わりに、applyする前の自分は以前より少しだけ起きています。
