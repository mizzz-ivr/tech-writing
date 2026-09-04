---
title: GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
status: published
published_at: '2026-08-26'
article_type: case-study
level: intermediate
topics:
- GitHub
- GitHubActions
- GitHubAPI
- Python
- 個人開発
domains:
- devops
- developer-productivity
languages:
- Python
technologies:
- GitHub Actions
- GitHub API
- GitHub Search API
portfolio_signals:
- automation
- ci-cd
source_repositories:
- mizzz-ivr/mizzz-ivr
published:
  qiita: https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a
  zenn: null
---

# GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた

GitHubのプロフィールREADMEを整理していて、ふと思いました。

プロフィールには「何を作っているか」は書いてあるけど、**今日実際に何をしていたのかは分からない**。

自分は複数の個人開発を並行して触っているので、昨日と今日で一番触っているRepositoryが違うことも珍しくありません。Featured Repositoryや技術スタックだけでは、その日の開発の動きまでは見えませんでした。

そこでプロフィール上部に、`TODAY // Activity overview` というブロックを追加しました。

<!-- QIITA_IMAGE: 01-today-activity-overview.jpg -->

画像を撮った2026-08-26 19:00 JST前後では、次のような状態でした。

```text
264  COMMITS
 16  PRS OPENED
  5  ISSUES CREATED
  3  ISSUES DONE
```

この数字は固定値ではなく、その日の公開GitHub Activityから自動生成しています。その後もActivityが増えれば数字は更新されます。

READMEだけでなく、日次JSONと7日グラフもRepository内へ保存し、GitHub Actionsから定期更新する構成にしました。

## 欲しかったのは累計Statsではなく「今日」だった

GitHubプロフィールを動的に見せる仕組み自体はいろいろあります。

ただ、今回見たかったのは累計Starsや言語比率ではありませんでした。

- 今日どれくらいCommitしたか
- 今日PRを何件作ったか
- 今日Issueを何件作ったか
- 今日完了したIssueはいくつか
- 直近では何を触っていたか

という、かなり短い時間軸です。

さらに、READMEへ表示して終わりではなく、後からWeekly / Monthlyで振り返れるようにしたかったので、外部のStatsカードを貼るのではなく、GitHub Actionsで自分用のActivityデータを作ることにしました。

## 全体構成

最初の実装はかなり単純です。

```text
GitHub Search API
        ↓
Python collector
        ↓
Daily JSON
        ├─ README TODAY section
        └─ 7-day SVG
        ↓
GitHub Actions
        ↓
mainへ自動commit
```

使っているものはほぼGitHub内で完結しています。

- Profile README
- GitHub REST Search API
- Python
- GitHub Actions
- Repository内のJSON / SVG

別サーバーやDBは使っていません。

## 「今日」はJSTで切る

最初に気をつけたのが日付でした。

自分は日本時間で活動しているので、READMEに表示する「今日」も `Asia/Tokyo` 基準にしたい。

そこでJSTの0:00〜23:59:59を作ってからUTCへ変換しています。

```python
def zulu(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_window(day: date) -> str:
    start_local = datetime.combine(day, time.min, TZ)
    end_local = start_local + timedelta(days=1) - timedelta(seconds=1)
    return f"{zulu(start_local)}..{zulu(end_local)}"
```

例えば2026-08-26 JSTなら、検索範囲は次のUTCになります。

```text
2026-08-25T15:00:00Z
..
2026-08-26T14:59:59Z
```

Actions側もtimezoneを指定しています。

```yaml
on:
  schedule:
    - cron: "17 */3 * * *"
      timezone: "Asia/Tokyo"
  workflow_dispatch:
```

毎日1回ではなく3時間ごとにしたのは、朝に集計した数字が夜まで残り続けるのを避けたかったからです。

ただし、実行のたびにCommitを増やすわけではありません。生成結果に変更がなければ何もしません。

## Commit / PR / Issueをどう数えているか

現在のTODAY Collectorは4種類をSearch APIから取得しています。

```python
commits = search(
    "/search/commits",
    f"author:{LOGIN} author-date:{window}",
    "author-date",
)

prs = search(
    "/search/issues",
    f"is:pr author:{LOGIN} created:{window}",
    "created",
)

issues_created = search(
    "/search/issues",
    f"is:issue author:{LOGIN} created:{window}",
    "created",
)

issues_completed = search(
    "/search/issues",
    f"is:issue author:{LOGIN} is:closed reason:completed closed:{window}",
    "updated",
)
```

