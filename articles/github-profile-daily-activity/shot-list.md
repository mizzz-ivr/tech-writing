# Shot List — GitHub Profile Daily Activity

公開用スクリーンショット候補。

## 必須

### 01. Profile README — TODAY全体

含めるもの:

- `TODAY // Activity overview`
- COMMITS / PRS OPENED / ISSUES CREATED / ISSUES DONE
- Today's signalの一部
- 7-day SVG

注意:

- Browserの不要なAccount UIはCropする。
- Private Repository情報が映り込んでいないことを確認する。
- 数値は記事本文と同じ確認時点に合わせる。

### 02. GitHub Actions — Update profile activity success

含めるもの:

- Workflow名
- success状態
- Scheduleまたはmanual runであることが分かる範囲

不要:

- 個人用通知
- Secret名の詳細説明
- Account / Billing情報

### 03. Repository tree — generated data

見せたい構成:

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
assets/activity-7d.svg
scripts/update-profile-activity.py
.github/workflows/update-readme.yml
```

GitHub UIまたは記事用の簡易図でよい。

## 任意

### 04. Placeholder → 実データ

初回Scheduled run前後の比較が残せる場合のみ。

```text
Before
Public GitHub activity is refreshed automatically in JST.

After
87 commits / 13 PRs / ...
```

実装体験が伝わりやすい。

### 05. Profile Signal Phase 1

記事公開までにMerge済みなら末尾の予告として掲載候補。

- LIVE SIGNAL
- CURRENT FOCUS

Qiita #2の本題になるため、第1弾では大きく見せすぎない。

## Mask / Crop checklist

- [ ] Secret / Tokenなし
- [ ] Private Repository名なし
- [ ] Private Issue / PR titleなし
- [ ] 個人情報なし
- [ ] 不要なBrowser Bookmark / Tabなし
- [ ] 公開可能なメールアドレスだけか確認
- [ ] 数値の確認日時をnotesに残す
