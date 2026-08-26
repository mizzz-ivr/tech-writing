---
title: "2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信する"
status: draft
topics:
  - cloudflare
  - email
  - smtp
  - dns
source_repositories:
  - mizzz-ivr/tech-writing
published:
  qiita: null
  zenn: null
---

# 2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信する

> 実作業前に章立てと撮影ポイントを固定し、Cloudflare Dashboardの実測を追加しながら仕上げるドラフト。Secretや個人用destinationは公開しない。

## 独自ドメインの受信はある。次は送信経路をCloudflareへ寄せたい

今回扱うのは「メールボックスをCloudflareへ移す」話ではない。

現在のブランド / ドメイン方針では、公開ブランドのルートは `ivrm.jp`。いゔる。とmizzzを統合した個人Identityは `ivmz` とし、個人ポートフォリオのcanonicalは `ivmz.ivrm.jp`。`mizzz.jp` はWebの主URLから外し、旧リンク互換とメール資産のため維持する。

メールも同じIdentity設計に揃える。

- `ivmz@ivrm.jp` — Unified Personal / General。X / GitHub / 個人サイト等で案内する総合窓口
- `ivuru@ivrm.jp` — 「いゔる。」として対応するperson-facing From / Reply
- `mizzz@ivrm.jp` — 技術 / OSS / 個人開発などDeveloper文脈のFrom / Reply
- `contact@ivrm.jp` — ivRooom / Team / Community / Project
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy alias。原則として受信互換

今回の主目的は、**`ivrm.jp` の既存受信を壊さず、Cloudflare Email Sendingを送信経路として追加し、IdentityごとにFromを使い分けられる状態を作ること**。

`mizzz.jp` はlegacy aliasとして送信が本当に必要か確認し、必要な場合だけ追加でOnboardする。

## 参考にした2022年の記事と2026年現在の違い

参考にした記事:

- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

2022年の記事ではCloudflare Email Routingで受信し、送信にはGmail SMTPとGoogleアプリパスワードを使っていた。

2026年6月、Cloudflare Email ServiceにAuthenticated SMTP submissionが追加された。現在は `smtp.mx.cloudflare.net:465` へ認証付きSMTPで送信できる。

この記事では「Gmailを送信基盤にする」のではなく、Cloudflare Email Sending自体を送信基盤として検証する。

## 今回作る構成

```text
ivrm.jp
  ├─ ivmz@ivrm.jp       General / Unified Personal
  ├─ ivuru@ivrm.jp      Person-facing
  ├─ mizzz@ivrm.jp      Developer / OSS
  ├─ contact@ivrm.jp    ivRooom / Team
  └─ security@ivrm.jp   Security
       ↓
Cloudflare DNS
  ├─ Email Routing               ← 既存受信を維持
  └─ Email Service
       └─ Email Sending
            └─ smtp.mx.cloudflare.net:465
                 ↓
              外部宛先

mizzz.jp
  └─ contact@mizzz.jp            ← legacy alias
       └─ 原則受信互換
          必要な場合だけ送信側もOnboard
```

## 変更前のDNSと受信状態を記録する

設定前に `ivrm.jp` と `mizzz.jp` の両方を確認した。

確認対象:

- MX
- SPF
- DKIM
- DMARC
- Email Routing / 転送経路
- 用途別アドレスのrouting rule
- 実際の受信可否

`ivrm.jp` ではCloudflare Email Routing用のMX / SPF / DKIM / DMARCに加えて、`send.ivrm.jp` のAmazon SES系レコードとResend系DKIMも確認できた。

ここは「古そうだから消す」と判断しない。現行利用有無を確認し、Email Sending導入だけを理由に既存送信DNSを削除しない。

![変更前のivrm.jpメール関連DNS](./assets/01-before-ivrm-dns.png)

![変更前のmizzz.jpメール関連DNS](./assets/02-before-mizzz-dns.png)

公開版ではdestination address、記事に不要なorigin IP、無関係なDNSレコードをmask / cropする。

## FreeのままEmail Sendingを開くとWorkers Paidが要求された

変更前のEmail Sending画面も記録した。

