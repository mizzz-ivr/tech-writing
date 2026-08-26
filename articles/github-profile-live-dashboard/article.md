---
title: "GitHubプロフィールをライブな開発ダッシュボードにしてみた"
status: review
topics: [GitHub, GitHubActions, GitHubAPI, Python, 個人開発]
source_repositories: [mizzz-ivr/mizzz-ivr]
published:
  qiita: null
  zenn: null
---

# GitHubプロフィールをライブな開発ダッシュボードにしてみた

前回、GitHubプロフィールREADMEに `TODAY // Activity overview` を追加して、その日のCommit / PR / Issueを自動表示するようにしました。

第1弾の記事はこちらです。

https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a

TODAYを実際に使い始めた直後は、プロフィールを開けば「今日はどれくらい開発していたか」が分かるだけでもかなり楽しかったです。

ただ、数時間使っていると別のことが気になりました。

**活動量は分かるけど、今何を作っているのかはまだ分からない。**

自分は複数の個人開発Repositoryを並行して触ることが多いので、`300 commits` と表示されても、それがどのProjectに集中していたのかは数字だけでは分かりません。

そこでTODAYを起点に、GitHubプロフィールを「今の開発状態」が見える小さなDashboardへ広げることにしました。

<!-- QIITA_IMAGE: 01-profile-dashboard-overview.jpg -->

この画像は2026-08-26 22:02 JST前後の実プロフィールです。数値は時間とともに更新されるため、この記事では撮影時点の例として扱います。

現在の上部構成は次のようになっています。

```text
LIVE SIGNAL
TODAY // Activity overview
CURRENT FOCUS + TODAY'S STACK
DEV PULSE // Last 7 days + CI SIGNAL
NOW BUILDING // Active repositories + PROJECT HEALTH
ACTIVITY STREAM // Latest public signals
```

単純にWidgetを増やした話というより、**情報を増やしながらREADMEを散らかさないために、どう責務を整理したか**が今回の中心です。

## 最初に出した案は14個あった

TODAYを作ったあと、追加したい機能を考えるとかなり出てきました。

- CURRENT FOCUS
- BUILD STREAK
- DEV PULSE
- NOW BUILDING
- DEV STATUS
- TODAY'S STACK
- CODE WEATHER
- ACHIEVEMENTS
- LIVE TERMINAL
- ACTIVITY TICKER
- WEEKLY DEV RECAP
- MONTHLY BUILD REPORT
- PROJECT HEALTH
- CI SIGNAL

全部そのまま `##` セクションとして並べると、プロフィールというより監視画面になってしまいます。

そこで「実装する機能数」と「READMEで見せるブロック数」を分けることにしました。

## 14機能を6つの表示ブロックへ整理した

Dashboard部分では、機能を次の役割へまとめました。

```text
LIVE SIGNAL
  DEV STATUS
  CODE WEATHER
  BUILD STREAK

CURRENT FOCUS
  CURRENT FOCUS
  TODAY'S STACK

DEV PULSE
  7-day activity
  CI SIGNAL

NOW BUILDING
  active repositories
  PROJECT HEALTH

ACTIVITY STREAM
  latest development events

DEV RECAP
  weekly
  monthly
  achievements
```

`LIVE TERMINAL` は独立Widgetにせず、将来のTheme / Rendererとして扱う予定です。

この整理をしたことで、機能案を捨てるのではなく、**見せる単位だけ減らす**ことができました。

この記事を書いている時点では、DEV RECAP以外のDashboard部分までmainで動いています。

## TODAYは逆に小さくした

最初のTODAYには、4つのカウンターだけでなく直近Activityのリストと7日グラフも入れていました。

Dashboardを広げ始めると役割が重複します。

```text
最新イベント
→ ACTIVITY STREAM

7日推移
→ DEV PULSE
```

そこでTODAYは4つの数字だけに戻しました。

```text
TODAY // Activity overview

COMMITS
PRS OPENED
ISSUES CREATED
ISSUES DONE
```

Widgetを追加するときに表示を足すだけでなく、**既存Widgetから何を消すかも同時に決める**ようにしたのは良かったです。

## LIVE SIGNAL — 今の状態を1行で見る

プロフィールの先頭にはLIVE SIGNALを置いています。

撮影時点では次の状態でした。

```text
● BUILDING
🌩️ STORM
🔥 2 DAY STREAK
```

### DEV STATUS

最後のPublic GitHub Activityからの経過時間で判定します。

```text
0-1h   BUILDING
1-6h   RECENTLY ACTIVE
6-24h  OFFLINE
24h+   QUIET
```

ここで「ONLINE」とは書かないようにしました。

最後にGitHub上でPublic Activityがあった時刻が分かるだけで、実際にPCの前にいるかまでは分からないからです。

