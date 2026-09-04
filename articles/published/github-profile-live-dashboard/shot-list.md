# Shot List — GitHub Profile Live Dashboard

Qiita #2公開用スクリーンショット。最終版は3枚に集約する。

## 01. Profile dashboard overview

Qiita用名:

`01-profile-dashboard-overview.jpg`

元画像:

`IMG_0183.jpeg`

含まれるもの:

- GitHub Profile全景
- LIVE SIGNAL
- TODAY
- CURRENT FOCUS + TODAY'S STACK
- DEV PULSE上部

目的:

Qiita #1のTODAY単体から、プロフィール全体がLive Dashboardへ発展したことを冒頭で見せる。

撮影時点: 2026-08-26 22:02 JST前後。

## 02. DEV PULSE + CI SIGNAL

Qiita用名:

`02-dev-pulse-ci-signal.jpg`

元画像:

`IMG_0184.jpeg`

含まれるもの:

- DEV PULSE 7-day SVG
- `C 345 · PR 19 · ISSUE 10`
- activity 374
- ATTENTION
- 56% PASS RATE
- 15 / 27 PASSED / EVALUATED
- 3 REPOS WITH CI

目的:

Daily JSONを7日グラフへ再利用したことと、Phase 3でCI SIGNALを同じWidgetへ統合したことを1枚で見せる。

注意:

- CI値は撮影時点の実測例。
- ATTENTIONをRepository品質の絶対評価として説明しない。

## 03. NOW BUILDING + PROJECT HEALTH + ACTIVITY STREAM

Qiita用名:

`03-now-building-health-activity-stream.jpg`

元画像:

`IMG_0185.jpeg`

含まれるもの:

```text
01 mizzz-ivr/ivmz-home
ATTENTION · CI 0/10 · 0%

02 ivRooom/Herta
WATCH · CI 5/7 · 71%

03 mizzz-ivr/mizzz-ivr
HEALTHY · CI 10/10 · 100%
```

加えてACTIVITY STREAM:

- PR #21 merged
- PR #7 opened
- tech-writing push

目的:

NOW BUILDING / PROJECT HEALTH / ACTIVITY STREAMを別々のスクリーンショットにせず、情報密度を抑えて統合した完成形を見せる。

## Article placeholder mapping

```text
<!-- QIITA_IMAGE: 01-profile-dashboard-overview.jpg -->
<!-- QIITA_IMAGE: 02-dev-pulse-ci-signal.jpg -->
<!-- QIITA_IMAGE: 03-now-building-health-activity-stream.jpg -->
```

Qiitaへアップロード後、発行された画像Markdownへ置換する。

## 不採用になった個別Screenshot

以下は3枚へ統合できたため省略する。

- LIVE SIGNAL単体
- CURRENT FOCUS単体
- DEV PULSE単体
- NOW BUILDING単体
- ACTIVITY STREAM単体
- PROJECT HEALTH / CI SIGNAL追加カット

記事の画像枚数を増やすより、実際のプロフィール構成が伝わる3枚を優先する。

## Mask / Crop checklist

- [x] Secret / Tokenなし
- [x] Private Repository名なし
- [x] Private Issue / PR titleなし
- [x] Notificationなど第三者情報なし
- [x] 数値・Health / CI状態を撮影時点の例として扱う
- [ ] Qiita upload後のPreviewで可読性確認
