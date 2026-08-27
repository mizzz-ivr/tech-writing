# Writing Analytics / Technical Portfolio

`tech-writing` を記事置き場ではなく、執筆履歴・技術テーマ・公開頻度・外部反応を継続的に分析できるTechnical Portfolioとして運用するための設計です。

## Source of Truth

優先順位は次のとおりです。

1. `articles/<slug>/article.md` の本文とfront matter
2. `ideas/published.md` の公開記録（移行期間の照合用）
3. `data/metrics/YYYY-MM-DD.json` の外部メトリクスsnapshot
4. `reports/writing-profile.md` / README内の集計表示（生成物）
5. Notion（方針・運用・レビュー結果）

Notionへ記事台帳を複製しません。記事そのものの状態はRepositoryを正とします。

## 推奨front matter

既存項目との後方互換を維持しつつ、分析したい項目を明示します。

```yaml
---
title: "記事タイトル"
status: published
published_at: 2026-08-27
article_type: case-study
level: intermediate
topics: [GitHub, GitHubActions, Python]
domains: [devops, developer-productivity]
languages: [Python]
technologies: [GitHub Actions, GitHub API]
portfolio_signals: [automation, ci-cd, oss]
source_repositories: [mizzz-ivr/mizzz-ivr]
published:
  qiita: https://qiita.com/...
  zenn: null
  note: null
---
```

### 各項目

- `status`: `draft` / `review` / `published` / `archived`
- `published_at`: 初回公開日。`YYYY-MM-DD`
- `article_type`: `how-to` / `case-study` / `architecture` / `incident` / `comparison` / `opinion` など
- `level`: `beginner` / `intermediate` / `advanced`
- `topics`: 媒体タグに近い検索用キーワード
- `domains`: frontend / backend / infra / devops / security / ai / databaseなどの技術分野
- `languages`: 言語単位の集計用。Python / TypeScript / Goなど
- `technologies`: Next.js / Docker / GitHub Actions / PostgreSQLなど
- `portfolio_signals`: architecture / automation / testing / observability / ossなど、仕事・営業・ポートフォリオで示したい能力軸
- `source_repositories`: 記事の根拠になったRepository
- `published`: 媒体別URL。`qiita` / `zenn` / `note` を正式な公開platformとして扱う

過去記事に不足項目があっても、スクリプトが推測してfront matterを書き換えることはしません。未分類は `Unclassified` とdata quality警告で可視化します。

### 未分類とN/Aを分ける

記事によっては、技術分野や技術スタックは分類できても特定のプログラミング言語を扱わない場合があります。

この場合はfieldを省略せず、明示的に空配列を記録します。

```yaml
languages: []
```

Writing Analyticsでは次のように区別します。

- fieldが無い / `null` / 空文字: **Unclassified**。data quality対象
- `[]`: **明示的にN/A**。Unclassifiedへ加算しない
- 1件以上の値: 通常の分類として集計

これにより、言語非依存の記事へ無理にPythonやTypeScriptを付与して分析結果を歪めることを避けます。

## Publication Registry

`ideas/published.md` は `公開日 / タイトル / Qiita / Zenn / note / その他` を記録します。

- Qiita / Zenn / noteの公開URLはfront matterとRegistryの両方で照合する
- note-only記事も正式なpublished articleとして扱う
- 既存の旧5列形式は後方互換のため読み取り可能とし、旧「その他」列をnote URLとして誤解釈しない
- Recent Articles / READMEは代表URLを `Qiita → Zenn → note` の順で選び、note-only記事ではnote URLを使う

## 生成物

### `reports/writing-profile.md`

人が読む分析レポートです。

- 公開記事数
- 最終投稿日
- 最近の公開記事
- topics / domains / languages / technologies / portfolio signalsの集計
- latest snapshotのplatform別Reactions
- positive reactionが観測された記事のNotable表示
- data quality

### README

READMEは外向けプロフィールとして短く保ちます。

- Writing Profile summary
- 最近のピックアップ
- Notable記事
- 主な技術テーマ
- 詳細レポートへのリンク

READMEではreactionの全件表を出さず、positive reactionが観測された記事だけをNotableとして短く表示します。likes同率などを理由に順位付けはしません。

READMEの自動生成部分はmarker内だけを更新し、手書き部分を壊しません。

## External Metrics

公開platformとmetrics取得platformは分離します。

- 公開platform: Qiita / Zenn / note
- metrics取得platform: Qiita / Zennのみ

noteは公開URLと投稿履歴だけを正式対応し、安定した公式取得方法を確認できるまでPV / スキ / コメント等を自動収集しません。不安定なHTML scrapingや推測値は導入しません。

### Qiita

Qiita API v2を利用します。

取得対象:

- `likes_count`
- `stocks_count`
- `comments_count`
- `page_views_count`（APIが返す場合）

`QIITA_TOKEN` は任意です。設定する場合はGitHub ActionsのRepository Secretへ保存し、Repositoryへ値を書きません。

