# Article Backlog

書きたいテーマを雑に残す場所です。タイトルは仮で構いません。

## 次に着手

- [ ] 生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計
  - 媒体: Zenn
  - 目標: 2026-08-30までに初回投稿
  - 本文: review
  - Source of Truth: `ivRooom/Herta`
  - 注意: 2026-08-27時点のimplemented providerはOpenAIのみ。Claude / Gemini対応済みとは書かない
- [ ] 個人開発でもPRを切ってCIを通すようにしている理由

## Zenn候補 — Design / Deep Dive

ZennはQiitaより投稿頻度を下げ、設計判断・内部構造・Trade-offまで掘れる題材を優先する。

- [ ] AI Runtimeへ2つ目のProviderを追加したとき、どこまで共通化できたか
  - Claude / Gemini等を実際に実装・検証した後に着手する
  - Provider固有機能を共通interfaceへ押し込みすぎない設計を振り返る
- [ ] Discord BotをPlugin Runtime中心の構成にしていった話
  - Plugin isolation / capability / lifecycle / failure boundary中心
- [ ] 個人開発のAI機能でRate Limitだけでは足りなかった — Quota / Cost / Concurrency設計
  - AI Runtime記事と重複しすぎる場合は独立記事にしない
- [ ] 個人開発にSBOMとGrypeを入れるだけでは終わらない — CIでSecurity Gateを運用する設計
- [ ] GitHub Actions / CI成功後だけProduction Deployするパイプライン設計
  - build/deploy cost、preview、rollback、branch protectionまで含められる場合に記事化

## Profile Signal シリーズ

- [x] GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
- [x] GitHubプロフィールをライブな開発ダッシュボードにしてみる
  - LIVE SIGNAL
  - CURRENT FOCUS
  - DEV PULSE
  - NOW BUILDING
  - ACTIVITY STREAM
- [ ] 自作GitHubプロフィール機能をGitHub ActionとしてOSS化してみた
  - Widget selector
  - Preset
  - Theme
  - Marker
  - 導入手順
- [ ] GitHub ActionsだけでWeekly / Monthly開発レポートを自動生成する
  - Weekly recap
  - Monthly report
  - Achievements
  - CI / Project health

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

## 投稿ペース

### Qiita

- 目安: 3〜7日に1本
- 最低ライン: 月1本
- 実装・検証・トラブルシュートなど、比較的短い周期で得た知見も記事化する

### Zenn

- Qiitaより低頻度
- 本数を埋めるためには投稿しない
- Architecture / Security / Performance / Reliability / Cost / Trade-offなど、深掘りできる題材がまとまったときに投稿する

共通して、投稿間隔を守るためだけの記事は作らず、実際の開発・技術検証で得た題材を優先する。

## メモ

記事化する前に、対象Repositoryの最新状態を確認する。すでに実装・変更・廃止されている内容を、古いIssueや過去の会話だけで記事にしない。

QiitaとZennへ同一本文を重複投稿しない。同じ開発経験を扱う場合も、記事が答える問い・構成・コード例・深さを分ける。
