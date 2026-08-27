# tech-writing

個人開発やエンジニア業務で得た知見を、**Qiita / Zenn / note** 向けの記事として管理・公開するための執筆リポジトリです。

このRepositoryは「何を、どう発信したか」のSource of Truthです。記事の技術的な事実確認は、元になった各開発Repositoryを優先します。

## まず見る

| 媒体 | 主な役割 | Canonical source | 公開方法 | 詳細 |
| --- | --- | --- | --- | --- |
| Qiita | 実装・検証・問題解決 | `public/*.md` | `main` merge後にGitHub Actionsからpublish | [Runbook](./docs/QIITA_GITHUB_PUBLISH.md) |
| Zenn | 設計・技術深掘り | `articles/<slug>.md` / `books/` | Zenn GitHub Deploy | [Runbook](./docs/ZENN_GITHUB_DEPLOY.md) |
| note | 経験・考え・キャリア | `articles/YYMMDD-<slug>/article.md` | `note:publish` → Web Editorで最終公開 | [Runbook](./docs/NOTE_PUBLISH_HELPER.md) |

同じ経験を複数媒体で扱うことはありますが、同一本文をそのまま重複投稿しません。媒体ごとの役割は [note Editorial Strategy](./docs/NOTE_EDITORIAL.md) を参照してください。

## 普段の流れ

1. `ideas/backlog.md` にテーマを残す。
2. 実体験・Issue・PR・コード・CIなど、記事の根拠を集める。
3. 媒体に合わせて原稿を作り、branch / PRでレビューする。
4. Qiita / Zenn / noteそれぞれの公開フローで公開する。
5. 公開URLと公開日を `ideas/published.md` に記録する。
6. Writing Analyticsが公開履歴・技術coverage・外部reactionを更新する。

記事ID・ファイル名のルールは [Article ID / File Naming](./docs/ARTICLE_NAMING.md) を参照してください。

## よく使うコマンド

```bash
# 初回セットアップ
npm install
pip install -r requirements.txt

# note: Markdown本文をコピーして新規投稿画面を開く
npm run note:publish -- articles/YYMMDD-<slug>/article.md

# Qiita / Zenn preview
npm run qiita:preview
npm run zenn:preview

# Writing Analyticsの検証
python scripts/writing_analytics.py --check
```

Qiitaの既存記事同期、新規記事作成、Zenn本・スクラップなどの詳細コマンドは各Runbookへ集約しています。

## Writing Analytics / Portfolio

公開履歴・技術分野・Portfolio coverage・外部reactionをRepository内のデータから生成します。

- [Writing Profile](./reports/writing-profile.md) — 公開頻度・技術傾向・reaction
- [Content Opportunities](./reports/content-opportunities.md) — 次の記事候補・coverage gap
- [Visual Dashboard](./reports/visual-dashboard.md) — 可視化
- [Public Writing Portfolio JSON](./data/exports/writing-portfolio.json) — 外部Portfolio向けstable schema

**Portfolio全体の公開記事数やcoverageは `writing-portfolio.json` を参照してください。** Zenn-native記事を含む統合データはこちらを正とします。

<details>
<summary>README用の詳細Writing Analyticsを表示</summary>

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

</details>

## 主なディレクトリ

| Path | 用途 |
| --- | --- |
| `public/` | Qiita publish対象 |
| `articles/` | Zenn記事 / 共通原稿 / note原稿 |
| `books/` | Zenn本 |
| `scraps/` | ZennスクラップのGit管理 |
| `ideas/` | backlog / 公開記録 |
| `social/` | SNS投稿案 |
| `reports/` | Writing Analytics生成レポート |
| `data/` | metrics snapshot / public export |
| `docs/` | 詳細Runbook・設計 |

## Docs

| Document | 内容 |
| --- | --- |
| [STYLE_GUIDE.md](./STYLE_GUIDE.md) | 執筆方針 |
| [ARTICLE_NAMING.md](./docs/ARTICLE_NAMING.md) | Article ID / ファイル命名 |
| [QIITA_GITHUB_PUBLISH.md](./docs/QIITA_GITHUB_PUBLISH.md) | Qiita同期・投稿・rollback |
| [ZENN_GITHUB_DEPLOY.md](./docs/ZENN_GITHUB_DEPLOY.md) | Zenn GitHub Deploy |
| [NOTE_EDITORIAL.md](./docs/NOTE_EDITORIAL.md) | note媒体戦略 |
| [NOTE_PUBLISH_HELPER.md](./docs/NOTE_PUBLISH_HELPER.md) | note公開helper |
| [WRITING_ANALYTICS.md](./docs/WRITING_ANALYTICS.md) | Writing Analytics設計 |
| [PORTFOLIO_EXPORT.md](./docs/PORTFOLIO_EXPORT.md) | public Portfolio JSON |

## 執筆方針

一般論を増やすより、**実際に起きたこと・迷ったこと・失敗したこと・設計や運用を変えた理由**を中心に書きます。技術的な主張は可能な限り元Repositoryのコード・Issue・PR・Docs・CIで確認します。

Secret / Token / Password / Cookieなどの認証情報はRepository・Issue・PR・記事へ記載しません。
