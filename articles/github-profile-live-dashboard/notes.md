# Notes — GitHubプロフィールをライブな開発ダッシュボードにしてみた

## 記事の中心

Qiita #1のTODAY Activityを実運用したあと、「活動量は見えるが今何を作っているかは分からない」と感じたところからProfile Signalを拡張した実体験を書く。

単純にWidgetを追加した話ではなく、14機能案を表示ブロックへ整理し、情報量を増やしつつREADMEの重複を減らした設計判断を中心にする。

## GitHub verified state — 2026-08-26 22:20 JST

対象: `mizzz-ivr/mizzz-ivr`

### Merge済み

- PR #18 — TODAY Activity
- PR #19 — Profile Signal Phase 1
- PR #20 — Profile Signal Phase 2
- PR #21 — Profile Signal Phase 3 Operations

### mainの現在構成

```text
LIVE SIGNAL
TODAY // counters only
CURRENT FOCUS + TODAY'S STACK
DEV PULSE // Last 7 days + CI SIGNAL
NOW BUILDING // top 3 + PROJECT HEALTH
ACTIVITY STREAM // latest 4 public development events
---
NOW // What I build
PUBLIC BUILDS
STACK
```

Phase 3までmainへ反映済み。

- latest events → ACTIVITY STREAM
- 7-day trend + CI → DEV PULSE
- project health + repo CI → NOW BUILDING

へ責務を集約している。

## Phase 1 analytics

- DEV STATUS
- CODE WEATHER
- BUILD STREAK
- CURRENT FOCUS
- TODAY'S STACK

CURRENT FOCUS weight:

```text
commit        = 1
issue create  = 2
issue done    = 3
PR opened     = 4
PR merged     = 6
release       = 10
```

## Phase 2

- `dev_pulse`
- `now_building`
- `activity_stream`

DEV PULSE:

- `data/activity/YYYY/MM/YYYY-MM-DD.json`を7日分利用
- `assets/dev-pulse.svg`生成
- light/dark mode

NOW BUILDING:

- weighted repository activity上位3件
- share / score / event count / last activity

ACTIVITY STREAM:

- PushEvent
- PullRequestEvent
- IssuesEvent
- ReleaseEvent
- CreateEvent

を短い表示へ正規化し最大4件表示。

## Phase 3 — Operations

PR #21 `feat: add Profile Signal operations health and CI` はMerge済み。

追加内容:

- PROJECT HEALTHをNOW BUILDINGへ統合
- CI SIGNALをDEV PULSEへ統合
- Public Repository metadata
- Public GitHub Actions runs
- state schema v3

### CIルール

各NOW BUILDING Repositoryについてcompleted runs最大10件を取得し、直近7日を評価。

Pass:

- success

Fail:

- failure
- timed_out
- action_required
- startup_failure

Pass rateから除外:

- cancelled
- skipped
- neutral
- その他評価対象外conclusion

### PROJECT HEALTHルール

- ARCHIVED — archived / disabled
- QUIET — 30日以上pushなし
- ATTENTION — latest evaluated CI failure等
- WATCH — recent CI mixed
- HEALTHY — active + recent CI passing/stable
- ACTIVE — active but no evaluated CI signal

Issue数だけでHealthを判定しない。

Health / CIはRepository品質の絶対評価ではなく、最近のPublic GitHub Actionsとpush recencyから作る運用Signalとして扱う。

### Request budget

Phase 3追加分:

- Repository metadata × 最大3
- Actions runs × 最大3

= 最大6 standard REST requests/run。

TODAYのSearch APIとは別枠でPublic dataのみ扱う。

## Screenshot facts — 2026-08-26 22:02 JST前後

### Dashboard overview

撮影画像: `01-profile-dashboard-overview.jpg`

- LIVE SIGNAL: BUILDING / STORM / 2 DAY STREAK
- TODAY: 350 commits / 21 PRs / 6 issues created / 4 issues done
- CURRENT FOCUS: `mizzz-ivr/ivmz-home`
- DEV PULSEまで1画面で確認可能

### DEV PULSE + CI SIGNAL

撮影画像: `02-dev-pulse-ci-signal.jpg`

```text
C 345 · PR 19 · ISSUE 10
activity 374
ATTENTION
56% PASS RATE
15 / 27 PASSED / EVALUATED
3 REPOS WITH CI
```

値は撮影後に変動しているため記事では撮影時点の例と明記する。

### NOW BUILDING + PROJECT HEALTH + ACTIVITY STREAM

撮影画像: `03-now-building-health-activity-stream.jpg`

```text
mizzz-ivr/ivmz-home
ATTENTION · CI 0/10 · 0%

ivRooom/Herta
WATCH · CI 5/7 · 71%

mizzz-ivr/mizzz-ivr
HEALTHY · CI 10/10 · 100%
```

Activity StreamにはPR #21 Merge / PR #7 Open / tech-writing pushが表示されている。

## Qiita #1

公開済み:

https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a

第2弾の冒頭からリンクする。

## Phase 4 — History

PR #22 `feat: add Profile Signal history and dev recap` を作成済み。

CI成功:

- 18 tests
- Daily snapshots
- Weekly reports
- Monthly reports
- state schema v4
- DEV RECAP
- 7 generated profile sections

Qiita #2はPhase 3までのLive Dashboardを本編スコープとし、Phase 4は「次に進めていること」として末尾で触れる程度にする。

## Qiita #2 タグ

1. GitHub
2. GitHubActions
3. Python
4. GitHubAPI
5. 個人開発

## 公開前チェック

- [x] STYLE_GUIDE.md確認
- [x] Repository main / PR #21 / CIを再確認
- [x] Private RepositoryやPrivate Activityが画像にない
- [x] Healthを絶対的な品質指標として書かない
- [x] CODE WEATHERを生産性指標として書かない
- [x] Contribution Graphと独自Activity指標を混同しない
- [x] 第1弾と同じ説明を必要以上に繰り返さない
- [x] Qiita #1から自然に続く導入へ更新
- [ ] 3枚の画像をQiitaへアップロードしてPlaceholder置換
- [ ] Qiita Preview / スマホPreview
- [ ] 公開
