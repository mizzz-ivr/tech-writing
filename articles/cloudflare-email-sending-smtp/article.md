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

> 実作業前に章立てと撮影ポイントを固定したドラフト。TODOと画像は実測後に埋める。

## 独自ドメインの受信はある。次は送信経路をCloudflareへ寄せたい

今回扱うのは「メールボックスをCloudflareへ移す」話ではない。

現在のブランド / ドメイン方針では、公開ブランドのルートは `ivrm.jp`、個人ポートフォリオのcanonicalは `mizzz.ivrm.jp`。`mizzz.jp` はWebの主URLから外し、旧リンク互換とメール資産のため維持する。

メールも同じ考え方に揃える。

- `mizzz@ivrm.jp` — 個人の主連絡先
- `contact@ivrm.jp` — Team / Community / Project
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy alias

今回の主目的は、**`ivrm.jp` をCloudflare Email Sending SMTPへOnboardし、主系メールアドレスから外部へ送信できる経路を作ること**。

`mizzz.jp` はlegacy aliasとして送信が本当に必要か確認し、必要なら追加でOnboardする。

## 参考にした2022年の記事と2026年現在の違い

参考にした記事:

- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

2022年の記事ではCloudflare Email Routingで受信し、送信にはGmail SMTPとGoogleアプリパスワードを使っていた。

2026年6月、Cloudflare Email ServiceにAuthenticated SMTP submissionが追加された。現在は `smtp.mx.cloudflare.net:465` へ認証付きSMTPで送信できる。

この記事では「Gmailを送信基盤にする」のではなく、Cloudflare Email Sending自体を送信基盤として検証する。

## 今回作る構成

```text
ivrm.jp
  ├─ contact@ivrm.jp
  ├─ mizzz@ivrm.jp
  └─ security@ivrm.jp
       ↓
Cloudflare DNS
  ├─ 既存の受信経路            ← まず確認して維持
  └─ Email Service
       └─ Email Sending
            └─ smtp.mx.cloudflare.net:465
                 ↓
              外部宛先

mizzz.jp
  └─ contact@mizzz.jp           ← legacy alias
       └─ 受信経路を確認
          必要な場合のみ送信側もOnboard
```

## 変更前のDNSと受信状態を記録する

設定前に `ivrm.jp` と `mizzz.jp` の両方を確認する。

確認対象:

- MX
- SPF
- DKIM
- DMARC
- Email Routing / 転送経路
- `mizzz@ivrm.jp` の受信可否
- `contact@ivrm.jp` の受信可否
- `security@ivrm.jp` の受信可否
- `contact@mizzz.jp` の受信可否

ここは推測で埋めない。実際のCloudflare設定と受信テストで確認した結果を書く。

![変更前のivrm.jpメール関連DNS](./assets/01-before-ivrm-dns.png)

![変更前のmizzz.jpメール関連DNS](./assets/02-before-mizzz-dns.png)

## `ivrm.jp` をCloudflare Email SendingへOnboardする

Cloudflare Dashboardで `Compute > Email Service > Email Sending` を開き、まず `ivrm.jp` をOnboardする。

![Email SendingのOnboard Domain画面](./assets/03-onboard-ivrm-domain.png)

確定前に、Cloudflareが追加しようとしているDNSレコードを記録する。

![Onboard前のDNS追加Preview](./assets/04-onboard-dns-preview.png)

TODO: 実際に表示されたレコード種別・ホスト名を記載する。

## Onboard後のDNSを確認する

確認したいポイント:

- Email Sending用のbounce / SPF / DKIM関連レコード
- 既存受信用MXが維持されていること
- SPFが同一ホストで重複していないこと
- DMARCに意図しない変更が入っていないこと

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

## まずcurlで `mizzz@ivrm.jp` から送る

メールクライアントへ設定する前にSMTP endpoint単体で確認する。

```bash
export CF_API_TOKEN='***'

cat > mail.txt <<'EOF'
From: mizzz@ivrm.jp
To: <検証用宛先>
Subject: Cloudflare Email Sending SMTP test

Cloudflare Email Sending SMTP test.
EOF

curl --ssl-reqd \
  --url "smtps://smtp.mx.cloudflare.net:465" \
  --user "api_token:$CF_API_TOKEN" \
  --mail-from "mizzz@ivrm.jp" \
  --mail-rcpt "<検証用宛先>" \
  --upload-file mail.txt
```

実際の公開記事では宛先など不要な情報をマスクする。

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

## 主系アドレスを用途別に確認する

`mizzz@ivrm.jp` の送信成功後、必要に応じて次も確認する。

- `contact@ivrm.jp`
- `security@ivrm.jp`

問い合わせフォームやアプリ側で使うFrom / Reply-Toについても、ブランド方針と揃える。

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
| 受信 | Cloudflare Email Routing | 現行受信経路を確認して維持 |
| 主メールドメイン | 独自ドメイン | `ivrm.jp` |
| legacy | - | `contact@mizzz.jp` |
| 送信SMTP | `smtp.gmail.com` | `smtp.mx.cloudflare.net` |
| 送信認証 | Googleアプリパスワード | Cloudflare API Token |
| Cloudflare SMTP submission | 当時なし | 2026年6月から提供 |
| 送信基盤 | Gmail | Cloudflare Email Service |

## 使ってみて分かった制約と注意点

実測後に更新する。

確認予定:

- Workers Paid要件
- Beta / 提供状態
- SMTP port / TLS要件
- API Token権限
- message size limit
- Delivery Logs
- transactional用途としての適性
- `ivrm.jp` と `mizzz.jp` を両方持つ場合の運用負荷

## 今のところの結論

TODO: 設定・送受信検証完了後に書く。

記事の着地点は「Cloudflare SMTPが使えた」で終わらせず、**ブランド整理で主ドメインを決めたうえで、送信元ドメインを無駄に増やさない構成にした**ところまで含める。

## 参考資料

- https://developers.cloudflare.com/email-service/get-started/send-emails/
- https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- https://developers.cloudflare.com/email-service/configuration/domains/
- https://developers.cloudflare.com/changelog/post/2026-06-08-smtp-submission/
- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

<!--
画像撮影時:
- API Token / Secretは絶対に含めない
- 個人用転送先を隠す
- Account ID / Zone IDは不要なら隠す
- Message-ID / recipientは必要なければマスク

公開前:
- ブランド / ドメイン正本を再確認
- Cloudflare公式Docsの提供状態を再確認
- ivrm.jp / mizzz.jpの実測結果を再確認
- Secret / 個人情報 / 本番環境情報を確認
-->
