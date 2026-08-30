# 独自ドメインメール記事 — スクリーンショット計画

Qiita canonical: `public/custom-domain-email-cloudflare.md`

無加工原本は公開Repositoryへ置かない。公開時はmask / cropしたコピーだけを使う。

## 取得済み

- [x] `ivrm.jp` DNS一覧
- [x] `mizzz.jp` DNS一覧
- [x] `ivrm.jp` Email Routing rules
- [x] `mizzz.jp` Email Routing rule
- [x] Destination Addresses一覧（内部証跡のみ）
- [x] Email Sending / Workers Paid gate

## 公開記事で使う候補

### 01-before-dns.png

`ivrm.jp` のメール関連DNS。MX / SPF / DKIM / DMARCと、必要ならSES / Resend系既存レコードが分かる範囲。

公開時:
- unrelated A / CNAME / origin IPをcrop
- Account / Zone情報を不要なら除外

### 02-email-routing-rule.png

Email RoutingでCustom AddressからVerified Destinationへ転送する設定が分かる画面。

公開時:
- destination addressを完全にmask
- Inbox側の個人情報を含めない

### 03-inbound-test.png

`ivmz@ivrm.jp` 等へ外部から送り、実際に受信できた代表1件。

公開時:
- destination mailboxをmask
- unrelated inbox contentをcrop

### 04-workers-paid-gate.png

Free状態でEmail Sendingを開いた際のWorkers Paid要求画面。

記事で伝えること:
- 「無料でできる」が主題ではない
- 送信基盤選択には料金・制約がある
- 今回のCloudflare Email Sending採用判断ではここがgateになった

### 05-onboard-domain.png

`Email Service > Email Sending > Onboard Domain` で `ivrm.jp` を選ぶ画面。

### 06-dns-preview.png

Onboard確定前のDNS Preview。

**最重要。Done / Confirm前に撮る。**

記事で伝えること:
- 送信基盤導入時に何がDNSへ追加されるのか確認してから変更した

### 07-after-dns.png

Email Sending Onboard後のメール関連DNS。

Beforeと比較できる粒度に揃える。

### 08-api-token-permission.png

API Token作成時の `Email Sending: Edit` Permission設定。

**Token値が表示される発行完了画面は撮らない。**

### 09-curl-smtp-success.png

`ivmz@ivrm.jp` からcurl SMTP送信が成功したターミナル。

mask:
- API Token
- recipient
- unnecessary Message-ID

### 10-delivery-logs.png

Cloudflare Delivery Logs。

mask:
- recipient
- unnecessary Message-ID

### 11-authentication-results.png

受信側メールヘッダーのSPF / DKIM / DMARC実測。

記事では実測値をそのまま使い、最初からPASS前提にしない。

### 12-inbound-regression.png

Email Sending追加後もEmail Routingで受信できることを示す代表1件。

## 補助素材

次は記事本文の理解に必要な場合だけ使う。

- `mizzz.jp` legacy DNS
- `ivuru@ivrm.jp` からの送信
- `mizzz@ivrm.jp` からの送信
- `contact@ivrm.jp` からの送信
- `security@ivrm.jp` からの送信
- legacy `contact@mizzz.jp` の送信判断

同じ結果を示すスクリーンショットを大量に並べない。

## エラーが出た場合

成功画面より価値が高い可能性があるため、その場で保存する。

候補:
- SMTP auth failure (`535`)
- sender domain not onboarded (`550`)
- TLS / portミス
- DNS verification待ち
- SPF / DKIM / DMARC failure
- SES / Resend既存DNSとの競合

Secretやrecipientを含む場合は原本のみ保持し、公開用コピーを別に作る。

## 画像を入れるタイミング

現時点ではQiita原稿にHTML commentのplaceholderだけを置く。

理由:
- 無加工スクリーンショットをpublic Repositoryへ置かない
- 現RepositoryにQiita画像の共通アップロード規約がまだない
- 検証途中で画像を確定するとBefore / After差分が崩れる

公開直前にmask / crop済み画像の置き場所・URLを確定して本文へ差し込む。
