---
title: 独自ドメインを取得したあと、メールを送受信するには？3つの方法を比較してAWSで構築してみる
tags:
  - AWS
  - AmazonSES
  - DNS
  - Email
  - 個人開発
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: true
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# 独自ドメインを取得したあと、メールを送受信するには？3つの方法を比較してAWSで構築してみる

独自ドメインを取得してWebサイトには使えるようになった。

次に、こんなメールアドレスも使いたくなりました。

```text
contact@example.com
me@example.com
security@example.com
```

ただ、ドメインを取得しただけではメールを送受信できるようにはなりません。

独自ドメインのメールを使う方法を調べると、大きく次のような選択肢がありました。

1. お名前.comなどでメールサーバー / メールサービスを契約する
2. Cloudflare Email Routing / Email Sendingを使う
3. AWSでメール基盤を構築する

この記事では、まずこの3パターンの違いを整理したうえで、**今回はAWSを使って独自ドメインメールを構築する方法**を、`ivrm.jp` の実環境を例に紹介します。

> 現在は実装前のDraftです。`ivmz-home` のAWSメール基盤を実装・検証してから、実測値・スクリーンショット・トラブルシュートを追加して公開します。`ignorePublish: true` を維持します。

## まず、独自ドメインメールを使う方法を整理する

独自ドメインを取得したあとにメールを使う方法は1つではありません。

### 1. ドメイン事業者 / レンタルサーバーのメールサービスを契約する

一番分かりやすいのは、お名前.comなどが提供しているメールサービスやレンタルサーバーのメール機能を使う方法です。

お名前.comの公式ヘルプでも、登録したドメインでホームページやメールアドレスを運用するには別途サーバーが必要と案内されています。Webサイトが不要でメールだけ利用する場合は「お名前メール」のようなメール専用サービスも用意されています。

この方法は、

- メールボックス
- Webメール
- SMTP / IMAP等
- アカウント管理

といった一般的なメール環境をまとめて用意したい場合に分かりやすい選択肢です。

一方で、既にWebホスティングやDNSを別サービスで管理している場合は、メールだけのために追加サービスを契約することになります。

### 2. Cloudflare Email Routing / Email Sendingを使う

CloudflareをDNSとして使っている場合は、Email Routingで独自ドメイン宛のメールを既存のメールアドレスへ転送できます。

```text
name@example.com
    ↓
Cloudflare Email Routing
    ↓
普段使っているメールボックス
```

ただし、**受信できるようになることと、そのアドレスから送信できることは別です。**

CloudflareにはEmail Sendingもありますが、任意の外部宛先への送信はWorkers Paidが必要です。

今回もCloudflare Email Sendingを候補として検討し、実際にDashboardまで確認しましたが、最終的にはAWSを採用する方針にしました。

Cloudflare案は記事後半で「検討した代替案」として簡潔に触れます。

### 3. AWSで構築する

AWSではAmazon SESを中心に、独自ドメインの送信基盤を構築できます。

また、受信についてもSES Email ReceivingやMail Managerなどの仕組みがあります。ただし、SESの受信機能は一般的なIMAP / POPメールボックスそのものではありません。

そのため、AWSを選ぶ場合でも、

```text
送信
  Amazon SES

受信
  現行メール転送を維持
  または
  SES Email Receiving / Mail Manager等を設計
```

のように、送信と受信を分けて考える必要があります。

今回AWSを選ぶ理由は、単純に「最安だから」ではなく、既にAWSを他のインフラ用途でも利用する前提があり、送信・IAM・ログ・イベント処理などを同じ基盤で管理しやすいためです。

## 今回はAWSを使って構築する

この記事では、最終的に次の状態を目指します。

```text
独自ドメイン
ivrm.jp
   │
   ├─ 受信
   │    └─ 採用した受信経路
   │
   └─ 送信
        └─ Amazon SES
             ↓
           外部メールアドレス
```

ただし、AWSへ移行するからといって、現在正常に動いているMXレコードをいきなり変更しません。

まず既存構成を記録し、送信と受信を分けて移行します。

## 記事で答えること

- 独自ドメインを取得しただけでメールは使えるのか
- メールサーバーを契約する方法 / Cloudflare / AWSは何が違うのか
- 受信には何が必要か
- 送信には何が必要か
- MX / SPF / DKIM / DMARCは何をしているのか
- Amazon SESでできること / できないことは何か
- 既存DNSを壊さず移行するには何を確認するか
- 実際に送受信できたことをどう検証するか

## 現在の実環境

公開ブランドの主ドメインは `ivrm.jp`。

用途別のメールアドレスは次のように整理しています。

| Address | Role |
| --- | --- |
| `ivmz@ivrm.jp` | General / Personal |
| `ivuru@ivrm.jp` | Person-facing |
| `mizzz@ivrm.jp` | Developer / OSS |
| `contact@ivrm.jp` | ivRooom / Team |
| `security@ivrm.jp` | Security |
| `contact@mizzz.jp` | Legacy |

現在の受信経路は既存構成で稼働しているため、AWS移行を理由にMXを推測で変更しません。

## まず理解しておきたい: 受信と送信は別

独自ドメインを所有していること、メールを受信できること、そのアドレスから送信できることは別の話でした。

