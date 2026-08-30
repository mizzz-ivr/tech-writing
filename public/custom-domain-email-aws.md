---
title: 独自ドメインを取得したあと、メールを送受信できるようにするまで — AWSで構築してみた
tags:
  - AWS
  - AmazonSES
  - DNS
  - Email
  - 個人開発
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: true
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# 独自ドメインを取得したあと、メールを送受信できるようにするまで — AWSで構築してみた

独自ドメインを取得してWebサイトには使えるようになった。でも、`name@example.com` のようなアドレスでメールを受信・送信するには何が必要なのか。

この記事では、`ivrm.jp` の実環境でAWSを使ったメール基盤を構築した過程をベースに、独自ドメイン取得後に必要だった設定と判断を整理する。

> 現在は実装前のDraft。`ivmz-home` のAWSメール基盤を実装・検証してから、実測値・スクリーンショット・トラブルシュートを追加して公開する。`ignorePublish: true` を維持する。

## 記事で答えること

- 独自ドメインを取得しただけでメールは使えるのか
- 受信には何が必要か
- 送信には何が必要か
- MX / SPF / DKIM / DMARCは何をしているのか
- AWSではSES / WorkMail等をどう使い分けるのか
- 既存DNSを壊さず移行するには何を確認するか
- 実際に送受信できたことをどう検証するか

## 現在の実環境

公開ブランドの主ドメインは `ivrm.jp`。

用途別のメールアドレスは次のように整理している。

| Address | Role |
| --- | --- |
| `ivmz@ivrm.jp` | General / Personal |
| `ivuru@ivrm.jp` | Person-facing |
| `mizzz@ivrm.jp` | Developer / OSS |
| `contact@ivrm.jp` | ivRooom / Team |
| `security@ivrm.jp` | Security |
| `contact@mizzz.jp` | Legacy |

現在の受信経路は既存構成で稼働しているため、AWS移行を理由にMXを推測で変更しない。

## まず理解しておきたい: 受信と送信は別

独自ドメインを所有していること、メールを受信できること、そのアドレスから送信できることは別の話だった。

```text
Domain / DNS
   ├─ Incoming mail
   │    └─ MX → 受信基盤
   └─ Outgoing mail
        └─ SES / SMTP / API等の送信基盤
```

AWSを使う場合も、この2つを分けて考える。

Amazon SESはメール送信だけでなく受信も扱えるが、SESの受信endpointはIMAP / POP3メールボックスではない。通常のメールクライアントで直接Inboxとして使う場合はAmazon WorkMail等、別のmailbox設計が必要になる。

## AWSでどの受信構成にするか

ここは実装前に確定する。

候補:

1. 現行受信経路を維持し、送信だけAmazon SESへ移す
2. Amazon SES Email Receiving + Receipt RulesでS3 / Lambda等へ処理する
3. 通常のメールボックスが必要ならAmazon WorkMailを採用する

最終記事では、実際に採用した構成だけを手順として説明し、不採用案は判断理由として簡潔に残す。

## 送信はAmazon SESを第一候補にする

`ivmz-home` のapplication email adapterはAmazon SESを第一候補として設計する。

実装時に確認する内容:

- SES identityとして `ivrm.jp` をverify
- DKIM
- SPF / custom MAIL FROMの要否
- DMARC alignment
- SES sandbox / production access
- IAM least privilege
- Production / Preview credential分離
- bounce / complaint handling
- application adapterからSESを呼び出す境界

## 変更前DNSを必ず記録する

AWS側を設定する前に、現在のMX / SPF / DKIM / DMARCを記録する。

`ivrm.jp` には過去構成由来のSES / Resend系と思われるDNSレコードも確認できているため、利用有無を確認するまで削除しない。

<!-- IMAGE: before DNS, masked/cropped -->

## AWS実装後に追記する章

以下は実装完了後に実測値で書く。

### Amazon SESでドメインIdentityを作る

TODO: 実際のConsole画面と生成されたDNSレコード。

<!-- IMAGE: SES identity -->

### DKIM / MAIL FROM / SPFを設定する

TODO: 採用した設定と理由。

<!-- IMAGE: DNS preview / verified identity -->

### SandboxからProductionへ進める

TODO: 実環境で必要だった手続きと制約。

### `ivmz@ivrm.jp` から実際に送信する

TODO: application / SDK / SMTPのうち実際に採用した方法。

<!-- IMAGE: send success -->

### SPF / DKIM / DMARCを受信側で確認する

```text
SPF   : TODO
DKIM  : TODO
DMARC : TODO
```

<!-- IMAGE: Authentication-Results -->

### 受信経路も実測する

TODO: 採用した受信方式で `ivmz@ivrm.jp` 等が正常に届くことを確認。

<!-- IMAGE: representative inbound result -->

### 変更後も既存アドレスが壊れていないか確認する

TODO: `ivmz@` / `ivuru@` / `mizzz@` / `contact@` / `security@` / legacyの回帰テスト。

## 公開前チェック

- [ ] AWS側の受信方式を確定
- [ ] Amazon SES送信を実装
- [ ] Productionで実送信成功
- [ ] SPF / DKIM / DMARCを実測
- [ ] bounce / complaint handlingを確認
- [ ] 受信を実測
- [ ] 既存受信経路の回帰テスト
- [ ] 公開用スクリーンショットをmask / crop
- [ ] Secret / credential / destination / account情報を除去
- [ ] `ignorePublish: false`へ変更

## 今の結論

記事はAWSメール基盤の実装より先に完成させない。

独自ドメイン取得後に必要だったことを、AWSの公式手順を並べるだけではなく、実際のDNS・Identity設計・送受信検証・失敗と修正まで含めて記事化する。
