# Content Gap / Next Article Opportunities

Writing Analytics Phase 2Cで生成する `reports/content-opportunities.md` の運用仕様です。

## 目的

記事数や外部reactionだけではなく、Portfolio / career coverage、実装根拠、最近扱っていない分類、draft/review中の記事との重複を見て「次に何を書くべきか」を判断できるようにします。

## Source of Truth

優先順位は次のとおりです。

1. `articles/<slug>/article.md` のfront matter
2. `ideas/published.md` の公開記録
3. `ideas/backlog.md` に明示された候補・Source of Truth
4. `data/metrics/YYYY-MM-DD.json` のplatform別reaction
5. `reports/content-opportunities.md` は再生成可能なderived report

本文やbacklog自由文からdomain / technology / source repositoryを推測してmetadataへ書き戻しません。

## 推薦優先順位

候補を単一の総合Popularity Scoreへ変換せず、次の順で辞書的に比較します。

1. Portfolio / career coverage gap
2. `source_repositories` 等で実装・検証根拠が明示されているか
3. 未公開classification / 最終投稿日からのcoverage gap
4. 関連する公開記事のpositive reaction
5. 同条件なら `review` を `draft` よりreadyとして扱う

reactionは補助情報です。stocks / likes / commentsなどを合算して、反応が良いテーマだけを推薦することはしません。

## Coverage

公開済み記事について以下を集計します。

- topics
- domains
- languages
- technologies
- portfolio_signals

各値について、公開記事数、最終投稿日、基準日からの経過日数、30 / 90 / 365日coverageを表示します。

基準日は最新の正常なmetrics snapshotの日付を優先し、snapshotが無ければ公開済みmetadataの最新日を使用します。欠測日を補間しません。

## Pipeline-only gap

`draft` / `review` のmetadataには存在するが、公開済み記事にはまだ存在しないclassificationを表示します。

これは「必ず次に書くべき」という意味ではなく、現在の執筆pipelineに既に存在するPortfolio coverage候補です。

## Backlog overlap

`ideas/backlog.md` の未完了項目について、既存のpublished / draft / reviewタイトルとの高い類似だけを検出します。

- `Zenn:` / `Qiita:` / `note #N:` の媒体prefixは比較時に除外
- 類似度しきい値は `0.88`
- 高い類似は重複候補として表示するが、自動でbacklogを編集しない
- 自由文からclassificationを推測しない

明示的な `Source of Truth:` があるbacklog項目は、既存記事と重複しない場合だけevidence-backed候補として表示します。

## Missing metadata

候補記事に `domains` / `languages` / `technologies` / `portfolio_signals` / `source_repositories` が無い場合、スクリプトは値を補完しません。

`not recorded` / `Metadata needed before stronger scoring` として可視化し、推測による推薦精度の水増しを避けます。

## コマンド

生成:

```bash
python scripts/writing_opportunities.py
```

PR validation:

```bash
python scripts/writing_opportunities.py --check
```

`--check` はRepositoryを書き換えず、現在のmetadataからreportを最後までrenderできることを検証します。

## GitHub Actions

`Writing Analytics` workflowで次を行います。

- PR: unit tests + `writing_opportunities.py --check`
- main / schedule / manual refresh: metrics/profile更新後にcontent opportunitiesを生成
- `reports/content-opportunities.md` に差分があればanalytics bot commitへ含める

## 制約

- Repositoryのrecent commit / PRをこのPhaseでは自動crawlしない
- `source_repositories` が存在することを「最近実装した」と読み替えない
- GitHub recent activityから記事候補を抽出するのはIssue #18のFuture `GitHub → Writing Funnel` で扱う
- Phase 2Cは現在Repositoryに記録済みの執筆metadataを根拠にする
