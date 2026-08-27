---
title: GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
tags:
  - GitHubActions
  - GitHub
  - Python
  - GitHubAPI
private: false
updated_at: '2026-08-26T22:07:11+09:00'
id: 73bd3a3874aa8adacc1a
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---


# GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた

GitHubのプロフィールREADMEを更新していて、ふと思いました。

プロフィールには「何を作っているか」は書いてあるけど、**今日実際に何をしていたのかは分からない**。

Featured Repositoryや技術スタックは自己紹介としては便利です。ただ、自分の場合は複数の個人開発を並行して触っているので、昨日と今日で一番触っているRepositoryが違うことも珍しくありません。

そこでプロフィール上部に、こんなブロックを自動表示することにしました。

![IMG_3763.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4394245/4d9ba5b3-1b32-482c-8ea3-460ba8503873.jpeg)

数値は手入力ではありません。

GitHub ActionsがGitHub APIからその日の公開Activityを取得し、README、7日グラフ、日次JSONを自動更新しています。

今回は、この仕組みを作るときに考えたことと、実際の構成をまとめます。

## 最初はGitHub Stats系のカードを置こうとしていた

GitHubプロフィールを動的に見せる方法自体はいろいろあります。

ただ、自分が今回欲しかったのは累計Starsや言語比率ではありませんでした。

見たかったのはもっと短い時間軸です。

- 今日どれくらいCommitしたか
- 今日PRを何件作ったか
- 今日Issueを何件作ったか
- 今日完了したIssueはいくつか
- 直近では何を触っていたか

そして、表示するだけでなく、後から週次・月次で振り返れるようにしたかった。

そのため外部のStatsサービスを貼るのではなく、**GitHub Actionsで自分用のActivityデータを作る**ことにしました。

## 構成

今の構成はかなり単純です。

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

利用しているのは基本的にGitHub内の機能だけです。

- Profile README
- GitHub REST Search API
- Python
- GitHub Actions
- Repository内のJSON / SVG

別サーバーやDBは使っていません。

GitHubのプロフィールREADMEは、自分のユーザー名と同名のPublic Repositoryのルートに`README.md`を置くとプロフィールへ表示できます。

## 「今日」はJSTで切りたかった

最初に気をつけたのが日付でした。

自分は日本時間で活動しているので、READMEに表示する「今日」も`Asia/Tokyo`基準にしたい。

そのため、まずJSTの0:00〜23:59:59を作ってからUTCへ変換しています。

```python
def zulu(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_window(day: date) -> str:
    start_local = datetime.combine(day, time.min, TZ)
    end_local = start_local + timedelta(days=1) - timedelta(seconds=1)
    return f"{zulu(start_local)}..{zulu(end_local)}"
```

例えば2026-08-26 JSTなら、検索に使うUTC範囲は次のようになります。

```text
2026-08-25T15:00:00Z
..
2026-08-26T14:59:59Z
```

ActionsのCron側も現在はtimezoneを指定しています。

```yaml
on:
  schedule:
    - cron: "17 */3 * * *"
      timezone: "Asia/Tokyo"
  workflow_dispatch:
```

毎日1回ではなく3時間ごとにしたのは、朝の数字が夜まで残り続けるのを避けたかったからです。

ただし毎回Commitを作るわけではありません。生成結果に変更がなければ何もしません。

## Commit / PR / Issueをどう数えているか

現在は4種類をSearch APIから取得しています。

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

ここで表示している数値には意味を固定しています。

### COMMITS

指定したJST日付範囲で、Commit Searchに`author:<username>`としてヒットした公開Commit数です。

Contribution Graphの数字そのものではありません。

### PRS OPENED

その日に自分が作成したPublic Pull Request数です。

### ISSUES CREATED

その日に自分が作成したPublic Issue数です。

### ISSUES DONE

自分が作成したIssueのうち、その日に`reason:completed`でCloseされたPublic Issue数です。

これは「自分がClose操作したIssue数」ではありません。

数字だけ出すと後で意味が曖昧になるので、この定義はコード側でもREADME側でも崩さないようにしています。

## README全体を生成し直さない

プロフィールREADMEには手書きの自己紹介やFeatured Repositoryもあります。

Activity更新のたびにREADME全体を生成する構成にはしたくありませんでした。

そこで、自動更新する範囲だけMarkerで囲っています。

```md
<!-- DAILY-ACTIVITY:START -->

## TODAY // Activity overview

...

<!-- DAILY-ACTIVITY:END -->
```

Python側ではこの2つのMarker間だけを置換します。

```python
start = text.index(START_MARKER)
end = text.index(END_MARKER, start) + len(END_MARKER)
updated = text[:start] + block + text[end:]
```

これなら、それ以外のプロフィールを普通に手編集できます。

このMarker方式は、あとで機能をパーツ化するときにもそのまま使えそうです。

## 日次JSONも一緒に残す

READMEだけ更新すると、昨日の数字は消えてしまいます。

そこでActivityは日別JSONとしてRepositoryにも残しています。

```text
data/
└─ activity/
   └─ 2026/
      └─ 08/
         ├─ 2026-08-25.json
         └─ 2026-08-26.json
```

中身は例えばこんな形です。

```json
{
  "schema_version": 1,
  "date": "2026-08-26",
  "timezone": "Asia/Tokyo",
  "scope": "public",
  "metrics": {
    "commits": 87,
    "prs_opened": 13,
    "issues_created": 3,
    "issues_completed": 1
  }
}
```

