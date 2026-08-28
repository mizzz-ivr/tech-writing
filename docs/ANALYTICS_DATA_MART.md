# Writing Analytics Data Mart / Decision Dashboard

## 目的

Writing Analyticsの集計ロジックと表示先が増えても、同じ数字を別々のscriptで再計算しないための共通derived layerです。

優先順位は次の3段です。

1. **集計しやすい** — machine-readable JSONへ正規化する
2. **分析しやすい** — pipeline / coverage / reactions / freshness / quality / readinessを同じschemaで扱う
3. **見やすい** — Decision Dashboardでは「今どうなっているか / 次に何を見るか」を先に出す

## Data Layers

### 1. Raw Source of Truth

- Article metadata: `articles/**`
- Publication registry: `ideas/published.md`
- Raw metrics snapshot: `data/metrics/YYYY-MM-DD.json`

これらをderived reportから逆生成しません。

### 2. Normalized Analytics Data Mart

生成物:

```text
data/analytics/writing-analytics.json
```

主なtop-level field:

```text
schema_version
as_of
overview
pipeline
trend_readiness
freshness
coverage
reactions
next_article_candidates
data_quality
articles
```

`articles` は共通原稿と、`ideas/published.md` に公開記録のあるZenn-native記事を同じanalytics universeへ正規化します。

Zenn-nativeの `published: true` だけからdraft/review状態を推測しません。公開状態・公開日はPublication Registryを使います。

### 3. Human Views

- `reports/visual-dashboard.md`: Decision Dashboard
- `reports/writing-profile.md`: 詳細Profile / reactions
- `reports/content-opportunities.md`: coverage全件 / recommendation detail
- README: Repository入口だけ

## Decision Dashboard

Dashboard冒頭では次を優先して確認します。

- Published / Draft / Review
- Last Published
- Source Freshness
- Metric Snapshot Count / Trend Readiness
- Data Quality Findings
- Pipeline-only Coverage Gaps
- Next Article Candidate

全classificationの長い一覧はDashboardへ重複させず、Content Opportunitiesへ委譲します。

## 集計ルール

### Published universe

共通記事だけでなく、Publication Registryへ公開記録されたZenn-native `articles/*.md` も含みます。

このため、Dashboard / Writing Profile / Data Mart / Public Portfolio ExportでPublished母数が一致する状態を維持します。

### Source Freshness

記事metadataの `verified_at` / `source_refs` を使って、published articleの技術的事実確認状態を可視化します。

Data Martの `freshness` には次を保持します。

- published article総数
- verified article数
- `needs_initial_verification` 件数
- oldest verification age
- articleごとのverified date / days since verified / source ref count

過去記事へverification日・commit SHAを推測で補完しません。metadata未記録のpublished articleは `needs_initial_verification` として表現します。

`source_refs` のrepository名・commit SHAそのものはderived Data Martへ複製せず、件数だけを保持します。詳細ルールは [SOURCE_FRESHNESS.md](./SOURCE_FRESHNESS.md) を参照してください。

### Trend readiness

7 / 30 / 90日Trendは、実際に保存されているsnapshotの最初と最後の観測期間がwindow以上になった場合だけreadyにします。

- 欠測日を直線補間しない
- synthetic historyを作らない
- snapshot不足を0として扱わない

### Reactions

Qiita / Zenn固有のfieldをそのまま保持します。

- observed `0`: 実際に0を観測
- `null`: platform/API上でunavailable
- field missing: not collected

これらを同じ0へ変換しません。

likes / stocks / bookmarks / commentsを単一Popularity Scoreへ合算しません。page viewsはData Martには保持しますがreaction chartには混ぜません。

### Coverage

対象:

- topics
- domains
- languages
- technologies
- portfolio_signals

各値について、公開件数・最終公開日・経過日数・30/90/365日coverageを保持します。

さらにdraft/reviewに存在するがpublishedにはまだ存在しない値を `pipeline_only_values` として分離します。

## Security / Privacy

Data Martはpublic Repositoryへ保存されるderived dataです。

- Secret / Token / Password / Cookie / Authorization等のsensitive-looking fieldをvalidatorでrejectする
- source repository名そのものはData Martへ複製せず、`source_evidence.recorded` と件数だけを保持する
- Freshnessのsource refもrepository名 / commit SHAをData Martへ複製しない
- private repository情報を新しいderived artifactから増幅しない
- Public Portfolio Exportのallowlist方針は引き続き別途維持する

## コマンド

```bash
# unified article universe + Writing Profile / README render validation
python scripts/writing_analytics_pipeline.py --check

# normalized Data Mart + Source Freshness validation
python scripts/writing_data_mart.py --check

# Decision Dashboard validation
python scripts/writing_decision_dashboard.py --check
```

main refreshではGitHub Actionsが順に再生成します。

## 分析例

`jq` を使う場合:

```bash
# 現状KPI
jq '.overview' data/analytics/writing-analytics.json

# Source Freshness summary
jq '.freshness | {published_articles, verified_articles, needs_initial_verification, oldest_verification_age_days}' data/analytics/writing-analytics.json

# initial verification未完了記事
jq '.freshness.articles[] | select(.status == "needs_initial_verification")' data/analytics/writing-analytics.json

# 7/30/90日Trend readiness
jq '.trend_readiness' data/analytics/writing-analytics.json

# 次の記事候補
jq '.next_article_candidates[:3]' data/analytics/writing-analytics.json

# 公開済みtechnology coverage
jq '.coverage.technologies.values' data/analytics/writing-analytics.json

# pipeline-only gap
jq '{domains: .coverage.domains.pipeline_only_values, technologies: .coverage.technologies.pipeline_only_values, signals: .coverage.portfolio_signals.pipeline_only_values}' data/analytics/writing-analytics.json
```

## Future Extension

Source Freshnessの次段階としてsource repository最新HEADとの差分やdependency/API変更を扱う場合も、別Dashboardを増やさず同じData Martへ追加します。

ただし、差分量だけで記事が古いと断定せず、実運用で必要なpolicyが確認できてから拡張します。
