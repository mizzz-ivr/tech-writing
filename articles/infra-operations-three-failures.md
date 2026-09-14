---
title: "インフラ運用で3回ハマって、apply前に見るものが変わった"
emoji: "🧯"
type: "tech"
topics: ["aws", "terraform", "devops", "インフラ", "障害対応"]
published: false
---

最初のときは、ただの名前衝突だと思っていました。

次のときは、単純にメモリが足りなかっただけだと思っていました。

3回目に、ようやく「あ、これ全部同じところでつまずいているのかもしれない」と気づきました。

短い期間に、インフラまわりで3回ハマりました。

- instance profileの名前衝突
- 2GBクラスのマシンで発生したOOM
- mainへ入る前のinfraブランチから個別にapplyしてしまったこと

原因だけ見れば、全部違います。

でも、自分の作業を振り返ると共通点がありました。

**「いま実際にどうなっているか」を見る前に、「次にどう変えるか」へ進んでいた。**

この3回の失敗で、Terraformの書き方よりも先に、apply前の見方が変わりました。

## 最初は、名前が被っているだけだと思った

AWSのIAMまわりをTerraformへ寄せていたときでした。

instance profileをresourceとして追加して、planを確認して、そのまま作ろうとしました。

```hcl
resource "aws_iam_instance_profile" "app" {
  name = "app-instance-profile"
  role = aws_iam_role.app.name
}
```

コードだけ見れば、特に変なところはありません。

ところがapplyすると失敗しました。

同じ名前のinstance profileが、AWS側にすでに存在していたからです。

その瞬間は、かなり単純に考えていました。

「じゃあ名前を変えれば通るか」

でも、そこで止まりました。

別名で作ったら、似た用途のinstance profileが2つできます。

どちらが現行なのか。
どのEC2がどちらを使っているのか。
古いものを消してよいのか。

問題が消えるどころか、むしろ分かりにくくなります。

ここで初めて、Terraform側だけを見ていたことに気づきました。

Terraformに定義がないからといって、AWSにも存在しないとは限りません。

既存resourceをTerraform管理へ寄せるなら、新規作成ではなくimportが必要な場合があります。

```bash
terraform import aws_iam_instance_profile.app app-instance-profile
```

この件のあと、名前が一意になりやすいresourceを追加するときは、コードを書く前にCloud側も見るようになりました。

ただ、この時点ではまだ「TerraformとAWSの状態を合わせる話」だと思っていました。

次のトラブルが起きるまでは。

## 次は、アプリが落ちたと思った

別の日、サービスが不安定になりました。

最初に疑ったのはアプリケーションです。

ログを見る。
processを見る。
再起動する。

一度は戻る。

でも、しばらくするとまたおかしくなる。

アプリ側の処理を追いながら、なんとなく噛み合わない感じがありました。

そこでOS側を見ました。

原因はOOMでした。

2GBクラスの小さなマシン上で複数のprocessやcontainerが動いていて、メモリの余白がほとんど残っていませんでした。

```bash
free -h
```

```bash
ps aux --sort=-%mem | head
```

kernel logも確認します。

```bash
journalctl -k | grep -i -E "oom|killed process|out of memory"
```

そこでようやく、アプリが突然おかしくなったのではなく、OSからprocessを落とされていたことが分かりました。

普段は動いていたので、気づきにくかったです。

Node.js、Docker、reverse proxy、monitoring、databaseやcache。

一つずつは大きくなくても、積み重なると2GBはすぐに狭くなります。

さらにbuildやdeployのような一時的な負荷が重なると、普段は耐えている構成でも限界を超えます。

このとき、自分の中で少し引っかかりました。

前回は「Terraformに書かれているもの」しか見ていなかった。

今回は「アプリのログ」しか見ていなかった。

どちらも、**自分がいま触っている範囲だけを見て、実際の状態を見落としていた**という意味では似ていました。

それでも、まだ偶然だと思っていました。

3回目までは。

## 3回目は、apply自体は成功した

