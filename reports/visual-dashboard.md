# Writing Analytics — Decision Dashboard

> Analytics as of: 2026-08-28 · Freshness as of: 2026-08-28 · Derived from Repository metadata / publication registry / stored metric snapshots

## まず見る

| 判断軸 | 現在 |
| --- | --- |
| Published | **5** |
| Pipeline | Draft **1** / Review **1** |
| Last published | **2026-08-28** |
| Source freshness | Initial verification **4** / Verified **1** |
| Metric snapshots | **2** / observed span **1d** |
| Data Quality | **3件 — 下のData Qualityを確認** |
| Pipeline-only coverage gaps | **5** |
| GitHub → Writing Funnel | Untracked **297** / Evidence **297** |
| 次の記事候補 | [技術記事とは別に、エンジニアとして考えていることを書く場所を作ることにした](../articles/260827-engineer-thinking-place/article.md) (`draft`) |

### 今の判断

- GitHub実装evidenceに未記事化候補が **297件** あります。先頭候補: `mizzz-ivr/profile-signal` / Profile Signal v0.4.0。
- Published記事 **4件** はinitial verification未記録です。過去の確認日は推測せず、次回実確認時に `verified_at` を記録します。
- 7日Trendはまだ待機中です。現在の実snapshot spanは **1日** で、補間はしません。
- Data Quality findingが **3件** あります。記事追加より先に、必要ならmetadata整備対象として確認できます。
- 次記事候補の主な根拠: `communication`

## Editorial Pipeline

![Editorial pipeline](./assets/pipeline.svg)

## Coverage Gaps

draft / reviewにはあるが、公開済みPortfolioではまだ示せていないclassificationです。

- **topics:** `ci`, `engineering`, `github-actions`, `writing`
- **portfolio_signals:** `communication`

## GitHub → Writing Funnel

> GitHub snapshot as of: **2026-08-28**

最近のpublic Repository実装から、article/backlog titleと明示的に重複していないevidenceだけを日常判断用に表示します。tracked evidenceを含む監査用全件はContent Opportunities / Data Martで確認します。意味的な重複や重要度は推測しません。

