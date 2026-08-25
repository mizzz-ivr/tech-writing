# Article Backlog

書きたいテーマを雑に残す場所です。タイトルは仮で構いません。

## 次に着手

- [ ] 個人開発でもPRを切ってCIを通すようにしている理由

## AI開発 / 開発運用

- [x] AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話
- [ ] AIに「次に何を作るか」まで任せるためにやっていること
- [ ] 長い引き継ぎプロンプトを書くよりRepositoryを読ませるようになった話
- [ ] GitHubとNotionをどう役割分担しているか

## Herta / Discord

- [ ] Discord BotをPlugin Runtime中心の構成にしていった話
- [ ] Reminder / Pollを作って終わりにしないための運用設計
- [ ] Discord BotのBirthday Card生成を実装した話
- [ ] Rule EngineをDiscord運用へつないだ話

## CI / Security / Platform

- [ ] 個人開発にSBOMとGrypeを入れてみた話
- [ ] CIをDefinition of DoneとしてAI開発エージェントに守らせる

## Cloudflare / Infrastructure

- [ ] 2026年版：Cloudflare Email Sending SMTPで独自ドメインメールを送信した話
  - mizzz.jpで実際に設定・検証してから記事化する
  - 2022年の「Cloudflare Email Routing + Gmail SMTP」方式との差分を扱う
  - SMTP、SPF、DKIM、DMARC、Workers Paid、Betaの注意点を実測ベースで書く
  - 調査・実施ログ: `articles/cloudflare-email-sending-smtp/notes.md`

## 投稿ペース

- 目安: 3〜7日に1本
- 最低ライン: 月1本
- 投稿間隔を守るためだけの記事は作らず、実際の開発・技術検証で得た題材を優先する

## メモ

記事化する前に、対象Repositoryの最新状態を確認する。すでに実装・変更・廃止されている内容を、古いIssueや過去の会話だけで記事にしない。
