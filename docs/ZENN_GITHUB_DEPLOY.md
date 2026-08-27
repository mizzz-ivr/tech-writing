# Zenn GitHub Deploy

`mizzz-ivr/tech-writing` をZennのGitHub連携リポジトリとして使うための運用手順です。

## 方針

- Zennの同期ブランチは `main`
- Zenn公開対象はRepository rootの `articles/<slug>.md`
- 下書きは `published: false`
- 公開は `published: true` へ変更したPRを `main` へmergeすることで行う
- `articles/<slug>/` はnotesや媒体共通の補助資料を置く場所として残せるが、Zennの公開本文は置かない
- Secret / Token / API Keyは記事・Front Matter・GitHub Issue / PRへ記載しない

## 初回セットアップ

1. Zennへログインし、`https://zenn.dev/dashboard/deploys` を開く。
2. 「リポジトリを連携」を選ぶ。
3. GitHub AppのRepository accessは `Only select repositories` を選択する。
4. `mizzz-ivr/tech-writing` だけを選択して `Install & Authorize` する。
5. Zennのリポジトリ設定で同期対象ブランチを `main` にする。
6. 連携後に、このRepositoryのZenn対応PRを `main` へmergeする。
7. Zenn Dashboardのデプロイ履歴で成功を確認する。

Zenn公式仕様では、登録ブランチに変更がpushされると同期が開始されます。連携前に存在していたファイルだけでは初回同期が走らない場合があるため、**Repository連携を先に完了し、その後にsetup PRをmergeする**順番を推奨します。

## 記事ファイル

Zenn記事は次の形式で配置します。

```text
articles/
├─ ai-runtime-safety-boundary.md   # Zenn同期対象
├─ ai-runtime-safety-boundary/
│  └─ notes.md                     # 執筆メモ。Zenn同期対象外
└─ other-article/
   └─ article.md                   # Qiita等の媒体共通原稿。Zenn同期対象外
```

Front MatterはZenn形式にします。

```yaml
---
title: "記事タイトル"
emoji: "🔐"
type: "tech"
topics: ["typescript", "openai"]
published: false
---
```

`slug` はファイル名です。公開後に変更すると別記事になるため、公開前に確定します。

## ローカルPreview

初回のみ依存関係をインストールします。

```bash
npm install
```

Preview:

```bash
npm run zenn:preview
```

新規記事をCLIで作る場合:

```bash
npm run zenn:new -- --slug <12-50文字のslug>
```

生成された `articles/<slug>.md` は、公開準備が完了するまで `published: false` を維持します。

## 公開フロー

1. `main` から記事用branchを作る。
2. `articles/<slug>.md` を編集する。
3. `published: false` のままPRを作り、内容とZenn Previewを確認する。
4. 公開直前にSource Repositoryの最新状態を再確認する。
5. `published: true` に変更する。
6. PRを `main` へmergeする。
7. Zenn Dashboardのデプロイ履歴を確認する。
8. 公開URLをfront matterとは別のRepository管理情報（`ideas/published.md` など）へ記録する。

Zenn側の公開URLは `https://zenn.dev/<username>/articles/<slug>` です。

## 注意点

- Zennが同期するのは `articles` 直下のMarkdownです。`articles/<slug>/article.md` はZenn記事として扱いません。
- Zennアカウントに連携できるRepository数には上限があります。GitHub Appでは必要なRepositoryだけを許可します。
- commit messageに `[ci skip]` または `[skip ci]` が入っているとZenn deployがskipされるため、公開・更新commitでは使いません。
- Zenn上で一度作成したslugは変更しません。
- 記事削除はRepositoryからファイルを消すだけでは完了しないため、Zenn Dashboard側の投稿管理も確認します。

## 公式ドキュメント

- GitHub連携: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI導入: https://zenn.dev/zenn/articles/install-zenn-cli
- Zenn CLI: https://zenn.dev/zenn/articles/zenn-cli-guide
- slug: https://zenn.dev/zenn/articles/what-is-slug
