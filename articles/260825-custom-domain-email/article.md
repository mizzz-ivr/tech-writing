# 独自ドメイン取得後にメールを送受信できるようにするまで — 記事企画・検証メモ

## Article ID

`260825-custom-domain-email`

執筆開始日は2026-08-25 JST。Repositoryの現行命名ルールに合わせ、このArticle IDを固定する。

## 媒体

- 本命: Qiita
- Qiita canonical source: `public/custom-domain-email-cloudflare.md`
- このファイル: 企画・検証・構成判断の共通メモ

Qiitaでは「実際に何をすれば独自ドメインメールを送受信できるのか」を再現可能な形で扱う。Cloudflare Email Sendingの料金やSMTPだけを主題にはしない。

## 読者

次の状態の人を主対象とする。

> 独自ドメインを取得してWebサイトには使い始めた。でも `name@example.com` のようなメールアドレスを作って、受信・送信するには次に何をすればいいのか分からない。

## 記事が答える問い

1. 独自ドメインを取っただけでメールは使えるのか
2. メールを受信するには何が必要か
3. メールを送信するには何が必要か
4. MX / SPF / DKIM / DMARCは何のためにあるのか
5. Cloudflareを使う場合、Email RoutingとEmail Sendingはどう役割分担するのか
6. 実際に送受信できたことを何で確認するのか

## 主題にしないもの

- 「無料で独自ドメインメールが使える」という訴求
- Cloudflare Email Sending SMTPだけの設定手順
- Gmailを長期的な送信基盤として使う方法
- ivmzのBrand設計そのもの

`ivmz` / `ivuru` / `mizzz` のIdentity設計は実例として使うが、読者が自分の `contact@` / `info@` / `me@` へ置き換えられる説明を優先する。

## 実環境

### Domain / DNS

- Primary domain: `ivrm.jp`
- Legacy domain: `mizzz.jp`
- Registrar: ムームードメイン
- Authoritative DNS: Cloudflare

### Mail identity

- `ivmz@ivrm.jp` — Unified Personal / General
- `ivuru@ivrm.jp` — person-facing
- `mizzz@ivrm.jp` — Developer / OSS
- `contact@ivrm.jp` — ivRooom / Team / Community
- `security@ivrm.jp` — Security
- `contact@mizzz.jp` — legacy alias

### Target architecture

```text
Inbound
External sender
  -> MX
  -> Cloudflare Email Routing
  -> Verified Destination Address
  -> existing inbox

Outbound
Mail client / application
  -> Cloudflare authenticated SMTP
  -> recipient
```

Cloudflare Email Routingは一般的なIMAP mailboxを新設する構成ではなく、verified destinationへのroutingとして扱う。

## 現在確認済み

### Before DNS

`ivrm.jp`:

- Cloudflare Email Routing用MXを確認済み
- root SPFを確認済み
- Cloudflare DKIMを確認済み
- DMARCを確認済み
- Amazon SES系の送信DNSが残っている
- Resend系DKIMが残っている

`mizzz.jp`:

- Cloudflare Email Routing用MXを確認済み
- SPF / DKIM / DMARCを確認済み

既存SES / Resend系DNSは、現行利用有無をRepositoryで確認するまで推測で削除しない。

### Email Routing

- `ivrm.jp` Email Routing有効
- 用途別routing ruleが存在
- `mizzz.jp` Email Routing有効
- `contact@mizzz.jp` はlegacy routingとして存在
- verified destinationは存在するが、公開記事へ実アドレスを記載しない

### Email Sending

FreeプランのDashboardでEmail Sendingを開いたところ、Workers Paidが必要というgateを実測した。

この記事では「無料か有料か」を主題にせず、送信基盤選択時の現実的な制約として扱う。

## 2026-08-31 公式仕様再確認

Cloudflare公式Docsで現在確認した内容:

### Email Routing

- routing ruleは独自ドメイン側のaddress patternとdestinationを紐付ける
- destinationにはverified email addressまたはEmail Workerを指定できる

Reference:
https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/

