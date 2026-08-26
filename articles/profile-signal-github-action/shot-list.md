# Shot List — Profile Signal Release / Fork distribution

Qiita #3用。

## Required

### 01. 完成形Profile overview

保存済み:

- `IMG_3769.jpeg`

用途:

- 冒頭で「最終的に何が動いているか」を見せる完成形プレビュー

注意:

- 縦長なので記事本文へ原寸では貼らない
- 小さめのプレビューとして使う
- 直後にGitHubプロフィール本体へのリンクを置く
- 各Widgetの詳細画像は第2弾で既に見せているため、第3弾では重複させない

### 02. PR #24 Release package CI success

見せたいもの:

- `Profile Signal release` workflow
- `Build release archive` success
- `Smoke test extracted install` success
- Secret / Tokenが映らない範囲

目的:

- Release ZIPを作っただけではなく、clean fixtureへ展開して実行できたことを示す

### 03. GitHub Release `v0.1.0`

見せたいもの:

```text
Profile Signal v0.1.0
profile-signal-v0.1.0.zip
```

目的:

- 実際の配布導線を示す

### 04. Release ZIP導入後のRepository tree

見せたい構成:

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
README.md
```

可能ならWorkflowの次の部分も同じ画面またはコードブロックで示す。

```yaml
uses: ./.profile-signal
```

目的:

- 外部Action呼び出しではなく、利用者自身のProfile Repository内で完結することを示す

## Optional

### 05. Config / Preset

```yaml
preset: standard
theme: signal
```

Screenshotよりコードブロックで十分なら省略。

### 06. Marker auto insert before / after

導入前の短いREADMEと、初回実行後のREADME diff。

### 07. Fork導線

Forkは補助導線なので、スクリーンショットは必須ではない。

記事では:

- Release ZIP = 推奨
- Fork = Showcase全体を参考にしたい人向け

と文章で説明すれば十分。

## 不要になったScreenshot

外部Repositoryから:

```yaml
uses: mizzz-ivr/profile-signal@v1
```

と呼ぶ画面は不要。

今回の配布モデルでは採用しない。

## Safety

- [ ] Token / Secretなし
- [ ] Private Repositoryなし
- [ ] third-party notificationなし
- [ ] `GITHUB_TOKEN`値やAuthorization headerなし
- [ ] Release assetに個人READMEや秘密情報が含まれていない