数字だけ表示すると意味が曖昧になるので、それぞれの定義は固定しています。

### COMMITS

指定したJST日付範囲で、Commit Searchに `author:<username>` としてヒットしたPublic Commit数です。

これはGitHub Contribution Graphの数字そのものではありません。

### PRS OPENED

その日に自分が作成したPublic Pull Request数です。

### ISSUES CREATED

その日に自分が作成したPublic Issue数です。

### ISSUES DONE

自分が作成したIssueのうち、その日に `reason:completed` でCloseされたPublic Issue数です。

つまり「自分がClose操作したIssue数」とは限りません。

このあたりを曖昧にして「今日のContribution数」と書かないようにしています。

## README全体を自動生成し直さない

プロフィールREADMEには、自動生成したい部分だけでなく、手書きの自己紹介やFeatured Repositoryもあります。

Activity更新のたびにREADME全体を書き換える構成にはしたくなかったので、自動更新する範囲だけMarkerで囲いました。

```md
<!-- DAILY-ACTIVITY:START -->

## TODAY // Activity overview

...

<!-- DAILY-ACTIVITY:END -->
```

Python側ではMarker間だけを置換します。

```python
start = text.index(START_MARKER)
end = text.index(END_MARKER, start) + len(END_MARKER)
updated = text[:start] + block + text[end:]
```

これなら、それ以外のREADMEは普通に手編集できます。

後でWidgetを増やしたときも、このMarker方式をそのまま流用できました。

## 日次JSONを残す

READMEだけ更新すると、昨日の数字は消えてしまいます。

そこでActivityは日別JSONとしてRepositoryにも保存しています。

```text
data/
└─ activity/
   └─ 2026/
      └─ 08/
         ├─ 2026-08-25.json
         └─ 2026-08-26.json
```

イメージはこんな形です。

```json
{
  "schema_version": 1,
  "date": "2026-08-26",
  "timezone": "Asia/Tokyo",
  "scope": "public",
  "metrics": {
    "commits": 264,
    "prs_opened": 16,
    "issues_created": 5,
    "issues_completed": 3
  }
}
```

ここにある数値も、この記事用に固定したサンプルではなく、スクリーンショット撮影時点の実測例です。

1ファイルへ追記し続けず、1日1ファイルにしたのはGitの差分を読みやすくするためです。

この履歴を使って、現在は7日グラフも生成しています。今後のWeekly / Monthly Reportの入力にもできます。

## 昨日分も毎回取り直す

定期実行では今日だけでなく昨日も再取得しています。

```python
today_snapshot = write_snapshot(today, collect_day(today), now)
write_snapshot(yesterday, collect_day(yesterday), now)
```

日付変更直前のActivityや、検索結果への反映が少し遅れたケースを翌日の実行でも拾いやすくするためです。

現在のTODAY実装では、今日4検索 + 昨日4検索で1回あたり8 Search API requestです。

Widgetを増やすたびにAPIを好き勝手に叩く構成にはせず、今後はCollectorを共通化していく予定です。

## Public-onlyを最初から仕様にした

このプロフィールは誰でも見られます。

そのためTODAY Collectorは、意図的に認証なしでPublic GitHub APIを読んでいます。

```python
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": API_VERSION,
    "User-Agent": USER_AGENT,
}
```

Private Repository名やPrivate Issue titleを一度取得して、表示するときだけmaskする方式にはしていません。

**最初からPrivate dataを取得しない**方針です。

Activity表示のためにPrivate Repositoryの情報をPublic READMEやJSONへ誤ってCommitするのは、一番避けたかったことでした。

Public dataだけでもGitHub REST APIのRate Limitはあるので、リクエスト数を抑えることも意識しています。

## GitHub Actionsから自動Commitする

生成後に変更がある場合だけCommitします。

```bash
if [ -z "$(git status --porcelain -- README.md assets/activity-7d.svg data/activity)" ]; then
  echo "No profile activity changes"
  exit 0
fi
```

プロフィールRepositoryでは他にも自動更新Workflowが動いているため、Pushが競合する可能性があります。

そのためPushに失敗したら最新mainへRebaseしてRetryしています。

```bash
for attempt in 1 2 3; do
  if git push origin HEAD:main; then
    exit 0
  fi

  git fetch origin main
  git rebase origin/main
done
```

小さい部分ですが、自動生成系Workflowを複数動かすなら入れておいて良かった処理でした。

実際のScheduled runも正常終了しています。

