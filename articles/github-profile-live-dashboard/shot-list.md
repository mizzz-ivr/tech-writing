# Shot List — GitHub Profile Live Dashboard

Qiita #2公開用スクリーンショット候補。

## 必須

### 01. Profile dashboard overview

含めるもの:

- LIVE SIGNAL
- TODAY
- CURRENT FOCUS
- DEV PULSE
- NOW BUILDING
- ACTIVITY STREAM

1枚に全部入らない場合は2枚へ分ける。

目的:

- Qiita #1のTODAY単体からDashboardへ発展したことを最初に見せる。

### 02. LIVE SIGNAL

含めるもの:

- DEV STATUS
- CODE WEATHER
- BUILD STREAK

注意:

- CODE WEATHERは生産性評価ではなく演出であることを本文で説明する。

### 03. CURRENT FOCUS + TODAY'S STACK

含めるもの:

- Focus Repository
- weighted activity share
- score / event count
- language stack

### 04. DEV PULSE

含めるもの:

- 7-day SVG
- Phase 3 Merge後はCI SIGNAL部分も含める

### 05. NOW BUILDING

含めるもの:

- top 3 active repositories
- share / score / events
- Phase 3 Merge後はPROJECT HEALTH / repo CIも含める

### 06. ACTIVITY STREAM

含めるもの:

- timestamp
- event type
- repository
- normalized summary

## Phase 3 Merge後に必須

### 07. PROJECT HEALTH + CI SIGNAL

できれば04 / 05と兼用する。

見せたいもの:

```text
DEV PULSE
CI SIGNAL
PASS RATE
PASSED / EVALUATED
REPOS WITH CI

NOW BUILDING
HEALTHY / WATCH / ATTENTION / ACTIVE
per-repo CI pass ratio
```

CI結果は時間で変わるので、記事中では撮影時点の実測例として扱う。

## 任意

### 08. state JSON

`data/profile-signal-state.json`の一部。

見せたいkey:

- status
- code_weather
- streak
- current_focus
- dev_pulse
- now_building
- activity_stream
- ci_signal

スクリーンショットよりコードブロックで十分なら省略。

### 09. GitHub Actions validation success

Phase 3 PRのCI success。

Qiita #1でもActions画面を使っているため、第2弾では優先度低め。

## Mask / Crop checklist

- [ ] Secret / Tokenなし
- [ ] Private Repository名なし
- [ ] Private Issue / PR titleなし
- [ ] Browserの不要なAccount UIなし
- [ ] Notificationなど第三者情報なし
- [ ] 数値・Health / CI状態の撮影日時をnotesへ記録