### CODE WEATHER

その日のActivity量を少し遊びのある表現へ変換しています。

```text
0      REST DAY
1-5    LIGHT CODING
6-20   ACTIVE
21-50  HEAVY CODING
51+    STORM
```

これは生産性評価ではなく、プロフィール上の演出です。

### BUILD STREAK

Profile Signalで追跡しているPublic Activityが1件以上ある日をActive dayとし、今日から遡って連続日数を計算しています。

GitHub Contribution Graphとは別の独自指標です。

## CURRENT FOCUS — Commit数だけでは決めない

次に欲しかったのが「今一番触っているRepository」でした。

最初はRepositoryごとのCommit数だけで決めようとしました。

でも、それだと小さなfix commitを大量に積んだRepositoryが常に勝ちやすくなります。PRをMergeしたりIssueを完了したProjectも、ある程度Focusとして評価したかったのでWeightを付けました。

```text
commit        = 1
issue create  = 2
issue done    = 3
PR opened     = 4
PR merged     = 6
release       = 10
```

Public Events APIからRepositoryごとのscoreを計算し、最大のものをCURRENT FOCUSにします。

撮影時点では次の表示でした。

```text
mizzz-ivr/ivmz-home
37% of weighted repository activity
score 127
111 events
```

Focusは固定ではなく、その日の活動によって変わります。

### TODAY'S STACK

Focus Repositoryが決まったら、そのRepositoryのLanguages APIから上位言語を表示します。

```text
TypeScript
CSS
JavaScript
```

「自分が使える技術一覧」ではなく、**今動かしているProjectの技術**を見せるための表示です。

## DEV PULSE — Daily JSONをそのまま再利用する

TODAYを作った時点で、Activityは日次JSONとして保存していました。

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
```

DEV PULSEでは、このJSONを7日分読み、`assets/dev-pulse.svg` を生成しています。

```text
Daily JSON
   ↓
7 days
   ↓
DEV PULSE SVG
```

新しいAPIを7日分叩き直すのではなく、すでにRepositoryへ保存しているSnapshotを使っています。

履歴を残しておいたことで、次のWidgetを作るときに再利用できました。今回の実装で特に良かった設計判断の一つです。

## CI SIGNAL — CIを絶対評価にはしない

DEV PULSEの下には、直近7日のPublic GitHub ActionsをまとめたCI SIGNALを入れています。

<!-- QIITA_IMAGE: 02-dev-pulse-ci-signal.jpg -->

撮影時点では次の状態でした。

```text
ATTENTION
56% PASS RATE
15 / 27 PASSED / EVALUATED
3 REPOS WITH CI
```

completed runのうち、判定対象は次のようにしています。

```text
success
→ pass

failure / timed_out / action_required / startup_failure
→ fail

cancelled / skipped / neutral
→ pass rateから除外
```

ここで表示している `ATTENTION` や `56%` は、Repositoryそのものの品質を採点したものではありません。

開発中のbranchやPRでCIを何度も回せば失敗も増えます。あくまで、**最近のPublic GitHub ActionsがどんなSignalを出しているか**を見るための情報です。

## NOW BUILDING — Featuredとは分ける

CURRENT FOCUSは1Repositoryだけですが、実際には2〜3個を並行して触ることがあります。

そこでweighted activity上位3件を `NOW BUILDING` として表示しています。

```text
01 mizzz-ivr/ivmz-home
02 ivRooom/Herta
03 mizzz-ivr/mizzz-ivr
```

既存の `PUBLIC BUILDS // Featured` は消していません。

```text
NOW BUILDING
→ 最近実際に動いているProject

PUBLIC BUILDS
→ 代表作品として見せたいProject
```

Featuredを自動ランキングにすると、短期的に触っていない代表作が消えます。逆にNOW BUILDINGを手動管理すると「今」が見えません。

役割を分けた方が自然でした。

## PROJECT HEALTH — push recencyとCIを組み合わせる

NOW BUILDINGにはPROJECT HEALTHも統合しました。

<!-- QIITA_IMAGE: 03-now-building-health-activity-stream.jpg -->

撮影時点ではこうなっていました。

```text
mizzz-ivr/ivmz-home
! ATTENTION · CI 0/10 passed · 0%

ivRooom/Herta
◐ WATCH · CI 5/7 passed · 71%

mizzz-ivr/mizzz-ivr
● HEALTHY · CI 10/10 passed · 100%
```

HealthはIssue件数だけでは決めていません。

現在の初期ルールは次の要素を組み合わせています。

- Repositoryがarchived / disabledか
- 最終pushからどれくらい経っているか
- 直近CIがpassing / mixed / attentionのどれか

表示ラベルは次の6種類です。

```text
HEALTHY
WATCH
ATTENTION
ACTIVE
QUIET
ARCHIVED
```

