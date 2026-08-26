# Shot List — GitHub Profile Daily Activity

Qiita公開用スクリーンショット。2026-08-26撮影済み。

## 採用する4枚

### 01. Profile README — TODAY全体

ファイル名:

`01-today-activity-overview.jpg`

含まれているもの:

- `TODAY // Activity overview`
- 2026-08-26 JST
- 264 COMMITS
- 16 PRS OPENED
- 5 ISSUES CREATED
- 3 ISSUES DONE
- Today's signal

用途:

記事冒頭の完成イメージ。この記事の主役として最初に掲載する。

注意:

撮影後もActivityは変化しているため、本文では「撮影時点の実測」と明記する。

### 02. GitHub Actions — Success

ファイル名:

`02-actions-success.jpg`

含まれているもの:

- `Update profile activity #5`
- Triggered via Schedule
- main
- Status: Success
- `update-profile-activity` Job success

用途:

GitHub Actionsによる自動更新が実運用で動作している裏付けとして掲載する。

### 03. Profile Signal — LIVE SIGNAL

ファイル名:

`03-live-signal.jpg`

含まれているもの:

- `LIVE SIGNAL // Development status`
- BUILDING
- STORM
- 2 DAY STREAK
- last public activity 19:00 JST

用途:

記事後半の「TODAYからProfile Signalへ拡張した」で掲載する。

Qiita #2ではこの機能を本題として詳しく扱うため、第1弾では仕組みの概要だけに留める。

### 04. Profile Signal — CURRENT FOCUS

ファイル名:

`04-current-focus.jpg`

含まれているもの:

- `CURRENT FOCUS // What is moving now`
- `mizzz-ivr/ivmz-home`
- 34% weighted repository activity
- score 118 / 101 events
- TODAY'S STACK
- TypeScript / CSS / JavaScript

用途:

Profile Signal Phase 1が記事執筆中に実装・Mergeまで進んだことを見せる締めの画像。

## 記事内の配置

```text
書き出し
  ↓
[01 TODAY]
  ↓
設計 / JST / Search API / JSON / Privacy
  ↓
GitHub Actions
  ↓
[02 Actions Success]
  ↓
実際に動かしてみて
  ↓
Profile Signal Phase 1
  ↓
[03 LIVE SIGNAL]
[04 CURRENT FOCUS]
  ↓
OSS / Template化構想
```

`article.md` には現在、次のPlaceholderを配置済み。

```text
<!-- QIITA_IMAGE: 01-today-activity-overview.jpg -->
<!-- QIITA_IMAGE: 02-actions-success.jpg -->
<!-- QIITA_IMAGE: 03-live-signal.jpg -->
<!-- QIITA_IMAGE: 04-current-focus.jpg -->
```

Qiita公開画面へ4枚をアップロード後、各PlaceholderをQiitaが発行する画像Markdownへ置換する。

## Repository tree画像

当初候補だったRepository treeのスクリーンショットは今回は不要。

以下は記事内のtext treeで十分伝わるため、画像を増やさない。

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
assets/activity-7d.svg
scripts/update-profile-activity.py
.github/workflows/update-readme.yml
```

## Placeholder → 実データ比較

初回Placeholder画像が手元に残っていなくても記事成立に影響なし。

本文で、Merge直後はPlaceholder、Scheduled Workflow後に実データへ置換された経緯を説明する。

## Publicチェック

- [x] Secret / Tokenなし
- [x] Private Repository名なし
- [x] Private Issue / PR titleなし
- [x] 個人情報なし
- [x] 不要なBrowser Bookmark / Tabなし
- [x] Billing / Account設定なし
- [x] Actions画像にWorkflow名 / trigger / Successが表示されている
- [x] 数値を撮影時点の実測としてnotesへ記録

## 公開時の残作業

- [ ] Qiitaへ4枚をアップロード
- [ ] `QIITA_IMAGE` Placeholderを置換
- [ ] Qiita Previewで画像幅・改行を確認
- [ ] スマホPreviewでも本文が画像に押されすぎないか確認
