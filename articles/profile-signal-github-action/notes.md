# Notes — Profile Signal Standalone OSS / Release / Wiki

## Article focus

単にComposite Actionの書き方を説明する記事にはしない。

自分用のGitHub Profile generatorを、**Standalone OSS Repository + Release ZIP + local runtime**として配布できる形へ変えた実体験を中心にする。

外部Repositoryから `uses: owner/repo@v1` で直接呼ぶモデルは採用しない。

## Source of Truth — 2026-08-28 JST

### OSS本体

- Repository: `mizzz-ivr/profile-signal`
- current release: `v0.4.0`
- asset: `profile-signal-v0.4.0.zip`
- GitHub Wiki: standalone Repository側で公開・自動同期
- root MIT License
- 8公式Preset
- public-only / 標準PAT・API Key不要

### Consumer / Live Demo

- Repository: `mizzz-ivr/mizzz-ivr`
- Profile Signal本体のSource of Truthではない
- installed `.profile-signal` runtimeをDogfooding
- 個人README / 画像 / ScreenshotはStandalone OSSのMIT対象として扱わない

## Release history relevant to article

### v0.2.0

- YAML Preset Registry
- 8 Presetへ拡張

### v0.3.0

- `mizzz-ivr/profile-signal` へStandalone OSS移行
- runtime / tests / Release / Wiki Sourceを分離
- `mizzz-ivr/mizzz-ivr` はConsumer / Live Demoへ縮小

### v0.4.0

- Latest Signals lightweight runtime追加
- distributionへ `profile-signal-stream.yml` を追加
- default cadence:
  - Full refresh: 3時間
  - Latest Signals: 30分
- lightweight対象:
  - LIVE SIGNAL
  - CURRENT FOCUS
  - ACTIVITY STREAM
- CI / History / Health等の重いstateを保持
- live-facing stateに実質変更がなければcommitしない

## Distribution decision

推奨:

```text
mizzz-ivr/profile-signal
        ↓
GitHub Release ZIP
        ↓
利用者の GitHub Profile Repository
        ↓
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
.github/workflows/profile-signal-stream.yml
        ↓
uses: ./.profile-signal
```

Release builderがpackageする主なファイル:

- `.profile-signal/**`
- `.github/profile-signal.yml`
- `.github/workflows/profile-signal.yml`
- `.github/workflows/profile-signal-stream.yml`
- `PROFILE_SIGNAL_INSTALL.md`
- `PROFILE_SIGNAL_VERSION`

## Preset

- minimal
- standard
- full
- terminal
- compact
- developer
- activity
- oss

## Scheduler note

Consumer `mizzz-ivr/mizzz-ivr` ではlive-facing signalをより短い間隔でDogfoodingする設定を試しているが、記事では**v0.4.0配布物のdefault 30分**を仕様として書く。

2026-08-26〜27 UTCにGitHub Actions trigger/dispatch障害が公式に発生。Consumer側の5分schedule acceptanceは未完了でIssue #52管理中。

記事ではGitHub Actions scheduleをリアルタイム保証として表現しない。

## Screenshot selection — v0.4.0へ撮り直す

継続利用候補:

1. `01-profile-overview.jpeg`
   - 現在のProfile表示として内容に問題がなければ再利用

新規撮影:

2. `02-standalone-repository.png`
   - `mizzz-ivr/profile-signal` root / Latest Release
3. `03-release-package-ci-success.png`
   - standalone Repositoryのv0.4.0 Release workflow success
4. `04-release-v0.4.0.png`
   - v0.4.0 Release + ZIP asset
5. `05-installed-repository.png`
   - Consumer側 `.profile-signal/` / config / workflow配置

古いv0.2.0 Release画像は記事から外す。

## Before publish

- [x] Qiita #2公開
- [x] 第3弾からQiita #2へリンク
- [x] Release ZIP配布モデルへ記事を変更
- [x] Standalone OSS Repository移行完了
- [x] v0.4.0 Release公開
- [x] v0.4.0 ZIP asset確認
- [x] GitHub Wiki standalone移行・同期確認
- [x] root MIT License確認
- [x] YAML Preset Registry / 8公式Preset確認
- [x] article本文をv0.4.0へ追従
- [ ] v0.4.0基準Screenshotを撮影 / 選定
- [ ] Qiitaへ画像Upload
- [ ] Qiita image Markdownをplaceholderへ反映
- [ ] Qiita Preview / mobile preview
- [ ] 公開直前に`mizzz-ivr/profile-signal` main / Releaseを再確認
- [ ] 公開
- [ ] `ideas/published.md` とfront matterへ公開URL反映

## Tags

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