infraの変更をbranchで作業していました。

まだmainへmergeしていませんでしたが、変更内容は確認済みで、Terraformとしてもapplyできる状態でした。

だから、そのbranchから個別にapplyしました。

失敗はしませんでした。

むしろ、きれいに通りました。

Cloud側の構成も意図した通り変わりました。

一見すると成功です。

でも、その瞬間にこうなりました。

```text
Git main
  ↓
旧構成

作業branch
  ↓
新構成

Cloud
  ↓
新構成
```

本番環境だけが、mainより先に進みました。

ここでかなり嫌な感じがしました。

もしこのあと別の作業を始めたら？

数日空いたら？

branchを作り直したら？

別の人がmainだけ見たら？

個人開発でも、「あとでmergeすればいい」は思ったより危ないです。

infraはコードを変更しただけでは終わりません。

applyした瞬間、Gitの外にある実環境が変わります。

この3回目で、ようやく最初の2件とつながりました。

instance profileのときは、TerraformとAWSがずれていた。

OOMのときは、アプリへの認識とRuntimeの実態がずれていた。

今回は、Git mainとCloudがずれた。

問題の種類は違うのに、自分がやっていたことは同じでした。

**「自分が見ている状態」と「実際の状態」が一致している前提で進めていた。**

## そこで、apply前に4つ見るようになった

この3件以降、本番infraを変更するときに最初に見るものを決めました。

```text
Git     : どの変更を本番へ出そうとしているか
State   : Terraformは何を管理していると思っているか
Cloud   : 実際には何が存在しているか
Runtime : その構成を動かす余力があるか
```

以前は、まずコードを開いていました。

今は先に現状を見ます。

Gitでは、いまどこにいるかを確認します。

```bash
git status
git branch --show-current
git log -1 --oneline
```

Terraformでは、少なくともformat、validate、planを見ます。

```bash
terraform fmt -check
terraform validate
terraform plan
```

必要ならstateも確認します。

```bash
terraform state list
```

名前が衝突しそうなresourceなら、Cloud側の現物も確認します。

サーバー構成を変えるなら、CPUだけではなくmemoryやdiskの余白も見ます。

ここで大事なのは、毎回すべてのコマンドを機械的に打つことではありません。

**「いま見ている世界が、本番の実態と一致しているか」**を確認するための材料として使っています。

## planが通っても、GitとRuntimeまでは見てくれない

Terraformでは`terraform plan`がかなり重要です。

これは今も変わりません。

ただ、今回の3件で、planに全部を期待してはいけないことも分かりました。

既存resourceとの関係はCloud側を見る必要があります。

OOMはplanでは分かりません。

未merge branchからapplyしてよいかどうかもTerraformは判断してくれません。

TerraformはTerraformの範囲を見てくれます。

その外側にあるGit運用やRuntime capacityは、自分で見る必要があります。

## 今は、変更より先に現状を見る

この3件が起きる前は、infra作業を始めるとまず「何を変えるか」を考えていました。

今は順番が逆です。

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

instance profileの名前衝突も、OOMも、未merge branchからのapplyも、技術的な原因は全部違います。

でも、自分にとっては同じ学びになりました。

**変更内容を確認する前に、今の状態を確認する。**

インフラでは、コードの外に本番があります。

だからapply前に見るべきなのは、Terraformの差分だけではありませんでした。

Git、state、Cloud、Runtime。

この4つを見るようになってから、少なくとも「自分が今どの状態を相手にしているのか」が分からないままapplyすることは減りました。

3回ハマって、やっとそこに気づきました。

## 参考資料

- [Import existing resources - Terraform](https://developer.hashicorp.com/terraform/cli/import)
- [terraform plan command - Terraform](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [State - Terraform](https://developer.hashicorp.com/terraform/language/state)
- [Out of Memory Management - Linux Kernel Documentation](https://docs.kernel.org/mm/oom.html)
- [IAM roles for Amazon EC2 - AWS Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
