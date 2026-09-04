# note Publish Helper Runbook

## 目的

`tech-writing` で生成・編集したnote記事を、Repository管理用metadataを混ぜずにMarkdown本文としてクリップボードへコピーし、noteの新規投稿画面をすぐ開けるようにする。

noteへの公開自体はWeb Editorで行い、noteの認証情報や非公開APIには依存しない。

## Article ID / ファイル名

新規の共通原稿・note原稿は次の形式で作る。

```text
articles/<lifecycle>/YYMMDD-<slug>/article.md
```

通常は執筆開始時に `draft`、公開準備へ入ったら `review`、公開後は `published` へ移す。

例:

```text
articles/draft/260901-example/article.md
articles/review/260901-example/article.md
articles/published/260901-example/article.md
```

`YYMMDD` はJSTの執筆開始日。lifecycle directoryを除いたフォルダ名を安定したArticle IDとして扱い、タイトル変更後も原則renameしない。

詳細は [Article ID / File Naming](./ARTICLE_NAMING.md) と [Article Lifecycle Directories](./ARTICLE_LIFECYCLE.md) を参照する。

## 基本フロー

```text
articles/draft/YYMMDD-<slug>/article.md を生成・編集
  ↓
reviewへ移動してGit / PRでレビュー・履歴管理
  ↓
npm run note:publish -- articles/review/YYMMDD-<slug>/article.md
  ↓
Repository用YAML front matterを除外
  ↓
Markdown本文をクリップボードへコピー
  ↓
https://note.com/new を既定ブラウザで開く
  ↓
note Editorへ貼り付け・最終調整・公開
  ↓
公開後にarticles/published/へ移動
```

## コマンド

### Markdown本文だけコピー

```bash
npm run note:copy -- articles/review/YYMMDD-<slug>/article.md
```

指定した `article.md` の先頭にRepository管理用YAML front matterがある場合、そのfront matterだけを除外して本文をコピーする。

見出し、箇条書き、リンク、引用、code blockなどのMarkdown本文は文字列として維持する。

### note新規投稿画面を開く

```bash
npm run note:open
```

開くURL:

```text
https://note.com/new
```

### コピーしてそのままnoteを開く

通常はこちらを使う。

```bash
npm run note:publish -- articles/review/YYMMDD-<slug>/article.md
```

処理順:

1. Markdownファイルを読む
2. Repository用YAML front matterを除外する
3. Markdown本文をクリップボードへコピーする
4. `https://note.com/new` を既定ブラウザで開く
5. note Editorへ貼り付ける
6. 見出し画像・装飾・ハッシュタグ・公開設定をnote側で最終確認する
7. 公開後、Repository側のfront matterを `status: published` にして `articles/published/` へ移す

## OS対応

### Windows

PowerShell `Set-Clipboard` と `Start-Process` を使用する。

追加ツールは不要。

### macOS

- clipboard: `pbcopy`
- browser: `open`

### Linux

clipboardは利用可能なものを順番に使用する。

1. `wl-copy`
2. `xclip`
3. `xsel`

browserは `xdg-open` を使用する。

WSLではPowerShellが利用可能ならWindows側のclipboard / browserを優先する。

## Source of Truth

note記事の生成・編集・履歴管理はRepositoryをSource of Truthとする。

`note:publish` はRepositoryの内容をnoteへ自動投稿する機能ではない。クリップボードへのコピーと投稿画面への導線だけを提供する。

note上で公開後に本文を変更した場合は、必要な変更をRepository側にも反映し、Git上の最終原稿とnote公開内容が大きく乖離しない状態を維持する。

## front matter

Repository内の記事にはWriting Analytics等のためのfront matterを持つ場合がある。

```yaml
---
title: example
status: review
published:
  note: null
---
```

このmetadataはnote本文ではないため、`note:copy` / `note:publish` ではデフォルトで除外する。

front matterが `---` で開始しているのに単独行の終了delimiter `---` がない場合は、metadataを誤って公開することを避けるため処理を失敗させる。

## Security / Privacy

このhelperは以下を扱わない。

- note ID / Password
- Cookie / Session
- note API Token
- Browser automation
- 自動公開

記事本文だけをローカルのOS clipboardへ渡す。

機密情報、Secret、顧客情報、個人情報が本文に含まれていないことは公開前チェックで別途確認する。

## note Editorでの最終確認

Markdownをコピーした時点では公開完了ではない。

note側で最低限以下を確認する。

- タイトル
- 見出し・太字・箇条書き等の表示
- code block
- リンク
- 画像
- ハッシュタグ
- 無料 / 有料設定
- 公開範囲

noteはMarkdownファイルの直接importを前提にした投稿フローではないため、貼り付け後の見た目は必ずWeb Editorで確認する。

## Test

```bash
npm run note:test
```

テスト対象:

- Repository front matter除去
- Markdown本文保持
- front matter不正時のfail-safe
- UTF-8 / 日本語本文
- ファイル不存在
- `https://note.com/new` の導線

## 参考

- hitosee「AIとGitHub連携で実現するnote記事作成効率化フロー」
- note公式「note.com/newですぐに記事やつぶやきを書きはじめられます！」
