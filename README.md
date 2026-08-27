# tech-writing

個人開発で得た知見や、エンジニアとしての経験・考えを、Qiita・Zenn・note・SNSなどで継続的に発信するための執筆リポジトリです。

## このリポジトリの役割

- 技術記事とnote記事の元原稿・企画を管理する
- Qiitaの記事をQiita CLI + GitHub Actionsで投稿・更新する
- Zennの記事・本をGitHub連携で投稿・更新する
- Zennスクラップの原稿・履歴・バックアップを管理する
- 記事から展開するSNS投稿を管理する
- 次に書きたいテーマや公開済み記事を整理する
- 執筆時のテンプレートと文章方針を共通化する
- 投稿履歴・技術分野・言語/技術スタック・公開頻度を分析する
- Qiita / Zennの取得可能な外部指標を時系列で保存する
- 転職・フリーランス・営業でも使えるTechnical Portfolioとして育てる
- 技術だけでなく、経験・判断・価値観を残すThinking Portfolioとしても育てる

実装内容そのものの事実確認は、各開発リポジトリを優先します。このリポジトリは「何を、どう発信したか」のSource of Truthとして扱います。

## 媒体戦略

同じ経験を複数媒体で扱うことはありますが、同一本文は重複投稿しません。媒体ごとに記事が答える問いを分けます。

| 媒体 | 主な役割 | 基本の問い |
| --- | --- | --- |
| Qiita | 実装・検証・問題解決 | How: どう実装・解決したか |
| Zenn | 設計・技術深掘り | Design / Why technically: なぜその設計にしたか |
| note | 経験・思想・キャリア・社会 | Why personally / What I think: なぜそう考えるか |

noteは月1本程度を目安にし、エンジニアとしての考え方、個人開発の裏側、キャリア・仕事・学習、技術×経済・社会を主な柱にします。詳細は [note Editorial Strategy](./docs/NOTE_EDITORIAL.md) を参照してください。

## Qiita GitHub Publish

Qiitaは公式Qiita CLIとGitHub Actionsで管理します。Qiitaへ実際に反映されるcanonicalな公開ソースは `public/*.md` です。

PRは下書き・レビュー境界として扱い、PR作成・更新ではQiitaへpublishしません。`public/**/*.md` が `main` にmergeされたときだけ `.github/workflows/qiita-publish.yml` が起動し、Repository Secret `QIITA_TOKEN` を使ってQiitaへ投稿・更新します。

既存Qiita記事は本文を手作業で複製せず、`Sync Qiita articles` workflowから `qiita pull` してPRとして取り込みます。これにより既存のQiita item IDを維持した状態でRepository管理へ移行します。

```bash
npm install
npm run qiita:preview
npm run qiita:new:article -- <article-slug>
npm run qiita:pull
```

ローカルCLIは公開の必須条件ではありません。公開処理はGitHub Actionsが担当します。

Tokenには `read_qiita` / `write_qiita` を付与し、GitHub ActionsのRepository Secret `QIITA_TOKEN` として保存します。Token値はRepositoryへ保存しません。

初回取り込み・公開・更新・削除・rollbackの詳細は [Qiita GitHub Publish Runbook](./docs/QIITA_GITHUB_PUBLISH.md) を参照してください。

## Zenn GitHub Deploy

ZennアカウントにこのRepositoryを連携し、同期branchを `main` にします。

| 種別 | 管理場所 | GitHubからZennへ同期 |
| --- | --- | --- |
| 記事 | `articles/<slug>.md` | 対応 |
| 本 | `books/<book-slug>/` | 対応 |
| スクラップ | `scraps/<slug>.md` | 非対応（Repository管理 + Zenn Web UI） |

2026-08-27時点のZenn公式仕様ではGitHub同期対象は記事と本のみで、スクラップは非対応です。スクラップについて自動投稿できるものとして扱いません。

記事・本は公開準備中 `published: false` を維持し、公開PRで `true` にして `main` へmergeします。

```bash
npm install
npm run zenn:preview
npm run zenn:new:article -- --slug <article-slug>
npm run zenn:new:book -- --slug <book-slug>
```

初回接続・公開・削除・スクラップ運用の詳細は [Zenn GitHub Deploy Runbook](./docs/ZENN_GITHUB_DEPLOY.md) を参照してください。

## Writing Analytics

<!-- WRITING_ANALYTICS:START -->
### Writing Profile

**3 published** · Last post **2026-08-27** · Avg interval **1.5日**

- Topics: GitHub (2), GitHubActions (2), GitHubAPI (2), Python (2), 個人開発 (2)
- Domains: developer-productivity (3), devops (2), ai (1)
- Languages: Python (2)

#### Recent

- 2026-08-27 — [GitHubプロフィールをライブな開発ダッシュボードにしてみた](https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630)
- 2026-08-26 — [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a)
- 2026-08-24 — [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e)

#### Notable

- [GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた](https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a) — likes 0 · stocks 2 · comments 0 (qiita)