```text
Domain / DNS
   ├─ Incoming mail
   │    └─ MX → 受信基盤
   └─ Outgoing mail
        └─ SES / SMTP / API等の送信基盤
```

AWSを使う場合も、この2つを分けて考えます。

Amazon SESはメール送信だけでなく受信も扱えますが、SESの受信endpointはIMAP / POP3メールボックスではありません。SES Email ReceivingではReceipt Rulesを使ってS3 / Lambda / SNS等へメールを処理します。

通常のメールクライアントで直接Inboxとして使いたい場合は、SESとは別にmailbox providerが必要になります。

Amazon WorkMailは2026年4月30日から新規顧客受付を終了し、2027年3月31日にサービス終了予定のため、新規構成の候補にはしません。

## AWSでどの受信構成にするか

ここは実装前に確定します。

候補:

1. 現行受信経路を維持し、送信だけAmazon SESへ移す
2. Amazon SES Email Receiving + Receipt RulesでS3 / Lambda / SNS等へ処理する
3. 通常のメールボックスが必要ならAWS外を含む別mailbox providerを組み合わせる

最終記事では、実際に採用した構成だけを手順として説明し、不採用案は判断理由として簡潔に残します。

## 送信はAmazon SESを第一候補にする

`ivmz-home` のapplication email adapterはAmazon SESを第一候補として設計します。

実装時に確認する内容:

- SES identityとして `ivrm.jp` をverify
- DKIM
- SPF / custom MAIL FROMの要否
- DMARC alignment
- SES sandbox / production access
- IAM least privilege
- Production / Preview credential分離
- bounce / complaint handling
- application adapterからSESを呼び出す境界

## 変更前DNSを必ず記録する

AWS側を設定する前に、現在のMX / SPF / DKIM / DMARCを記録します。

`ivrm.jp` には過去構成由来のSES / Resend系と思われるDNSレコードも確認できているため、利用有無を確認するまで削除しません。

<!-- IMAGE: before DNS, masked/cropped -->

## AWS実装後に追記する章

以下は実装完了後に実測値で書きます。

### Amazon SESでドメインIdentityを作る

TODO: 実際のConsole画面と生成されたDNSレコード。

<!-- IMAGE: SES identity -->

### DKIM / MAIL FROM / SPFを設定する

TODO: 採用した設定と理由。

<!-- IMAGE: DNS preview / verified identity -->

### SandboxからProductionへ進める

TODO: 実環境で必要だった手続きと制約。

### `ivmz@ivrm.jp` から実際に送信する

TODO: application / SDK / SMTPのうち実際に採用した方法。

<!-- IMAGE: send success -->

### SPF / DKIM / DMARCを受信側で確認する

```text
SPF   : TODO
DKIM  : TODO
DMARC : TODO
```

<!-- IMAGE: Authentication-Results -->

### bounce / complaintを扱う

TODO: 実際に採用したSNS / Event Destinations等の構成と運用。

### 受信方式を構築する

TODO: 現行受信維持 / SES Email Receivingのどちらを採用したか、理由と構成を記載する。

AWSへ受信も移す場合は、Receipt RulesとS3 / Lambda / SNS等の実際の処理を記録します。

<!-- IMAGE: inbound architecture -->

### 受信を実測する

TODO: 採用した受信方式で `ivmz@ivrm.jp` 等が正常に届くことを確認。

<!-- IMAGE: representative inbound result -->

### 変更後も既存アドレスが壊れていないか確認する

TODO: `ivmz@` / `ivuru@` / `mizzz@` / `contact@` / `security@` / legacyの回帰テスト。

## 独自ドメイン取得後にやったこと

最終的には、実体験から次のようなチェックリストにまとめます。

- [ ] メールサービスの方式を比較する
- [ ] 使うメールアドレス / Roleを決める
- [ ] 現在のMX / SPF / DKIM / DMARCを記録する
- [ ] 受信方式を決める
- [ ] 送信providerを決める
- [ ] Amazon SES domain identityをverifyする
- [ ] DKIM / SPF / DMARCを設定する
- [ ] custom MAIL FROMの要否を決める
- [ ] sandbox / Production accessを整理する
- [ ] least-privilege IAMを用意する
- [ ] bounce / complaint handlingを用意する
- [ ] 実際に送信する
- [ ] SPF / DKIM / DMARCを実測する
- [ ] 実際に受信する
- [ ] 既存アドレスの回帰テストを行う

## 公開前チェック

- [ ] AWS側の受信方式を確定
- [ ] Amazon SES送信を実装
- [ ] Productionで実送信成功
- [ ] SPF / DKIM / DMARCを実測
- [ ] bounce / complaint handlingを確認
- [ ] 受信を実測
- [ ] 既存受信経路の回帰テスト
- [ ] 公開用スクリーンショットをmask / crop
- [ ] Secret / credential / destination / account情報を除去
- [ ] `ignorePublish: false`へ変更

## 今の結論

独自ドメインでメールを使う方法は、メールサービスを契約する方法、Cloudflareを使う方法、AWSで構築する方法など複数あります。

今回はAWSを選び、実際に構築・検証してから記事を完成させます。

AWSの公式手順を並べるだけではなく、実際のDNS・Identity設計・送受信検証・失敗と修正まで含めて記事化します。