今回のCloudflareアカウントはFreeプランで、Dashboardの `Email Sending` を開くと「メール送信は現在、Workers Paidプランでのみ利用可能」と表示され、Onboardへは進めなかった。

![Freeプランで表示されたEmail Sending有効化画面](./assets/00-email-sending-workers-paid-gate.png)

ここは記事上の重要な実測結果として残す。

つまり、本番でCloudflare Email Sending SMTPを使う場合は、少なくとも今回の環境ではWorkers Paidへの切り替えが実装gateになる。

## 先に受信Identityを完成させる

Paid化やEmail Sending Onboardの前に、受信側のIdentity設計を完成させる。

- `ivmz@ivrm.jp` をUnified Personal / Generalとして新規作成・受信確認
- `ivuru@ivrm.jp` の受信確認
- `mizzz@ivrm.jp` の受信確認
- `contact@ivrm.jp` の受信確認
- `security@ivrm.jp` の受信確認
- `contact@mizzz.jp` のlegacy受信確認

テストメールは同報でもよいが、各宛先としてroutingされたことを個別に確認する。

## `ivrm.jp` をCloudflare Email SendingへOnboardする

Workers Paidへ切り替えてEmail Sendingを採用すると決定した場合、Cloudflare Dashboardで `Email Service > Email Sending` を開き、まず `ivrm.jp` をOnboardする。

![Email SendingのOnboard Domain画面](./assets/03-onboard-ivrm-domain.png)

確定前に、Cloudflareが追加しようとしているDNSレコードを記録する。

![Onboard前のDNS追加Preview](./assets/04-onboard-dns-preview.png)

TODO: 実際に表示されたレコード種別・ホスト名を記載する。

## Onboard後のDNSを確認する

確認するポイント:

- Email Sending用のbounce / SPF / DKIM関連レコード
- 既存受信用MXが維持されていること
- SPFが同一ホストで重複していないこと
- DMARCに意図しない変更が入っていないこと
- SES / Resend系の既存レコードと意図しない競合がないこと

![Onboard後のivrm.jpメール関連DNS](./assets/05-after-ivrm-dns.png)

## SMTP専用のCloudflare API Tokenを作る

SMTP認証は次の値を使う。

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
Username: api_token
Password: Cloudflare API Token
Permission: Email Sending: Edit
```

![API Tokenの権限設定](./assets/06-api-token-permission.png)

Tokenそのものは記事・GitHub・Notion・スクリーンショットへ載せない。

## まずcurlで `ivmz@ivrm.jp` から送る

メールクライアントへ設定する前にSMTP endpoint単体で確認する。最初の総合個人Fromは `ivmz@ivrm.jp` とする。

```bash
export CF_API_TOKEN='***'

cat > mail.txt <<'EOF'
From: ivmz@ivrm.jp
To: <検証用宛先>
Subject: Cloudflare Email Sending SMTP test

Cloudflare Email Sending SMTP test.
EOF

curl --ssl-reqd \
  --url "smtps://smtp.mx.cloudflare.net:465" \
  --user "api_token:$CF_API_TOKEN" \
  --mail-from "ivmz@ivrm.jp" \
  --mail-rcpt "<検証用宛先>" \
  --upload-file mail.txt
