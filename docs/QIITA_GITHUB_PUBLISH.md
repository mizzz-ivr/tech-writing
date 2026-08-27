# Qiita GitHub Publish Runbook

## 目的

`tech-writing` でQiita記事をGitHub管理し、普段の運用を次の流れに統一します。

```text
branch
  ↓
public/<article>.md を編集
  ↓
Pull Request = 下書き・レビュー境界
  ↓
mainへmerge
  ↓
GitHub Actions
  ↓
Qiitaへ投稿・更新
```

Qiitaへの投稿・更新にはQiita公式の `@qiita/qiita-cli` と `increments/qiita-cli/actions/publish@v1` を使用します。独自のQiita API投稿処理は持ちません。

## Source of Truth

用途ごとの正本を分けます。

| 対象 | Source of Truth |
| --- | --- |
| Qiitaへ実際に投稿するMarkdown | `public/*.md` |
| 媒体共通の企画・notes・Writing Analytics用metadata | `articles/<slug>/article.md` |
| Qiita上の公開状態・記事ID | `public/*.md` のQiita CLI front matterとQiita |
| 実装・検証内容の事実確認 | 各開発Repository |
| 動的なIssue / PR / CI状態 | GitHub |

`articles/<slug>/article.md` と `public/*.md` は自動同期しません。Qiitaで公開する最終原稿は `public/*.md` をcanonicalな公開ソースとして扱います。

## 前提

### Qiita Personal Access Token

QiitaでPersonal Access Tokenを発行し、次の権限を付与します。

- `read_qiita`
- `write_qiita`

Token値はRepository、Issue、PR、Notion、記事本文へ記載しません。

### GitHub Repository Secret

RepositoryのActions Secretへ次の名前で登録します。

```text
QIITA_TOKEN
```

公開workflowと同期workflowはこのSecretだけを参照します。

## 初回セットアップ

既存Qiita記事は、手作業で `articles/<slug>/article.md` から `public/` へコピーしません。既存記事のQiita IDや現在のfront matterを保持するため、Qiita CLIから取得します。

1. Qiita GitHub Publish基盤のPRをmainへmergeする。
2. GitHub Repository Secret `QIITA_TOKEN` を設定する。
3. GitHub Actionsから `Sync Qiita articles` を手動実行する。
4. Workflowが `qiita pull` を実行する。
5. 差分があれば `sync/qiita-articles-<run-id>-<attempt>` branchを作成する。
6. Workflowが同期PRを作成する。Repository設定でGitHub ActionsからのPR作成が禁止されている場合は、branch pushまで成功扱いとし、Actions Summaryに表示されたリンクから手動PRを作成する。
7. `public/*.md` の `id`、`title`、`tags`、`private`、本文をQiita上の記事と照合する。
8. 問題がなければ同期PRをmainへmergeする。
9. `Publish Qiita articles` workflowが実行され、既存IDの記事として同期されることを確認する。

2026-08-27時点でRepository metadataから確認できる既存Qiita記事は次の3件です。初回同期PRでは少なくともこれらがQiita上の既存IDを保持していることを確認します。

| 記事 | Qiita item ID |
| --- | --- |
| AI開発エージェントを「Repository is the Source of Truth」で動かしたら個人開発がかなり変わった話 | `44cd3077d732eea1bf6e` |
| GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた | `73bd3a3874aa8adacc1a` |
| GitHubプロフィールをライブな開発ダッシュボードにしてみた | `b5cc51f17c9d9e69f630` |

初回同期で想定外の記事・限定共有記事が不足する場合は、`qiita.config.json` の `includePrivate` 設定とQiitaアカウントを確認します。現在は `includePrivate: false` です。

## 日常の執筆フロー

### 新規記事

ローカルでQiita CLIを使える場合は次のコマンドで雛形を作成できます。

```bash
npm install
npm run qiita:new:article -- <article-slug>
```

ローカルCLIは投稿の必須条件ではありません。`public/<article-slug>.md` を正しいQiita CLI front matterで作成し、GitHub経由でPRを作成しても運用できます。

新規記事の基本front matterはQiita CLIが生成する形式を維持します。

```yaml
---
title: 記事タイトル
tags:
  - GitHub
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
```

### プレビュー

ローカルでプレビューする場合:

```bash
npm install
npm run qiita:preview
```

デフォルトでは `http://localhost:8888` を使用します。

### PR

PRはQiita記事の下書き・レビュー境界です。

- `pull_request` eventではQiita publish workflowを起動しない。
- PR branch上で何度編集してもQiitaには反映しない。
- title / tags / private / body / Secret混入の有無をレビューする。
- 公開してはいけない記事をmain上へ置く必要がある場合は `ignorePublish: true` を使用する。

### 公開・更新

`public/**/*.md` がmainへmergeされると `.github/workflows/qiita-publish.yml` が起動します。

