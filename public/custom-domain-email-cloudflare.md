---
title: 独自ドメインを取得したあと、メールを送受信できるようにするまで — Cloudflareで構築してみた
tags:
  - Cloudflare
  - DNS
  - Email
  - SMTP
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
# 独自ドメインを取得したあと、メールを送受信できるようにするまで — Cloudflareで構築してみた

`ivrm.jp` という独自ドメインを使い始めたあと、Webサイトだけではなくメールも独自ドメインへ揃えたくなりました。

たとえば、こんなアドレスです。

```text
contact@example.com
me@example.com
security@example.com
```

ただ、ここで最初に勘違いしていたのが、**ドメインを取得しただけではメールは送受信できない**ということでした。

WebサイトはDNSを設定してホスティング先へ向ければ表示できますが、メールには別の経路が必要です。

今回、自分の環境ではCloudflare DNSを使っていたので、

- 受信: Cloudflare Email Routing
- 送信: Cloudflare Email Sending / SMTP

という構成を試しています。

この記事ではCloudflareを「無料でメールできるサービス」として紹介するのではなく、**独自ドメイン取得後に、メールを受信・送信できる状態へ持っていくには何が必要なのか**を、自分の構成を例に整理します。

> この記事は現在も実環境で検証中です。`ignorePublish: true` の下書きとして管理し、送信・認証・回帰テストまで完了してから公開します。

## 先に全体像

独自ドメインメールを使うには、大きく分けて次の3つが必要でした。

| 項目 | 役割 | 今回使うもの |
| --- | --- | --- |
| ドメイン / DNS | `example.com` のDNSレコードを管理する | Cloudflare DNS |
| 受信経路 | `name@example.com` 宛のメールをどこへ届けるか | Cloudflare Email Routing |
| 送信経路 | `name@example.com` をFromにして外部へ送る | Cloudflare Email Sending SMTP |

イメージするとこうなります。

```text
受信

外部の送信者
   ↓
name@example.com
   ↓ MX
Cloudflare Email Routing
   ↓
普段使っている受信先メールボックス


送信

メールクライアント / アプリ
   ↓ SMTP
Cloudflare Email Sending
   ↓
外部の受信者
```

ここで重要なのは、**受信と送信は別の仕組み**だということです。

## ドメインを取っただけではメールボックスはできない

自分は最初、ドメインをCloudflareへ向けてWebサイトが表示できたので、メールアドレスも同じように作れる感覚でいました。

実際には、DNS上で `@example.com` を所有していることと、メールを保管するInboxがあることは別です。

Cloudflare Email Routingでは、独自ドメイン宛のメールをVerified Destination Addressへ転送できます。

つまり今回の構成では、Cloudflareの中に新しいメールボックスを作るのではなく、

```text
ivmz@ivrm.jp
    ↓
Cloudflare Email Routing
    ↓
既存のメールボックス
```

という経路を作ります。

Cloudflare公式:

https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/

## まず「どんなメールアドレスが必要か」を決めた

技術設定より先に、どのアドレスを何に使うかを整理しました。

自分の場合は現在こうしています。

| Address | Role |
| --- | --- |
| `ivmz@ivrm.jp` | 個人の総合窓口 |
| `ivuru@ivrm.jp` | 「いゔる。」名義で対応する用途 |
| `mizzz@ivrm.jp` | Developer / OSS / 技術用途 |
| `contact@ivrm.jp` | ivRooom / Team / Community |
| `security@ivrm.jp` | Security |
| `contact@mizzz.jp` | 旧ドメイン互換用 |

すべてを公開するわけではなく、表に出す窓口は絞ります。

```text
General / Personal : ivmz@ivrm.jp
Team / Community   : contact@ivrm.jp
Security           : security@ivrm.jp
```

`ivuru@` と `mizzz@` は、問い合わせ内容や返信するIdentityによってFromを切り替えるために残しています。

これは必須の設計ではありませんが、独自ドメインを取った直後に `info@` や `contact@` を何となく増やすより、**誰が・どの文脈で使うアドレスなのかを先に決めておく**方が後から整理しやすかったです。

## 受信はMXとEmail Routingを設定する

メールの受信先を決めるのがMXレコードです。

今回の `ivrm.jp` ではCloudflare Email Routingを有効にして、Cloudflare側のMX / SPF / DKIM / DMARC関連レコードを確認しました。

変更前の状態を先にスクリーンショットへ残しています。

<!-- IMAGE: before ivrm.jp mail-related DNS. Publish only a masked/cropped copy. -->

