# Article ID / File Naming

## 目的

記事タイトルだけに依存せず、Repository上で記事を日付順・用途別・状態別に見つけやすくする。

## 新規記事の基本形式

共通原稿・note原稿は次の形式で作成する。

```text
articles/<lifecycle>/YYMMDD-<slug>/article.md
```

`<lifecycle>` は次のいずれか。

```text
draft
review
published
old
```

例:

```text
articles/draft/260827-engineer-thinking-place/article.md
articles/review/260901-ai-role-of-engineer/article.md
articles/published/261005-personal-dev-management/article.md
```

Lifecycleの意味と移動ルールは [Article Lifecycle Directories](./ARTICLE_LIFECYCLE.md) を参照する。

## `YYMMDD` の意味

- JSTで記事の執筆を開始した日を使う
- 公開日ではない
- 公開日が変わってもArticle IDは変更しない

## slug

- 英小文字・数字・hyphenを基本とする
- 内容が分かる短い名前にする
- タイトル全文をローマ字化しない
- タイトル変更後も原則としてslugを変更しない

lifecycle directoryを除いた記事フォルダ名を**安定したArticle ID**として扱う。

たとえば、次の3つは同じArticle IDである。

```text
articles/draft/260901-example/article.md
articles/review/260901-example/article.md
articles/published/260901-example/article.md
```

## 既存記事

既存Article IDは一括renameしない。

folderをlifecycle directory配下へ移動しても、Article ID部分は維持する。

理由:

- Writing Analyticsのslugを維持するため
- source / social / metrics等の参照を不必要に壊さないため
- 公開済み記事の履歴追跡を維持するため

新規記事は `YYMMDD-<slug>` を推奨するが、既存Article IDはそのまま利用する。

## 媒体別

### note / 共通原稿

```text
articles/<lifecycle>/YYMMDD-<slug>/article.md
```

### Qiita

Qiita CLIのcanonical sourceは引き続き:

```text
public/<qiita-article-slug>.md
```

共通原稿を別に持つ場合は `articles/<lifecycle>/YYMMDD-<slug>/article.md` を使う。

### Zenn

Zenn GitHub Deployのcanonical articleは引き続き:

```text
articles/<zenn-article-slug>.md
```

Zenn側のslug/filename制約を優先し、Zenn canonicalはlifecycle directoryへ移動しない。

共通notesや検証資料を別に持つ場合だけ、対応するlifecycle folderへ置く。

## 探し方

執筆中の記事:

```text
articles/draft/*/article.md
```

公開準備中の記事:

```text
articles/review/*/article.md
```

公開済みの記事:

```text
articles/published/*/article.md
```

中止・統合済みの記事:

```text
articles/old/*/article.md
```

記事タイトルが変わっても、Article IDは原則固定する。