```

実際の公開記事ではTokenと検証用宛先をマスクする。

![curlでSMTP送信に成功したターミナル](./assets/07-curl-smtp-success.png)

## Cloudflare Delivery Logsを確認する

SMTPで投入したメールがDelivery Logsへ載るか確認する。

TODO:

- status
- timestamp
- 公開可能な範囲のMessage-ID
- エラーが出た場合の内容

![Cloudflare Email Sending Delivery Logs](./assets/08-delivery-logs.png)

## 受信側でSPF / DKIM / DMARCを確認する

受信メールのAuthentication-Resultsを確認する。

```text
SPF:   TODO
DKIM:  TODO
DMARC: TODO
```

![受信メールの認証結果](./assets/09-authentication-results.png)

Gmail / Outlook等の複数宛先で、到着・迷惑メール判定も確認する。

## IdentityごとにFromを使い分ける

`ivmz@ivrm.jp` の送信成功後、用途別Fromも確認する。

- `ivuru@ivrm.jp` — 「いゔる。」としての返信
- `mizzz@ivrm.jp` — 技術 / OSS / Developerとしての返信
- `contact@ivrm.jp` — ivRooom / Teamとしての返信
- `security@ivrm.jp` — Security窓口

公開導線ではすべての個別アドレスを並べるのではなく、原則として次の3つを表に出す。

- General / Personal → `ivmz@ivrm.jp`
- ivRooom / Team → `contact@ivrm.jp`
- Security → `security@ivrm.jp`

`ivuru@ivrm.jp` と `mizzz@ivrm.jp` は問い合わせ内容や返信文脈に応じて使い分ける。

## 受信経路が壊れていないことを再確認する

Email Sending追加後も、変更前に受信できていたアドレスへ外部から送信して確認する。

![設定後の受信確認](./assets/10-inbound-still-working.png)

`contact@mizzz.jp` はlegacy aliasとして受信継続を確認する。

## `mizzz.jp` も送信可能にするか判断する

ここは最初からOnboardしない。

`contact@mizzz.jp` をlegacy aliasとして「受信だけ維持」で十分なら、`mizzz.jp` のEmail Sending Onboardは不要。

旧名義での返信・送信を継続する要件がある場合だけ、`mizzz.jp` も追加Onboardして同じ検証を行う。

この判断自体も記事に残す。

## 2022年の構成と比較する

| 項目 | 2022年参考記事 | 今回の2026年構成 |
|---|---|---|
| 受信 | Cloudflare Email Routing | 既存Email Routingを確認して維持 |
| 主メールドメイン | 独自ドメイン | `ivrm.jp` |
| 総合個人Identity | - | `ivmz@ivrm.jp` |
| 用途別Identity | - | `ivuru@ivrm.jp` / `mizzz@ivrm.jp` |
| legacy | - | `contact@mizzz.jp` |
| 送信SMTP | `smtp.gmail.com` | `smtp.mx.cloudflare.net` |
| 送信認証 | Googleアプリパスワード | Cloudflare API Token |
| Cloudflare SMTP submission | 当時なし | 2026年6月から提供 |
| 送信基盤 | Gmail | Cloudflare Email Service |
| 今回の実装gate | - | Workers Paid |

## 使ってみて分かった制約と注意点

現時点で実測済み:

- FreeプランのDashboardではEmail Sending有効化前にWorkers Paid購入を要求された
- 既存受信DNSとSES / Resend系の送信DNSが同居しているため、送信基盤変更時にDNS棚卸しが必要

今後確認する:

- Onboard時に実際に追加されるDNS
- SMTP port / TLS要件
- API Token権限
- Delivery Logs
- SPF / DKIM / DMARC実測
- transactional用途としての適性
- `mizzz.jp` を受信only legacyにした場合の運用

## 今のところの結論

まだEmail Sendingの本番送信検証は完了していない。

ただし、先にブランドと連絡先を整理したことで、単に「独自ドメインから送れればよい」ではなく、**`ivmz` を総合入口にし、`ivuru` / `mizzz` / `contact` / `security` を役割別Fromとして運用する**というゴールが明確になった。

記事の着地点は「Cloudflare SMTPが使えた」で終わらせず、既存受信を壊さず、Identityとlegacyドメインを整理した状態まで含める。

## 参考資料

- https://developers.cloudflare.com/email-service/get-started/send-emails/
- https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- https://developers.cloudflare.com/email-service/configuration/domains/
- https://developers.cloudflare.com/email-service/platform/pricing/
- https://developers.cloudflare.com/changelog/post/2026-06-08-smtp-submission/
- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

<!--
画像撮影時:
- API Token / Secretは絶対に含めない
- 個人用転送先を隠す
- Account ID / Zone IDは不要なら隠す
- Message-ID / recipientは必要なければマスク
- 加工前原本は公開assetsへ置かない

公開前:
- ブランド / ドメイン正本を再確認
- Cloudflare公式Docsの提供状態を再確認
- ivrm.jp / mizzz.jpの実測結果を再確認
- Secret / 個人情報 / 本番環境情報を確認
-->
