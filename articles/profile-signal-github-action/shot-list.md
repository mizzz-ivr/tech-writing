# Shot List — Profile Signal Standalone OSS / v0.4.0

Qiita #3用。

## 方針

GitHubプロフィール全景は縦長すぎて記事内では読めないため、**スクリーンショットを掲載しない**。

本文から実プロフィールへ直接誘導する。

```text
https://github.com/mizzz-ivr
```

記事で使う画像は `02`〜`05` の4枚に絞る。

## 採用4枚

### 02. `02-standalone-repository.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal
```

撮影範囲:

- Repository名 `mizzz-ivr/profile-signal`
- rootのファイルtree
- `.github/`
- `.profile-signal/`
- `distribution/`
- `docs/`
- `release-notes/`
- `scripts/`
- `tests/`
- 右側のAbout / Releasesは無理なく入る場合だけ含める

目的:

- OSS本体が個人Profile Repositoryから独立したことを示す
- `mizzz-ivr/profile-signal` がSource of Truthであることを視覚的に伝える

構図:

- browser chromeは最小限
- treeの文字が読める倍率を優先
- README本文までは入れなくてよい

### 03. `03-release-package-ci-success.png`

撮影場所:

`mizzz-ivr/profile-signal` → **Actions** → `Profile Signal release` → `v0.4.0` を発行したsuccess run。

撮影範囲:

- Workflow名
- Success状態
- Release package validation / smoke testのjob
- GitHub Release publishのjob

本文側で説明するポイント:

- Release archive生成
- clean fixtureへ展開してruntime smoke test
- installed workflow staging validation
- GitHub Release publish

目的:

- ZIPを作るだけでなく、配布物単体をCIで検証してからReleaseしていることを示す

注意:

- 詳細log本文は不要
- Token / Authorization header /不要なAccount情報が見える画面は使わない

### 04. `04-release-v0.4.0.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0
```

撮影範囲:

- `Profile Signal v0.4.0`
- `Latest` badge（表示される場合）
- Release Notesの冒頭数行
- **Assets** の `profile-signal-v0.4.0.zip`

目的:

- Standalone Repositoryから正式Releaseしていることを示す
- v0.4.0の配布物がZIPとして存在することを見せる

構図:

- 可能なら1枚でReleaseタイトル〜Assetsまで収める
- 文字が潰れる場合は本文を少し縮めても、Assets名が読めることを優先する
- 上下2枚の連結画像にはしない

### 05. `05-sample-profile.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal/tree/main/examples/sample-profile
```

`README.md` の**GitHubレンダリング表示**を撮る。Raw / Code表示は使わない。

撮影範囲:

- `Profile Signal — Sample Profile`
- `Sample output only` の注記
- `LIVE SIGNAL`
- `TODAY`
- `CURRENT FOCUS`
- `DEV PULSE` 上部まで

目的:

- 実Consumer Repositoryを見せずに、導入後の出力イメージを再現可能な形で見せる
- サンプル値が架空・固定であることを同じ画面で明示する
- OSS Repository内のサンプルなので、記事読者もそのまま開いて確認できる

注意:

- 下の `NOW BUILDING / ACTIVITY STREAM / DEV RECAP` まで1枚へ詰め込まない
- 全体はSample Profileページへのリンクで見てもらう

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

### Profile overview screenshot

使わない。

理由:

- Profile全体が縦長で記事幅へ収めると読めない
- Qiita #2ですでにWidget表示を扱っている
- 第3弾では実プロフィールURLへの直接誘導の方が情報量を保てる

### Consumer installed tree screenshot

使わない。

理由:

- ConsumerはDogfooding用custom workflowで、標準Release ZIPのtreeと完全一致しない
- `examples/sample-profile` の方が再現可能で誤解が少ない

### v0.2.0 Release画像

旧記事用の以下は使わない。

- `03-release-v0.2.0-top.png`
- `04-release-v0.2.0-assets.png`

理由:

- 最新Releaseがv0.4.0
- Release Source of Truthが `mizzz-ivr/profile-signal` へ移行済み

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
02-standalone-repository.png
→ <!-- QIITA_IMAGE: 02-standalone-repository.jpg -->

03-release-package-ci-success.png
→ <!-- QIITA_IMAGE: 03-release-package-ci-success.jpg -->

04-release-v0.4.0.png
→ <!-- QIITA_IMAGE: 04-release-v0.4.0.jpg -->

05-sample-profile.png
→ <!-- QIITA_IMAGE: 05-sample-profile.jpg -->
```

QiitaへUploadした際に生成されたMarkdownを対応placeholderへ置換する。

## Safety check

撮影時に確認する:

- [ ] Token / Secretなし
- [ ] Private Repositoryなし
- [ ] Authorization headerなし
- [ ] 公開GitHub Repositoryの範囲
- [ ] Issue / PRなど記事読者に不要な内部管理情報を映さない
- [ ] Sample Profileに実ユーザーの動的数値を混ぜない
