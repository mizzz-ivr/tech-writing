# Cloudflare Email Sending SMTP 記事用スクリーンショット計画

`article.md` の章立てと、NotionのBrand / Identity / Domain / Contact Architecture正本に対応する撮影チェックリスト。

## 撮影ルール

- API Token / Secret / passwordは絶対に映さない
- 個人用destination addressは隠す
- Account ID / Zone ID / Message-IDは記事上不要なら隠す
- Billing情報は映さない
- ブラウザ全画面ではなく説明対象UIが読める範囲へトリミングする
- 作業前 / 作業後を同じ粒度で撮る
- 元画像は加工前も保持し、公開用コピーのみマスクする

## 必須画像 10枚

### 01-before-ivrm-dns.png

**タイミング:** 何も変更する前

**撮るもの:** `ivrm.jp` のメール関連DNS。MX / SPF / DKIM / DMARCが分かる範囲。

**記事で伝えること:** 主メールドメイン `ivrm.jp` の変更前状態を保存した。

### 02-before-mizzz-dns.png

**タイミング:** 何も変更する前

**撮るもの:** `mizzz.jp` のメール関連DNS。

**記事で伝えること:** `mizzz.jp` はlegacy aliasとして維持するため、こちらも変更前状態を記録した。

### 03-onboard-ivrm-domain.png

**タイミング:** `Email Sending > Onboard Domain`

**撮るもの:** `ivrm.jp` を選択する画面。

**記事で伝えること:** 送信の主系は `ivrm.jp` から構築した。

**注意:** Confirm / Doneを押す前に撮る。

### 04-onboard-dns-preview.png

**タイミング:** Onboard確定直前

**撮るもの:** Cloudflareが `ivrm.jp` に追加予定として表示するDNSレコード。

**記事で伝えること:** Onboardで何が変わるかを確定前に確認した。

**最重要:** 設定後に再現しにくい可能性があるため必ず撮る。

### 05-after-ivrm-dns.png

**タイミング:** `ivrm.jp` Onboard完了後

**撮るもの:** 実際に追加されたEmail Sending関連DNS + 既存受信用MXが残っている状態。

**記事で伝えること:** 送信用DNSと既存受信経路を共存させた。

### 06-api-token-permission.png

**タイミング:** SMTP専用API Token作成時

**撮るもの:** Permissionで `Email Sending: Edit` を設定している画面。

**絶対に撮らない:** 発行後のToken文字列。

### 07-curl-smtp-success.png

**タイミング:** `mizzz@ivrm.jp` から最初のSMTP送信に成功した時

**撮るもの:** `curl` 実行と成功が分かるターミナル。

**マスク:** Token、検証先アドレス。

### 08-delivery-logs.png

**タイミング:** curl送信直後

**撮るもの:** Cloudflare Email Sending Delivery Logsの成功レコード。

**記事で伝えること:** SMTP submissionがCloudflareのdelivery pipeline / logsへ載った。

### 09-authentication-results.png

**タイミング:** 受信側でメール到着後

**撮るもの:** SPF / DKIM / DMARC結果が分かるヘッダー部分。

**目標:** 実測結果をそのまま掲載する。PASSを前提に記事を書かない。

### 10-inbound-still-working.png

**タイミング:** `ivrm.jp` Email Sending設定完了後

**撮るもの:** 変更前に受信できていたアドレスへ外部から送って正常受信できたことが分かる画面。

**記事で伝えること:** 送信追加によって既存受信を壊していない。

## 追加で撮る可能性がある画像

### 11-contact-ivrm-send.png

`contact@ivrm.jp` を実際の送信元として使う場合のみ。

### 12-security-ivrm-send.png

`security@ivrm.jp` の送信経路を用意する場合のみ。公開画面に不要なセキュリティ運用情報を含めない。

### 13-mizzz-legacy-decision.png

`mizzz.jp` をEmail SendingへOnboardする場合のみ。

記事上は「legacy aliasを受信onlyにした」ならスクリーンショット不要。送信も残す判断をした場合だけ、追加Onboardの差分を撮る。

### 14-error-and-fix.png

設定中にエラーが発生した場合は最優先で残す。

候補:

- SMTP authentication失敗
- Sender denied
- TLS / port設定ミス
- DNS verification待ち
- SPF重複

### 15-email-sending-overview.png

最終的なEmail Sending domain status一覧。記事の完了状態を示す必要がある場合のみ使う。

## 記事では原則使わない画像

- API Token発行完了画面でSecretが見えるもの
- Cloudflare billing情報
- Inbox全体
- DNSレコード全件を無加工で表示した画面
- destination addressが読めるEmail Routing画面
- 同じことを示す似たスクリーンショット

## 作業順 = 撮影順

1. `ivrm.jp` 変更前DNS → `01`
2. `mizzz.jp` 変更前DNS → `02`
3. `ivrm.jp` Email Sending Onboard → `03`
4. DNS追加preview → `04`
5. `ivrm.jp` Onboard完了・DNS確認 → `05`
6. API Token権限設定 → `06`
7. `mizzz@ivrm.jp` からcurl SMTP送信 → `07`
8. Delivery Logs → `08`
9. 受信メール認証結果 → `09`
10. 既存受信の再テスト → `10`
11. 用途別Fromを追加するなら `11` / `12`
12. `mizzz.jp` 送信を残す場合だけ `13`
13. エラーが起きたらその場で `14`

## 最初に絶対やること

**Onboard前に `01` と `02` を撮る。**

今回の記事では「主系を `ivrm.jp` に寄せ、`mizzz.jp` をlegacyとして必要最小限に残した」という判断自体が重要なので、2ドメインのbefore状態が記事の根拠になる。
