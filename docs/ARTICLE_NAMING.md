# Article ID / File Naming

## 目的

記事タイトルだけに依存せず、Repository上で記事を日付順・用途別に見つけやすくする。

## 新規記事の基本形式

共通原稿・note原稿は次の形式で作成する。

```text
articles/YYMMDD-<slug>/article.md
```

例:

```text
articles/260827-engineer-thinking-place/article.md
articles/260901-ai-role-of-engineer/article.md
articles/261005-personal-dev-management/article.md
```

## `YYMMDD` の意味

- JSTで記事の執筆を開始した日を使う
- 公開日ではない
- 公開日が変わっても記事IDは変更しない

## slug

- 英小文字・数字・hyphenを基本とする
- 内容が分かる短い名前にする
- タイトル全文をローマ字化しない
- タイトル変更後も原則としてslugを変更しない

記事フォルダ名全体を**安定したArticle ID**として扱う。

## 既存記事

既存の `articles/<slug>/article.md` は一括renameしない。

理由:

- Writing Analyticsのslugが変わる
- source / social / metrics等の参照に影響する可能性がある
- 公開済み記事の履歴追跡を不必要に壊さない

新規記事から `YYMMDD-<slug>` を適用する。

## 媒体別

### note / 共通原稿

```text
articles/YYMMDD-<slug>/article.md
```

### Qiita

Qiita CLIのcanonical sourceは引き続き:

```text
public/<qiita-article-slug>.md
```

共通原稿を別に持つ場合は `articles/YYMMDD-<slug>/article.md` を使う。

### Zenn

Zenn GitHub Deployのcanonical articleは引き続き:

```text
articles/<zenn-article-slug>.md
```

Zenn側のslug/filename制約を優先し、共通原稿フォルダのArticle IDとは分離する。

## 探し方

日付で探す:

```text
articles/260827-*
```

内容で探す:

```text
articles/*-engineer-*
```

記事タイトルが変わっても、Article IDは原則固定する。
