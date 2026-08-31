# Article Backlog

書きたいテーマを雑に残す場所です。タイトルは仮で構いません。

## 次に着手

- [ ] Zenn: 生成AIを「APIを呼ぶだけ」で終わらせない — Secret・Quota・Kill Switchを分離したAI Runtime設計
  - 媒体: Zenn
  - 目標: 2026-08-30までに初回投稿
  - 本文: review
  - Source of Truth: `ivRooom/Herta`
  - 注意: 2026-08-27時点のimplemented providerはOpenAIのみ。Claude / Gemini対応済みとは書かない
- [ ] 個人開発でもPRを切ってCIを通すようにしている理由
- [ ] note #1: 技術記事とは別に、エンジニアとして考えていることを書く場所を作ることにした
  - 媒体: note
  - 役割: noteの自己紹介 / 編集方針宣言
  - 内容: Qiita / Zenn / noteの使い分け、個人開発・AI・キャリア・社会について書く理由
  - 投稿時期: note運用開始時。月1ペースの起点にする

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

## note候補 — Experience / Opinion / Society

noteはQiita / Zennの技術記事を言い換える場所にしない。実体験・判断・価値観・キャリア・技術と社会の接点を中心にする。

### エンジニアとしての考え方

- [ ] 個人開発を「完成させること」より「続けること」を大事にしている
- [ ] AIにコードを書かせるようになって、エンジニアの仕事について考えた
- [ ] 趣味の個人開発なのにIssue・PR・CIまで使う理由
- [ ] 技術者として「何を知っているか」より「どう判断するか」が大事になってきた
- [ ] コードを書く時間が減ってもエンジニアと言えるのか
- [ ] 技術選定で「一番新しい技術」を選ばなくなった理由

### 個人開発の裏側

- [ ] 個人開発を複数抱えると、コードを書くより管理の方が難しくなってきた
- [ ] 趣味なのにGitHub ProjectsやNotionで管理する理由
- [ ] 個人開発を止めないために、あえてやらないことを決めている
- [ ] OSSを作る側になって分かったこと

### キャリア・仕事・学習

- [ ] 技術者として成長できる会社とは何か
- [ ] 年収だけで転職先を決めない理由
- [ ] 「設計ができる人」より「実装できる人」でいたいと思う理由
- [ ] スペシャリストを目指すという選択
- [ ] 本業と個人開発を両立して分かったこと
- [ ] 資格勉強と個人開発、どちらへ時間を使うか
- [ ] GitHubをPortfolioとして育てるようになって変わったこと

### 技術 × 経済・社会

- [ ] AIで一人の開発者が作れるものはどこまで増えるのか
- [ ] AIでソフトウェア開発の価値は下がるのか
- [ ] 個人開発者がAIによって一人企業に近づいている
- [ ] SaaSを作るコストはどこまで下がるのか
- [ ] OSSはなぜ無料なのに成立するのか
- [ ] GitHubはエンジニアの履歴書になっていくのか
- [ ] AI時代にプログラミングを学ぶ意味はあるのか
- [ ] クラウド時代なのに自宅サーバーを持つ意味
- [ ] 巨大プラットフォームと個人開発者は共存できるのか

### 将来の有料記事候補

最初から有料化を前提にせず、無料記事だけでも読後価値を成立させる。有料記事は、再現可能な追加価値がある場合だけ検討する。

- [ ] 個人開発を継続するための実際の管理・運用テンプレート
- [ ] AI開発を運用するためのルールと判断基準
- [ ] GitHub Portfolioを0から構築する実践ガイド
- [ ] エンジニア転職の比較・判断フレームワーク
- [ ] 個人サービスを低コスト運用するインフラ設計・コスト判断

詳細: `docs/NOTE_EDITORIAL.md`

## Profile Signal シリーズ

- [x] GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
- [x] GitHubプロフィールをライブな開発ダッシュボードにしてみた
  - LIVE SIGNAL
  - CURRENT FOCUS
  - DEV PULSE
  - NOW BUILDING
  - ACTIVITY STREAM
- [x] 自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた
  - 公開: https://qiita.com/mizzz-ivr/items/f20a2d58f623097a5904
  - Standalone Repository / Release ZIP + local runtime / v0.4.0 Latest Signals分離を記事化

### 次記事は現時点では保留

Profile Signalだけで連続投稿を増やすのではなく、**新しい実装・運用知見が十分に増えたときだけ再開する**。

候補として残すテーマ:

- GitHub ActionsだけでWeekly / Monthly開発レポートを自動生成する
  - Weekly recap
  - Monthly report
  - Achievements
  - CI / Project health
  - 現時点では既存3記事との重複が大きいため「次に着手」には置かない
  - 実運用データが蓄積し、履歴・集計・運用上の学びが独立した記事になる段階で再評価する
- v0.5+で配布方式・Preset / Theme・Analytics・運用設計に大きな変化が入った場合のDeep Dive
- 外部利用者から導入フィードバックや実運用事例が得られた場合の導入・改善記事

**現在の方針:** Profile Signalシリーズは一旦3本で区切る。投稿本数のためだけに第4弾を作らない。

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

- [~] Qiita: GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた
  - 媒体: Qiita
  - 本文: draft (`articles/260831-selfhosted-graviton-runner/article.md`)
  - Source of Truth: `ivRooom/ivrm-web`
  - 注意: account id / instance id / subnet / GitHub App id は記事に出さない
- [~] Zenn: 常時起動のCI runnerをephemeral scale-to-zeroに移す設計と、その途中で全部踏んだ話
  - 媒体: Zenn
  - 本文: draft (`articles/260831-runner-scale-to-zero-design/article.md`)
  - Source of Truth: `ivRooom/ivrm-web`
  - 上記 Qiita と同題材だが、Qiita=立てる手順 / Zenn=移行の設計判断と失敗（module アーカイブ、prefix 衝突、OOM、未マージ infra ブランチの個別 apply）
  - 注意: account id / instance id / subnet / GitHub App id は非掲載
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

### note

- 目安: 月1本程度
- エンジニアとしての考え方 / 個人開発の裏側 / キャリア・仕事・学習 / 技術×経済・社会を主軸にする
- 年間の目安は、技術思想・個人開発4本 / キャリア・仕事3本 / AI・社会・経済3本 / 技術以外2本
- 年12本を埋めること自体は目的にせず、体験や考えが十分に溜まった題材を優先する
- 有料化は急がず、まず無料記事を蓄積する

共通して、投稿間隔を守るためだけの記事は作らず、実際の開発・技術検証・経験から得た題材を優先する。

## メモ

記事化する前に、対象Repositoryの最新状態を確認する。すでに実装・変更・廃止されている内容を、古いIssueや過去の会話だけで記事にしない。

Qiita / Zenn / noteへ同一本文を重複投稿しない。同じ経験を扱う場合も、記事が答える問い・構成・コード例・深さ・視点を分ける。

noteで経済・制度・時事情報を扱う場合は、公開時点の最新情報を確認し、確認できた事実と自分の意見を区別する。
