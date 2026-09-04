# Notes: 個人開発でもPRを切ってCIを通すようにしている理由

本文を書く前の体験整理・事実確認メモです。

## 記事の中心

- 個人開発ではレビュー相手がいないので、以前はmainへ直接変更を入れても困らないと思っていた
- 規模が大きくなり、複数機能・複数Repository・AIを使った実装が増えると、変更理由と差分を後から追える価値が上がった
- PRは「誰かに承認してもらうため」だけではなく、変更を1単位にまとめ、何を変えたかを自分で確認する境界として使っている
- CIは品質保証の全部ではなく、自動確認できる範囲のDefinition of Doneとして扱う
- AIで実装速度が上がるほど、生成された変更をそのままmainへ流さない仕組みの価値が上がった
- 「個人開発でもチーム開発っぽくしよう」ではなく、数日後の自分とAIが変更を追いやすくするための運用として書く

## 2026-08-24 事実確認

### 現在のCI

Hertaの現行 `.github/workflows/ci.yml` を確認。

基本gate:

- Format Check
- Lint
- Typecheck
- Test
- Build

追加で以下も実行している。

- Prisma Generate
- Supply chain policy tests
- vulnerability exception validation
- Production Compose Validation
- Origin protection configuration validation
- Production Docker Build
- production runtime verification
- Syft / Grypeのpinned install + checksum verification
- Grype vulnerability DB refresh
- vulnerability failure gate probe
- CycloneDX SBOM generation
- High / Critical vulnerability scan
- security report artifact upload

記事本文では項目を大量列挙せず、基本gate + 「projectによってDocker / Supply Chainまで」と要約する。

### 最新main

確認時点:

`7cd9d99063be1c64a5a4cecd77b83cc33ce80cc4`

PR #322 merge commit。

記事公開直前には再確認する。

### PRを境界にした具体例

Core Utility v5 JSON commandの実装では、最初の実装後に以下の追加修正が入っている。

- JSON utilityの回帰テスト追加
- 型境界 / 整形修正
- test formatting
- Core Catalog分類test
- JSON整形で値とnumeric lexemeを保持する修正
- 値保持 / 境界test
- 最終format調整

記事ではPR番号や自Repository URLを参考リンクにせず、
「JSONコマンド実装 → 値保持問題に気づく → fix / test / formatを追加してからmerge」
という実体験として書く。

### CI GREENでも完了扱いにしなかった例

Plugin OperationsのMobile UI改善では、Repository上のtestを追加しても、認証済みStudioでDesktop / Mobile実ブラウザQAが完了するまでIssueをCloseしない方針だった。

記事では「CIが見られるもの」と「実ブラウザ / UXの人間確認」を分ける具体例として使う。

## 外部参考資料

自分のRepository / Issue URLは記事の参考資料に掲載しない。

確認済み:

1. GitHub Docs — About pull requests
   - PRはbranch間の変更提案
   - Conversation / Commits / Checks / Files changedにレビュー情報をまとめる
   - automated tests / builds / code scanningもPR上で確認できる

2. GitHub Docs — About protected branches
   - required status checksをmerge条件にできる
   - 記事では現在の自Repositoryのbranch protection設定を確認していないので「自分はrequired checksを設定している」とは断定しない

3. Martin Fowler — Continuous Integration
   - integrationごとにautomated build / testで検証し、integration errorを早く検出する考え方
   - CIの項目数ではなく継続的に機械検証する意味の補強に使う

4. GitHub Docs — Review output from Copilot
   - coding agentのPull Requestもmerge前に十分レビューすることを案内
   - 「AIを信用しないからPR」ではなく「AIの速度を活かしつつmerge判断を分離する」という本文の補強に使う

## 記事で分ける役割

- branch: 作業中の変更をmainから分離する
- PR: 変更の目的・差分・review単位を残す
- CI: 機械的に確認できる完了条件を揃える
- 人間: Product判断、UX、危険な変更、最終merge判断

## 避ける書き方

- 「個人開発でも絶対にPRを使うべき」と断定する
- チーム開発のBest Practiceをそのまま個人へ当てはめる
- CI GREENなら品質が保証されると書く
- HertaのCI項目を大量に列挙して記事の主題をぼかす
- 自分のRepository / Issueを参考URLとして掲載する
- AIを使うから危険、またはAIなら全部自動化できる、のどちらかに寄せる
- 根拠なく開発速度やバグ削減率を数値化する

## 読者

- 個人開発でGitHubを使っている人
- mainへ直接pushしているがPR運用が気になっている人
- AIコーディングツールを個人開発に取り入れている人
- CIをどこまで整えるべきか迷っている人

## 公開前チェック

- [x] 現在使っているbranch / PRの流れを確認
- [x] CIで実際に実行しているFormat / Lint / Typecheck / Test / Buildを確認
- [x] Security / Supply Chain系checkを確認
- [x] PRが役立った具体例を選定
- [x] CI GREENでも人間が確認する具体例を選定
- [x] 外部参考資料を選定
- [ ] 公開直前のmain / CIを再確認
- [ ] Qiita用タグを最終調整
- [ ] 公開後にfront matter / published.mdを更新
