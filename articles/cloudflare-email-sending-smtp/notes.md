# Cloudflare Email Sending SMTP 記事メモ

## ステータス

実施前の調査・記事化準備。

ブランド / Identity / Domain / Contact Architectureの正本に合わせ、**主系メールドメインは `ivrm.jp`、`mizzz.jp` はlegacy互換**として進める。

## Source of Truth

Notion:

- Brand / Identity / Domain / Contact Architecture 2026-08-25
- 公開ブランドのルート: `ivrm.jp`
- 個人ポートフォリオ canonical: `mizzz.ivrm.jp`
- `mizzz.jp`: Webの主URLではなく、旧リンク互換とメール資産のため維持

メールアドレス:

- `contact@ivrm.jp` — ivRooom / Team / Community / Project
- `mizzz@ivrm.jp` — Personal / Developer identity
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy alias

## 今回の実環境・方針

- Registrar: ムームードメイン
- Authoritative DNS / Nameserver: Cloudflare
- Lolipop: 解約済み。古い設計資料から除外する
- Outbound: Cloudflare Email Service / Email Sending SMTP
- Primary sending domain: `ivrm.jp`
- Legacy domain: `mizzz.jp`

受信経路の具体的なMX / 転送先 / Routing状態はCloudflareの現行設定で確認してから記載する。推測しない。

## 記事の核

2022年の参考記事ではCloudflare Email Routingで受信し、送信はGmail SMTP + Googleアプリパスワードだった。

2026年にはCloudflare Email ServiceのAuthenticated SMTP submissionが利用できるため、送信側もCloudflareへ寄せられる。

今回の記事では単なるSMTP設定手順ではなく、**ブランド整理で主メールドメインを `ivrm.jp` に決めたうえで、legacyの `mizzz.jp` を無駄に主系へ残さない**ところまで含める。

参考記事:
- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