Tokenなしでも取得できる公開指標を優先し、PVが取得できなければ `null` のまま保存します。

### Zenn

Zennの記事一覧JSON endpointは公式ドキュメントで安定性が保証された公開APIとして扱いません。

そのため以下を守ります。

- best-effort
- timeoutを設ける
- 取得失敗で記事管理/CIを壊さない
- 取得できない値は `null`
- endpoint変更時にadapterだけ差し替えられる構成にする

PVは取得できる前提にしません。

### note

Writing Analyticsでは次だけを扱います。

- `published.note` の公開URL
- `ideas/published.md` のnote URL
- 公開日 / Recent Articles / README / Portfolio exportへの反映
- Registryとfront matterのData Quality照合

Non-goals:

- noteのPV / スキ / コメント等の自動収集
- note HTMLのscraping
- note認証情報の保持
- noteへの自動投稿

### Reaction / Notableのderived view

Phase 2Aではraw snapshot schemaを変更せず、表示時だけderived viewを作ります。

値の意味は次のように分けます。

- 数値 `0`: APIから取得できた **観測済み0**
- `null`: snapshotにfieldは存在するが値を取得できない **unavailable**
- field欠落: **not collected**

特に `page_views: null` は正常状態です。PVが取得できないことだけでdata quality errorにはしません。

reaction指標は媒体ごとの意味を維持します。

- Qiita: likes / stocks / comments
- Zenn: likes / bookmarks / comments

QiitaのstocksとZennのbookmarksを同じ尺度として扱いません。また、likes / stocks / commentsを加算した総合Popularity Scoreは作りません。

`Notable` はpositive reactionが1つ以上観測された記事を抽出するだけで、異なる指標間の順位付けは行いません。全指標が0の場合は「positive reaction未観測」として扱い、likes同率0による意味のない人気順を作りません。

## Snapshotを残す理由

最新値だけ上書きすると、「公開後7日でどれくらい伸びたか」「long-tailで伸びたか」が分かりません。

`data/metrics/YYYY-MM-DD.json` を日次で残すことで、将来的に次を分析できます。

- 7日 / 30日 / 90日の増分
- 記事ごとの初速
- 長期的に読まれる記事
- topic / domainごとの反応差
- QiitaとZennの媒体差

記事数が少ないうちはデータ量も小さいため、JSONをGit管理する方式で十分です。規模が増えた時点でSQLite / DuckDB / external storageを検討します。

Trend計算では、必要な日付のsnapshotが存在する場合だけ差分を計算します。欠測値を補間したり、存在しない7日前の値を推測したりしません。

## Data Quality

最低限、次を検出します。

- `ideas/published.md` にあるがfront matterが `published` ではない
- `ideas/published.md` のQiita / Zenn / note URLがfront matterに無い、または不一致
- `status: published` なのにQiita / Zenn / noteの公開URLがない
- `status: published` なのに `published_at` がない
- `domains` / `languages` / `technologies` が未分類

不整合を自動修正はしません。記事ごとの意図を壊さないよう、レポートに出して人が直します。

### Writing Analytics導入前の記事

PR #15より前に公開済みだった3記事は、記事本文と `ideas/published.md` を確認したうえで `scripts/migrations/20260827_normalize_published_metadata.py` に明示的な移行値を固定しています。

このmigrationは推論エンジンではありません。対象slugと値を固定したidempotentな移行処理で、main refresh時に既存front matterを正規化した後は変更を発生させません。

## GitHub Actions

- Pull Request: unit test / migration check / 集計スクリプトを検証
- `main` push: legacy metadataをidempotentに正規化して集計レポートを更新
- daily schedule: 外部メトリクスをsnapshotし、README / reportを更新
- manual dispatch: 任意タイミングで再取得

外部API障害はwarningとして扱い、front matter検証などRepository内部の問題と分離します。

GitHub Actions bot自身のanalytics commitではrefresh jobを再実行しないため、自動commitのループを防ぎます。

## Portfolio / Career活用

`data/exports/writing-portfolio.json` をstable public schemaとして利用します。公開URLはQiita / Zenn / noteを出力できますが、reaction metricsは取得済みのQiita / Zennだけを扱います。

表示候補:

- 最近90日で扱った技術分野
- 継続的に書いている言語・技術
- 設計 / Security / CI/CD / OSSなどのportfolio signals
- Notable記事とplatform別reaction
- 実装Repositoryと記事の対応
- 公開頻度と継続期間

「書いた記事数」だけではなく、どの技術をどの深さで継続的に扱っているかを示せる状態を目標にします。

## Review cadence

- Weekly: 最終投稿日 / 次記事候補 / 未分類metadata
- Monthly: topic / domain / languageの偏り、platform別reaction、投稿頻度
- Quarterly: 転職・フリーランス・営業で見せたいportfolio signalsと実際の記事構成の差
- Yearly: 年間テーマ、技術スタック変化、long-tail記事、翌年の重点分野
