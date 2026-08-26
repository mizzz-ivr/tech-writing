# Notes — GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた

## 記事の中心

GitHubプロフィールを静的な自己紹介ではなく、「今日何を作っているか」が見える場所へしたかった。

外部Statsカードではなく、GitHub API + GitHub Actions + Repository内JSONで自分用Activity表示を作った実体験を書く。

## 2026-08-26 実装確認

対象: `mizzz-ivr/mizzz-ivr`

### TODAY

- PR #18で導入、2026-08-26にmainへMerge済み。
- `README.md` の `NOW // What I build` 上に `TODAY // Activity overview`。
- Marker:
  - `<!-- DAILY-ACTIVITY:START -->`
  - `<!-- DAILY-ACTIVITY:END -->`
- COMMITS / PRS OPENED / ISSUES CREATED / ISSUES DONE。
- Today's signal 最大5件。
- 7-day public activity SVG。
- Merge直後はPlaceholder、Scheduled Workflow初回実行後に実データへ置換。

### スクリーンショット撮影時点

2026-08-26 19:00 JST前後に撮影。

```text
264 commits
16 PRs opened
5 issues created
3 issues done
```

撮影後もActivityは増加しており、同日21時台のmain再確認では `ISSUES CREATED` が6へ変化していた。

したがって記事では、上記を**画像撮影時点の実測例**として扱い、仕様値として固定しない。

### Collector

`scripts/update-profile-activity.py`

- `Asia/Tokyo` で対象日を決定。
- JST 00:00:00〜23:59:59をUTC rangeへ変換。
- Search APIを4種類利用。
- today + yesterday再取得で1run 8 Search requests。
- unauthenticated Public API requestを意図的に使用。
- Public metadataだけを扱う。
- Retryあり。
- Daily JSONは内容が変わらない限り`generated_at`を更新しない。

### Daily JSON

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
```

用途:

- 日次数値の保存
- 7-day chart入力
- Weekly / Monthly集計への拡張
- Git diffを日単位で小さく保つ

### Workflow

`.github/workflows/update-readme.yml`

- Pull Requestでは実generatorでpreview validation。
- Scheduled runは3時間ごと、minute 17。
- `timezone: "Asia/Tokyo"`。
- `workflow_dispatch`あり。
- 変更時だけCommit。
- Push競合時はfetch / rebase / retry。

## 数値の定義

### COMMITS

GitHub Commit Searchで対象JST日付range + `author:<login>`にヒットしたPublic Commitの`total_count`。

Contribution Graphと同義ではない。

### PRS OPENED

`is:pr author:<login> created:<UTC range>`。

### ISSUES CREATED

`is:issue author:<login> created:<UTC range>`。

### ISSUES DONE

`is:issue author:<login> is:closed reason:completed closed:<UTC range>`。

「本人がClose操作した数」ではなく、本人がauthorのIssueがその日にcompleted reasonでCloseされた数。

## Profile Signal Phase 1

PR #19 `feat: add Profile Signal core widgets` は2026-08-26にmainへMerge済み。

実装済み:

- Analytics core
- DEV STATUS
- CODE WEATHER
- BUILD STREAK
- CURRENT FOCUS
- TODAY'S STACK
- `LIVE SIGNAL` Widget
- `CURRENT FOCUS` Widget
- unit tests 6件
- PR CIで実GitHub API preview validation

スクリーンショット撮影時点:

```text
LIVE SIGNAL
● BUILDING
🌩️ STORM
🔥 2 DAY STREAK

CURRENT FOCUS
mizzz-ivr/ivmz-home
34% weighted activity
TypeScript / CSS / JavaScript
```

Current Focusは時間とともに変化するため、これも撮影時点の実測として扱う。

## Privacy方針

- Private activityを取得してからmaskしない。
- Collector自体をPublic-onlyにする。
- Private Repository名 / Issue title / PR title / Commit messageをPublic JSONへ保存しない。
- 将来Private contribution countを扱う場合も、公開可能な集計値だけに限定する。

## 公開用画像

ユーザー撮影済み4枚:

1. `01-today-activity-overview.jpg`
2. `02-actions-success.jpg`
3. `03-live-signal.jpg`
4. `04-current-focus.jpg`

公開時はQiitaへ画像をアップロードし、`article.md` の `<!-- QIITA_IMAGE: ... -->` 4箇所をQiita画像Markdownへ置換する。

画像内容を確認済み:

- Secret / Token表示なし
- Private Repository名なし
- Private Issue / PR titleなし
- 不要なBilling / Account設定なし
- Actions画像はWorkflow名 / Schedule / Successが読み取れる

## 参考資料

### GitHub公式

- Profile README
  - https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- Issue / PR search
  - https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests
- Scheduled workflows
  - https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- REST API rate limits
  - https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

## Qiitaタグ候補

優先:

1. GitHubActions
2. GitHub
3. Python
4. GitHubAPI
5. 個人開発

公開直前にQiita上のタグ表記を再確認する。

## 公開前チェック

- [x] `mizzz-ivr/mizzz-ivr` mainのREADMEを再取得
- [x] PR #19のMerge状態を確認
- [x] 最新WorkflowがScheduled runでSuccessしていることを確認
- [x] Activity値を「撮影時点の実測例」として整理
- [x] 画像4枚を確認
- [x] READMEスクリーンショットにPrivate情報がないことを確認
- [x] Actionsスクリーンショットに不要なAccount情報がないことを確認
- [x] 記事末尾をPhase 1 Merge済みへ更新
- [x] 自分のIssue / PR URLを参考文献として並べない
- [ ] Qiitaへ画像4枚をアップロード
- [ ] `QIITA_IMAGE` コメントをQiita画像Markdownへ置換
- [ ] Qiita Previewでレイアウト確認
- [ ] 公開直前にmainをもう一度確認
- [ ] 公開後URLを`ideas/published.md`へ記録
