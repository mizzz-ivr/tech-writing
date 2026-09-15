# 独自ドメインメール記事 — スクリーンショット計画

Qiita canonical: `public/custom-domain-email-aws.md`

無加工原本は公開Repositoryへ置かない。公開時はmask / cropしたコピーだけを使う。

## 公開時の基本方針

公開記事では、**環境を特定できる情報は原則として一般化する**。

- 実ドメイン名 → `example.com` / `mail.example.com`
- 実メールアドレス → `me@example.com` / `contact@example.com`
- IPv4 → 必要ならRFC 5737の `192.0.2.0/24` / `198.51.100.0/24` / `203.0.113.0/24` から例示
- IPv6 → 必要なら `2001:db8::/32` を使用
- AWS Account ID → mask
- ARN内のAccount ID / unique resource name → maskまたは一般化
- S3 bucket名 / Lambda名 / resource ID / request ID / Message-ID → 再現に不要ならmask
- verified destination / Inbox / Billing / Console account情報 → 非掲載
- Access Key / Secret Access Key / SMTP credential / Session token → 絶対に掲載しない

AWS / Cloudflare等の**公開サービスendpoint、DNSレコード種別、設定項目名**は、再現性に必要で秘密情報ではない場合は掲載可。

スクリーンショットで文字列置換が不自然になる場合は、値を黒塗りまたはぼかし、本文側で `example.com` を使って説明する。

## 取得済みBefore素材

- [x] 実環境のDNS一覧
- [x] 旧ドメイン側DNS一覧
- [x] 現在の受信Routing構成
- [x] Destination Addresses一覧（内部証跡のみ）

Cloudflare Email Sending / Workers Paid画面はAWS採用後の主手順には使用しない。必要なら「検討した代替案」の補助画像として扱う。公開時は実ドメイン・destination・account情報をmaskする。

## AWS実装時の必須画像

### 01-before-mail-dns.png

AWS変更前のMX / SPF / DKIM / DMARC。公開時はメール関連だけcropし、実ドメイン名・実メール・origin IP等をmaskする。

### 02-ses-domain-identity.png

Amazon SESでdomain identityを作成する画面。

実ドメインは `example.com` として本文で説明し、Console画像上の実値はmaskする。Secret / AWS Account ID / ARNは映さない。

### 03-ses-dkim-records.png

SESが要求するDKIM用DNSレコード。

実際に表示された値を基に記事を書くが、公開版では環境固有のdomain label / token等を必要に応じて一般化する。provider側の公開endpointは再現に必要なら残してよい。

### 04-mail-from-records.png

custom MAIL FROMを採用する場合のみ。

MX / SPFの追加内容が分かる画面を残す。実domain部分はmaskまたは `mail.example.com` として本文で説明する。

### 05-ses-identity-verified.png

identity / DKIM / MAIL FROMのverification完了状態。

実domain / ARN / Account IDをmaskする。

### 06-ses-production-access.png

Sandbox / Production accessの状態が分かる範囲。

申請本文、Account情報、Billing、quota以外の環境固有情報は映さない。

### 07-iam-permission.png

SES送信用IAMの権限設計が分かる画面または公開可能なpolicy抜粋。

Access Key / Secret Access Keyは絶対に映さない。ARNを掲載する場合はAccount IDやresource nameを一般化する。

### 08-send-success.png

`me@example.com` 相当の送信元から実際に送信できたことが分かるログ / UI。

sender / recipient / request ID / Message-ID / unique resource IDはmaskする。

### 09-authentication-results.png

受信メールのSPF / DKIM / DMARC実測。

PASSを前提にせず、実際の結果を掲載する。実domain / email / Message-ID / IPはmaskまたはドキュメント用値へ置換する。

### 10-bounce-complaint.png

bounce / complaint handlingを記事で扱う場合のみ。

第三者アドレス、Message-ID、request ID、SNS topic ARN等を公開しない。

### 11-inbound-architecture.png

最終的に採用した受信方式が分かる画面。

- 現行受信を維持する場合: 代表Routing画面
- SES Email Receivingの場合: receipt rule / S3 / Lambda / SNS action
- 通常mailboxを別providerへ置く場合: AWS側との境界が分かる範囲

実domain / bucket / function / rule名等、一意なResource名は一般化する。

### 12-inbound-test.png

`me@example.com` 相当への受信成功を示す代表1枚。

Inbox全体は不要。sender / destination / other mail / Message-IDはmaskする。

### 13-after-mail-dns.png

AWS構築後のメール関連DNS。

Beforeと同じ粒度で比較できるようにする。実domain / IP / unique tokenは必要最小限だけ見せる。

## エラー時に必ず残す画像

- SES identity verification待ち / failure
- DKIM verification failure
- custom MAIL FROM failure
- sandbox宛先制限
- IAM AccessDenied
- MessageRejected
- SPF / DKIM / DMARC failure
- MX migration failure
- receipt rule / Lambda / S3 delivery failure

成功だけでなく、実際に詰まった箇所を記事の価値にする。ただしエラー画面にはARN / Request ID / Account ID / Domain / Email等が含まれやすいため、公開前に必ず確認する。

## 公開しないもの

- 実ドメイン名（記事では原則 `example.com` 系へ置換）
- Production origin IP / private IP / public IP
- 実メールアドレス / verified destination
- AWS Access Key / Secret Access Key
- SMTP credential
- Session token
- AWS Account ID
- ARN内のAccount ID / environment-specific resource name
- Billing情報
- Inbox全体
- 不要なMessage-ID / request ID
- S3 bucket名 / Lambda function名 / unique rule名など、再現に不要な一意識別子

## 作業順 = 撮影順

1. Before DNS（取得済み）
2. AWS受信方式を決定
3. SES domain identity
4. DKIM設定
5. custom MAIL FROMを使う場合のみ設定
6. identity verification
7. sandbox / Production access
8. least-privilege IAM
9. SES adapter / 実送信
10. SPF / DKIM / DMARC
11. bounce / complaint handling
12. 採用した受信方式を構築
13. 受信テスト
14. After DNS
15. 全用途の回帰テスト
16. 公開用mask / crop
17. 本文・コード例を `example.com` 系へ統一
18. Secret / Account ID / ARN / IP / Message-ID / request IDの残存チェック

## Dependency

この撮影は `mizzz-ivr/ivmz-home` Issue #35 のAWS mail implementationと同時に行う。

記事作業だけを先行させない。
