# Article Source Freshness

## 目的

技術記事の内容を最後にいつ・何を根拠に再確認したかを、推測せずRepository metadataとして記録します。

Source Freshnessは独立した台帳やDashboardを増やさず、Writing Analyticsの共通Data MartとDecision Dashboardへ統合します。

## Metadataの保存場所

### 共通記事

`articles/<slug>/article.md` のfront matterへoptionalで記録します。

```yaml
verified_at: 2026-08-28
source_repositories:
  - owner/repository
source_refs:
  - repository: owner/repository
    commit: 0123456789abcdef0123456789abcdef01234567
```

### Platform-native記事

Zenn-native `articles/<slug>.md` のfront matterはZenn側のschemaを優先し、Analytics専用fieldを追加しません。

代わりに次のsidecarをSource of Truthとして使用します。

```text
metadata/platform-native-analytics.yml
```

```yaml
schema_version: 1
articles:
  articles/example.md:
    source_repositories:
      - owner/repository
    verified_at: 2026-08-28
    source_refs:
      - repository: owner/repository
        commit: 0123456789abcdef0123456789abcdef01234567
```

sidecarで許可するfieldは次の3つだけです。

- `source_repositories`
- `verified_at`
- `source_refs`

`title` / `status` / `published_at` / 公開URL等はoverrideできません。sidecarはPublication Registryに存在する公開済みの直接 `articles/<slug>.md` だけを対象にできます。

## `verified_at`

- 形式: `YYYY-MM-DD`
- 意味: 元Repository / Docs / CI等を見て、記事内の技術的事実を最後に実確認した日
- 実確認していない過去日を推測して入れない
- Source Freshnessは外部metrics snapshotの日付に依存せず、JSTの当日を独立した `freshness.as_of` として使う
- `freshness.as_of` より未来の日付はCIでrejectする

これにより、最新metrics snapshotが昨日でも、今日行った正当なarticle verificationをfuture dateとして誤判定しません。

## `source_refs`

verification時に確認したimmutable source commitを残したい場合だけ使用します。

- list形式
- 各要素は `repository` / `commit` の2fieldのみ
- `repository`: `owner/repository` 形式
- `repository` は同じ記事の `source_repositories` に含まれている必要がある
- `commit`: 40文字commit SHA
- `source_refs` を記録する場合は `verified_at` が必須
- 同じrepository + commitの重複はrejectする

`source_refs` は必須ではありません。Docsや複数の外部仕様を確認した記事など、commit SHAだけではverification evidenceを表現しきれない場合でも `verified_at` は記録できます。

## 既存記事

既存記事へ過去のverification日・commit SHAを自動生成しません。

metadataが無いpublished articleはAnalytics上で:

```text
needs_initial_verification
```

として表示します。

次回その記事を実際に再確認した時点で `verified_at` と、必要なら `source_refs` を追加します。

## Analytics

共通derived data:

```text
data/analytics/writing-analytics.json
```

`freshness` sectionでは次を確認できます。

- `as_of`: Freshness専用のJST基準日
- published article総数
- verified article数
- needs initial verification件数
- oldest verification age
- articleごとのverified date / age / source ref count

Data Martには `source_refs.repository` やcommit SHAそのものを複製せず、`source_ref_count` だけを出します。元のevidenceはarticle front matterまたはplatform-native sidecarをSource of Truthとします。

同じslugを持つ `articles/<slug>.md` と `articles/<slug>/article.md` が存在しても、Freshnessのarticle identityはrepository内pathで分離します。

Decision Dashboard:

```text
reports/visual-dashboard.md
```

上部KPIと `Source Freshness` sectionでinitial verification件数と記事別状態を確認できます。

## Freshness threshold

このPhaseでは「90日を超えたらstale」のような閾値を設けません。

記事・技術領域によって更新頻度が異なるため、根拠のない一律thresholdを決めず、まず以下を正確に保持します。

- verification有無
- verified date
- days since verified

将来、実運用データを見て必要性が確認できた場合だけreview policyを別途決定します。

## CI

```bash
python scripts/writing_data_mart.py --check
python -m unittest discover -s tests -v
```

reject対象:

- invalid / future `verified_at`
- malformed / duplicate source ref
- `source_refs.repository` と `source_repositories` の不整合
- `verified_at` が無い状態で `source_refs` を記録
- duplicate analytics article path
- sidecarのunsupported field
- sidecarから共通記事や未公開native記事をoverrideすること

## Non-goals

- GitHub APIでsource repositoryの最新HEADを自動取得する
- source commitから現在HEADまでの差分量を自動評価する
- dependency / API breaking changeを自動判定する
- private repository情報をderived Data Mart / Public Portfolio Exportへ追加する
- 過去verificationをAIで推測する
