# Cloudflare Email Sending SMTP 記事メモ

## ステータス

実施前調査 + Phase 0実測中。

ブランド / Identity / Domain / Contact Architectureの正本に合わせ、**Unified Personal Identityは `ivmz`、主メールドメインは `ivrm.jp`、`mizzz.jp` はlegacy互換**として進める。

## Source of Truth

Notion:

- Brand / Identity / Domain / Contact Architecture 2026-08-26
- 公開ブランドのルート: `ivrm.jp`
- Unified Personal Identity: `ivmz`
- 個人ポートフォリオ canonical: `ivmz.ivrm.jp`
- Personal Web Platform repository: `mizzz-ivr/ivmz-home`
- `mizzz.jp`: 旧リンク互換 / legacy brand / メール資産として維持

メールアドレス:

- `ivmz@ivrm.jp` — Unified Personal / General。X / GitHub / 個人サイト等の総合公開窓口
- `ivuru@ivrm.jp` — 「いゔる。」として対応するperson-facing identity
- `mizzz@ivrm.jp` — Developer / OSS / 技術文脈
- `contact@ivrm.jp` — ivRooom / Team / Community / Project
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy alias。原則受信互換

## 今回の実環境・方針

- Registrar: ムームードメイン
- Authoritative DNS / Nameserver: Cloudflare
- Lolipop: 解約済み。古い設計資料から除外する
- Inbound: Cloudflare Email Routing
- Outbound target: Cloudflare Email Service / Email Sending SMTP
- Primary sending domain: `ivrm.jp`
- Legacy domain: `mizzz.jp`
- Cloudflare Dashboard実測: FreeプランではEmail Sending有効化画面でWorkers Paid購入を要求される

受信経路の具体的なdestinationやSecretは公開資料へ記録しない。

## 記事の核

2022年の参考記事ではCloudflare Email Routingで受信し、送信はGmail SMTP + Googleアプリパスワードだった。

2026年にはCloudflare Email ServiceのAuthenticated SMTP submissionが利用できるため、送信側もCloudflareへ寄せられる。

今回の記事では単なるSMTP設定手順ではなく、次を実体験ベースで扱う。

1. `ivmz` / `ivuru` / `mizzz` / ivRooom / Securityの役割を先に整理する
2. 既存Email Routingを壊さず送信を追加する
3. 既存のSES / Resend系DNSを推測で削除しない
4. Free環境でWorkers Paid gateに遭遇したことを記録する
5. `ivrm.jp` を送信主系にし、`mizzz.jp` はlegacyとして必要最小限に残す
6. Delivery Logs / SPF / DKIM / DMARCまで実測する

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

API TokenはSecretとして扱い、GitHub / Notion / 記事 / スクリーンショットへ残さない。

## Phase 0 実測

### 取得済みスクリーンショット

- `ivrm.jp` DNS一覧
- `mizzz.jp` DNS一覧
- `ivrm.jp` Email Routing rules
- `mizzz.jp` Email Routing rule
- Destination Addresses一覧（内部証跡。記事では原則不使用）
- Email Sending変更前Overview / Workers Paid要求画面

無加工画像にはdestination addressや記事不要のインフラ情報が含まれるため、**公開用assetsへはまだ追加しない。公開時にmask / cropしたコピーを使用する。**

### `ivrm.jp` DNS

確認済み:

- Cloudflare Email Routing用MX: `route1.mx.cloudflare.net` / `route2.mx.cloudflare.net` / `route3.mx.cloudflare.net`
- root SPF: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- Cloudflare DKIM (`cf2024-1._domainkey...`)
- `_dmarc.ivrm.jp`、現状 `p=none`
- `send.ivrm.jp` にAmazon SES feedback MX
- `send.ivrm.jp` にAmazon SESをincludeするSPF
- Resend系DKIMレコード

**重要:** `ivrm.jp` にはCloudflare Email Routing以外の既存送信系DNSが残っている。Email Sending導入だけを理由に削除・置換しない。現行利用有無を先に確認する。

### `mizzz.jp` DNS

確認済み:

- Cloudflare Email Routing用MX: `route1.mx.cloudflare.net` / `route2.mx.cloudflare.net` / `route3.mx.cloudflare.net`
- root SPF: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- Cloudflare DKIM (`cf2024-1._domainkey...`)
- `_dmarc.mizzz.jp`、現状 `p=none`
- 全8件が1画面に収まっておりbefore画像として使いやすい

### Email Routing

`ivrm.jp`:

- Email Routing: 有効
- DNS records: ロック済み
- `mizzz@ivrm.jp` routing rule: 存在 / 有効
- `contact@ivrm.jp` routing rule: 存在 / 有効
- `security@ivrm.jp` routing rule: 存在 / 有効
- `ivuru@ivrm.jp` を含む用途別aliasが存在
- Catch-all: 有効、未一致はDrop

`mizzz.jp`:

- Email Routing: 有効
- `contact@mizzz.jp` routing rule: 存在 / 有効
- Catch-all: 無効

### Workers Paid gate

Email Sendingの変更前Overviewを取得済み。

