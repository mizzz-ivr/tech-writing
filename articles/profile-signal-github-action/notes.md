# Notes — Profile Signal Standalone OSS / Release

## Article focus

Qiita #3では、実装詳細を網羅しない。

伝える内容は次の3点に絞る。

1. 自分用Profile generatorをStandalone OSSへ分離した
2. 外部ActionではなくRelease ZIP + local runtimeを選んだ
3. v0.4.0でFull refreshとLatest Signals refreshを分離した

詳細なPreset validator、Wiki同期、License境界、CI job構成は本文では深掘りしない。

## Source of Truth — 2026-08-28 JST

- OSS: `mizzz-ivr/profile-signal`
- Consumer / Live Demo: `mizzz-ivr/mizzz-ivr`
- Current Release: `v0.4.0`
- Asset: `profile-signal-v0.4.0.zip`
- public-only / 標準PAT・API Key不要
- 8 Preset

## Distribution

```text
mizzz-ivr/profile-signal
        ↓
GitHub Release ZIP
        ↓
<username>/<username>
        ↓
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
.github/workflows/profile-signal-stream.yml
```

Workflowは `uses: ./.profile-signal` でlocal runtimeを実行する。

## Release history used in article

### v0.3.0

- Standalone OSS Repositoryへ移行
- Consumer / Live DemoとOSS本体を分離

### v0.4.0

- Full refresh: 3時間
- Latest Signals refresh: 30分
- Latest Signals対象: LIVE SIGNAL / CURRENT FOCUS / ACTIVITY STREAM
- 重いAnalytics stateを維持
- 表示変更がなければcommitしない

## Sample Profile

```text
https://github.com/mizzz-ivr/profile-signal/tree/main/examples/sample-profile
```

- 固定の架空データ
- 実Consumer固有情報を使わない
- GitHub上で出力イメージを確認可能

## Screenshot selection — 2枚

採用:

- Standalone Repository
- Sample Profile

不採用:

- Profile overview
- Release CI
- v0.4.0 Release
- Consumer installed tree
- 古いv0.2.0画像

Qiita Web Editorで画像反映済み。canonicalにもQiita Image Store URLを同期済み。

## Before publish

- [x] Qiita #2公開
- [x] Standalone OSS移行
- [x] v0.4.0 Release
- [x] Sample Profile追加
- [x] 記事本文をv0.4.0へ更新
- [x] 記事を簡潔化
- [x] Screenshotを2枚へ削減
- [x] Qiita canonical `public/profile-signal-standalone-oss.md` 作成
- [x] Qiita限定共有でPreview
- [x] Qiita Web Editorの画像をGitHub canonicalへ同期
- [x] Release画像を不採用に確定
- [ ] 公開PRをmergeしてQiita一般公開
- [ ] 公開成功後に `ideas/published.md` とmetadataへ公開URL反映

## Tags

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
