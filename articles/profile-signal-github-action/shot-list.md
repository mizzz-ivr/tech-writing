# Shot List — Profile Signal Release / Wiki / Preset distribution

Qiita #3用。

## 採用5枚

### 01. `01-profile-overview.jpeg`

元画像:

- `IMG_3769.jpeg`

用途:

- 冒頭の完成形プレビュー
- 縦長なので原寸ではなく縮小表示
- 直後にGitHubプロフィール本体へのリンクを置く
- Widget詳細は第2弾で見せているため、第3弾では重複させない

### 02. `02-release-package-ci-success.png`

見えているもの:

- `Profile Signal release #11`
- Status: Success
- `validate-package` success
- `release` success

本文側では、同run内で確認済みの以下も説明する。

- Build release archive
- Smoke test extracted install
- Validate installed workflow staging without assets
- Publish GitHub Release

目的:

- ZIP生成だけでなくclean fixture検証とRelease publishまで通っていることを示す

### 03. `03-release-v0.2.0-top.png`

見えているもの:

- `Profile Signal v0.2.0`
- Latest
- 日本語Release Notes上部

目的:

- v0.2.0を正式Releaseしていることを示す

### 04. `04-release-v0.2.0-assets.png`

見えているもの:

- MIT License説明
- GitHub Wikiへの導線
- Assets
- Profile Signal v0.2.0 ZIP asset

目的:

- 配布物・License・ドキュメントの導線を1枚で示す

Releaseページは03と04を画像編集で連結しない。

```text
03 Release上部
↓
本文説明
↓
04 Release下部
```

の順で置く。

全文はRelease URLへ誘導する。

### 05. `05-repository-root.png`

見えているもの:

- `.github/`
- `.profile-signal/`
- `distribution/`
- `docs/`
- `release-notes/`
- `scripts/`
- `tests/`
- Latest Release `Profile Signal v0.2.0`

目的:

- runtimeを利用者Repository内へ置く配布モデルを示す
- `.profile-signal/` と設定・WorkflowがRepository内で管理されることを説明する

Preset一覧はScreenshotではなく本文コードブロックで示す。

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

### `test-profile-signal-v0.2.0` tree

記事には使わない。

理由:

- 作業用directoryに見える
- `test file add` などのcommit messageが見える
- 展開物がflattenして見える
- `profile-signal (1).yml` など、正式な導入構造と誤解されやすい要素がある

配布構造の説明には05のRepository rootとコードブロックを使う。

## Optional

### GitHub Wiki

スクリーンショットは必須にしない。

記事中ではWiki URLへ誘導する。

### Config

```yaml
preset: developer
theme: signal
```

コードブロックで十分。

### Marker auto insert before / after

第3弾では必須にしない。

## Qiita placeholder mapping

```text
01-profile-overview.jpeg
→ <!-- QIITA_IMAGE: 01-profile-overview.jpg -->

02-release-package-ci-success.png
→ <!-- QIITA_IMAGE: 02-release-package-ci-success.jpg -->

03-release-v0.2.0-top.png
→ <!-- QIITA_IMAGE: 03-release-v0.2.0-top.jpg -->

04-release-v0.2.0-assets.png
→ <!-- QIITA_IMAGE: 04-release-v0.2.0-assets.jpg -->

05-repository-root.png
→ <!-- QIITA_IMAGE: 05-repository-root.jpg -->
```

QiitaへUploadした際に生成されたMarkdownを対応placeholderへ置換する。

## Safety check

今回採用する5枚について確認済み:

- [x] Token / Secretなし
- [x] Private Repositoryなし
- [x] `GITHUB_TOKEN`値やAuthorization headerなし
- [x] Release assetに個人READMEや秘密情報が含まれている表示なし
- [x] 公開GitHubプロフィール / 公開Repositoryの範囲
- [x] 不要なtest tree画像は除外
