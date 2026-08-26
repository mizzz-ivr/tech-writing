# Notes — GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた

## 記事の中心

GitHubプロフィールを静的な自己紹介ではなく、「今日何を作っているか」が見える場所へしたかった。

外部Statsカードを貼るのではなく、GitHub API + GitHub Actions + Repository内JSONだけで自分用Activity表示を作った実体験を書く。

## 2026-08-26 実装確認

対象: `mizzz-ivr/mizzz-ivr`

### TODAY実装

- `README.md` の `NOW // What I build` 上に `TODAY // Activity overview` を追加済み。
- Marker:
  - `<!-- DAILY-ACTIVITY:START -->`
  - `<!-- DAILY-ACTIVITY:END -->`
- 表示項目:
  - COMMITS
  - PRS OPENED
  - ISSUES CREATED
  - ISSUES DONE
  - Today's signal 最大5件
  - 7-day public activity SVG
- PR #18 で導入し、2026-08-26にmainへMerge済み。
- Merge直後はPlaceholderで、Scheduled Workflow初回実行後に実データへ置換された。

### 実測例

確認時点のREADMEでは以下を表示していた。

```text
2026-08-26 JST
87 commits
13 PRs opened
3 issues created
1 issue done
```

記事公開時は値が変わる可能性があるため、公開直前に最新READMEを再確認する。

### Collector

`scripts/update-profile-activity.py`

- `Asia/Tokyo` で対象日を決定。
- JST 00:00:00〜23:59:59をUTC rangeへ変換。
- Search APIを4種類利用。
- today + yesterdayを再取得するため1runあたり8 Search requests。
- unauthenticated requestを意図的に使用。
- Public metadataだけを扱う。
- Retryあり。
- Daily JSONは内容が変わらない限り`generated_at`を更新しない。

### Daily JSON

保存先:

```text
data/activity/YYYY/MM/YYYY-MM-DD.json
```

目的:

- 日次数値を消さずに残す
- 7-day chartの入力
- Weekly / Monthly集計への拡張
- Git diffを日単位で小さく保つ

### Workflow

`.github/workflows/update-readme.yml`

- Pull Requestでは実際にgeneratorを実行してpreview validation。
- Scheduled runは3時間ごと、minute 17。
- `timezone: "Asia/Tokyo"`。
- `workflow_dispatch`あり。
- 変更時だけCommit。
- 他のProfile自動更新WorkflowとのPush競合に備えてfetch / rebase / retry。

## 数値の定義

### COMMITS

GitHub Commit Searchで対象JST日付range + `author:<login>`にヒットしたPublic Commitの`total_count`。

Contribution Graphと同義とは書かない。

### PRS OPENED

`is:pr author:<login> created:<UTC range>`。

### ISSUES CREATED

`is:issue author:<login> created:<UTC range>`。

### ISSUES DONE

`is:issue author:<login> is:closed reason:completed closed:<UTC range>`。

「自分自身がClose操作した数」ではなく、自分がauthorのIssueがその日にcompleted reasonでCloseされた数。

## Privacy方針

- Private activityを取得してからmaskする構成にしない。
- Collector自体をPublic-onlyにする。
- Private Repository名 / Issue title / PR title / Commit messageをPublic JSONへ保存しない。
- 将来Private contribution countを扱うとしても、公開可能な集計値だけに限定する。

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

確認事項:

- GitHub公式DocsではPublic data取得にunauthenticated REST requestを利用可能。
- unauthenticated REST APIのprimary rate limitは60 requests/hour。
- Search endpointには通常RESTとは別のcustom rate limitがある。
- Scheduled workflowsはIANA timezoneを指定可能。
- Scheduled workflowsはdefault branchの最新Commitに対して実行される。

## 次の実装とのつながり

記事作成と並行してProfile Signal Phase 1を開始。

Phase 1:

- Analytics core
- DEV STATUS
- CODE WEATHER
- BUILD STREAK
- CURRENT FOCUS
- TODAY'S STACK
- `LIVE SIGNAL` Widget
- `CURRENT FOCUS` Widget

記事公開時点でPhase 1がMerge済みなら、記事末尾の「次に作り始めている」を「追加した」へ変更する。

## Qiitaタグ候補

優先:

1. GitHubActions
2. GitHub
3. Python
4. GitHubAPI

5つ目を付けるなら候補:

- 自動化
- 個人開発

Qiita上の既存tag表記を公開直前に確認する。

## 公開前チェック

- [ ] `mizzz-ivr/mizzz-ivr` mainのREADMEを再取得
- [ ] 最新Workflowを再取得
- [ ] 記事内の87 / 13 / 3 / 1を最新値または「実装当日の例」と明記
- [ ] Phase 1のMerge状態に合わせて末尾を修正
- [ ] README全体スクリーンショットにPrivate情報がないことを確認
- [ ] Actions run screenshotに不要なAccount情報がないことを確認
- [ ] 自分のIssue / PR URLを参考文献として並べない
- [ ] GitHub公式Docs URLの有効性を確認
- [ ] STYLE_GUIDE.mdチェック
