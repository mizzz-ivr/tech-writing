---
title: "GitHubプロフィールをライブな開発ダッシュボードにしてみた"
status: draft
topics: [GitHub, GitHubActions, GitHubAPI, Python, 個人開発]
source_repositories: [mizzz-ivr/mizzz-ivr]
published:
  qiita: null
  zenn: null
---

# GitHubプロフィールをライブな開発ダッシュボードにしてみた

GitHubプロフィールに `TODAY // Activity overview` を追加して、その日のCommit / PR / Issueを自動表示できるようにしました。

最初はこれだけでもかなり楽しかったです。プロフィールを開けば「今日はどれくらい触っていたか」が分かる。

ただ、実際に数時間使ってみると、別のことが気になりました。

**活動量は分かるけど、今何を作っているのかはまだ分からない。**

自分は複数の個人開発Repositoryを並行して触ることが多いので、300 commitsと表示されても、それがどのProjectに集中していたのかは数字だけでは分かりません。

そこでTODAYを起点に、プロフィールをもう少し「今の開発状態」が見えるダッシュボードへ広げることにしました。

<!-- QIITA_IMAGE: 01-profile-dashboard-overview.jpg -->

現在はプロフィール上部を、次のような構成にしています。

```text
LIVE SIGNAL
TODAY // Activity overview
CURRENT FOCUS + TODAY'S STACK
DEV PULSE // Last 7 days
NOW BUILDING // Active repositories
ACTIVITY STREAM // Latest public signals
```

この記事では、単純にWidgetを増やした話ではなく、**情報を増やしながらREADMEを散らかさないためにどう整理したか**を中心に書きます。

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

全部面白そうでした。

でも、これを全部 `##` セクションとしてREADMEへ並べると、プロフィールではなく監視Dashboardになってしまいます。

そこで「機能数」と「見せるブロック数」を分けました。

## 14機能を6つのWidgetへまとめた

最終的に表示単位は6つにしました。

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

`LIVE TERMINAL` は独立機能ではなくThemeとして扱う予定です。

この整理をしたことで、「作りたい機能を捨てる」のではなく、**見せる単位だけ減らす**ことができました。

現時点ではDEV RECAP以外の表示基盤まで実装しています。

## TODAYは逆に小さくした

最初のTODAYには、4つのカウンターだけでなく直近Activityのリストと7日グラフも入れていました。

機能を増やし始めると、これが重複しました。

- 最新イベント → ACTIVITY STREAMで見せたい
- 7日推移 → DEV PULSEで見せたい

なのでTODAYは、むしろ削りました。

```text
TODAY // Activity overview

COMMITS
PRS OPENED
ISSUES CREATED
ISSUES DONE
```

「今日の数字」に責務を絞っています。

Widgetを追加するとき、表示を足すだけでなく**既存Widgetから何を消すか**も一緒に考えたのは良かったです。

## LIVE SIGNAL — 今の状態を1行で見る

最上部にはLIVE SIGNALを置きました。

<!-- QIITA_IMAGE: 02-live-signal.jpg -->

表示しているのは3つです。

```text
● BUILDING
🌩️ STORM
🔥 2 DAY STREAK
```

### DEV STATUS

最後のPublic GitHub Activityからの経過時間で判定しています。

```text
0-1h   BUILDING
1-6h   RECENTLY ACTIVE
6-24h  OFFLINE
24h+   QUIET
```

ここでは「オンライン」とは書いていません。

GitHub上で最後にPublic Activityがあっただけなので、PCの前にいるとは限らないからです。

### CODE WEATHER

その日のActivity量を少し遊びのある表現にしています。

```text
0      REST DAY
1-5    LIGHT CODING
6-20   ACTIVE
21-50  HEAVY CODING
51+    STORM
```

これは生産性評価ではなく、プロフィール上の演出です。

### BUILD STREAK

Activityが1件以上ある日をActive dayとして、今日から遡って連続日数を計算しています。

GitHub Contribution Graphとは別の、自分のProfile Signal用指標です。

## CURRENT FOCUS — Commit数だけでは決めない

次に欲しかったのが「今一番触っているRepository」です。

<!-- QIITA_IMAGE: 03-current-focus.jpg -->

最初はRepositoryごとのCommit数だけで決めようと思いました。

でも、それだと小さいfix commitを大量に積んだRepositoryが常に勝ちやすい。

PRをMergeしたりIssueを完了したProjectも、ある程度Focusとして評価したかったのでWeightを付けました。

```text
commit        = 1
issue create  = 2
issue done    = 3
PR opened     = 4
PR merged     = 6
release       = 10
```

Public Events APIからRepositoryごとのscoreを計算し、最大のものをCURRENT FOCUSにしています。

例えば実際のプロフィールでは、ある時点で次のように表示されました。

```text
mizzz-ivr/ivmz-home
38% of weighted repository activity
```

このFocusは固定ではなく、その日の活動によって変わります。

### TODAY'S STACK

Focus Repositoryが決まったら、そのRepositoryのLanguages APIを取得します。

```text
TypeScript
CSS
JavaScript
```

普段使える技術一覧ではなく、**今触っているProjectの技術**を見せるための表示です。

## DEV PULSE — Daily JSONを再利用する

TODAYを作った時点で、Activityは日次JSONとして保存していました。

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
```

このデータをそのまま7日分読み、`assets/dev-pulse.svg` を生成しています。

<!-- QIITA_IMAGE: 04-dev-pulse.jpg -->

ここで新しいAPIを7日分叩き直してはいません。

すでにRepositoryに保存しているDaily Snapshotを読むだけです。

```text
Daily JSON
   ↓
