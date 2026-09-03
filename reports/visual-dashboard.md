# Writing Analytics — Decision Dashboard

> Analytics as of: 2026-09-04 · Freshness as of: 2026-09-04 · Derived from Repository metadata / publication registry / stored metric snapshots

## まず見る

| 判断軸 | 現在 |
| --- | --- |
| Published | **6** |
| Pipeline | Draft **2** / Review **1** |
| Last published | **2026-09-04** |
| Source freshness | Initial verification **4** / Verified **2** |
| Metric snapshots | **9** / observed span **8d** |
| Data Quality | **問題なし** |
| Pipeline-only coverage gaps | **7** |
| GitHub → Writing Funnel | Themes **223** / Events **304** |
| 次の記事候補 | [常時起動のCI runnerをephemeral scale-to-zeroに移す設計と、その途中で全部踏んだ話](../articles/260831-runner-scale-to-zero-design/article.md) (`draft`) |

### 今の判断

- GitHub実装の未記事化evidence **304件** を、明示scopeで **223 themes** に整理しています。先頭theme: `mizzz-ivr/profile-signal` / Profile Signal v0.4.0（1 events、代表: Profile Signal v0.4.0）。
- Published記事 **4件** はinitial verification未記録です。過去の確認日は推測せず、次回実確認時に `verified_at` を記録します。
- 7日Trendを実データだけで分析できる状態です。
- Data Quality blockerはありません。
- 次記事候補の主な根拠: `cost-optimization`, `technologies:AWS Lambda (not yet published)`, `technologies:github-aws-runners (not yet published)`

## Editorial Pipeline

![Editorial pipeline](./assets/pipeline.svg)

## Coverage Gaps

draft / reviewにはあるが、公開済みPortfolioではまだ示せていないclassificationです。

- **topics:** `engineering`, `terraform`, `writing`
- **technologies:** `AWS Lambda`, `github-aws-runners`
- **portfolio_signals:** `communication`, `cost-optimization`

## GitHub → Writing Funnel

> GitHub snapshot as of: **2026-09-04**

最近のpublic Repository実装を、明示的なConventional Commit scopeだけでtheme groupingして表示します。scopeが無いeventは無理にまとめません。tracked evidenceを含む監査用全件はContent Opportunities / Data Martで確認します。意味的な重複や重要度は推測しません。

| Repository | Theme | Events | Representative evidence | Latest |
| --- | --- | ---: | --- | --- |
| `mizzz-ivr/profile-signal` | release | **1** | [Profile Signal v0.4.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0) | 2026-08-27 |
| `mizzz-ivr/profile-signal` | release | **1** | [Profile Signal v0.3.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.3.0) | 2026-08-27 |
| `mizzz-ivr/roomate-voice` | release | **1** | [RooMate Voice v0.1.0 (Preview)](https://github.com/mizzz-ivr/roomate-voice/releases/tag/v0.1.0) | 2026-08-26 |
| `ivRooom/Herta` | scope `studio` | **19** | [feat(studio): AI Runtime Settingsをprovider-agnostic化する](https://github.com/ivRooom/Herta/pull/343) | 2026-08-27 |
| `ivRooom/Herta` | scope `ai` | **15** | [feat(ai): Studio設定RoleメンションをAI triggerへ追加](https://github.com/ivRooom/Herta/pull/370) | 2026-09-02 |
| `mizzz-ivr/mizzz-ivr` | scope `profile` | **12** | [fix(profile): make Profile Signal dashboard full width](https://github.com/mizzz-ivr/mizzz-ivr/pull/59) | 2026-08-29 |
| `ivRooom/Herta` | scope `birthday` | **9** | [fix(birthday): 未登録Guildメンバーの自己登録を許可](https://github.com/ivRooom/Herta/pull/301) | 2026-08-21 |
| `ivRooom/Herta` | scope `deps` | **8** | [chore(deps): Next.js security patchとReact Query更新](https://github.com/ivRooom/Herta/pull/352) | 2026-08-29 |
| `ivRooom/Herta` | scope `moderation` | **5** | [feat(moderation): 設定画面をNGワード・自動検知中心に再編](https://github.com/ivRooom/Herta/pull/274) | 2026-08-18 |
| `ivRooom/Herta` | scope `deploy` | **4** | [fix(deploy): Runtime Secret Encryption master keyをproductionへ注入する](https://github.com/ivRooom/Herta/pull/357) | 2026-08-29 |
| `ivRooom/Herta` | scope `suggestion` | **3** | [feat(suggestion): Staff向けSuggestion履歴を追加](https://github.com/ivRooom/Herta/pull/327) | 2026-08-25 |
| `ivRooom/Herta` | scope `runtime` | **3** | [docs(runtime): Worker Runtime consumer要否を明文化](https://github.com/ivRooom/Herta/pull/317) | 2026-08-24 |

Raw untracked evidence **304件** → deterministic theme **223件**。Compression: **1.36x**。

Grouping: `release`は独立theme、`feat(scope)` / `fix(scope)`等は同一Repository内の明示scopeでgrouping、scope無しはsingleton。AI semantic clustering / significance scoreは使いません。

## Source Freshness

> Freshness as of: **2026-09-04**

技術的事実を最後に再確認した記録です。未記録の記事へ過去日付を推測して補完しません。現段階では任意のstale thresholdも置かず、initial verificationと経過日数をそのまま表示します。

| Article | Status | Verified at | Age | Commit refs |
| --- | --- | --- | ---: | ---: |
| [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](../articles/repository-is-source-of-truth/article.md) | Needs initial verification | - | - | 0 |
| [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](../articles/github-profile-daily-activity/article.md) | Needs initial verification | - | - | 0 |
| [GitHubプロフィールをライブな開発ダッシュボードにしてみた](../articles/github-profile-live-dashboard/article.md) | Needs initial verification | - | - | 0 |
| [生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計](../articles/ai-runtime-safety-boundary.md) | Needs initial verification | - | - | 0 |
| [自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた](../articles/profile-signal-github-action/article.md) | Verified | 2026-08-28 | 7d | 0 |
| [GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた](../articles/260831-selfhosted-graviton-runner/article.md) | Verified | 2026-09-04 | 0d | 2 |

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
| [GitHub Actionsの無料枠が尽きたので、AWSにセルフホストのGraviton runnerを立てた](https://qiita.com/mizzz-ivr/items/e4c663c7f5d3f82fd0a9) | qiita | likes 0 · stocks 0 · comments 0 · page_views 16 |
| [生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計](https://zenn.dev/mizzz-ivr/articles/ai-runtime-safety-boundary) | zenn | metrics error |
| [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a) | qiita | likes 0 · stocks 2 · comments 0 · page_views 216 |
| [GitHubプロフィールをライブな開発ダッシュボードにしてみた](https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630) | qiita | likes 0 · stocks 0 · comments 0 · page_views 214 |
| [自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた](https://qiita.com/mizzz-ivr/items/f20a2d58f623097a5904) | qiita | likes 1 · stocks 1 · comments 0 · page_views 302 |
| [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e) | qiita | likes 0 · stocks 0 · comments 0 · page_views 392 |

## Trend Readiness

- Snapshot count: **9**
- First snapshot: **2026-08-27**
- Latest snapshot: **2026-09-04**
- Observed span: **8 days**

| Window | Status |
| --- | --- |
| 7d | **Ready** |
| 30d | **Waiting** |
| 90d | **Waiting** |

履歴不足時は推測・直線補間・synthetic historyを作りません。

## Data Quality

- No issues detected

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
