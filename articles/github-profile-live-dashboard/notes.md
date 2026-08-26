# Notes — GitHubプロフィールをライブな開発ダッシュボードにしてみた

## 記事の中心

Qiita #1のTODAY Activityを実運用したあと、「活動量は見えるが今何を作っているかは分からない」と感じたところからProfile Signalを拡張した実体験を書く。

単純にWidgetを追加した話ではなく、14機能案を6つの表示ブロックへ整理し、情報量を増やしつつREADMEの重複を減らした設計判断を中心にする。

## GitHub verified state — 2026-08-26

対象: `mizzz-ivr/mizzz-ivr`

### Merge済み

- PR #18 — TODAY Activity
- PR #19 — Profile Signal Phase 1
- PR #20 — Profile Signal Phase 2

### mainの現在構成

```text
LIVE SIGNAL
TODAY // counters only
CURRENT FOCUS + TODAY'S STACK
DEV PULSE // Last 7 days
NOW BUILDING // top 3 active repositories
ACTIVITY STREAM // latest 4 public development events
---
NOW // What I build
PUBLIC BUILDS
STACK
```

PR #20後、TODAYの`Today's signal`と旧7-day bar chartは削除済み。

- latest events → ACTIVITY STREAM
- 7-day trend → DEV PULSE

へ責務を移した。

### Phase 1 analytics

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

### Phase 2

State schema v2:

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

PR #21 `feat: add Profile Signal operations health and CI`

記事Source作成時点ではopen。

CI previewは成功済み。

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

### Request budget

Phase 3追加分:

- Repository metadata × 最大3
- Actions runs × 最大3

= 最大6 standard REST requests/run。

TODAYのSearch APIとは別枠でPublic dataのみ扱う。

### no-op commit対策

Phase 3 operations scriptはtracked HEADの`data/profile-signal-state.json`とsemantic stateを比較する。

最終stateが同じ場合は以前の`generated_at`を維持し、Phase 3層の追加だけを理由に3時間ごとの無意味なcommitが発生しないようにする。

## 記事公開前に更新する箇所

PR #21 Merge後:

- [ ] article内「実装しています」→「実装した」へ変更
- [ ] state schema v2の説明をv3まで発展した流れに更新
- [ ] PROJECT HEALTH + CI SIGNALの実スクリーンショット追加
- [ ] main READMEを再取得
- [ ] workflow / testsを再取得
- [ ] 実際のCI label / pass rateは撮影時点の例として扱う

## Qiita #2 タグ候補

候補:

1. GitHub
2. GitHubActions
3. Python
4. GitHubAPI
5. 個人開発

Qiita #1より「プロフィールを自分の開発Dashboardに育てた」という個人開発色が強いため、5つ目は`個人開発`を第一候補にする。

## 公開前チェック

- [ ] STYLE_GUIDE.md確認
- [ ] Repository main / PR / CIを再確認
- [ ] Private RepositoryやPrivate Activityが記事・画像にない
- [ ] Healthを絶対的な品質指標として書かない
- [ ] CODE WEATHERを生産性指標として書かない
- [ ] Contribution Graphと独自Activity指標を混同しない
- [ ] 第1弾と同じ説明を必要以上に繰り返さない
- [ ] Qiita #1から自然に続く記事として読めるか確認
