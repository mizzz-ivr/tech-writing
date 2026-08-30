# 独自ドメインメール記事 — スクリーンショット計画

Qiita canonical: `public/custom-domain-email-aws.md`

無加工原本は公開Repositoryへ置かない。公開時はmask / cropしたコピーだけを使う。

## 取得済みBefore素材

- [x] `ivrm.jp` DNS一覧
- [x] `mizzz.jp` DNS一覧
- [x] 現在の受信Routing構成
- [x] Destination Addresses一覧（内部証跡のみ）

Cloudflare Email Sending / Workers Paid画面はAWS採用後の主手順には使用しない。必要なら「検討した代替案」の補助画像として扱う。

## AWS実装時の必須画像

### 01-before-mail-dns.png

AWS変更前のMX / SPF / DKIM / DMARC。公開時はメール関連だけcropする。

### 02-ses-domain-identity.png

Amazon SESで `ivrm.jp` のdomain identityを作成する画面。

Secret / AWS account情報は映さない。

### 03-ses-dkim-records.png

SESが要求するDKIM用DNSレコード。

実際に表示された値を基に記事を書く。推測値は使わない。

### 04-mail-from-records.png

custom MAIL FROMを採用する場合のみ。

MX / SPFの追加内容が分かる画面を残す。

### 05-ses-identity-verified.png

identity / DKIM / MAIL FROMのverification完了状態。

### 06-ses-production-access.png

Sandbox / Production accessの状態が分かる範囲。

申請本文やaccount情報など公開不要情報は映さない。

### 07-iam-permission.png

SES送信用IAMの権限設計が分かる画面または公開可能なpolicy抜粋。

Access Key / Secret Access Keyは絶対に映さない。

### 08-send-success.png

`ivmz@ivrm.jp` から実際に送信できたことが分かるログ / UI。

recipientやrequest IDは必要に応じてmaskする。

### 09-authentication-results.png

受信メールのSPF / DKIM / DMARC実測。

PASSを前提にせず、実際の結果を掲載する。

### 10-bounce-complaint.png

bounce / complaint handlingを記事で扱う場合のみ。

第三者アドレスやMessage-ID等を公開しない。

### 11-inbound-architecture.png

最終的に採用した受信方式が分かる画面。

- 現行受信を維持する場合: 代表Routing画面
- SES Email Receivingの場合: receipt rule / action
- WorkMailの場合: domain / mailbox設定の公開可能部分

### 12-inbound-test.png

`ivmz@ivrm.jp` 等への受信成功を示す代表1枚。

Inbox全体は不要。destinationと他メールはmaskする。

### 13-after-mail-dns.png

AWS構築後のメール関連DNS。

Beforeと同じ粒度で比較できるようにする。

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

成功だけでなく、実際に詰まった箇所を記事の価値にする。

## 公開しないもの

- AWS Access Key / Secret Access Key
- SMTP credential
- Session token
- AWS Account ID（記事に不要なら）
- verified destinationの実アドレス
- Billing情報
- Inbox全体
- Production origin IP
- 不要なMessage-ID / request ID

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
15. 全アドレス回帰テスト
16. 公開用mask / crop

## Dependency

この撮影は `mizzz-ivr/ivmz-home` Issue #35 のAWS mail implementationと同時に行う。

記事作業だけを先行させない。