WorkflowはQiita公式Actionから `qiita publish --all` を実行します。Qiita CLIが `id` や `updated_at` 等を更新した場合、公式Actionがその差分をGitHub Actions botとしてmainへcommitします。

## Qiita側で記事を編集した場合

RepositoryとQiita Web UIを同時に編集すると競合しやすくなるため、通常はRepositoryから編集します。

Qiita Web UIで緊急修正した場合は、次のRepository編集より先に `Sync Qiita articles` workflowを実行し、生成された同期PRでQiita側の変更を取り込みます。

ローカルで行う場合:

```bash
npm run qiita:pull
```

Qiita CLIの通常の `pull` は、Qiita側で更新され、ローカル側に競合する変更がない記事を同期します。強制同期が必要な場合は、内容を失わないことを確認したうえでQiita CLIの `pull --force` を使用します。

## 削除

Qiita CLIから記事削除はできません。

`public/<article>.md` をRepositoryから削除しても、Qiita上の記事は削除されません。Qiita記事そのものを削除する場合はQiita Web UIで削除し、その後Repository側のファイルと公開記録を整理します。

削除操作は復旧可否を確認してから実施します。

## Rollback

### 誤った更新を公開した場合

1. 問題のcommitを特定する。
2. Repositoryでrevert用PRを作成する。
3. `public/*.md` の内容を直前の正常状態へ戻す。
4. mainへmergeする。
5. publish workflowでQiitaへ再反映されることを確認する。

Repositoryの履歴を残したままrollbackし、Qiita Web UIだけを手作業で過去状態へ戻す運用は避けます。

### 誤ってQiita記事自体を削除した場合

Qiita CLIでは削除復旧できません。Qiita側の仕様に従って復旧可否を確認し、復旧できない場合はRepositoryの原稿から新規記事として再作成します。この場合、Qiita item IDは変わる可能性があります。

## Security

- `QIITA_TOKEN` はGitHub Actions Secretでのみ管理する。
- Token値をRepository、ログ、Issue、PR、Notionへ貼らない。
- Token権限は `read_qiita` / `write_qiita` に限定する。
- Token漏えいが疑われる場合はQiitaで失効し、新しいTokenへrotateする。
- publish workflowは `contents: write` のみを要求する。
- sync workflowは同期branchとPR作成のため `contents: write` / `pull-requests: write` を要求する。
- 外部Fork由来PRではSecretを使用したpublish処理を実行しない。

## Workflow

### Publish Qiita articles

`.github/workflows/qiita-publish.yml`

- Trigger: `main` へのpush
- Path filter: `public/**/*.md`
- Manual trigger: 対応
- Qiitaへの書き込み: あり
- GitHubへのmetadata commit: Qiita公式Actionが必要時に実施

### Sync Qiita articles

`.github/workflows/qiita-sync.yml`

- Trigger: 手動のみ
- Qiitaからの取得: `qiita pull`
- mainへの直接push: しない
- 差分がある場合: 専用branchを作成してpushする
- GitHub ActionsからPR作成できる場合: 同期PRを自動作成する
- Repository設定でPR作成が禁止されている場合: workflowを失敗させずwarning + Actions Summaryへ手動PRリンクを出す
- 上記以外の `gh pr create` エラー: workflowをfailureにして異常を隠さない

Repository全体のActions権限を緩和しなくても同期を継続できるようにし、PR作成不可だけを既知のfallbackとして扱います。

## Troubleshooting

### `QIITA_TOKEN` がない / 認証エラー

Repository Secret名が正確に `QIITA_TOKEN` になっていること、Tokenが失効していないこと、`read_qiita` / `write_qiita` が付与されていることを確認します。

### 同期PRが作成されない

- `Sync Qiita articles` workflowのログを確認する。
- `No changes` なら同期差分はありません。
- Actions Summaryに `Qiita sync branch created` が表示された場合、branch pushは成功済みです。表示された `Open a pull request` リンクからPRを作成します。
- `GitHub Actions is not permitted to create or approve pull requests` は既知のfallback対象であり、branch push成功後はworkflow自体をfailureにしません。
- それ以外のPR作成エラーはworkflow failureとして調査します。

### 既存記事が新規記事として作られそう

publishを止め、`public/*.md` の `id` を確認します。既存記事の初回取り込みは手動コピーではなく `qiita pull` を使用します。

### QiitaとRepositoryで本文が食い違う

どちらを正とするかを決めずに `--force` を実行しません。通常運用ではRepositoryを編集元とし、Qiita Web UIで変更した場合のみ先にsync workflowでRepositoryへ取り込みます。

## Version baseline

2026-08-27時点の導入基準:

- `@qiita/qiita-cli`: `1.10.0`
- Node.js: Qiita CLI要件を満たす22系（workflowでは `22.23.2`）
- Publish Action: `increments/qiita-cli/actions/publish@v1`

Qiita CLIやActionを更新する場合は、公式Repository / Release / READMEを確認してからversionを更新します。