1ファイルへ追記し続けるのではなく、1日1ファイルにしました。

理由は単純で、Gitの差分が読みやすいからです。

このJSONがあることで、現在は7日グラフを生成できていますし、今後はWeekly / Monthly Reportにも使えます。

## 昨日分も毎回取り直している

定期実行では今日だけでなく昨日も再取得しています。

```python
today_snapshot = write_snapshot(today, collect_day(today), now)
write_snapshot(yesterday, collect_day(yesterday), now)
```

これは日付変更直前のActivityや、検索結果への反映が少し遅れたケースを翌日の実行で拾いやすくするためです。

現在の実装では、今日4検索 + 昨日4検索の計8 Search API requestです。

APIを無駄に叩かないことも、この構成では意識しています。

## Public-onlyを最初から仕様にした

このプロフィールは誰でも見られます。

そのためCollectorは、意図的に認証なしでPublic GitHub APIを読んでいます。

```python
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": API_VERSION,
    "User-Agent": USER_AGENT,
}
```

Private Repository名やPrivate Issue titleなどを、一度取得してから表示時に隠す設計にはしていません。

**最初からPrivate dataを取得しない**ようにしました。

これは自分の中ではかなり重要でした。

プロフィール生成処理で一番避けたいのは、便利なActivity表示を作った結果、Private Repositoryの情報を誤ってPublic READMEやJSONへCommitしてしまうことです。

Public dataだけなら認証なしREST APIも利用できます。ただしGitHub REST APIにはRate Limitがあり、Search endpointには通常のREST APIとは別の制限もあります。

そのため、今後Widgetを増やすときも「WidgetごとにAPIを好き勝手に叩く」構成にはしない予定です。

## GitHub Actionsから自動Commitする

生成後に変更がある場合だけCommitします。

```bash
if [ -z "$(git status --porcelain -- README.md assets/activity-7d.svg data/activity)" ]; then
  echo "No profile activity changes"
  exit 0
fi
```

プロフィールRepositoryでは他にも自動更新Workflowが動いているため、Pushが競合する可能性があります。

そのためPush失敗時は最新mainへRebaseしてRetryしています。

```bash
for attempt in 1 2 3; do
  if git push origin HEAD:main; then
    exit 0
  fi

  git fetch origin main
  git rebase origin/main
done
```

小さいところですが、自動生成系Workflowを複数動かすなら入れておいて良かった部分です。


## 実際に動かしてみて

最初にPRをMergeした直後は、READMEにはまだPlaceholderだけが表示されていました。

Workflowは3時間ごとのScheduleなので、次の実行で初めて実データへ置き換わります。

その後、プロフィールを確認すると今日の数値と直近Commit、7日グラフまで自動で表示されました。

自分で毎日更新するなら絶対に続かないので、プロフィールを開くだけで「今日は結構触っていたな」と分かるのは思った以上に楽しいです。

一方で、今の実装にもまだ課題があります。

- Commit / PR / Issueを別々のSearchで取っている
- Activityの意味はContribution Graphとは一致しない
- 直近Activityリストは件数を絞っている
- 7日分を貯めるまではグラフの履歴が薄い
- Projectごとの「今一番触っているもの」はまだ分からない

最後の点が特に気になったので、現在は次の機能を作り始めています。

```text
LIVE SIGNAL
● BUILDING | 🌩️ STORM | 🔥 BUILD STREAK

CURRENT FOCUS
今一番触っているRepository
+ TODAY'S STACK
```

この先は単なるActivity Counterではなく、GitHubプロフィールを小さな開発ダッシュボードにしていく予定です。

## この仕組み自体をテンプレート化したい

実装しているうちに、自分のプロフィールだけで終わらせるより、好きなWidgetだけ選べる形にしたくなってきました。

最終的にはこんな設定だけで使えるGitHub Actionにしたいと考えています。

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

README側はMarkerを好きな場所へ置くだけです。

```md
<!-- PROFILE-SIGNAL:FOCUS:START -->
<!-- PROFILE-SIGNAL:FOCUS:END -->
```

ここまでできれば、Profile READMEのテンプレートというより、**公開GitHub Activityからプロフィール用Widgetを生成する小さなGitHub Action**として配布できます。

今は自分のプロフィールをDogfooding環境として先に作っています。

## 今のところの結論

GitHubプロフィールは、完成した自己紹介を置いておく場所だと思っていました。

でも実際にActivityを自動表示してみると、少し印象が変わりました。

「何が作れるか」だけでなく、**今何を作っているか**も見せられる。

しかもGitHub ActionsとGitHub APIだけでかなり遊べます。

今後はCurrent Focus、Build Streak、Dev Pulse、Project Healthなどを追加しつつ、表示がごちゃつかないようWidgetとして整理していく予定です。

そして、ある程度安定したら誰でも一部だけ持っていける形でOSS化します。

## 参考

- [Managing your profile README - GitHub Docs](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
- [Filtering and searching issues and pull requests - GitHub Docs](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests)
- [Events that trigger workflows - GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [Rate limits for the REST API - GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)

<!--
公開前:
- STYLE_GUIDE.md を確認
- mizzz-ivr/mizzz-ivr の最新main / Workflow / READMEを再確認
- 記事内の実測値を公開時点へ更新
- Profile Signal Phase 1の実装状態に合わせて「現在作り始めている」部分を調整
- Secret / Private Repository情報がスクリーンショットにないことを確認
- Qiita Markdownでtable / details / code blockを確認
-->