| Repository | Kind | Untracked evidence | Date |
| --- | --- | --- | --- |
| `mizzz-ivr/profile-signal` | `release` | [Profile Signal v0.4.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0) | 2026-08-27 |
| `mizzz-ivr/profile-signal` | `release` | [Profile Signal v0.3.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.3.0) | 2026-08-27 |
| `mizzz-ivr/roomate-voice` | `release` | [RooMate Voice v0.1.0 (Preview)](https://github.com/mizzz-ivr/roomate-voice/releases/tag/v0.1.0) | 2026-08-26 |
| `mizzz-ivr/ivmz-home` | `pull_request` | [security: isolate Netlify preview database migrations](https://github.com/mizzz-ivr/ivmz-home/pull/21) | 2026-08-28 |
| `mizzz-ivr/ivmz-home` | `pull_request` | [security: harden Payload admin and auth boundaries](https://github.com/mizzz-ivr/ivmz-home/pull/19) | 2026-08-27 |
| `ivRooom/Herta` | `pull_request` | [feat(ai): add secure image generation artifact runtime](https://github.com/ivRooom/Herta/pull/349) | 2026-08-27 |
| `mizzz-ivr/profile-signal` | `pull_request` | [docs: add deterministic sample profile page](https://github.com/mizzz-ivr/profile-signal/pull/7) | 2026-08-27 |
| `mizzz-ivr/mizzz-ivr` | `pull_request` | [fix(profile): add scheduler freshness fallback](https://github.com/mizzz-ivr/mizzz-ivr/pull/55) | 2026-08-27 |
| `mizzz-ivr/mizzz-ivr` | `pull_request` | [fix(profile): reactivate schedules with direct workflow edit](https://github.com/mizzz-ivr/mizzz-ivr/pull/54) | 2026-08-27 |
| `mizzz-ivr/mizzz-ivr` | `pull_request` | [fix(profile): re-register Profile Signal schedules](https://github.com/mizzz-ivr/mizzz-ivr/pull/53) | 2026-08-27 |
| `mizzz-ivr/mizzz-ivr` | `pull_request` | [chore: prune merged profile work branches](https://github.com/mizzz-ivr/mizzz-ivr/pull/51) | 2026-08-27 |
| `mizzz-ivr/mizzz-ivr` | `pull_request` | [feat(profile): add Engineering DNA public evidence profile](https://github.com/mizzz-ivr/mizzz-ivr/pull/50) | 2026-08-27 |

Priority: `release` → `pull_request` → labeled `issue` → recency。AI significance scoreは使いません。

## Source Freshness

> Freshness as of: **2026-08-28**

技術的事実を最後に再確認した記録です。未記録の記事へ過去日付を推測して補完しません。現段階では任意のstale thresholdも置かず、initial verificationと経過日数をそのまま表示します。

| Article | Status | Verified at | Age | Commit refs |
| --- | --- | --- | ---: | ---: |
| [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](../articles/repository-is-source-of-truth/article.md) | Needs initial verification | - | - | 0 |
| [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](../articles/github-profile-daily-activity/article.md) | Needs initial verification | - | - | 0 |
| [GitHubプロフィールをライブな開発ダッシュボードにしてみた](../articles/github-profile-live-dashboard/article.md) | Needs initial verification | - | - | 0 |
| [生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計](../articles/ai-runtime-safety-boundary.md) | Needs initial verification | - | - | 0 |
| [自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた](../articles/profile-signal-github-action/article.md) | Verified | 2026-08-28 | 0d | 0 |

## Portfolio Coverage

全classificationの詳細表は [Content Opportunities](./content-opportunities.md) に委譲し、ここでは分布だけを確認します。

### Domains

![Published domains](./assets/domains.svg)

### Technologies

![Technology coverage](./assets/technologies.svg)

### Portfolio Signals

![Portfolio signals](./assets/portfolio-signals.svg)

## Reactions

![Observed reactions](./assets/reactions.svg)

reaction chartはlikes / stocks / bookmarks / commentsのみを描画します。page viewsはData Martの観測値として保持します。`0` / `unavailable` / field missingは別状態で、単一のPopularity Scoreには集約しません。

| Article | Platform | Reactions / observed metrics |
| --- | --- | --- |
| [生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計](https://zenn.dev/mizzz-ivr/articles/ai-runtime-safety-boundary) | zenn | likes 1 · bookmarks 0 · comments 0 · page_views unavailable |
| [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a) | qiita | likes 0 · stocks 2 · comments 0 · page_views 159 |
| [GitHubプロフィールをライブな開発ダッシュボードにしてみた](https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630) | qiita | likes 0 · stocks 0 · comments 0 · page_views 160 |
| [自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた](https://qiita.com/mizzz-ivr/items/f20a2d58f623097a5904) | qiita | likes 0 · stocks 0 · comments 0 · page_views 80 |
| [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e) | qiita | likes 0 · stocks 0 · comments 0 · page_views 346 |

## Trend Readiness

- Snapshot count: **2**
- First snapshot: **2026-08-27**
- Latest snapshot: **2026-08-28**
- Observed span: **1 days**

| Window | Status |
| --- | --- |
| 7d | **Waiting** |
| 30d | **Waiting** |
| 90d | **Waiting** |

履歴不足時は推測・直線補間・synthetic historyを作りません。

## Data Quality

- `ai-runtime-safety-boundary`: `domains` が未分類
- `ai-runtime-safety-boundary`: `languages` が未分類
- `ai-runtime-safety-boundary`: `technologies` が未分類

## Analysis Data

- [Normalized Writing Analytics Data Mart](../data/analytics/writing-analytics.json) — 集計・分析用の共通derived JSON
- [Public Writing Portfolio JSON](../data/exports/writing-portfolio.json) — 外部公開向けstable schema
- [Writing Profile](./writing-profile.md) — 詳細テキスト分析
- [Content Opportunities](./content-opportunities.md) — coverage全件・次記事推薦の詳細

## Source of Truth

- Article metadata: `articles/**`
- Platform-native analytics evidence: `metadata/platform-native-analytics.yml`
- Publication registry: `ideas/published.md`
- Raw external metrics: `data/metrics/YYYY-MM-DD.json`
- Raw GitHub writing evidence: `data/github-funnel/YYYY-MM-DD.json`
- Data Mart / Dashboard / reports: **derived / regeneratable**