<!-- QIITA_IMAGE: 02-actions-success.jpg -->

スクリーンショットでは `Update profile activity` がSchedule起動され、`update-profile-activity` JobがSuccessになっています。

## 実際に動かしてみて

最初にTODAY機能をMergeした直後は、READMEにはPlaceholderだけが表示されていました。

Workflowは3時間ごとのScheduleなので、次の実行で初めて実データへ置き換わります。

その後はプロフィールを開くだけで、その日の数値・直近Commit・7日グラフが見えるようになりました。

自分で毎日READMEを書き換える方式なら確実に続かないので、「プロフィールを見たら今日の開発量も勝手に更新されている」という状態は思っていた以上に楽しいです。

一方でTODAYだけでは、まだ分からないこともありました。

- 今、一番動いているRepositoryはどれか
- 直近で開発中なのか、しばらく離れているのか
- 連続して活動している日数
- 今日のActivity強度
- 今触っているRepositoryで使われている言語

そこで、記事を書いている途中で次のPhaseまで実装しました。

## TODAYからProfile Signalへ拡張した

TODAY実装の次に、`Profile Signal` として `LIVE SIGNAL` と `CURRENT FOCUS` を追加しました。

このPhaseは記事執筆中の2026-08-26に実装・CI確認を行い、mainへMerge済みです。

`LIVE SIGNAL` では、開発状態・Activity強度・Streakを1行にまとめています。

<!-- QIITA_IMAGE: 03-live-signal.jpg -->

撮影時点では次の状態でした。

```text
● BUILDING
🌩️ STORM
🔥 2 DAY STREAK
```

`CURRENT FOCUS` はPublic GitHub Eventsへ重みを付けて、今一番動いているRepositoryを判定します。

<!-- QIITA_IMAGE: 04-current-focus.jpg -->

撮影時点では `mizzz-ivr/ivmz-home` が34%でCurrent Focusになり、Repository language dataから `TypeScript / CSS / JavaScript` をTODAY'S STACKとして表示していました。

この部分はTODAYのSearch API集計とは別のAnalytics層として実装しています。いきなり既存Collectorを全面改修せず、動いているTODAYを残したまま段階的に拡張しました。

今後はこの2系統をNormalized Activity Modelへまとめる予定です。

## 好きなWidgetだけ使える形で配布したい

ここまで作ると、自分のプロフィール専用スクリプトで終わらせるより、好きなパーツだけ選べる形にしたくなりました。

最終的には、例えばこんな設定だけで使えるGitHub Actionを考えています。

```yaml
profile:
  username: octocat
  timezone: Asia/Tokyo

widgets:
  today:
    enabled: true

  current_focus:
    enabled: true

  dev_pulse:
    enabled: true
    days: 7
```

README側にはWidgetごとのMarkerを置きます。

```md
<!-- PROFILE-SIGNAL:FOCUS:START -->
<!-- PROFILE-SIGNAL:FOCUS:END -->
```

こうすれば、TODAYだけ欲しい人、Current Focusだけ欲しい人、全部使いたい人を同じ仕組みで扱えます。

自分のプロフィールを先にDogfooding環境として使い、安定したWidgetからGitHub Actionとして切り出していく予定です。

## 今のところの結論

GitHubプロフィールは、完成した自己紹介を置いておく場所だと思っていました。

でもActivityを自動表示してみると、少し印象が変わりました。

「何が作れるか」だけでなく、**今何を作っているか**も見える場所にできます。

今回はTODAYのActivity Counterから始めましたが、日次JSONを残しておいたことで7日グラフやProfile Signalへの拡張にもつながりました。

最初から大きなDashboardを作るより、まず1日分を正しく集計して履歴を残すところから始めたのは良かったと思っています。

次はDEV PULSE、NOW BUILDING、ACTIVITY STREAMを追加しながら、Widgetを選択できるGitHub Actionとして切り出していきます。

## 参考

- GitHub Docs — Managing your profile README
  - https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- GitHub Docs — Filtering and searching issues and pull requests
  - https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests
- GitHub Docs — Events that trigger workflows
  - https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub Docs — Rate limits for the REST API
  - https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

<!--
Qiita公開時:
- QIITA_IMAGEコメント4箇所をQiitaへアップロードした画像Markdownへ置換
- 公開直前にmizzz-ivr/mizzz-ivr mainを再確認
- Activity値は撮影時点の例であることを維持
- Secret / Private Repository / 不要なAccount情報が画像にないことを再確認
-->
