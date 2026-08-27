# Shot List — Profile Signal Standalone OSS / v0.4.0

Qiita #3用。

## 採用予定5枚

### 01. `01-profile-overview.jpeg`

用途:

- 冒頭の完成形プレビュー
- Consumer / Live Demoとして実際にProfile Signalを使っていることを示す
- 内容が現在のProfileと大きくズレていなければ既存画像を再利用可能

確認:

- Widget詳細はQiita #2と重複させない
- 縦長の場合は縮小表示
- 直後にGitHubプロフィール本体へのリンクを置く

### 02. `02-standalone-repository.png`

撮影対象:

- `mizzz-ivr/profile-signal` Repository root
- `.profile-signal/`
- `distribution/`
- `docs/`
- `release-notes/`
- `scripts/`
- `tests/`
- Latest Release `Profile Signal v0.4.0`

目的:

- OSS本体が個人Profile Repositoryから独立したことを示す
- `mizzz-ivr/profile-signal` がSource of Truthであることを視覚的に伝える

### 03. `03-release-package-ci-success.png`

撮影対象:

- standalone `mizzz-ivr/profile-signal` のv0.4.0 Release workflow
- Release ZIP build / smoke test / publishがsuccessしている画面

本文側で説明するポイント:

- Release archive生成
- clean fixtureへ展開してruntime smoke test
- workflow staging validation
- GitHub Release publish

目的:

- ZIPを作るだけでなく、配布物単体で動作確認していることを示す

### 04. `04-release-v0.4.0.png`

撮影対象:

- `Profile Signal v0.4.0`
- Latest
- 日本語Release Notesの主要部分
- Assets `profile-signal-v0.4.0.zip`

目的:

- standalone Repositoryから正式Releaseしていることを示す
- v0.4.0でLatest Signals lightweight refreshが追加されたことを見せる

Release URL:

```text
https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0
```

### 05. `05-installed-repository.png`

撮影対象:

Consumer `mizzz-ivr/mizzz-ivr` 側で、少なくとも以下が分かる構図。

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/update-readme.yml
```

可能ならinstalled runtimeが利用者Repository内に存在することを中心にする。

注意:

- Consumerは配布templateそのままではなくDogfooding用custom workflowを使っているため、「配布ZIPを展開した標準tree」と誤解させない
- 標準Release ZIPの構成は本文コードブロックで示す

## 本文でコード表示するもの

### Release ZIP構成

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
.github/workflows/profile-signal-stream.yml
PROFILE_SIGNAL_INSTALL.md
PROFILE_SIGNAL_VERSION
```

### Preset Registry

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

## 不採用

### v0.2.0 Release画像

旧記事用の以下は使わない。

- `03-release-v0.2.0-top.png`
- `04-release-v0.2.0-assets.png`

理由:

- 最新Releaseがv0.4.0
- Release Source of Truthが `mizzz-ivr/profile-signal` へ移行済み
- `mizzz-ivr/mizzz-ivr/releases` を最新配布元と誤認させる

### `test-profile-signal-v0.2.0` tree

引き続き不採用。

理由:

- 作業用directoryに見える
- 正式な導入構造と誤解されやすい

## Optional

### GitHub Wiki

スクリーンショットは必須にしない。

記事中では以下へ誘導する。

```text
https://github.com/mizzz-ivr/profile-signal/wiki
```

### Config

```yaml
preset: developer
theme: signal
```

コードブロックで十分。

## Qiita placeholder mapping

```text
01-profile-overview.jpeg
→ <!-- QIITA_IMAGE: 01-profile-overview.jpg -->

02-standalone-repository.png
→ <!-- QIITA_IMAGE: 02-standalone-repository.jpg -->

03-release-package-ci-success.png
→ <!-- QIITA_IMAGE: 03-release-package-ci-success.jpg -->

04-release-v0.4.0.png
→ <!-- QIITA_IMAGE: 04-release-v0.4.0.jpg -->

05-installed-repository.png
→ <!-- QIITA_IMAGE: 05-installed-repository.jpg -->
```

QiitaへUploadした際に生成されたMarkdownを対応placeholderへ置換する。

## Safety check

撮影時に確認する:

- [ ] Token / Secretなし
- [ ] Private Repositoryなし
- [ ] Authorization headerなし
- [ ] 公開GitHubプロフィール / 公開Repositoryの範囲
- [ ] Issue / PRなど記事読者に不要な内部管理情報を映さない
- [ ] Consumer固有の個人情報・不要な管理情報を映さない