Freeプランでは画面上に「メール送信は現在、Workers Paidプランでのみ利用可能」と表示され、Onboardへ進めなかった。

この画面は記事で「公式Docsに書いてある料金情報」ではなく、**実環境で最初に遭遇した実装gate**として使う。

## 今回の作業順

### Phase 0: Identityと変更前受信を確定

- [x] `ivrm.jp` のMX / SPF / DKIM / DMARCを記録
- [x] `mizzz.jp` のMX / SPF / DKIM / DMARCを記録
- [x] Email Routing / Email Serviceの現在状態を確認
- [x] 現在のrouting / destinationを非公開メモとして確認
- [x] Email Sendingの変更前Overview / Workers Paid gateを撮影
- [ ] `ivmz@ivrm.jp` のEmail Routingを作成
- [ ] `ivmz@ivrm.jp` の受信確認
- [ ] `ivuru@ivrm.jp` の受信確認
- [ ] `mizzz@ivrm.jp` の受信確認
- [ ] `contact@ivrm.jp` の受信確認
- [ ] `security@ivrm.jp` の受信確認
- [ ] `contact@mizzz.jp` の受信確認
- [ ] 受信テスト結果を記録

### Gate A: Workers Paidを採用するか決定

- [ ] Cloudflare Email Sending SMTPを本番送信基盤として採用するか最終決定
- [ ] 採用する場合はWorkers Paidへ切り替える
- [ ] 採用しない場合は既存SES / Resend等の代替送信経路を再評価し、記事の結論も変更する

### Phase 1: `ivrm.jp` をEmail SendingへOnboard

Gate Aで採用した場合のみ進む。

- [ ] Email Service → Email Sendingで `ivrm.jp` をOnboard
- [ ] Onboard前DNS previewを撮影
- [ ] 実際に追加されたDNSを記録
- [ ] 既存受信用MXが壊れていないことを確認
- [ ] SPF重複がないことを確認
- [ ] DKIM / DMARC状態確認
- [ ] SES / Resend系既存DNSとの競合がないことを確認

### Phase 2: SMTP送信

- [ ] `Email Sending: Edit` の専用API Tokenを作成
- [ ] Tokenはパスワードマネージャーへ保存
- [ ] curlで `ivmz@ivrm.jp` → 検証用外部アドレスへ送信
- [ ] Delivery Logs確認
- [ ] SPF / DKIM / DMARC確認
- [ ] Gmail / Outlook等で到着・迷惑メール判定確認

### Phase 3: 用途別From

- [ ] `ivuru@ivrm.jp` — person-facing
- [ ] `mizzz@ivrm.jp` — Developer / OSS
- [ ] `contact@ivrm.jp` — ivRooom / Team
- [ ] `security@ivrm.jp` — Security
- [ ] 問い合わせフォームのRouting / From / Reply-To設計を `ivmz` 方針へ統一

### Phase 4: legacy `mizzz.jp`

- [ ] `contact@mizzz.jp` が受信onlyで十分か判断
- [ ] 旧名義からの送信が必要なら `mizzz.jp` もEmail SendingへOnboard
- [ ] 不要なら送信ドメインを増やさずlegacy受信のみ維持

## 記事タイトル

第一候補:

> 2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信する

タイトルは一般化し、本文で `ivmz` / `ivuru` / `mizzz` / `ivrm.jp` / `mizzz.jp` の実運用設計を扱う。

## 記事構成

1. 独自ドメイン受信はある。次は送信経路を作りたい
2. 2022年のCloudflare Email Routing + Gmail SMTP方式
3. 2026年のCloudflare Email Sending SMTP
4. 先にIdentityと主メールドメインを決める
5. `ivrm.jp` / `mizzz.jp` の変更前DNSを記録
6. FreeでEmail Sendingを開いたらWorkers Paidが必要だった
7. `ivmz@ivrm.jp` を総合受信窓口として成立させる
8. `ivrm.jp` をEmail SendingへOnboard
9. API Tokenを作る
10. `smtp.mx.cloudflare.net:465` で `ivmz@ivrm.jp` から送る
11. Delivery Logs / SPF / DKIM / DMARCを確認
12. `ivuru` / `mizzz` / `contact` / `security` の用途別Fromを確認
13. 既存受信を再確認
14. `mizzz.jp` を送信可能にする必要があるか判断
15. 2022年方式との比較
16. 制約・料金・Secret管理
17. 実際に使ってみた結論

## 公開判断

最低限以下が揃ってから公開する。

- `ivmz`方針がNotion / Repositoryで一貫している
- `ivmz@ivrm.jp` の受信が成立
- Cloudflare Email Sendingを採用する場合は `ivrm.jp` のOnboard実測
- `ivmz@ivrm.jp` から実際に送信成功
- SPF / DKIM / DMARCの実測結果
- Delivery Logs確認
- 変更後も既存受信が壊れていない
- `contact@mizzz.jp` をlegacyとしてどう扱うか決定
- 実作業で詰まった点を検証結果付きで説明できる

## Secret / 公開情報ルール

記事・GitHub・Notion・公開スクリーンショットへ載せないもの:

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
