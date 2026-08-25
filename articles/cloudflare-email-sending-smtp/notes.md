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

## 今回の作業順

### Phase 0: 変更前状態を確定

- [ ] `ivrm.jp` のMX / SPF / DKIM / DMARCを記録
- [ ] `mizzz.jp` のMX / SPF / DKIM / DMARCを記録
- [ ] Email Routing / Email Serviceの現在状態を確認
- [ ] `mizzz@ivrm.jp` の受信可否確認
- [ ] `contact@ivrm.jp` の受信可否確認
- [ ] `security@ivrm.jp` の受信可否確認
- [ ] `contact@mizzz.jp` の受信可否確認
- [ ] 現在のrouting / destinationを非公開メモとして確認
- [ ] 変更前の受信テスト

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
