# Zenn GitHub Deploy

`mizzz-ivr/tech-writing` をZenn連携Repositoryとして使うためのRunbookです。

## 対応範囲

2026-08-27時点のZenn公式仕様では、GitHub Repository同期に対応するのは **記事（article）と本（book）** です。

**スクラップ（scrap）はGitHub同期非対応**です。そのためこのRepositoryでは、スクラップも原稿・履歴をGit管理できますが、Zennへの作成・更新はWeb UIで行います。

| 種別 | Repository管理 | GitHub Deploy | Zenn CLI Preview |
| --- | --- | --- | --- |
| 記事 | `articles/<slug>.md` | 対応 | 対応 |
| 本 | `books/<book-slug>/...` | 対応 | 対応 |
| スクラップ | `scraps/<slug>.md` | 非対応 | 非対応 |

## 初回セットアップ

1. Zennへログインし、`https://zenn.dev/dashboard/deploys` を開く。
2. 「リポジトリを連携」を選ぶ。
3. GitHub AppのRepository accessは `Only select repositories` を選ぶ。
4. `mizzz-ivr/tech-writing` だけを許可してInstall / Authorizeする。
5. Zenn側の同期対象Repositoryを `mizzz-ivr/tech-writing` にする。
6. 同期対象branchを `main` にする。
7. このsetup PRを `main` へmergeする。
8. Zenn DashboardのDeploy履歴で同期成功を確認する。

Zennは登録branchへのpushをトリガーに同期します。初回は **Zenn連携を先に完了し、その後setup PRをmergeする** 順番にします。

## 記事

Zenn記事はRepository root直下の `articles/<slug>.md` に置きます。

```yaml
---
title: "記事タイトル"
emoji: "🔐"
type: "tech"
topics: ["typescript", "openai"]
published: false
---
```

- `published: false`: 下書き
- `published: true`: 公開
- `published_at`: 必要な場合のみ公開予約日時をJSTで指定
- ファイル名がslugになるため、公開後は原則変更しない

新規記事:

```bash
npm run zenn:new:article -- --slug <12-50文字のslug>
```

## 本

本はZenn公式形式で管理します。

```text
books/
└─ <book-slug>/
   ├─ config.yaml
   ├─ cover.png          # 任意
   ├─ introduction.md
   └─ chapter-01.md
```

`config.yaml` の基本形:

```yaml
title: "本のタイトル"
summary: "本の紹介文"
topics: ["typescript", "architecture"]
published: false
price: 0
chapters:
  - introduction
  - chapter-01
```

各chapter:

```yaml
---
title: "チャプタータイトル"
---
```

新規本:

```bash
npm run zenn:new:book -- --slug <12-50文字のslug>
```

公開前は `config.yaml` の `published: false` を維持し、公開PRで `true` にします。

## スクラップ

スクラップはZennのGitHub同期対象ではありません。

Repository側では `scraps/<slug>.md` を原稿・履歴・バックアップとして使います。`templates/zenn-scrap.md` をコピーして作成します。

```text
scraps/
└─ <slug>.md
```

運用:

1. Repositoryで原稿・URL・追記履歴を管理する。
2. Zenn Web UIでスクラップを作成する。
3. Zennへ追記した内容を必要に応じてRepository側にも反映する。
4. ZennからexportしたscrapをバックアップとしてRepositoryへ保存してもよい。

**GitHubへpushしてもスクラップはZennへ自動投稿・更新されません。**

## Preview

初回:

```bash
npm install
```

記事・本をPreview:

```bash
npm run zenn:preview
```

スクラップはZenn CLIのGitHub同期対象外なので、Web UIで確認します。

## 公開フロー

### 記事

1. `main` から記事branchを作る。
2. `articles/<slug>.md` を `published: false` で作成・編集する。
3. `npm run zenn:preview` で確認する。
4. Source Repositoryの最新状態を再確認する。
5. 公開するPRで `published: true` にする。
6. `main` へmergeする。
7. Zenn DashboardのDeploy履歴を確認する。
8. 公開URLを `ideas/published.md` 等へ記録する。

### 本

記事と同様にPRで管理し、公開時だけ `books/<book-slug>/config.yaml` の `published` を `true` にします。

### スクラップ

Repositoryで下書き・履歴を管理したうえで、Zenn Web UIから作成・更新します。公開URLはRepository側にも記録します。

## Repository構成

```text
tech-writing/
├─ articles/
│  ├─ <zenn-article-slug>.md       # Zenn記事: deploy対象
│  └─ <common-article-slug>/       # Qiita等の元原稿・notes
├─ books/                          # Zenn本: deploy対象
│  └─ <book-slug>/
│     ├─ config.yaml
│     └─ <chapter-slug>.md
├─ scraps/                         # Git管理のみ。Zenn deploy対象外
├─ templates/
│  └─ zenn-scrap.md
└─ docs/
   └─ ZENN_GITHUB_DEPLOY.md
```

## 注意点

- Secret / Token / API Key / private URLを記事・本・スクラップ・Issue / PRへ記載しない。
- commit messageに `[ci skip]` または `[skip ci]` があるとZenn Deployがskipされるため、公開commitでは使わない。
- 記事や本のslug変更は別コンテンツ扱いになるため、公開後は変更しない。
- Repositoryからファイルを削除しただけではZenn上のコンテンツ削除は完了しない。Dashboard側でも削除する。
- GitHub Appには必要なRepositoryだけを許可する。

## 公式ドキュメント

- GitHub連携: https://zenn.dev/zenn/articles/connect-to-github
- 途中からGitHub連携: https://zenn.dev/zenn/articles/setup-zenn-github-with-export
- Zenn CLI: https://zenn.dev/zenn/articles/zenn-cli-guide
- Scraps: https://zenn.dev/zenn/articles/about-zenn-scraps