詳細なreaction値と未取得状態: [Writing Profile / Analytics](./reports/writing-profile.md) · [運用設計](./docs/WRITING_ANALYTICS.md)
<!-- WRITING_ANALYTICS:END -->

## 構成

```text
tech-writing/
├─ README.md
├─ STYLE_GUIDE.md
├─ package.json
├─ qiita.config.json
├─ requirements.txt
├─ public/                         # Qiita CLI publish対象
│  └─ <qiita-article-slug>.md
├─ articles/
│  ├─ <zenn-article-slug>.md      # Zenn GitHub Deploy対象
│  └─ <article-slug>/             # 媒体共通原稿・notes・analytics metadata
│     ├─ article.md
│     ├─ notes.md
│     └─ assets/
├─ books/                         # Zenn GitHub Deploy対象
│  └─ <book-slug>/
│     ├─ config.yaml
│     ├─ cover.png
│     └─ <chapter-slug>.md
├─ scraps/                        # Git管理のみ。Zenn同期非対応
│  └─ <scrap-slug>.md
├─ social/
│  └─ <article-slug>/
│     └─ x.md
├─ ideas/
│  ├─ backlog.md
│  └─ published.md
├─ data/
│  └─ metrics/
│     └─ YYYY-MM-DD.json
├─ reports/
│  └─ writing-profile.md
├─ docs/
│  ├─ NOTE_EDITORIAL.md
│  ├─ QIITA_GITHUB_PUBLISH.md
│  ├─ WRITING_ANALYTICS.md
│  └─ ZENN_GITHUB_DEPLOY.md
├─ scripts/
│  └─ writing_analytics.py
├─ templates/
│  ├─ article.md
│  ├─ note.md
│  ├─ social-post.md
│  └─ zenn-scrap.md
└─ .github/
   ├─ PULL_REQUEST_TEMPLATE.md
   └─ workflows/
      ├─ qiita-publish.yml
      ├─ qiita-sync.yml
      └─ writing-analytics.yml
```

## 基本フロー

1. `ideas/backlog.md` にテーマを残す。
2. 実体験・根拠・具体例をnotesへ集める。
3. `articles/<slug>/article.md` に媒体共通の元原稿・企画・Writing Analytics用metadataを整理する。
4. Qiita記事は `public/<slug>.md` をcanonicalな公開ソースとしてPRでレビューし、mainへのmerge後にGitHub Actionsから投稿・更新する。
5. Zenn記事は `articles/<slug>.md`、Zenn本は `books/<book-slug>/` をcanonicalな公開ソースとして扱う。
6. Zenn記事・本は `published: false` でPR・Previewし、公開時に `true` へ変更して `main` へmergeする。
7. Zennスクラップは `scraps/` で原稿・履歴をGit管理し、Zenn Web UIへ手動反映する。
8. `social/<slug>/` にSNS投稿案を作る。
9. 公開後に公開URL・公開日を `ideas/published.md` 等へ記録する。
10. Writing AnalyticsがREADME / report / metrics snapshotを更新する。

`articles/<slug>/article.md` とQiitaの `public/*.md` は自動同期しません。Qiita公開時は `public/*.md`、Zenn公開時は `articles/<slug>.md` / `books/` を各媒体の公開Source of Truthとして扱います。

## 執筆方針

読みやすさは大事にしますが、文章を必要以上に整えすぎません。

一般論を並べるより、実際に開発中に起きたこと、迷ったこと、失敗したこと、そこから設計や運用を変えた理由を中心に書きます。技術的な主張は可能な限り対象リポジトリのコード・Issue・PR・Docs・CIを確認してから記載します。

noteでは技術的な正確性を維持しつつ、実装手順の網羅よりも「なぜその考えに至ったか」「経験して何が変わったか」を優先します。経済・社会・制度・時事情報を扱う場合は、事実と意見を分け、公開時点の情報を確認します。

詳しくは [STYLE_GUIDE.md](./STYLE_GUIDE.md)、[docs/NOTE_EDITORIAL.md](./docs/NOTE_EDITORIAL.md)、[docs/QIITA_GITHUB_PUBLISH.md](./docs/QIITA_GITHUB_PUBLISH.md)、[docs/ZENN_GITHUB_DEPLOY.md](./docs/ZENN_GITHUB_DEPLOY.md) を参照してください。

## Writing Analyticsの実行

```bash
pip install -r requirements.txt
python scripts/writing_analytics.py --check
python scripts/writing_analytics.py
```

外部メトリクスも更新する場合:

```bash
python scripts/writing_analytics.py --refresh-metrics
```

Qiitaの認証が必要な指標を取得する場合は `QIITA_TOKEN` を環境変数またはGitHub ActionsのRepository Secretとして設定します。Token値はRepositoryへ保存しません。

現時点の外部reaction取得対象はQiita / Zennです。noteの外部指標は、安定した取得方法を確認できるまで推測や不安定なスクレイピングを前提にしません。

## 最初の記事

- [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](./articles/repository-is-source-of-truth/article.md)