### Email Sending / SMTP

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
AUTH: PLAIN or LOGIN
Username: api_token
Password: Cloudflare API Token
Required permission: Email Sending: Edit
```

- Email Sending enabled accountが必要
- sender domainのOnboardが必要
- port 587 STARTTLSは送信submissionとして非対応
- SMTP / REST API / Workers bindingは同じdelivery pipelineへ入る
- SMTP submissionは2026-06-08にBetaとして公開

References:
https://developers.cloudflare.com/email-service/api/send-emails/smtp/
https://developers.cloudflare.com/changelog/post/2026-06-08-smtp-submission/

### Domain Onboard

Email SendingのOnboard時に `cf-bounce` サブドメインへ送信用DNSが追加される。

- bounce routing用MX
- SPF
- DKIM

Reference:
https://developers.cloudflare.com/email-service/get-started/send-emails/

### Authentication

公開後の記事ではSPF / DKIM / DMARCを概念だけで終わらせず、受信メールのAuthentication-Resultsで実測値を載せる。

Reference:
https://developers.cloudflare.com/email-service/concepts/email-authentication/

## 記事ストーリー

### 1. 独自ドメインを取った。でもメールはどうする？

Webは使えるようになったが、ドメイン取得だけではInboxも送信経路も作られないことに気付いた、という実体験から始める。

### 2. 受信と送信を分けて考える

```text
Domain / DNS
  ├─ Inbound: MX + Routing / Mailbox
  └─ Outbound: SMTP / API + Authentication
```

ここを記事の中心概念にする。

### 3. 使いたいアドレスを決める

実例として `ivmz@` / `contact@` / `security@` を示す。

### 4. Email Routingで受信経路を作る

- MX
- Routing Rule
- Verified Destination
- 実受信テスト

### 5. 受信できても送信はまだできない

Cloudflare Email RoutingとEmail Sendingの役割差を説明する。

### 6. 送信前に既存DNSを棚卸し

SES / Resend系レコードが残っていた実例を入れる。

### 7. 送信サービスを選ぶ

Cloudflare Email Sendingを今回採用候補にした流れを書く。Workers Paid gateはここで扱う。

### 8. Email Sending domain Onboard

DNS Previewを撮り、Before / Afterを比較する。

### 9. SMTPで1通送る

最初はcurlで transport 自体を確認する。

### 10. SPF / DKIM / DMARCを実測

受信側のAuthentication-Resultsを見る。

### 11. 受信回帰テスト

送信設定追加後もEmail Routingが壊れていないことを確認する。

### 12. メールクライアントから使うときの考え方

受信Inboxと送信SMTPが別設定になることを説明する。

### 13. 最終チェックリスト

独自ドメイン取得後に必要だった工程を順番でまとめる。

## 公開までの残作業

- [ ] `ivmz@ivrm.jp` を含む受信対象の実受信結果を確定
- [ ] SES / Resendの現行利用有無をRepositoryで確定
- [ ] Cloudflare Email Sendingを本番送信基盤として採用するか決定
- [ ] 採用する場合Workers Paidへ切り替え
- [ ] `ivrm.jp` Email Sending Onboard
- [ ] Onboard前DNS Previewを撮影
- [ ] After DNSを記録
- [ ] `Email Sending: Edit`専用Tokenを作成
- [ ] `ivmz@ivrm.jp`からcurl SMTP送信
- [ ] Delivery Logs確認
- [ ] SPF / DKIM / DMARC実測
- [ ] Gmail / Outlook等への到達確認
- [ ] Email Routing回帰テスト
- [ ] legacy `mizzz.jp`を受信onlyにするか判断
- [ ] 公開用スクリーンショットをmask / crop
- [ ] `public/custom-domain-email-cloudflare.md`からTODO / draft注記を除去
- [ ] `ignorePublish: false`へ変更

## Security / 公開ルール

Repository・記事・Issue・PR・スクリーンショットへ載せない:

- Cloudflare API Token
- Password / Secret
- verified destinationの実メールアドレス
- 不要なAccount ID / Zone ID
- Billing情報
- 公開不要なMessage-ID
- unrelated origin IP

無加工スクリーンショットはpublic Repositoryへ入れず、公開用にmask / cropしたコピーだけを使う。