この時点で確認したのは次の内容です。

- MX
- SPF
- DKIM
- DMARC
- Email Routing rule
- Destination Address

Destination Addressは実際の個人メールアドレスなので、記事や公開スクリーンショットには載せません。

### Routing Ruleを作る

たとえば `ivmz@ivrm.jp` を作る場合、Email RoutingでCustom Addressと転送先を紐付けます。

```text
Custom Address
ivmz@ivrm.jp

        ↓

Verified Destination Address
<普段使っているメールアドレス>
```

設定画面上にルールがあるだけでは十分ではないので、外部アドレスから実際にメールを送り、転送されることまで確認します。

今回の受信テスト対象は次の通りです。

```text
ivmz@ivrm.jp
ivuru@ivrm.jp
mizzz@ivrm.jp
contact@ivrm.jp
security@ivrm.jp
contact@mizzz.jp
```

複数宛先を1通でテストしても構いませんが、それぞれの宛先としてRoutingされたことは個別に確認します。

<!-- IMAGE: representative inbound mail to ivmz@ivrm.jp. Mask destination and unrelated inbox content. -->

## 受信できても、そのアドレスから送信できるわけではない

ここが今回一番分かりにくかったところです。

Email Routingで `ivmz@ivrm.jp` 宛のメールを受け取れるようになっても、それだけでは `ivmz@ivrm.jp` をFromにして外部へ送る経路はできません。

送信にはSMTPやメール送信APIなど、別の送信基盤が必要です。

以前なら、独自ドメインの受信だけCloudflareへ置き、送信には別のSMTPサービスを使う構成もありました。

2026年6月からCloudflare Email ServiceにはAuthenticated SMTP submissionが追加され、現在はCloudflare側にもSMTP送信経路があります。

Cloudflare公式:

https://developers.cloudflare.com/email-service/api/send-emails/smtp/

## 送信前に既存DNSを棚卸しした

今回 `ivrm.jp` のDNSを確認すると、Cloudflare Email Routingだけではなく、過去に使っていたAmazon SES / Resend系と思われる送信レコードも残っていました。

ここでやらなかったのが、

> もうCloudflareを使うから古そうなレコードは全部消す

という変更です。

DNSレコードだけでは、現在その送信基盤が使われているかまでは分かりません。

そのため、

1. DNSに何があるか確認する
2. Repository側でSES / Resendの実利用有無を調べる
3. 現在使っていないことを確認してから整理する

という順で進めています。

<!-- IMAGE: cropped DNS view showing relevant mail records only. -->

独自ドメインメールをあとから構成し直す場合は、**MX / SPF / DKIM / DMARCを先に記録してから変更する**のが安全だと感じました。

## Cloudflare Email Sendingを開いたらWorkers Paidが必要だった

送信側もCloudflareへ寄せようとして、DashboardからEmail Sendingを開きました。

自分の環境ではFreeプランのままだと、Email Sendingを有効化する前にWorkers Paidへの変更が必要という画面が表示されました。

<!-- IMAGE: Cloudflare Email Sending Workers Paid gate. -->

この部分は記事の主題ではありません。

独自ドメインメール自体を「無料で作れるかどうか」ではなく、**送信基盤として何を選ぶかによって費用や制約が変わる**という話です。

自分の場合は、Cloudflare Email Sendingを使うならこの時点が有料化の判断ポイントになります。

現在のCloudflare Workers Paidは最低月額5 USDです。

https://developers.cloudflare.com/workers/platform/pricing/

## Email Sendingを使う場合は送信ドメインをOnboardする

Cloudflare Email Sendingを採用する場合、まず送信元ドメインをEmail ServiceへOnboardします。

Cloudflare公式手順では、Dashboardから `Email Service > Email Sending > Onboard Domain` と進みます。

https://developers.cloudflare.com/email-service/get-started/send-emails/

Onboard時には `cf-bounce` サブドメイン側へ、bounce受信用MX、SPF、DKIMなどの送信用DNSレコードが追加されます。

今回の記事では、確定前に表示されるDNS Previewを必ず残します。

<!-- IMAGE: Email Sending Onboard Domain. -->

<!-- IMAGE: DNS records preview before confirmation. -->

設定後は、変更前との比較だけでなく、既存Email Routing用MXが壊れていないことも確認します。

## SMTPで実際に1通送ってみる

