# Content Gap / Next Article Opportunities

> As of: 2026-09-02

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
- Unchecked backlog items: **48**

### topics

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| GitHub | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| GitHubActions | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| Python | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| 個人開発 | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| GitHubAPI | 2 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| ai-development | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| architecture | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| github | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| individual-development | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| openai | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| OSS | 1 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| security | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| typescript | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| 生成ai | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |

### domains

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| developer-productivity | 4 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| devops | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| ai | 2 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |

### languages

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| Python | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| TypeScript | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |

### technologies

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| GitHub Actions | 4 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| GitHub API | 2 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| GitHub | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| GitHub Events API | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |
| GitHub Issues | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| GitHub Pull Requests | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| GitHub Releases | 1 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| GitHub Search API | 1 | 2026-08-26 | 7d | ✓ | ✓ | ✓ |
| OpenAI API | 1 | 2026-08-27 | 6d | ✓ | ✓ | ✓ |

### portfolio_signals

| Value | Published | Last published | Age | 30d | 90d | 365d |
| --- | ---: | --- | ---: | :---: | :---: | :---: |
| architecture | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| automation | 3 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |
| ai-assisted-development | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| ci-cd | 1 | 2026-08-26 | 7d | ✓ | ✓ | ✓ |
| development-process | 1 | 2026-08-24 | 9d | ✓ | ✓ | ✓ |
| oss | 1 | 2026-08-28 | 5d | ✓ | ✓ | ✓ |

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
- Related positive-reaction context: 2 published article(s)

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

- Count: **45**
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
  - … and 35 more

## Interpretation

- `30d / 90d / 365d` は公開済みclassificationの最終投稿日を基準にする。
- Zenn-native `articles/*.md` は `ideas/published.md` に公開記録がある記事だけcoverageへ含める。draft状態は推測しない。
- `not yet published` はtracked draft/review metadataにはあるが、公開済みcoverageにはまだ存在しない値。
- `source_repositories` が無い候補は、実装根拠が無いと断定せず **not recorded** とする。
- backlog自由文は分類推測しない。推薦精度を上げる場合はfront matterまたはbacklogへ根拠を明示する。
- metricsが無い / positive reactionが無い場合も推薦自体は成立する。

## GitHub → Writing Funnel

configured public repositoryのstored GitHub snapshotから、まだarticle/backlog titleと明示的に重複しない実装evidenceを可視化します。title overlap以外の意味的重複や重要度は推測しません。

- Snapshot: **2026-09-02**
- Monitored repositories: **5**
- Evidence rows: **301**
- Untracked evidence: **301**
- Tracked by explicit title overlap: **0**

| Repository | Kind | Evidence | Date | Tracking |
| --- | --- | --- | --- | --- |
| `mizzz-ivr/profile-signal` | `release` | [Profile Signal v0.4.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0) | 2026-08-27 | untracked |
| `mizzz-ivr/profile-signal` | `release` | [Profile Signal v0.3.0](https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.3.0) | 2026-08-27 | untracked |
| `mizzz-ivr/roomate-voice` | `release` | [RooMate Voice v0.1.0 (Preview)](https://github.com/mizzz-ivr/roomate-voice/releases/tag/v0.1.0) | 2026-08-26 | untracked |
| `ivRooom/Herta` | `pull_request` | [feat(ai): verified Discord AI request中にtypingを表示](https://github.com/ivRooom/Herta/pull/366) | 2026-09-01 | untracked |
| `ivRooom/Herta` | `pull_request` | [fix(ai): detailed Discord replyを安全に1 messageへ収束](https://github.com/ivRooom/Herta/pull/365) | 2026-09-01 | untracked |
| `mizzz-ivr/ivmz-home` | `pull_request` | [docs(ops): document Production Git sync recovery](https://github.com/mizzz-ivr/ivmz-home/pull/39) | 2026-09-01 | untracked |
| `ivRooom/Herta` | `pull_request` | [docs(ai): #354 production acceptanceを#359後の境界へ更新](https://github.com/ivRooom/Herta/pull/361) | 2026-09-01 | untracked |
| `ivRooom/Herta` | `pull_request` | [feat(ai): Discord返信継続とHerta会話ペルソナを追加する](https://github.com/ivRooom/Herta/pull/359) | 2026-08-31 | untracked |
| `ivRooom/Herta` | `pull_request` | [fix(deploy): Runtime Secret Encryption master keyをproductionへ注入する](https://github.com/ivRooom/Herta/pull/357) | 2026-08-29 | untracked |
| `ivRooom/Herta` | `pull_request` | [docs(ai): #354 production E2E rollout Runbookを更新](https://github.com/ivRooom/Herta/pull/355) | 2026-08-29 | untracked |
| `ivRooom/Herta` | `pull_request` | [chore(deps): Next.js security patchとReact Query更新](https://github.com/ivRooom/Herta/pull/352) | 2026-08-29 | untracked |
| `ivRooom/Herta` | `pull_request` | [feat(ai): Code Interpreterのbinary成果物を安全に配信する](https://github.com/ivRooom/Herta/pull/353) | 2026-08-29 | untracked |

Priorityは `release` → `pull_request` → labeled `issue` → recency の明示ルールです。単一のAI significance scoreは作りません。