これも「このRepositoryは健康 / 不健康」と断定するためのものではなく、最近触っているProjectの運用状態をプロフィール上でざっくり把握するためのSignalです。

## ACTIVITY STREAM — 最新イベントの置き場所を一つにする

TODAYに入れていた `Today's signal` はACTIVITY STREAMへ移しました。

Public Events APIから、開発活動として見せたいイベントだけを短い形へ正規化しています。

対象は今のところ次の5種類です。

```text
PushEvent
PullRequestEvent
IssuesEvent
ReleaseEvent
CreateEvent
```

Starなど、プロフィール上の開発履歴としてはノイズになりやすいEventは除外しています。

表示は最大4件です。

撮影した画面では、ちょうどProfile SignalのPR MergeもActivityに出ていました。

```text
22:01 PR    mizzz-ivr/mizzz-ivr — PR merged #21
21:57 PR    mizzz-ivr/tech-writing — Opened PR #7
21:56 PUSH  mizzz-ivr/tech-writing — 1 commit pushed ...
```

イベントを全部並べるのではなく、「プロフィールを開いたときに最近何をしていたか分かる」程度に留めています。

## CollectorとAnalyticsをすぐ全部統合しなかった

現時点では、TODAY CollectorとProfile Signal Analyticsを完全には一体化していません。

```text
GitHub Search API
      ↓
TODAY Collector
      ↓
Daily JSON
      ↓
Profile Signal Analytics
      ↑
Public Events API
      ↑
Public Repository / Actions API
```

コードとしては多少重複があります。

最初から共通Collectorへ全面リファクタリングする案もありましたが、TODAYはすでに3時間ごとの定期更新で動いていました。

そこで安定しているCollectorを維持したままAnalytics層を足し、実プロフィールでDogfoodingすることを優先しました。

GitHub Actionとして配布する段階でNormalized Activity Modelへ整理する予定です。

## StateをWidget間の共通データにする

計算結果は `data/profile-signal-state.json` にまとめています。

Phase 3ではschema v3として、例えば次の情報を持っています。

```json
{
  "schema_version": 3,
  "status": {},
  "code_weather": {},
  "streak": 2,
  "current_focus": {},
  "dev_pulse": [],
  "now_building": [],
  "activity_stream": [],
  "ci_signal": {}
}
```

Widgetごとに好き勝手GitHub APIへアクセスするのではなく、Collector / Analyticsで作ったstateをRendererが読む形へ寄せています。

将来テンプレート化するときにも、この境界をそのまま使う予定です。

## Public-onlyは維持する

プロフィールに表示する情報なので、TODAYから一貫して次の方針にしています。

**Private Activityを取得してから隠すのではなく、最初からPublic dataだけ取得する。**

現在使っているのはPublic情報です。

- Search API
- Public Events API
- Repository Languages
- Repository metadata
- Public GitHub Actions runs

Widgetが増えるほどAPI requestも増えるため、配布版ではrequest budgetもconfigと合わせて整理する必要があります。

## Markerを分けたことで「好きなパーツだけ使う」に近づいた

READMEではWidgetごとにMarkerを分けています。

```md
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:START -->
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:END -->

<!-- PROFILE-SIGNAL:FOCUS:START -->
<!-- PROFILE-SIGNAL:FOCUS:END -->

<!-- PROFILE-SIGNAL:PULSE:START -->
<!-- PROFILE-SIGNAL:PULSE:END -->
```

将来の配布版では、このMarkerをWidgetの配置契約として使う予定です。

利用者はREADMEへ使いたいMarkerだけ置き、設定側では例えば、

```yaml
widgets:
  live_signal:
    enabled: true
  current_focus:
    enabled: true
  dev_pulse:
    enabled: true
  now_building:
    enabled: false
```

のように選べる形を考えています。

自分のプロフィールは全機能を使うShowcase兼Dogfooding環境にします。

## 次は履歴と配布できる形へ

TODAYを作り始めたときは、自分のプロフィールに今日のCommit数が出れば十分でした。

実際に使っていくと、

```text
今日どれくらい動いたか
↓
今どのProjectに集中しているか
↓
直近7日はどうだったか
↓
最近動いているProjectは何か
↓
CIやProjectの状態はどうか
```

と、知りたいものが自然に増えていきました。

一方、README上では14個の機能を14個並べず、役割ごとのブロックへまとめています。

現在は次のPhaseとして、日次JSONからWeekly / Monthly / Achievementsを生成する `DEV RECAP` を追加しています。その後はCollector / Analytics / Widgetを分離して、好きなパーツを選べるGitHub Actionとして切り出す予定です。

今のところ、この **「機能は増やす。でも表示単位は増やしすぎない」** という方針が、自分のGitHubプロフィールにはかなり合っています。
