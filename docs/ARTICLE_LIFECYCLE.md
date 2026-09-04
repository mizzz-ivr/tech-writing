# Article Lifecycle Directories

## 目的

共通原稿・note原稿・Qiita用の補助原稿を、執筆状態ごとに見つけやすくする。

Zenn GitHub Deployのcanonical articleはZennの仕様を優先し、`articles/<slug>.md` を直下に維持する。

## Directory

```text
articles/
├── draft/       # 執筆中
├── review/      # 内容が固まり、レビュー・公開準備中
├── published/   # 公開済み
├── old/         # 中止・不要・置き換え済み。Writing Analytics対象外
└── <slug>.md    # Zenn canonical。lifecycle directoryへ移動しない
```

共通原稿の基本形:

```text
articles/<lifecycle>/YYMMDD-<slug>/article.md
```

既存のArticle IDはfolderを移動しても変更しない。

## Lifecycle rule

### `draft/`

- front matter: `status: draft`
- まだ構成・本文・fact checkが動く記事
- 公開canonicalが別にある場合も、公開準備前はここに置く

### `review/`

- front matter: `status: review`
- 本文が概ね完成し、レビュー・公開前確認を行う記事
- fact check、画像、公開先metadata等の最終確認を行う

### `published/`

- front matter: `status: published`
- Qiita / Zenn / note等で公開済みの共通原稿・補助資料
- 公開URLと公開日は `ideas/published.md` でも記録する

### `old/`

- 中止した記事
- 別記事へ統合され、今後更新しない記事
- 検証前提が崩れ、再利用予定もない記事
- Writing Analyticsのactive article universeから除外する

`old/` への移動は「古いから」だけでは行わない。公開済みで古い記事は `published/` のまま保持する。

## Zenn canonical

Zenn GitHub Deployでは以下をcanonicalとして使うため、lifecycle directoryへ移動しない。

```text
articles/<zenn-slug>.md
```

必要なnotesや検証資料だけを、対応するlifecycle folderへ置いてよい。

例:

```text
articles/ai-runtime-safety-boundary.md
articles/published/ai-runtime-safety-boundary/notes.md
```

## 状態変更

原稿の状態が変わったら、front matterとfolderを同じPRで変更する。

```text
draft → review → published
          ↘ old
 draft ───→ old
```

Writing Analyticsは `draft/`, `review/`, `published/` の `*/article.md` を追跡し、`old/` は集計しない。
