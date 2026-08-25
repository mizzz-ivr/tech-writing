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

> この原稿は実作業前に章立てと撮影ポイントを固定したドラフト。`TODO` と画像プレースホルダーは実測後に埋める。

## 受信はできていた。でも `@mizzz.jp` から送信できなかった

TODO: 実際に困っていた状況を書く。

- `mizzz.jp` はムームードメインで保有
- 権威DNS / NameserverはCloudflare
- 独自ドメイン宛の受信はすでに動いている
- ロリポップは解約済み
- 今回は既存の受信を壊さず、送信だけCloudflare Email Sending SMTPで追加する

![変更前のCloudflare Email Service / DNS状態](./assets/01-before-email-service.png)

## 参考にした2022年の記事と、2026年現在の違い

参考にした記事:

- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

2022年の構成ではCloudflare Email Routingで受信し、送信にはGmail SMTPとGoogleアプリパスワードを使っていた。

Cloudflareは2026年6月8日にAuthenticated SMTP submissionをBeta提供した。現在はCloudflare Email Serviceから `smtp.mx.cloudflare.net:465` へ認証付きSMTPで送信できる。

TODO: 実際に採用した理由を追記する。

## 今回作る構成

```text
ムームードメイン
  └─ mizzz.jp
       ↓ Nameserver
Cloudflare DNS
  ├─ 既存の受信経路        ← 維持
  └─ Email Service
       └─ Email Sending
            └─ smtp.mx.cloudflare.net:465
                 ↓
              送信先
```

今回は「メールボックスサービスをCloudflareへ移す」作業ではない。既存受信は維持して、送信経路を追加する。

## 変更前のDNSと受信状態を記録する

変更前に以下を確認した。

- MX
- SPF
- DKIM
- DMARC
- Email Routing / 受信経路
- `@mizzz.jp` 宛の受信テスト

TODO: 実際の確認結果を、公開して問題ない範囲で記載する。

![変更前のメール関連DNSレコード](./assets/02-before-dns-records.png)

> スクリーンショットでは個人用転送先、Secret、不要なアカウント情報をマスクする。

## Cloudflare Email Sendingへ `mizzz.jp` をOnboardする

Cloudflare Dashboardで `Compute > Email Service > Email Sending` を開き、`Onboard Domain` から `mizzz.jp` を選択する。

Cloudflare公式ドキュメントでは、Email SendingのOnboard時に送信用のDNSレコードが追加される。送信用レコードは主に `cf-bounce` サブドメイン側へ作られ、既存のEmail Routing用レコードとは分離される。

![Email SendingのOnboard Domain画面](./assets/03-onboard-domain.png)

![Onboard前に表示された追加DNSレコード](./assets/04-onboard-dns-preview.png)

TODO: 実際に追加されたMX / SPF / DKIM / DMARCを確認して記載する。

## 追加されたDNSレコードを確認する

TODO: Onboard後の実際のDNSを記載する。

確認したいポイント:

- `cf-bounce.mizzz.jp` のMX
- `cf-bounce.mizzz.jp` のSPF
- Cloudflare Email Sending用DKIM
- `_dmarc.mizzz.jp`
- 既存受信用MXが維持されていること

![Onboard後のメール関連DNSレコード](./assets/05-after-dns-records.png)

ここで重要だったのは、**送信を追加するために受信用MXを消さない**ことだった。

## SMTP専用のCloudflare API Tokenを作る

SMTP認証では次の値を使う。

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
Username: api_token
Password: Cloudflare API Token
Permission: Email Sending: Edit
```

![API Tokenの権限設定](./assets/06-api-token-permission.png)

Tokenそのものはスクリーンショットにも記事にも載せない。

## まずcurlで最小構成のSMTP送信を試す

メールクライアントへ設定する前に、Cloudflare公式例に近い形でSMTPそのものが通るか確認する。

```bash
export CF_API_TOKEN='***'

cat > mail.txt <<'EOF'
From: <送信元の@yourdomain.example>
To: <検証用宛先>
Subject: Cloudflare Email Sending SMTP test

Cloudflare Email Sending SMTP test.
EOF

curl --ssl-reqd \
  --url "smtps://smtp.mx.cloudflare.net:465" \
  --user "api_token:$CF_API_TOKEN" \
  --mail-from "<送信元>" \
  --mail-rcpt "<検証用宛先>" \
  --upload-file mail.txt
