# Cloudflare Email Sending SMTP 記事用スクリーンショット計画

`article.md` の章立てに対応する撮影チェックリスト。

## 撮影ルール

- API Token / Secret / passwordは絶対に映さない
- 個人用転送先メールアドレスは隠す
- Account ID / Zone ID / Message-IDは記事上不要なら隠す
- ブラウザ全画面ではなく、記事で説明するUIが読める範囲へトリミングする
- DNSレコードは「何が追加されたか」が分かる範囲を優先する
- 作業前 / 作業後を同じ粒度で撮る
- 元画像は加工前も保持し、公開用コピーのみマスクする

## 必須画像 10枚

### 01-before-email-service.png

**タイミング:** 何も変更する前

**撮るもの:** Cloudflare `Compute > Email Service` の現状。Email Routingが利用中なら、その状態が分かる画面。

**記事で伝えること:** 「受信はすでに動いているが、Email Sendingはまだ設定していない」という開始地点。

**マスク:** destination addressなど個人メール。

### 02-before-dns-records.png

**タイミング:** Onboard前

**撮るもの:** `mizzz.jp` のメール関連DNS。MX / SPF / DKIM / DMARCが分かるように絞り込む。

**記事で伝えること:** 既存受信を壊さないため変更前状態を記録した。

**マスク:** 不要なレコード、公開不要値。

### 03-onboard-domain.png

**タイミング:** `Email Sending > Onboard Domain`

**撮るもの:** `mizzz.jp` を選択する画面。

**記事で伝えること:** Cloudflare Email Sendingへの入口。

**注意:** Confirm / Doneを押す前に撮る。

### 04-onboard-dns-preview.png

**タイミング:** Onboard確定直前

**撮るもの:** Cloudflareが追加予定として表示するDNSレコード一覧。

**記事で伝えること:** Email Sending用に何が追加されるか。特に `cf-bounce` 側のMX / SPF / DKIM / DMARC。

**最重要:** この画面は設定後に再現しにくい可能性があるので必ず撮る。

### 05-after-dns-records.png

**タイミング:** Onboard完了後

**撮るもの:** DNSへ実際に追加されたメール送信用レコード + 既存受信用MXが残っていること。

**記事で伝えること:** 送信用DNSと受信用DNSの共存。

### 06-api-token-permission.png

**タイミング:** SMTP専用API Token作成時

**撮るもの:** Permissionで `Email Sending: Edit` を選択している画面。

**記事で伝えること:** SMTP passwordとして使うTokenに必要な最小権限。

**絶対に撮らない:** 発行後のToken文字列。

### 07-curl-smtp-success.png

**タイミング:** 最初のSMTP送信成功時

**撮るもの:** `curl` 実行と成功が分かるターミナル。

**記事で伝えること:** メールクライアントより前にSMTP endpoint単体を検証した。

**マスク:** Token、個人メールアドレス。Tokenは環境変数参照のコマンドだけを映す。

### 08-delivery-logs.png

**タイミング:** curl送信直後

**撮るもの:** Cloudflare Email Sending Delivery Logsの成功レコード。

**記事で伝えること:** SMTP submissionもCloudflareのdelivery pipeline / logsへ載ること。

**マスク:** recipient / Message-ID等は必要に応じて。

### 09-authentication-results.png

**タイミング:** 受信側でメール到着後

**撮るもの:** メールヘッダーまたは「メッセージのソース」でSPF / DKIM / DMARC結果が分かる箇所。

**記事で伝えること:** 「届いた」ではなく送信認証まで確認した。

**目標:** SPF PASS / DKIM PASS / DMARC PASS。実測結果をそのまま掲載する。

### 10-inbound-still-working.png

**タイミング:** Email Sending設定完了後

**撮るもの:** 外部メールアドレス → `@mizzz.jp` の受信成功が分かる画面。

**記事で伝えること:** 送信側を追加しても既存受信経路を壊していない。

## 任意画像

### 11-outlook-received.png

Gmail以外のプロバイダでも正常到着した場合のみ使用。

### 12-error-and-fix.png

設定中にエラーが発生した場合は最優先で残す。成功画面だけより記事価値が高い。

候補:

- `535 5.7.8 Authentication failed`
- `550 5.7.1 Sender denied`
- TLS / port設定ミス
- DNS verification待ち

### 13-email-sending-overview.png

最終的なEmail Sending domain statusの一覧。記事の完了状態を示すのに使える。

## 記事では原則使わない画像

- API Tokenの発行完了画面でSecretが見えるもの
- Cloudflare billingの個人情報・決済情報が見える画面
- Gmailの個人Inbox全体
- DNSレコードを無加工で全件表示した画面
- 同じことを示す似たスクリーンショット

## 作業順 = 撮影順

1. 変更前Email Service → `01`
2. 変更前DNS → `02`
3. Email Sending Onboard → `03`
4. DNS追加preview → `04`
5. Onboard完了・DNS確認 → `05`
6. API Token権限設定 → `06`
7. curl SMTP送信 → `07`
8. Delivery Logs → `08`
9. 受信メール認証結果 → `09`
10. 既存受信の再テスト → `10`
11. エラーが起きたらその場で `12`

この順番を崩さなければ、記事に必要な「before → configuration → send → verification → after」の画像が揃う。
