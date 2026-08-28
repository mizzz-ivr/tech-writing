# Content Gap / Next Article Opportunities

> As of: 2026-08-28

Repository metadataから再生成するderived reportです。本文やbacklog自由文から技術分類を推測せず、明示されたmetadataだけを使います。

## Recommendation Policy

候補は単一スコアへ潰さず、次の優先順位を辞書順に評価します。

1. Portfolio / career coverage gap
2. `source_repositories` 等で実装・検証根拠が明示されているか
3. 未公開classification / 最終投稿日からのcoverage gap・recency
4. 関連する公開記事のpositive reaction
5. 同条件なら `review` を `draft` よりreadyとして扱う

external reactionは4番目の補助情報で、反応が良いテーマだけを書く推薦にはしません。

## Current Portfolio Coverage

- Tracked articles: **7**
- Published articles: **5**
- Draft / review candidates: **2**
- Unchecked backlog items: **50**

### topics

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| GitHub | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| GitHubActions | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| Python | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| 個人開発 | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| GitHubAPI | 2 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| ai-development | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| architecture | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| github | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| individual-development | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| openai | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| OSS | 1 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| security | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| typescript | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| 生成ai | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |

### domains

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| developer-productivity | 4 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| devops | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| ai | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |

### languages

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| Python | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |

### technologies

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| GitHub Actions | 4 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| GitHub API | 2 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| GitHub | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| GitHub Events API | 1 | 2026-08-27 | 1d | ✓ | ✓ | ✓ |
| GitHub Issues | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| GitHub Pull Requests | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| GitHub Releases | 1 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| GitHub Search API | 1 | 2026-08-26 | 2d | ✓ | ✓ | ✓ |

### portfolio_signals

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| automation | 3 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| architecture | 2 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |
| ai-assisted-development | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| ci-cd | 1 | 2026-08-26 | 2d | ✓ | ✓ | ✓ |
| development-process | 1 | 2026-08-24 | 4d | ✓ | ✓ | ✓ |
| oss | 1 | 2026-08-28 | 0d | ✓ | ✓ | ✓ |

## Pipeline-only Coverage Gaps

draft / reviewには存在するが、公開済み記事ではまだ示せていないclassificationです。

- **topics:** `ci`, `engineering`, `github-actions`, `writing`
- **portfolio_signals:** `communication`

## Next Article Candidates

### 1. [技術記事とは別に、エンジニアとして考えていることを書く場所を作ることにした](../articles/260827-engineer-thinking-place/article.md)

- Status: `draft`
- Portfolio gap: `communication`
- Implementation evidence: `mizzz-ivr/tech-writing`
- Coverage gap / recency: no >30d or unpublished domain/language/technology gap detected
- Related positive-reaction context: 1 published article(s)

### 2. [個人開発でもPRを切ってCIを通すようにしている理由](../articles/personal-dev-pr-ci/article.md)

- Status: `review`
- Portfolio gap: no new published portfolio signal detected
- Implementation evidence: not recorded
- Coverage gap / recency: no >30d or unpublished domain/language/technology gap detected
- Related positive-reaction context: 0 published article(s)
- Metadata needed before stronger scoring: `domains`, `languages`, `technologies`, `portfolio_signals`, `source_repositories`

## Backlog Hygiene / Overlap

backlog自由文にはclassificationを自動付与せず、タイトル類似度が高い既存記事だけを重複候補として可視化します。

- `個人開発でもPRを切ってCIを通すようにしている理由` → **review** `個人開発でもPRを切ってCIを通すようにしている理由` (title similarity 1.00, section: 次に着手)
- `note #1: 技術記事とは別に、エンジニアとして考えていることを書く場所を作ることにした` → **draft** `技術記事とは別に、エンジニアとして考えていることを書く場所を作ることにした` (title similarity 1.00, section: 次に着手)
- `Zenn: 生成AIを「APIを呼ぶだけ」で終わらせない — Secret・Quota・Kill Switchを分離したAI Runtime設計` → **published** `生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計` (title similarity 0.89, section: 次に着手)

### Evidence-backed backlog items not already tracked

- None

### Backlog items intentionally left unscored

- Count: **47**
- 理由: source repository / classificationが明示されていない自由文へ推測を入れないため。
  - `AI Runtimeへ2つ目のProviderを追加したとき、どこまで共通化できたか` (Zenn候補 — Design / Deep Dive)
  - `Discord BotをPlugin Runtime中心の構成にしていった話` (Zenn候補 — Design / Deep Dive)
  - `個人開発のAI機能でRate Limitだけでは足りなかった — Quota / Cost / Concurrency設計` (Zenn候補 — Design / Deep Dive)
  - `個人開発にSBOMとGrypeを入れるだけでは終わらない — CIでSecurity Gateを運用する設計` (Zenn候補 — Design / Deep Dive)
  - `GitHub Actions / CI成功後だけProduction Deployするパイプライン設計` (Zenn候補 — Design / Deep Dive)
  - `個人開発を「完成させること」より「続けること」を大事にしている` (エンジニアとしての考え方)
  - `AIにコードを書かせるようになって、エンジニアの仕事について考えた` (エンジニアとしての考え方)
  - `趣味の個人開発なのにIssue・PR・CIまで使う理由` (エンジニアとしての考え方)
  - `技術者として「何を知っているか」より「どう判断するか」が大事になってきた` (エンジニアとしての考え方)
  - `コードを書く時間が減ってもエンジニアと言えるのか` (エンジニアとしての考え方)
  - … and 37 more

## Interpretation

- `30d / 90d / 365d` は公開済みclassificationの最終投稿日を基準にする。
- Zenn-native `articles/*.md` は `ideas/published.md` に公開記録がある記事だけcoverageへ含める。draft状態は推測しない。
- `not yet published` はtracked draft/review metadataにはあるが、公開済みcoverageにはまだ存在しない値。
- `source_repositories` が無い候補は、実装根拠が無いと断定せず **not recorded** とする。
- backlog自由文は分類推測しない。推薦精度を上げる場合はfront matterまたはbacklogへ根拠を明示する。
- metricsが無い / positive reactionが無い場合も推薦自体は成立する。
