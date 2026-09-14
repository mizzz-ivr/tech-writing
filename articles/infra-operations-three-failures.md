---
title: "インフラ運用で3回ハマって、apply前に見るものが変わった"
emoji: "🧯"
type: "tech"
topics: ["aws", "terraform", "devops", "インフラ", "障害対応"]
published: false
---

インフラを触っていて、短い期間に3回続けてハマりました。

ひとつは、**instance profileの名前衝突**。

ひとつは、**2GBクラスの小さなマシンで起きたOOM**。

もうひとつは、**まだmainへ入っていないinfraブランチの変更を、個別にapplyしてしまったこと**。

どれも、あとから振り返ると「そんなに難しい話ではない」です。

でも実際に作業しているときは、それぞれ別の問題に見えていました。

名前が衝突した。
メモリが足りなかった。
Terraformの変更を適用した。

ところが3件を並べると、共通していたのは技術そのものよりも、**いま何が存在していて、どの状態を正として、どこまで変更してよいかを確認する前に先へ進んでしまったこと**でした。

今は、applyの前に見るものを少し変えています。

## 1件目: instance profileを作ろうとしたら、同じ名前がすでにあった

AWSでIAM Roleまわりを整えていたとき、instance profileをTerraform側で管理しようとして失敗しました。

作成しようとした名前が、AWS側にすでに存在していたためです。

たとえばTerraformでは、こんなresourceを追加できます。

```hcl
resource "aws_iam_instance_profile" "app" {
  name = "app-instance-profile"
  role = aws_iam_role.app.name
}
```

コードだけを見ると、特におかしくありません。

問題は、AWS側ですでに同名のinstance profileが作られていたことでした。

Terraformにとっては「新しく作るresource」でも、AWSから見れば「その名前はもう使われている」。

結果として作成時に衝突します。

最初は単純に名前を変えれば通るようにも見えました。

でも、そこで別名を作ってしまうと、既存resourceを残したまま似た用途のinstance profileが増えます。

それでは、

- どちらが現行なのか
- どのEC2がどちらを使っているのか
- 古いものを消してよいのか

が余計に分かりにくくなります。

そこで先に確認するようにしたのが、**「Terraformにない = 存在しない」ではない**ということでした。

既存resourceをTerraform管理へ寄せるなら、必要なのは新規作成ではなくimportです。

```bash
terraform import aws_iam_instance_profile.app app-instance-profile
```

もちろん、実際のresource addressやimport IDは構成に合わせて確認します。

重要だったのはコマンドよりも、作成前にAWS側の現物を見ることでした。

今はIAMやネットワークなど、名前が一意になりやすいresourceを追加するとき、先に次を確認しています。

```text
1. Cloud側に同名・同用途のresourceが存在しないか
2. Terraform stateにすでに入っていないか
3. 既存resourceをimportすべきか
4. 本当に新規作成でよいか
```

TerraformのコードだけをSource of Truthだと思っていると、手作業や過去の構成で残っているresourceを見落とします。

実環境をTerraformへ寄せている途中では、特にこのズレが起こります。

## 2件目: アプリの問題だと思ったら、2GBのメモリが尽きていた

別の日、サービスが不安定になりました。

最初はアプリケーション側の不具合を疑いました。

ログを見る。
プロセスを見る。
再起動する。

一時的には戻る。

でも、しばらくするとまたおかしくなる。

調べていくと、原因はOOMでした。

小さなインスタンス上で複数のprocessやcontainerを動かしていて、合計のメモリ使用量が限界へ近づいていました。

Linuxでは、メモリが足りなくなるとOOM Killerがprocessを終了させることがあります。

確認するときは、たとえば次のような情報を見ます。

```bash
free -h
```

```bash
ps aux --sort=-%mem | head
```

systemd環境なら、kernel logやjournalも手掛かりになります。

```bash
journalctl -k | grep -i -E "oom|killed process|out of memory"
```

ここで反省したのは、CPU使用率やアプリログだけで「アプリが落ちた」と考えていたことでした。

2GB程度のマシンでは、

- Node.js process
- Docker daemon
- database / cache
- reverse proxy
- monitoring agent
- buildや一時処理

のようなものを少しずつ積み上げるだけでも、余裕は思ったほど残りません。

しかも普段は動いているため、通常時の使用量だけを見ると問題が見えにくいです。

buildやdeploy、アクセス増加、重いbatchなどが重なった瞬間だけ限界を超えることがあります。

この件以降、サーバーサイズを見るときにvCPUだけではなく、**平常時に何GB空いているか**を見るようになりました。

「今動いているか」ではなく、

**「一時的に使用量が増えても耐えられる余白があるか」**

を見る感じです。

小さな環境を使うこと自体が悪いわけではありません。

個人開発ではコストを抑えたいので、小さなインスタンスを選ぶことも多いです。

ただ、その場合は「2GBで動く」だけでなく、2GBという制約を運用ルールに含める必要がありました。

たとえば自分なら、次のどれかを検討します。

- 常駐processを減らす
- buildを別環境へ逃がす
- containerごとにmemory limitを設定する
- swapを使う場合は用途と副作用を理解して設定する
- memory metricsへalertを設定する
- 継続的に余裕がないならinstance sizeを上げる