7 days
   ↓
DEV PULSE SVG
```

TODAY用に履歴を残しておいたことで、次のWidgetを作るときにそのまま再利用できました。

これは今回の実装で一番良かった設計判断の一つです。

## NOW BUILDING — Featuredとは分ける

CURRENT FOCUSは1Repositoryだけです。

でも実際には2〜3個を並行して触っていることがあるので、weighted activity上位3件を `NOW BUILDING` として表示しています。

<!-- QIITA_IMAGE: 05-now-building.jpg -->

```text
01 mizzz-ivr/ivmz-home
02 ivRooom/Herta
03 mizzz-ivr/roomate-voice
```

ここで既存の `PUBLIC BUILDS // Featured` は消していません。

役割を分けています。

```text
NOW BUILDING
→ 最近実際に動いているProject

PUBLIC BUILDS
→ 代表作品として見せたいProject
```

Featuredを自動ランキングにすると、短期的に触っていない代表作が消えてしまいます。

逆にNOW BUILDINGを手動管理すると「今」が見えなくなる。

別のセクションとして持つ方が自然でした。

## ACTIVITY STREAM — 最新イベントの置き場所を一つにする

TODAYにあった `Today's signal` はACTIVITY STREAMへ移しました。

<!-- QIITA_IMAGE: 06-activity-stream.jpg -->

Public Events APIから、開発活動として見せたいイベントだけを正規化しています。

対象は今のところ次の5種類です。

```text
PushEvent
PullRequestEvent
IssuesEvent
ReleaseEvent
CreateEvent
```

Starなどプロフィール上の開発履歴としてはノイズになりやすいEventは除外しています。

表示は最大4件です。

```text
21:44 PR    repository — Merged PR #20
21:42 PUSH  repository — 1 commit pushed to ...
```

イベントを全部並べず、「プロフィールを開いたときに最近何をしていたか分かる」程度に留めています。

## CollectorとAnalyticsをすぐに全部統合しなかった

現時点では、TODAY CollectorとProfile Signal Analyticsは完全には一体化していません。

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
```

コードとしては多少重複があります。

最初から綺麗な共通Collectorへ全面リファクタリングする案もありました。

ただ、TODAYはすでに定期実行で動いていました。

そこで一度安定しているCollectorを維持したままAnalytics層を足し、実プロフィールでDogfoodingすることを優先しました。

最終的にGitHub Actionとして切り出す段階でNormalized Activity Modelへ整理する予定です。

## StateをWidget間の共通データにする

計算結果は `data/profile-signal-state.json` にまとめています。

Phase 2では例えば次のような情報を持っています。

```json
{
  "schema_version": 2,
  "status": {},
  "code_weather": {},
  "streak": 2,
  "current_focus": {},
  "dev_pulse": [],
  "now_building": [],
  "activity_stream": []
}
```

WidgetごとにGitHub APIへアクセスするのではなく、Collector / Analyticsで作ったstateをRendererが読む形へ寄せています。

今後テンプレート化するときにも、この境界はそのまま使えそうです。

## PROJECT HEALTHとCI SIGNALも同じブロックへ入れる

記事を書いている現在、次のPhaseとしてPROJECT HEALTHとCI SIGNALを実装しています。

ここでも新しいセクションは増やしません。

```text
DEV PULSE
  └─ CI SIGNAL

NOW BUILDING
  └─ PROJECT HEALTH
```

PROJECT HEALTHは単純なIssue件数ではなく、Repositoryの最終pushと最近のGitHub Actions結果を使う設計にしています。

CIも「1回失敗したら全部赤」という扱いにはせず、直近7日のcompleted runsを集計します。

```text
success
→ pass

failure / timed_out / action_required / startup_failure
→ fail

cancelled / skipped / neutral
→ pass rateから除外
```

このPhaseがmainへ入ったら、実際の表示をこの記事にも追加する予定です。

<!-- QIITA_IMAGE: 07-project-health-ci-signal.jpg -->

## Public-onlyは維持する

プロフィールに表示する情報なので、ここはTODAYと同じ方針を維持しています。

**Private Activityを取得してから隠すのではなく、最初からPublic dataだけ取得する。**

使っているのはPublic Repositoryの情報です。

- Search API
- Public Events API
- Repository Languages
- Repository metadata
- Public GitHub Actions runs

Widgetが増えるほどAPI requestも増えるので、今後はCollectorを統合するときにrequest budgetも明示的に管理する予定です。

## Markerを分けたことでパーツ化しやすくなった

READMEではWidgetごとにMarkerを分けています。

```md
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:START -->
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:END -->

<!-- PROFILE-SIGNAL:FOCUS:START -->
<!-- PROFILE-SIGNAL:FOCUS:END -->

<!-- PROFILE-SIGNAL:PULSE:START -->
<!-- PROFILE-SIGNAL:PULSE:END -->
```

これを将来の配布版でも契約として使う予定です。

利用者は使いたいMarkerだけREADMEへ置く。

設定側では例えば、

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

## 次は配布できる形へ近づけたい

TODAYを作り始めたときは、自分のプロフィールに今日のCommit数が出れば十分でした。

そこから実際に使っていくと、

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

ただし画面上では14個の機能を14個並べず、6つの役割へまとめました。

今のところ、この「機能は増やす、表示単位は増やしすぎない」という方針が自分のプロフィールには合っています。

次はWeekly / Monthly / Achievementsを `DEV RECAP` にまとめ、その後はWidgetを選べるGitHub Actionとして切り出す予定です。
