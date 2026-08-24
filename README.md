# tech-writing

個人開発で得た知見を、Qiita・Zenn・SNSなどで継続的に発信するための執筆リポジトリです。

## このリポジトリの役割

- 技術記事の元原稿を管理する
- 記事から展開するSNS投稿を管理する
- 次に書きたいテーマや公開済み記事を整理する
- 執筆時のテンプレートと文章方針を共通化する

実装内容そのものの事実確認は、各開発リポジトリを優先します。このリポジトリは「何を、どう発信したか」のSource of Truthとして扱います。

## 構成

```text
tech-writing/
├─ README.md
├─ STYLE_GUIDE.md
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
├─ templates/
│  ├─ article.md
│  └─ social-post.md
└─ .github/
   └─ PULL_REQUEST_TEMPLATE.md
```

## 基本フロー

1. `ideas/backlog.md` にテーマを残す
2. `articles/<slug>/notes.md` に実体験・根拠・使いたい具体例を集める
3. `article.md` を媒体共通の元原稿として書く
4. Qiita / Zenn向けの最終調整は公開時に行う
5. `social/<slug>/` にSNS投稿案を作る
6. 公開後に `ideas/published.md` へURLと公開日を記録する

## 執筆方針

読みやすさは大事にしますが、文章を必要以上に整えすぎません。

一般論を並べるより、実際に開発中に起きたこと、迷ったこと、失敗したこと、そこから設計や運用を変えた理由を中心に書きます。技術的な主張は可能な限り対象リポジトリのコード・Issue・PR・Docs・CIを確認してから記載します。

詳しくは [STYLE_GUIDE.md](./STYLE_GUIDE.md) を参照してください。

## 最初の記事

- [AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話](./articles/repository-is-source-of-truth/article.md)