OOMが起きたあとに再起動するだけだと、原因は残ったままです。

## 3件目: infraブランチを個別applyしたら、Gitの状態とCloudの状態がずれた

3件の中で一番運用を変えるきっかけになったのがこれでした。

infraの変更をbranchで作業していました。

まだmainへmergeしていない状態です。

変更内容自体は確認していて、applyもできる状態でした。

そこで、そのbranchから個別にapplyしました。

技術的には通ります。

Cloud側も変更されます。

でも、その時点でこうなりました。

```text
Git main
  ↓
まだ旧構成

作業branch
  ↓
新構成

Cloud
  ↓
新構成がすでに適用済み
```

つまり、**mainと本番環境が一致しない時間**を自分で作ってしまいました。

一人で触っていると、「このbranchをあとでmergeすればいい」と考えやすいです。

ただ、その間に別の変更を入れたり、数日空いたり、branchを作り直したりすると、一気に危険になります。

特にinfraはアプリコードと違い、Git上の変更だけでは終わりません。

applyした瞬間に外部の実環境が変わります。

そのため、

**「コードが正しいか」だけではなく「どのGit refから本番を変更してよいか」**

を決める必要がありました。

今は、少なくとも本番infraについては次の流れへ寄せています。

```text
branchで変更
    ↓
terraform fmt / validate
    ↓
planを確認
    ↓
PR
    ↓
CI / review
    ↓
mainへmerge
    ↓
mainを基準にapply
```

CI/CDで完全自動化するか、最後のapplyだけ手動にするかはprojectによって変わります。

ただし、**本番変更の基準refはmain**というルールは崩さないようにしています。

緊急対応で例外が必要なら、例外であることを明示して、直後にGit側へ状態を戻します。

## 3つとも「その場では合理的」に見えていた

面白かったのは、どの事故も作業中には極端におかしな操作をした感覚がなかったことです。

instance profileがないと思ったから作る。

サーバーが落ちたからアプリを調べる。

完成したinfra変更があるからapplyする。

ひとつずつ見ると、それなりに自然です。

でも足りていなかった確認を並べると、かなり似ています。

```text
AWS / Cloudに何があるか
Terraform stateに何があるか
Git mainに何があるか
実際のserver resourceにどれだけ余裕があるか
```

自分はコードや設定ファイルから作業を始めることが多かったのですが、インフラでは**外に存在する状態**を先に見る必要がありました。

## apply前チェックを増やした

この3件のあと、Terraformで本番変更をするときに簡単な確認を入れるようになりました。

まずGitです。

```bash
git status
git branch --show-current
git log -1 --oneline
```

次にTerraformです。

```bash
terraform fmt -check
terraform validate
terraform plan
```

必要ならstateも確認します。

```bash
terraform state list
```

そして、追加・変更するresourceに既存resourceとの衝突可能性があるならCloud側も確認します。

サーバー構成を変えるときは、CPUだけでなくmemoryやdiskの余白も見ます。

ここで大事なのは「このコマンドを全部毎回打つこと」ではありません。

自分が確認したいのは、次の4つです。

```text
Git     : どの変更を本番へ出そうとしているか
State   : Terraformは何を管理していると思っているか
Cloud   : 実際には何が存在しているか
Runtime : その構成を動かす余力があるか
```

この4つがずれている状態でapplyすると、問題が起きたときの切り分けが急に難しくなります。

## planが通っただけでは安心できなかった

Terraformを使っていると、`terraform plan`をしっかり見ることが重要です。

これは今も変わりません。

ただ、今回の3件で分かったのは、planだけでは見えないものもあることでした。

instance profileのようにCloud側の既存resourceとの関係を見る必要があることもあります。

OOMはTerraformのplanでは分かりません。

未merge branchからapplyしてよいかどうかもTerraformは判断してくれません。

Terraformが判断できるのはTerraformの範囲です。

Gitの運用やruntime capacityまで含めて安全にするのは、その外側にある運用でした。

## 今は「何を変更するか」より先に「今どうなっているか」を見る

以前は、infra作業を始めるとまずコードを開いていました。

今は少し順番が変わりました。

```text
現状を見る
  ↓
差分を作る
  ↓
planを見る
  ↓
Git上で確定させる
  ↓
applyする
  ↓
適用後を観測する
```

instance profileの名前衝突も、OOMも、未merge branchからのapplyも、原因そのものは別です。

でも自分の中では、全部「現状確認の不足」という同じカテゴリに入りました。

インフラは、コードを書き終えた時点ではまだ変更されていません。

applyした瞬間に、外の世界が変わります。

だからこそ、apply前にはコードだけではなく、Git・state・Cloud・runtimeを見る。

**変更内容を確認する前に、まず今の状態を確認する。**

この3回の失敗で、一番変わったのはそこでした。

## 参考資料

- [Import existing resources - Terraform](https://developer.hashicorp.com/terraform/cli/import)
- [terraform plan command - Terraform](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [State - Terraform](https://developer.hashicorp.com/terraform/language/state)
- [Out of Memory Management - Linux Kernel Documentation](https://docs.kernel.org/mm/oom.html)
- [IAM roles for Amazon EC2 - AWS Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
