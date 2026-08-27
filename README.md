# tech-writing

個人開発で得た知見を、Qiita・Zenn・SNSなどで継続的に発信するための執筆リポジトリです。

## このリポジトリの役割

- 技術記事の元原稿を管理する
- 記事から展開するSNS投稿を管理する
- 次に書きたいテーマや公開済み記事を整理する
- 執筆時のテンプレートと文章方針を共通化する
- 投稿履歴・技術分野・言語/技術スタック・公開頻度を分析する
- Qiita / Zennの取得可能な外部指標を時系列で保存する
- 転職・フリーランス・営業でも使えるTechnical Portfolioとして育てる

実装内容そのものの事実確認は、各開発リポジトリを優先します。このリポジトリは「何を、どう発信したか」のSource of Truthとして扱います。

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
├─ requirements.txt
├─ articles/
│  └─ <article-slug>/
│     ├─ article.md
│     ├─ notes.md
│     └─ assets/
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
│  └─ WRITING_ANALYTICS.md
├─ scripts/
│  └─ writing_analytics.py
├─ templates/
│  ├─ article.md
│  └─ social-post.md
└─ .github/
   ├─ PULL_REQUEST_TEMPLATE.md
   └─ workflows/
      └─ writing-analytics.yml
```

## 基本フロー

1. `ideas/backlog.md` にテーマを残す
2. `articles/<slug>/notes.md` に実体験・根拠・使いたい具体例を集める
3. `article.md` を媒体共通の元原稿として書く
4. Qiita / Zenn向けの最終調整は公開時に行う
5. `social/<slug>/` にSNS投稿案を作る
6. 公開後にfront matterの `status` / `published_at` / 公開URLを更新する
7. `ideas/published.md` にURLと公開日を記録する
8. Writing AnalyticsがREADME / report / metrics snapshotを更新する

## 執筆方針

読みやすさは大事にしますが、文章を必要以上に整えすぎません。

一般論を並べるより、実際に開発中に起きたこと、迷ったこと、失敗したこと、そこから設計や運用を変えた理由を中心に書きます。技術的な主張は可能な限り対象リポジトリのコード・Issue・PR・Docs・CIを確認してから記載します。

詳しくは [STYLE_GUIDE.md](./STYLE_GUIDE.md) を参照してください。

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

## 最初の記事

- [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](./articles/repository-is-source-of-truth/article.md)
