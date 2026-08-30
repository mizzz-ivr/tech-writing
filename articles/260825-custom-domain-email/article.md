# 独自ドメイン取得後にメールを送受信できるようにするまで — 記事企画・検証メモ

## Article ID

`260825-custom-domain-email`

## 媒体

Qiita

Canonical source:

`public/custom-domain-email-aws.md`

## 記事の主題

「無料で独自ドメインメールを作る」ではなく、**独自ドメインを取得したあと、実際にメールを受信・送信できる状態へ持っていくには何が必要か**を実体験ベースでまとめる。

AWSを利用した実装を完成させてから記事を仕上げる。

## 読者

- 独自ドメインを取得した
- Webサイトには使えている
- `name@example.com` でメールを使いたい
- MX / SPF / DKIM / DMARCやSESの役割がまだ整理できていない

## 実環境

- Primary domain: `ivrm.jp`
- General / Personal: `ivmz@ivrm.jp`
- Person-facing: `ivuru@ivrm.jp`
- Developer / OSS: `mizzz@ivrm.jp`
- ivRooom / Team: `contact@ivrm.jp`
- Security: `security@ivrm.jp`
- Legacy: `contact@mizzz.jp`
- Personal Web: `mizzz-ivr/ivmz-home`

## AWS方針

### Outbound

Amazon SESを第一候補にする。

確認・実装対象:

- SES Region
- `ivrm.jp` domain identity
- DKIM
- SPF / custom MAIL FROM
- DMARC alignment
- sandbox / Production access
- IAM least privilege
- bounce / complaint handling
- Production / Preview credential separation
- application email adapter

### Inbound

AWS利用を理由に即座にMXを変更しない。

Amazon SES Email Receivingは受信処理を行えるがIMAP / POP mailboxではない。

受信方式は実装時に次から確定する。

1. 現行受信経路を維持し、送信だけSESへ移行
2. SES Email Receiving + Receipt Rules + S3 / Lambda / SNS等
3. 通常mailboxが必要ならAWS外を含む別mailbox providerを組み合わせる

Amazon WorkMailは2026-04-30から新規顧客受付終了、2027-03-31にend of support予定のため、新規採用しない。

## Dependency

記事完成は `mizzz-ivr/ivmz-home` Issue #35 のAWS mail implementation / acceptance後。

Issue:

https://github.com/mizzz-ivr/ivmz-home/issues/35

現時点では記事を完成させず、Qiita原稿の `ignorePublish: true` を維持する。

## 取得済み素材

- `ivrm.jp` 変更前DNS
- `mizzz.jp` 変更前DNS
- 現行受信構成
- destination一覧（内部証跡のみ）

Cloudflare Email Sending / Workers Paid画面は、最終的にAWSを採用したため記事の主役から外す。必要なら「検討したが不採用にした案」として小さく扱う。

## AWS実装時に記録すること

- SES identity作成画面
- DKIM用DNS
- custom MAIL FROMを使う場合のMX / SPF
- sandbox / Production accessの状態
- IAM policyの権限名（Secret値は出さない）
- 実送信結果
- bounce / complaint handling
- SPF / DKIM / DMARC実測
- 採用した受信方式
- SES Email Receivingを採用した場合のReceipt Rules / S3 / Lambda / SNS
- 変更後受信テスト
- 既存DNSから削除したもの / 残したものと理由
- ハマった点と修正

## 記事構成案

1. 独自ドメインを取った。でもメールはどうする？
2. ドメイン取得だけではメールは使えない
3. 受信と送信は別の仕組み
4. 使うメールアドレスを先に決める
5. MX / SPF / DKIM / DMARCをざっくり理解する
6. 変更前DNSを記録する
7. AWSで受信をどうするか決める
8. Amazon SESで送信ドメインをverifyする
9. DKIM / MAIL FROM / SPF / DMARCを設定する
10. Sandbox / Production accessを整理する
11. `ivmz@ivrm.jp`から実送信する
12. SPF / DKIM / DMARCを実メールで確認する
13. bounce / complaintを扱う
14. 採用した受信方式を構築する
15. 受信を実測する
16. 既存アドレスが壊れていないか回帰テストする
17. 独自ドメイン取得後にやったことをチェックリスト化する

## 公開条件

- AWS受信方式が確定
- Amazon SES実送信成功
- Production利用条件を確認
- SPF / DKIM / DMARC実測
- bounce / complaint handling確認
- 受信実測
- 回帰テストPASS
- 公開画像をmask / crop
- Secret / AWS account情報 / destination / origin IPを除去
- `ignorePublish: false`