Cloudflare Email SendingのSMTP設定は現在次の通りです。

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
AUTH: PLAIN or LOGIN
Username: api_token
Password: Cloudflare API Token
Permission: Email Sending: Edit
```

Cloudflareは送信SMTPとしてport 465のImplicit TLSを提供しており、587のSTARTTLSは使いません。

最初はメールアプリへ設定する前に、`curl` でSMTP単体を確認します。

```bash
export CF_API_TOKEN='***'

cat > mail.txt <<'EOF'
From: ivmz@ivrm.jp
To: <test-recipient@example.com>
Subject: Custom domain SMTP test

Custom domain SMTP test.
EOF

curl --ssl-reqd \
  --url "smtps://smtp.mx.cloudflare.net:465" \
  --user "api_token:$CF_API_TOKEN" \
  --mail-from "ivmz@ivrm.jp" \
  --mail-rcpt "<test-recipient@example.com>" \
  --upload-file mail.txt
```

API TokenはSMTPのPasswordそのものなので、記事・GitHub・スクリーンショットには残しません。

<!-- IMAGE: successful curl SMTP submission. Mask recipient and any credential. -->

## 「届いた」で終わらずSPF / DKIM / DMARCも見る

独自ドメインからメールを送れたとしても、相手側で正しく認証されていなければ迷惑メール判定やなりすまし対策の問題が残ります。

そのため、受信したテストメールで次を確認します。

```text
SPF   : TODO
DKIM  : TODO
DMARC : TODO
```

ざっくり役割を整理すると、

- SPF: その送信サーバーがドメインから送ってよいか
- DKIM: メールへ電子署名を付け、改ざんされていないか確認する
- DMARC: SPF / DKIMを使ってFromドメインをどう検証・扱うか決める

という関係です。

Cloudflare Email Serviceでは送信用のSPF / DKIMを設定し、送信メールを認証します。

https://developers.cloudflare.com/email-service/concepts/email-authentication/

<!-- IMAGE: Authentication-Results showing actual SPF/DKIM/DMARC results. -->

ここは公開時に実測結果をそのまま書きます。最初からPASSした前提にはしません。

## 送信設定後に、受信が壊れていないかもう一度確認する

送信が成功したら終わりではなく、最初に確認した受信アドレスへもう一度外部からメールを送ります。

```text
Before
Email Routingで受信できる

        ↓

Email Sendingを追加

        ↓

After
同じアドレスで引き続き受信できる
```

特に既存MXやSPFを触った場合、送信だけ直って受信を壊してしまうのは避けたいところです。

<!-- IMAGE: representative inbound regression test after Email Sending setup. -->

## メールアプリから使う場合は「受信」と「送信」の設定が別になる

今回の構成は、Cloudflareに一般的なIMAPメールボックスを持つ構成ではありません。

受信はEmail Routingから普段のメールボックスへ転送し、送信はSMTPを使います。

そのため、SMTP対応のメールクライアントやアプリで独自ドメインFromを使う場合も、考え方は次のようになります。

```text
受信
既存Inbox ← Cloudflare Email Routing

送信
Mail Client → Cloudflare SMTP → Recipient
```

どのメールクライアントを使うかによって外部SMTPの設定方法や利用可能な機能は変わるので、Cloudflare側の設定とクライアント側の設定は分けて考えます。

## 最終的に理解したこと

独自ドメインを取ったあと、メールを使うために必要だったのは「メールアドレスを1個作る」だけではありませんでした。

自分の中では、次の順で考えると整理しやすかったです。

```text
1. 独自ドメインを取得する
2. DNSを管理できる状態にする
3. 使うメールアドレスを決める
4. MXを設定して受信経路を作る
5. 実際に受信できることを確認する
6. SMTP / APIなどの送信基盤を決める
7. SPF / DKIM / DMARCを確認する
8. 実際に外部へ送信する
9. 送信後も既存受信が壊れていないか確認する
```

Cloudflareを使う場合は、今回これを

```text
Cloudflare DNS
  + Email Routing
  + Email Sending SMTP
```

で構成しています。

最初は「独自ドメインを取ったから、このアドレスでメールも使いたい」というだけでしたが、受信・送信・認証がそれぞれ別の役割を持っていると分かると、構成を考えやすくなりました。

## 参考資料

- Cloudflare Email Routing rules and addresses
  - https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/
- Cloudflare Email Sending
  - https://developers.cloudflare.com/email-service/get-started/send-emails/
- Cloudflare SMTP
  - https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- Cloudflare Email authentication
  - https://developers.cloudflare.com/email-service/concepts/email-authentication/
- Cloudflare Workers pricing
  - https://developers.cloudflare.com/workers/platform/pricing/
