---
title: "独自ドメイン取得後にメールを送受信できるようにするまで — 記事企画・検証メモ"
status: draft
published_at: null
article_type: guide
level: beginner
topics:
  - email
  - dns
  - aws
  - amazon-ses
  - cloudflare
domains:
  - infra
  - web
languages: []
technologies:
  - Amazon SES
  - Cloudflare Email Routing
  - DNS
portfolio_signals:
  - architecture
  - infrastructure
source_repositories:
  - mizzz-ivr/ivmz-home
published:
  qiita: null
  zenn: null
  note: null
---

# 独自ドメイン取得後にメールを送受信できるようにするまで — 記事企画・検証メモ

## Article ID

`260825-custom-domain-email`

## 媒体

Qiita

Canonical source:

`public/custom-domain-email-aws.md`

## 記事の主題

**独自ドメインを取得したあと、メールを受信・送信できるようにするには何が必要か**を、代表的な3つの方法を比較したうえで、AWSを使った実構築を紹介する。

「無料で独自ドメインメールを作る」ことを主題にはしない。

記事冒頭では次の3パターンを整理する。

1. お名前.com等のメールサーバー / メールサービスを契約する
2. Cloudflare Email Routing / Email Sendingを使う
3. AWSでメール基盤を構築する

そのうえで、**今回はAWSを採用し、Amazon SESを中心に構築した方法を紹介する**という流れにする。

AWSを利用した実装を完成させてから記事を仕上げる。

## 読者

- 独自ドメインを取得した
- Webサイトには使えている
- `name@example.com` でメールを使いたい
- メールサーバーを別契約すべきか、CloudflareやAWSで構築すべきか迷っている
- MX / SPF / DKIM / DMARCやSESの役割がまだ整理できていない

## 比較パートで扱うこと

### お名前.com等のメールサービス

- ドメイン取得だけではメール運用できず、別途メールサーバー / サービスが必要
- 一般的なmailbox / Webメール / SMTP / IMAP等をまとめて用意しやすい
- 既にWeb / DNSを別providerで使っている場合は、メール用に追加契約する形になる

### Cloudflare

- Email Routingで独自ドメイン宛メールを既存mailboxへ転送できる
- 受信と送信は別
- arbitrary recipientへのEmail SendingはWorkers Paidが必要
- 今回は候補として実画面まで確認したが不採用

### AWS

- OutboundはAmazon SESを第一候補
- SES Email Receivingもあるが通常のIMAP / POP mailboxではない
- IAM / event / logging / application adapter等をAWS基盤と統合しやすい
- 今回の記事ではこの方法を実装する

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
- Cloudflare Email Sending / Workers Paid gate画面

Cloudflareの画面は主手順にはせず、「比較検討した方法」の補助素材として必要最小限に使う。

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
3. 独自ドメインメールを使う3つの方法
   - お名前.com等でメールサービスを契約
   - Cloudflare Email Routing / Email Sending
   - AWSで構築
4. 今回AWSを選んだ理由
5. 受信と送信は別の仕組み
6. 使うメールアドレスを先に決める
7. MX / SPF / DKIM / DMARCをざっくり理解する
8. 変更前DNSを記録する
9. AWSで受信をどうするか決める
10. Amazon SESで送信ドメインをverifyする
11. DKIM / MAIL FROM / SPF / DMARCを設定する
12. Sandbox / Production accessを整理する
13. `ivmz@ivrm.jp`から実送信する
14. SPF / DKIM / DMARCを実メールで確認する
15. bounce / complaintを扱う
16. 採用した受信方式を構築する
17. 受信を実測する
18. 既存アドレスが壊れていないか回帰テストする
19. 独自ドメイン取得後にやったことをチェックリスト化する
20. 3方式を振り返り、どんな人にどれが向くかまとめる

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