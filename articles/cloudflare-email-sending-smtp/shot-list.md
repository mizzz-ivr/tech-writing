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
- 無加工原本は公開Repositoryのassetsへ置かない

## 取得済みBefore素材

- [x] `ivrm.jp` DNS一覧
- [x] `mizzz.jp` DNS一覧
- [x] `ivrm.jp` Email Routing rules
- [x] `mizzz.jp` Email Routing rule
- [x] Destination Addresses一覧（内部証跡。公開記事では原則不使用）
- [x] Email Sending変更前Overview / Workers Paid要求画面

## 必須画像

### 00-email-sending-workers-paid-gate.png

**状態:** 取得済み

**タイミング:** Freeプランのまま `Email Sending` を最初に開いた時

**撮るもの:** 「メール送信は現在、Workers Paidプランでのみ利用可能」と表示される画面。

**記事で伝えること:** 今回の実環境ではEmail Sending有効化前にWorkers Paidが実装gateになった。

**公開時:** Account / Billing情報が不要に写っていないか再確認する。

### 01-before-ivrm-dns.png

**状態:** 原本取得済み

**撮るもの:** `ivrm.jp` のメール関連DNS。MX / SPF / DKIM / DMARC、必要に応じてSES / Resend系既存レコードが分かる範囲。

**記事で伝えること:** 既存受信と既存送信DNSを把握してから変更した。

**公開時:** MX / TXT中心にcropし、無関係なA / CNAME / origin IPを除外する。

### 02-before-mizzz-dns.png

**状態:** 原本取得済み

**撮るもの:** `mizzz.jp` のメール関連DNS。

**記事で伝えること:** `mizzz.jp` はlegacy aliasとして維持するため、変更前状態も記録した。

### 03-onboard-ivrm-domain.png

**タイミング:** Workers Paid採用後、`Email Sending > Onboard Domain`

**撮るもの:** `ivrm.jp` を選択する画面。

**記事で伝えること:** 送信ドメインは `ivrm.jp` から構築した。

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

**タイミング:** `ivmz@ivrm.jp` から最初のSMTP送信に成功した時

**撮るもの:** `curl` 実行と成功が分かるターミナル。

**マスク:** Token、検証先アドレス。

**記事で伝えること:** Unified Personal / Generalの送信元として `ivmz@ivrm.jp` を成立させた。

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

**撮るもの:** 変更前に受信できていたアドレスへ外部から送って正常受信できたことが分かる代表画面。

**記事で伝えること:** 送信追加によって既存受信を壊していない。

## 受信Identity確認用素材

Inbox全体のスクリーンショットは不要。代表1枚だけでよい。

受信結果は文章 / 表で次を記録する。

- `ivmz@ivrm.jp` — Unified Personal / General
- `ivuru@ivrm.jp` — person-facing
- `mizzz@ivrm.jp` — Developer / OSS
- `contact@ivrm.jp` — ivRooom / Team
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy

複数宛先を1通で同報してよいが、各Toとしてroutingされたことを個別に確認する。

## 追加で撮る可能性がある画像

### 11-ivuru-send.png

`ivuru@ivrm.jp` を「いゔる。」として実際の送信元に使う検証を記事に載せる場合。

### 12-mizzz-send.png

`mizzz@ivrm.jp` をDeveloper / OSS用途の送信元として確認する場合。

### 13-contact-ivrm-send.png

`contact@ivrm.jp` をivRooom / Teamの送信元として使う場合。

### 14-security-ivrm-send.png

`security@ivrm.jp` の送信経路を用意する場合。不要なセキュリティ運用情報を含めない。

### 15-mizzz-legacy-decision.png

`mizzz.jp` をEmail SendingへOnboardする場合のみ。

`contact@mizzz.jp` を受信onlyにした場合はスクリーンショット不要。送信も残す場合だけ追加Onboardの差分を撮る。

### 16-error-and-fix.png

設定中にエラーが発生した場合は最優先で残す。

候補:

- SMTP authentication失敗
- Sender denied
- TLS / port設定ミス
- DNS verification待ち
- SPF重複
- 既存SES / Resend系DNSとの競合

### 17-email-sending-overview.png

最終的なEmail Sending domain status一覧。記事の完了状態を示す必要がある場合のみ使う。

## 記事では原則使わない画像

- API Token発行完了画面でSecretが見えるもの
- Cloudflare billing情報
- Inbox全体
- DNSレコード全件を無加工で表示した画面
- destination addressが読めるEmail Routing画面
- 同じことを示す似たスクリーンショット

## 作業順 = 撮影順

1. `ivrm.jp` 変更前DNS → `01` ✅
2. `mizzz.jp` 変更前DNS → `02` ✅
3. Email Sending Free / Workers Paid gate → `00` ✅
4. `ivmz@ivrm.jp` を含む受信Identityを完成・受信確認
5. Workers Paid採用判断
6. 採用する場合 `ivrm.jp` Email Sending Onboard → `03`
7. DNS追加preview → `04`
8. `ivrm.jp` Onboard完了・DNS確認 → `05`
9. API Token権限設定 → `06`
10. `ivmz@ivrm.jp` からcurl SMTP送信 → `07`
11. Delivery Logs → `08`
12. 受信メール認証結果 → `09`
13. 既存受信の再テスト → `10`
14. 用途別Fromを記事に載せる場合 `11`〜`14`
15. `mizzz.jp` 送信を残す場合だけ `15`
16. エラーが起きたらその場で `16`

## 次に絶対やること

**Email Sending Onboardより先に `ivmz@ivrm.jp` のEmail Routingを作り、`ivmz` / `ivuru` / `mizzz` / `contact` / `security` / legacyの受信を実測する。**

その後でWorkers Paidを採用するか判断し、採用した場合だけOnboardへ進む。
