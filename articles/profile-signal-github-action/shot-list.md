# Shot List — Profile Signal Release / Wiki / Preset distribution

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

### 02. Profile Signal release package CI success

見せたいもの:

- `Profile Signal release` workflow run #11
- `Build release archive` success
- `Smoke test extracted install` success
- `Validate installed workflow staging without assets` success
- `Publish GitHub Release` success
- Secret / Tokenが映らない範囲

目的:

- Release ZIPを作っただけではなく、clean fixtureへ展開して実行し、実Releaseまで自動発行できたことを示す

### 03. GitHub Release `v0.2.0`

見せたいもの:

```text
Profile Signal v0.2.0
profile-signal-v0.2.0.zip
```

加えて日本語Release Notesと、新Presetが見える範囲。

目的:

- 実際の配布導線を示す
- Releaseページが日本語で案内されていることを示す
- `compact / developer / activity / oss` のPreset追加まで含む現在の配布版を見せる

### 04. Release ZIP導入後のRepository tree

見せたい構成:

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
README.md
```

可能なら `.profile-signal/presets/` も展開し、8Presetが見える状態にする。

Workflowの次の部分はコードブロックでもよい。

```yaml
uses: ./.profile-signal
```

目的:

- 外部Action呼び出しではなく、利用者自身のProfile Repository内で完結することを示す

## Useful / Optional

### 05. GitHub Wiki

見せたいもの:

- Wiki Home
- Installation / Configuration / Presets / License のSidebar

目的:

- Release ZIPだけを置くのではなく、導入・設定・Preset・Licenseの継続ドキュメントを用意したことを示す

記事ではスクリーンショットを省略し、Wiki URLへのリンクだけでもよい。

### 06. YAML Preset Registry

見せたいもの:

```text
.profile-signal/presets/
├─ minimal.yml
├─ standard.yml
├─ full.yml
├─ terminal.yml
├─ compact.yml
├─ developer.yml
├─ activity.yml
└─ oss.yml
```

Screenshotよりコードブロックで十分なら省略。

目的:

- Profile templateを追加するとき、runtimeへPreset名ごとの分岐を増やさずYAML追加中心で拡張できることを示す

### 07. Config / Preset

```yaml
preset: developer
theme: signal
```

Screenshotよりコードブロックで十分なら省略。

### 08. Marker auto insert before / after

導入前の短いREADMEと、初回実行後のREADME diff。

### 09. Fork導線

Forkは補助導線なので、スクリーンショットは必須ではない。

記事では:

- Release ZIP = 推奨
- Fork = Showcase全体を参考にしたい人向け

と文章で説明すれば十分。

## 不要なScreenshot

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
- [ ] Wiki / Release画面に不要なAccount情報が映っていない
