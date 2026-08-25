# Cloudflare Email Sending SMTP 記事メモ

## ステータス

実施前の調査・記事化準備。

mizzz.jp でCloudflare Email Sending SMTPを実際に設定し、送受信・認証・迷惑メール判定まで確認してから `article.md` を作る。

## 今回の実環境

- Domain: `mizzz.jp`
- Registrar: ムームードメイン
- Authoritative DNS / Nameserver: Cloudflare
- Inbound mail: 現在正常稼働中。送信設定時に既存MXを壊さない
- Lolipop: 解約済み。古い設計資料から除外する
- Outbound mail: Cloudflare Email Service / Email Sending SMTPを採用

受信経路の具体的なMX・転送先はCloudflareの現行設定で確認してから記事へ記載する。推測で書かない。

## 記事の核

2022年に公開されたQiita記事では、Cloudflare Email Routingで独自ドメイン宛メールを受信し、送信はGmailの `smtp.gmail.com` とGoogleアプリパスワードを利用していた。

2026年6月、Cloudflare Email Serviceに認証付きSMTP submissionが追加されたため、送信側もCloudflareへ寄せられるようになった。

今回の記事では、mizzz.jpで実際に移行してみて、2022年方式から何が変わったのかを記録する。

参考記事:
- https://qiita.com/rokuosan/items/e3415ea30ad5e48d3b0f

## 2026-08-25時点で公式確認できた仕様

Cloudflare Email Service SMTP:

```text
Host: smtp.mx.cloudflare.net
Port: 465
Security: Implicit TLS / SMTPS
AUTH: PLAIN or LOGIN
Username: api_token
Password: Cloudflare API Token
Required permission: Email Sending: Edit
```

重要:

- `587` + STARTTLS は非対応
- outbound submissionで25番ポートは使わない
- sender domainはEmail SendingへOnboard済みである必要がある
- SMTP submissionもREST API / Workers bindingと同じ送信pipelineを通る
- DKIM / ARC signingとDelivery Logsを利用できる
- API TokenはSecretとして扱う

公式:
- https://developers.cloudflare.com/email-service/api/send-emails/smtp/
- https://developers.cloudflare.com/email-service/examples/email-sending/smtp/
- https://developers.cloudflare.com/email-service/get-started/send-emails/
- https://developers.cloudflare.com/changelog/product/email-service/

## 料金メモ

2026-08-25時点:

- arbitrary recipientsへのEmail SendingはWorkers Paidが必要
- Workers Paidは3,000通/月を含む
- 超過は1,000通あたり$0.35
- Email RoutingのinboundはFree / PaidともUnlimited

公式:
- https://developers.cloudflare.com/email-service/platform/pricing/

「Cloudflareだけで無料」は現在の要件だと正確ではない。2022年記事との差分として記事内で明示する。

## 設定前に記録すること

- [ ] Cloudflare DNSの現在のMX
- [ ] SPF
- [ ] DKIM
- [ ] DMARC
- [ ] 現在使えている独自ドメイン受信アドレス
- [ ] 転送先 / 受信経路
- [ ] 変更前の受信テスト結果

Secret、Token、個人用転送先など公開不要な値は記事メモにも残さない。

## 実施予定

- [ ] Cloudflare Dashboardで `mizzz.jp` を Email Service → Email Sending にOnboard
- [ ] Onboard時にCloudflareが要求したDNSレコードを記録
- [ ] 既存の受信用MXが変更されていないことを確認
- [ ] `Email Sending: Edit` の専用API Tokenを作成
- [ ] curl等で最小SMTP送信テスト
- [ ] Gmail等の実使用クライアントへSMTPを設定
- [ ] Gmail宛に送信
- [ ] Outlook等の別プロバイダ宛にも送信
- [ ] 受信メールヘッダーでSPF / DKIM / DMARCを確認
- [ ] Cloudflare Delivery LogsとMessage-IDを確認
- [ ] 送信設定後もmizzz.jp宛の受信が正常なことを確認
- [ ] 迷惑メール判定を確認
- [ ] 詰まった点をその場で追記

## Gmail等へ登録する場合の値

```text
SMTP server: smtp.mx.cloudflare.net
Port: 465
SSL/TLS: enabled (Implicit TLS)
Username: api_token
Password: <Cloudflare API Token>
From: <使用する @mizzz.jp アドレス>
```

記事・スクリーンショットではAPI Tokenを絶対に表示しない。

## DNSで特に確認すること

- 既存の受信用MXをEmail Sending導入だけを理由に削除しない
- SPF TXTを複数作らない
- Cloudflareが追加する送信用レコードと既存レコードの整合を取る
- DKIMは実際にOnboardで発行されたselector / valueを記録する
- DMARCは現在設定を確認してから変更する

この部分は実際のmizzz.jp設定完了後に、具体的なレコード種別と確認結果へ更新する。

## 記事タイトル候補

第一候補:

> 2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信する

候補:

- Cloudflareだけで独自ドメインメールを送信する — Email Sending SMTPを試した
- Gmail SMTPをやめてCloudflare Email Sending SMTPへ移行した
- 2022年のCloudflare Email Routing構成を2026年版に更新してみた

「無料」はWorkers Paid要件があるためタイトルへ入れない。

## 記事構成案

1. 受信はできていたが、mizzz.jp名義で送信もしたくなった
2. 2022年のQiita記事を参考にした
3. 調べると2026年にはCloudflare自身のSMTPが増えていた
4. mizzz.jpの現在構成
5. Email SendingをOnboardする
6. API Tokenを作る
7. `smtp.mx.cloudflare.net:465` で最小テスト
8. Gmail等のクライアントへ設定する
9. SPF / DKIM / DMARCを確認する
10. 2022年方式と2026年方式を比較する
11. Workers Paid / Beta / Secret管理の注意点
12. 実際に運用してみた結論

## 2022年方式との比較表用メモ

| 項目 | 2022年参考記事 | 今回の2026年構成 |
|---|---|---|
| 受信 | Cloudflare Email Routing | 現行受信経路を維持・確認 |
| 送信SMTP | `smtp.gmail.com` | `smtp.mx.cloudflare.net` |
| 送信認証 | Googleアプリパスワード | Cloudflare API Token |
| SMTP Port | Gmail側設定 | `465` / Implicit TLS |
| 送信基盤 | Gmail | Cloudflare Email Service |
| Cloudflare Email Sending | 当時なし | 2026年6月にSMTP Beta追加 |
| 費用 | Gmail利用前提で無料構成 | arbitrary recipientsはWorkers Paid必要 |

## 公開判断

設定手順だけではなく、少なくとも以下が揃ってから公開する。

- 実際の送信成功
- 送信後も受信が壊れていない
- SPF / DKIM / DMARCの確認結果
- Delivery Logsの確認
- 実際に詰まった点が1つ以上ある、または「特に詰まらなかった」ことを検証内容付きで説明できる

STYLE_GUIDEの方針どおり、一般的なCloudflare SMTPの説明だけの記事にはしない。
