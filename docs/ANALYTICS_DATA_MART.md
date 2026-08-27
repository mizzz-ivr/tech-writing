# Writing Analytics Data Mart / Decision Dashboard

## 目的

Writing Analyticsの集計ロジックと表示先が増えても、同じ数字を別々のscriptで再計算しないための共通derived layerです。

優先順位は次の3段です。

1. **集計しやすい** — machine-readable JSONへ正規化する
2. **分析しやすい** — pipeline / coverage / reactions / quality / readinessを同じschemaで扱う
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
a s_of
overview
pipeline
trend_readiness
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

Dashboard冒頭では次だけを優先して確認します。

- Published / Draft / Review
- Last Published
- Metric Snapshot Count / Trend Readiness
- Data Quality Findings
- Pipeline-only Coverage Gaps
- Next Article Candidate

全classificationの長い一覧はDashboardへ重複させず、Content Opportunitiesへ委譲します。

## 集計ルール

### Published universe

共通記事だけでなく、Publication Registryへ公開記録されたZenn-native `articles/*.md` も含みます。

このため、Dashboard / Writing Profile / Data Mart / Public Portfolio ExportでPublished母数が一致する状態を維持します。

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

likes / stocks / bookmarks / commentsを単一Popularity Scoreへ合算しません。

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
- private repository情報を新しいderived artifactから増幅しない
- Public Portfolio Exportのallowlist方針は引き続き別途維持する

## コマンド

```bash
# unified article universe + Writing Profile / README render validation
python scripts/writing_analytics_pipeline.py --check

# normalized Data Mart validation
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

Issue #48 Source Freshnessは、このData Martへ次のような独立signalとして追加する方針です。

- initial verification missing
- last verified date
- verification age
- future: source commit drift

Source Freshnessを別の集計系統として増やさず、同じDecision Dashboardから確認できるようにします。
