# Notes: Repository is the Source of Truth

記事本文に入れる前の事実確認・体験メモです。

## 記事の中心にしたい話

- AIに次の機能候補を考えさせるだけだと、過去の会話や古いIssueを前提に判断することがある
- 実装済みの機能を候補として出してしまうことがあった
- そこで「Repository is the Source of Truth」を開発エージェントの最重要原則にした
- 現在状態を長いプロンプトに固定するより、毎回Repositoryから再構築させる方が長期の個人開発では扱いやすかった
- GitHubだけですべてを管理するのではなく、Issue / PR / Docs / Notion / 会話にもそれぞれ役割がある

## 2026-08-24 事実確認

記事初稿更新時に `ivRooom/Herta` のmainを再確認した。

- Latest main SHA: `047344e4eba9ba61bf8a254c62354543a50b4b71`
- Latest merge: PR #321 `feat(bot): Core Utility v5にJSONコマンドを追加`
- Open PR: 0件（確認時点）

### Poll

`apps/bot/src/plugins/poll.ts` を確認。

- `/poll` は `create / list / results / close` を実装
- 2〜10件の選択肢
- 単一 / 複数選択
- Button interactionによる投票
- live result設定
- Poll終了・期限切れ処理
- userごとのactive上限

記事では機能一覧を主役にせず、「追加候補として考えたが既にかなり実装されていた」という体験の根拠として使う。

### Reminder

`apps/bot/src/plugins/reminder.ts` を確認。

- `/remind` は `set / list / cancel` を実装
- channel / DM配信
- 1〜10080分
- userごとのactive上限
- 30秒周期でdue Reminderを処理
- 10分以上processingのstale Reminderをrecover
- delivery失敗時は5分後へretry

記事では「単なるReminderコマンド以上まで既に作っていたのに、自分で忘れていた」という具体例にする。

### Issueと実装のズレ

Issue #267 `feat(search): Studio Command PaletteをHybrid / Vector Search対応する` は確認時点でopen。

Issue本文にはsemantic searchが未対応という背景が残っているが、現在のRepositoryでは以下を確認できた。

- `apps/studio/src/app/api/search/semantic/route.ts` が存在
- authenticated session / Same-Origin / JSON / body limitを強制
- optional OpenAI embeddings provider
- provider failure時のlexical fallback
- Guild authorization
- semantic document embedding cache
- score threshold / result limit
- `docs/COMMAND_PALETTE_SEARCH.md` にHybrid Searchの現在仕様が記載

したがって「Issueがopen = 未実装とは限らない」の具体例として使用可能。

ただし、Issue全体の完了を断定しない。pgvector、distributed rate limit、observabilityなどDocs上のNext Phaseは残っている。

### Birthday

PR #278 `feat(birthday): 生年・年齢・Birthday Card・サーバー周年を追加` はmerge済み。

確認できた主な内容:

- optional birth year
- age / ageText / serverBirthdayNumber
- Birthday Card Studio
- 1672×941 PNG generation
- display ON/OFF / X/Y/size adjustment
- celebration snapshot
- granular IAM
- server anniversary setting
- Card failure時のtext fallback

記事本文では詳細を大量に出さず、「過去の引き継ぎに書いた次候補が、その後さらに実装されていく」背景例として必要な場合のみ使う。

### Plugin Runtime / Operations

`docs/PLUGIN_RUNTIME.md` を確認。

- Guildごとの公式Plugin Runtime
- Redis Pub/Subによる設定変更通知
- configVersion / duplicate / stale event保護
- consumer別apply ACK
- 現時点のactual Runtime consumerはbot
- Workerを機械的にconsumer化しない判断が文書化されている
- Workerは現在のDB状態へ通常scan / 実行時取得で再収束する設計

記事では内部設計の説明に寄りすぎるため、本文では詳細を省略。

### CI Quality Gate

`.github/workflows/ci.yml` を確認。

現在の主なgate:

- Prisma Generate
- Format Check
- Lint
- Typecheck
- Test
- Supply chain policy tests
- vulnerability exception validation
- Build
- Production Compose Validation
- Origin protection configuration validation
- Production Docker Build
- Production runtime verification
- CycloneDX SBOM
- Grype High / Critical scan

記事では「コードを書いて完了ではなく、Repositoryへ戻すまでが開発ループ」という説明に必要な範囲のみ掲載する。

## 公開前チェック状況

- [x] 最新main SHA
- [x] 現在のopen PR
- [x] Poll Pluginの現在のコマンドと機能
- [x] Reminder Pluginの現在のコマンドと再試行・復旧設計
- [x] Birthday機能の現在地点
- [x] Plugin Runtime / Operationsの現在地点
- [x] staleになっているIssueの具体例を記事に出して問題ないか
- [x] 現在のCI Quality Gate
- [ ] Qiita / Zenn公開直前にmainを再確認
- [ ] 公開媒体ごとのタグ / Front Matterを最終調整
- [ ] 公開URLを `published.md` に記録

## 書きすぎないこと

- Hertaの内部アーキテクチャ説明だけの記事にしない
- プロンプト全文を貼るだけの記事にしない
- AI万能論にしない
- すべてのチーム開発に同じ方法が正解だと断定しない
- 実装数や効果を根拠なく数字で盛らない
- Issue #267を「完全実装済み」と断定しない

## 記事の読者イメージ

AIでコードを書いている人だけではなく、以下の人も読めるようにする。

- GitHubを使って個人開発している人
- 複数のプロジェクトを並行している人
- 久しぶりに触るRepositoryの現在地点を思い出すのが大変な人
- AIエージェントをどこまで任せていいか迷っている人
