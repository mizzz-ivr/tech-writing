# Public Writing Portfolio Export

Writing Analytics Phase 2Dで生成する `data/exports/writing-portfolio.json` のstable public schemaとSecurity境界です。

## 目的

`ivmz-home` 等のconsumerがREADMEやMarkdown reportをscrapeせず、公開済みWriting Portfolioをversioned JSONとして利用できるようにします。

## Source of Truth

1. 公開済みarticle metadata
2. `ideas/published.md` の公開記録
3. `data/metrics/YYYY-MM-DD.json` のlatest snapshot
4. `config/portfolio-export.yml` のpublic export policy
5. `data/exports/writing-portfolio.json` は再生成可能なderived artifact

Zenn-native `articles/*.md` はPhase 2Cと同じく、`ideas/published.md` に公開記録がある記事だけexport対象です。Zenn固有front matterからdraft/review状態を推測しません。

## Stable schema

現在は `schema_version: 1` です。

Top-level:

- `schema_version`
- `as_of`
- `summary`
- `coverage`
- `recent_articles`
- `notable_articles`
- `export_quality`

既存fieldの意味を壊す変更は同じschema versionで行いません。破壊的変更が必要な場合はschema versionを上げ、consumer移行期間を設けます。

## Public data only

export対象は公開済み記事だけです。draft / review / backlog本文は含めません。

公開記事から次の情報だけを出力します。

- slug / title / published_at
- article_type / level
- topics / domains / languages / technologies / portfolio_signals
- Qiita / Zenn公開URL
- 明示的にpublic allowlistへ登録されたsource repository
- 30 / 90 / 365日coverage
- latest snapshotでpositive reactionがあるNotable記事

Secret、Token、Password、Cookie、Authorization、API Key相当のfield名をexport validatorで拒否します。

### source repository boundary

`source_repositories` を無条件にexportしません。

`config/portfolio-export.yml` の `public_source_repositories` を明示的な公開allowlistとし、article metadataとの積集合だけをJSONへ含めます。

allowlist外のsource repository参照は名前をexportせず、`export_quality.omitted_non_allowlisted_source_repository_references` の件数だけを出します。

このため、将来private repository名がarticle metadataへ混入してもstable exportへ自動伝播しません。public allowlistへ追加するときは、そのrepository名を外部Portfolioへ公開してよいことを人が確認します。

## Metrics boundary

Notableではplatform固有のpublic reactionを保持します。

- Qiita: likes / stocks / comments
- Zenn: likes / bookmarks / comments

複数指標を総合Popularity Scoreへ変換しません。

`page_views` はpublic exportへ含めません。Writing Analytics内部snapshotに存在していても、Portfolio consumerへ自動公開しない境界です。

## Determinism

exportには実行時刻を入れません。`as_of` はlatest valid metrics snapshotの日付を優先し、無ければ公開記事の最新日を使います。

同じRepository stateから同じJSONを生成でき、毎回不要なbot commitが発生しないようにします。

## Commands

生成:

```bash
python scripts/writing_portfolio_export.py
```

PR validation:

```bash
python scripts/writing_portfolio_export.py --check
```

`--check` はファイルを書き換えず、policy・schema・public data boundaryを検証します。

## GitHub Actions

`Writing Analytics` workflowで次を行います。

- PR: unit tests + portfolio export check
- main / schedule / manual refresh: analytics / content opportunities更新後にpublic exportを生成
- `data/exports/writing-portfolio.json` に差分があればanalytics bot commitへ含める

GitHub Actions bot自身のcommitからrefreshを再実行しない既存loop preventionを維持します。

## Consumer policy

`ivmz-home` 等は必ず `schema_version` を確認してから読むことを推奨します。

consumerは未定義fieldに依存せず、未知fieldを無視できる実装にします。READMEや`reports/*.md`をHTML/Markdown scrapeしてPortfolio data sourceとして使わない方針です。
