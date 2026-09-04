# Shot List — Profile Signal Standalone OSS / v0.4.0

Qiita #3用。

## 方針

画像は**2枚だけ**使う。

GitHubプロフィール全景は縦長すぎるため掲載せず、本文から実プロフィールへ直接誘導する。

```text
https://github.com/mizzz-ivr
```

Release CIとv0.4.0 Releaseページのスクリーンショットも使わない。Release ZIPやsmoke testについては本文とリンクだけで説明する。

## 採用2枚

### 02. Standalone Repository

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal
```

Qiita image:

```markdown
![IMG_3770.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4394245/a0ce3241-e6a0-44ce-89dc-bd2724ce7b84.jpeg)
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

### 05. Sample Profile

撮影場所:

```text
https://github.com/mizzz-ivr/profile-signal/tree/main/examples/sample-profile
```

Qiita image:

```markdown
![IMG_3774.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4394245/bc017304-a056-4bc1-9096-436fc4177385.jpeg)
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
- v0.4.0 Release screenshot
- Consumer installed tree screenshot
- v0.2.0 Release screenshot
- test用tree screenshot

## Safety check

- [x] Token / Secretなし
- [x] Private Repositoryなし
- [x] Authorization headerなし
- [x] 公開GitHub Repositoryだけを使用
- [x] 内部管理用Issue / PR情報を不要に映さない