## SMTP仕様メモ

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
AUTH: PLAIN or LOGIN
Username: api_token
Password: Cloudflare API Token
Required permission: Email Sending: Edit
```

公式確認事項:

- sender domainはEmail SendingへOnboard済みである必要がある
- SMTP submissionはCloudflare Email Serviceのdelivery pipelineを通る
- Delivery Logsを確認できる
- API TokenはSecretとして扱う

## 2026-08-25 Phase 0 実測

Cloudflare Dashboardの変更前スクリーンショットを取得済み。**無加工画像にはdestination address等が含まれるため、公開用assetsへはまだ追加しない。公開時にマスク / cropしたコピーを使用する。**

### `ivrm.jp` DNS

確認できたもの:

- Cloudflare Email Routing用MX: `route1.mx.cloudflare.net` / `route2.mx.cloudflare.net` / `route3.mx.cloudflare.net`
- root SPF: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- Cloudflare DKIM (`cf2024-1._domainkey...`) が存在
- `_dmarc.ivrm.jp` が存在し、現状 `p=none`
- `send.ivrm.jp` にAmazon SESのfeedback MXが存在
- `send.ivrm.jp` にAmazon SESをincludeするSPFが存在
- `resend._domainkey...` のレコードが存在

**重要:** `ivrm.jp` にはCloudflare Email Routing以外の既存送信系DNSが残っているため、Email Sending Onboard時に無条件で削除・置換しない。特にSES / Resend系の現行利用有無を別途確認する。

スクリーンショットは33件中1〜25件表示のため内部証跡としては十分。ただし公開記事ではA / CNAME等の無関係なレコードやorigin IPが写るため、MX / TXT中心にfilterまたはcropした公開用画像を作る。

### `mizzz.jp` DNS

確認できたもの:

- Cloudflare Email Routing用MX: `route1.mx.cloudflare.net` / `route2.mx.cloudflare.net` / `route3.mx.cloudflare.net`
- root SPF: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- Cloudflare DKIM (`cf2024-1._domainkey...`) が存在
- `_dmarc.mizzz.jp` が存在し、現状 `p=none`
- DNSレコードは全8件が1画面に収まっており、変更前証跡として良好

### Email Routing

`ivrm.jp`:

- Email Routing: 有効
- DNS records: ロック済み
- `mizzz@ivrm.jp` routing rule: 存在 / 有効
- `contact@ivrm.jp` routing rule: 存在 / 有効
- `security@ivrm.jp` routing rule: 存在 / 有効
- その他の用途別aliasも複数存在
- Catch-allは有効で、未一致メールはDropする設定

`mizzz.jp`:

- Email Routing: 有効
- DNS records: ロック済み
- `contact@mizzz.jp` routing rule: 存在 / 有効
- Catch-all: 無効

Destination Addresses:

- account共有のverified destinationが複数存在することを確認
- 実アドレスは記事 / GitHubへ記録しない

### スクリーンショット評価

取得済み6枚のうち、記事素材候補として優先するもの:

1. `ivrm.jp` 変更前DNS — 内部証跡OK。公開時はMX/TXT中心にcrop/filter
2. `mizzz.jp` 変更前DNS — そのまま構成説明に使いやすい。公開時に不要情報をマスク
3. `mizzz.jp` Email Routing rule — legacy aliasの現状説明に有効
4. `ivrm.jp` Email Routing rules —主系の現行alias構成説明に有効

Destination Addresses一覧の2枚は内容が重複するため、記事では原則1枚も使わず、必要な場合だけ1枚を強くマスクして補助画像にする。

Routing ruleが存在することは確認できたが、**実際に現在メールが配送されることまではスクリーンショットだけでは証明できない**。次に変更前受信テストを実施する。

## 今回の作業順

### Phase 0: 変更前状態を確定

- [x] `ivrm.jp` のMX / SPF / DKIM / DMARCを記録
- [x] `mizzz.jp` のMX / SPF / DKIM / DMARCを記録
- [x] Email Routing / Email Serviceの現在状態を確認
- [ ] `mizzz@ivrm.jp` の受信可否確認
- [ ] `contact@ivrm.jp` の受信可否確認
- [ ] `security@ivrm.jp` の受信可否確認
- [ ] `contact@mizzz.jp` の受信可否確認
- [x] 現在のrouting / destinationを非公開メモとして確認
- [ ] 変更前の受信テスト
- [ ] Email Sendingの変更前Overviewを撮影

### Phase 1: `ivrm.jp` を主系としてOnboard

- [ ] Email Service → Email Sendingで `ivrm.jp` をOnboard
- [ ] Onboard前DNS previewを撮影
- [ ] 実際に追加されたDNSを記録
- [ ] 既存受信用MXが壊れていないことを確認
- [ ] SPF重複がないことを確認
- [ ] DKIM / DMARC状態確認

### Phase 2: SMTP送信

- [ ] `Email Sending: Edit` の専用API Tokenを作成
- [ ] Tokenはパスワードマネージャーへ保存しGit / Notion / 記事へ残さない
- [ ] curlで `mizzz@ivrm.jp` → 検証用外部アドレスへ送信
- [ ] Delivery Logs確認
- [ ] SPF / DKIM / DMARC確認
- [ ] Gmail / Outlook等で到着・迷惑メール判定確認

### Phase 3: 用途別Fromを確認

- [ ] `contact@ivrm.jp` の送信要件確認
- [ ] `security@ivrm.jp` の送信要件確認
- [ ] 問い合わせフォームのFrom / Reply-To設計確認

### Phase 4: legacy `mizzz.jp` を判断

- [ ] `contact@mizzz.jp` が受信onlyで十分か判断
- [ ] 旧名義からの送信が必要なら `mizzz.jp` もEmail SendingへOnboard
- [ ] 不要なら送信ドメインを増やさずlegacy受信のみ維持

## 記事タイトル

第一候補:

> 2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信する

記事内では実環境として `ivrm.jp` / `mizzz.jp` の役割分担を扱うが、タイトルは特定ブランドに閉じず一般化する。

## 記事構成

1. 独自ドメイン受信はある。次は送信経路を作りたい
2. 2022年のCloudflare Email Routing + Gmail SMTP方式
3. 2026年のCloudflare Email Sending SMTP
4. 先に主メールドメインを `ivrm.jp` に決めた
5. `ivrm.jp` / `mizzz.jp` の変更前DNSを記録
6. `ivrm.jp` をEmail SendingへOnboard
7. API Tokenを作る
8. `smtp.mx.cloudflare.net:465` で `mizzz@ivrm.jp` から送る
9. Delivery Logs / SPF / DKIM / DMARCを確認
10. 既存受信を再確認
11. `mizzz.jp` を送信可能にする必要があるか判断
12. 2022年方式との比較
13. 制約・料金・Secret管理
14. 実際に使ってみた結論

## 公開判断

最低限以下が揃ってから公開する。

- `ivrm.jp` のOnboard実測
- `mizzz@ivrm.jp` から実際に送信成功
- SPF / DKIM / DMARCの実測結果
- Delivery Logs確認
- 変更後も受信が壊れていない
- `contact@mizzz.jp` をlegacyとしてどう扱うか決定
- 実作業で詰まった点、または詰まらなかった理由を検証結果付きで説明できる

## Secret / 公開情報ルール

記事・GitHub・Notion・スクリーンショットへ載せないもの:

- API Token
- password
- 個人用destination address
- 不要なAccount ID / Zone ID
- 公開不要なMessage-ID
- Billing情報

## 公式参考資料

- https://developers.cloudflare.com/email-service/get-started/send-emails/
- https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- https://developers.cloudflare.com/email-service/configuration/domains/
- https://developers.cloudflare.com/email-service/platform/pricing/
- https://developers.cloudflare.com/changelog/product/email-service/
