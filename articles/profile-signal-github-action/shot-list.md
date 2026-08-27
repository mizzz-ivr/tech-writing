# Shot List — Profile Signal Standalone OSS / v0.4.0

Qiita #3用。

## 方針

画像は**3枚だけ**使う。

GitHubプロフィール全景は縦長すぎるため掲載せず、本文から実プロフィールへ直接誘導する。

```text
https://github.com/mizzz-ivr
```

Release CIのスクリーンショットも使わない。CIでZIPの展開smoke testをしていることは本文で短く説明する。

## 採用3枚

### 02. `02-standalone-repository.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal
```

見せたいもの:

- root tree
- `.github/`
- `.profile-signal/`
- `distribution/`
- `docs/`
- `examples/sample-profile/`
- `release-notes/`
- `scripts/`
- `tests/`

目的:

Standalone OSSとして独立したRepositoryになっていることを見せる。

### 04. `04-release-v0.4.0.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0
```

見せたいもの:

- `Profile Signal v0.4.0`
- `Latest`
- Release Notes冒頭
- Assets

目的:

Standalone RepositoryからRelease ZIPを正式配布していることを見せる。

### 05. `05-sample-profile.png`

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal/tree/main/examples/sample-profile
```

見せたいもの:

- `Profile Signal — Sample Profile`
- `Sample output only`
- `LIVE SIGNAL`
- `TODAY`
- `CURRENT FOCUS`
- `DEV PULSE`

目的:

導入後の出力イメージを、実ユーザーのActivityに依存せず見せる。

## 不採用

- Profile overview screenshot
- Release workflow / CI screenshot
- Consumer installed tree screenshot
- v0.2.0 Release screenshot
- test用tree screenshot

## Qiita placeholder mapping

```text
02-standalone-repository.png
→ <!-- QIITA_IMAGE: 02-standalone-repository.jpg -->

04-release-v0.4.0.png
→ <!-- QIITA_IMAGE: 04-release-v0.4.0.jpg -->

05-sample-profile.png
→ <!-- QIITA_IMAGE: 05-sample-profile.jpg -->
```

## Safety check

- [ ] Token / Secretなし
- [ ] Private Repositoryなし
- [ ] Authorization headerなし
- [ ] 公開GitHub Repositoryだけを使用
- [ ] 内部管理用Issue / PR情報を不要に映さない