```

TODO: 実行時に使った公開可能なコマンドへ調整する。

![curlでSMTP送信に成功したターミナル](./assets/07-curl-smtp-success.png)

## Cloudflare Delivery Logsを確認する

SMTPで投入したメールもREST API / Workers bindingと同じdelivery pipelineを通り、Delivery Logsへ記録される。

TODO: 実際のStatus、Message-ID等を記載する。

![Cloudflare Email Sending Delivery Logs](./assets/08-delivery-logs.png)

## 受信側でSPF / DKIM / DMARCを確認する

送信できただけでは終わりにせず、受信メールのAuthentication-Resultsを確認する。

```text
SPF:   TODO
DKIM:  TODO
DMARC: TODO
```

![受信メールの認証結果](./assets/09-authentication-results.png)

TODO: Gmail / Outlookなど複数宛先での受信結果、迷惑メール判定を追記する。

## 送信追加後も `mizzz.jp` の受信が壊れていないか確認する

最後に外部アドレスから `@mizzz.jp` へメールを送り、変更前と同じ受信経路で届くことを確認する。

![設定後の受信確認](./assets/10-inbound-still-working.png)

TODO: 結果を書く。

## 2022年の構成と比較する

| 項目 | 2022年参考記事 | 今回の2026年構成 |
|---|---|---|
| 受信 | Cloudflare Email Routing | 現行受信経路を維持 |
| 送信SMTP | `smtp.gmail.com` | `smtp.mx.cloudflare.net` |
| 送信認証 | Googleアプリパスワード | Cloudflare API Token |
| SMTP | Gmail | Cloudflare Email Service |
| Cloudflare SMTP submission | 当時なし | 2026年6月からBeta |
| 費用 | Gmail利用前提 | arbitrary recipientsはWorkers Paidが必要 |

Gmail Webの第三者アドレス向け「Send mail as」は2027年1月に終了予定と案内されているため、今回の記事ではGmailを送信基盤の中心にはしない。

## 使ってみて分かった制約と注意点

2026年8月時点で把握している主な注意点:

- Email SendingはBeta
- arbitrary recipientsへの送信にはWorkers Paidが必要
- SMTP submissionは `465` / Implicit TLSのみ
- `587` / STARTTLSは非対応
- `25` はoutbound submissionには使わない
- API Tokenは `Email Sending: Edit` が必要
- SMTPメッセージサイズ上限は5 MiB
- Cloudflare Email Serviceはtransactional email用途を中心とする

TODO: 実作業で発生した制約・エラーも追記する。

## 今のところの結論

TODO: 設定・送受信検証を終えてから書く。

候補となる結論の方向性:

- Cloudflare DNSをすでに使っているなら送信基盤をCloudflareへ寄せやすい
- `cf-bounce` 側へ送信用レコードが分離されるため、受信経路を意識して作業しやすかったか
- Gmail SMTPを別途送信基盤として使わずに済む価値
- Beta / Workers Paidを許容できる用途か

## 参考資料

- Cloudflare Email Service — Send emails
  - https://developers.cloudflare.com/email-service/get-started/send-emails/
- Cloudflare Email Service — SMTP
  - https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- Cloudflare Email Service — Domain configuration
  - https://developers.cloudflare.com/email-service/configuration/domains/
- Cloudflare Changelog — Authenticated SMTP submission now available in beta
  - https://developers.cloudflare.com/changelog/post/2026-06-08-smtp-submission/
- Gmail Help — Send emails from a different address or alias
  - https://support.google.com/mail/answer/22370
- 参考にしたQiita記事
  - https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

<!--
画像撮影時:
- API Token / Secretは絶対に含めない
- Cloudflare Account ID / Zone IDは不要なら隠す
- 個人用転送先メールアドレスは隠す
- DNS値は公開してよい情報か都度確認
- Message-ID / recipientは公開不要ならマスク

公開前:
- STYLE_GUIDE.md を確認
- Cloudflare公式Docsの更新日とBeta状態を再確認
- 実際のmizzz.jp設定結果を再確認
- Secret / 個人情報 / 本番環境情報を確認
- Qiita / ZennそれぞれのMarkdown差分を確認
-->
