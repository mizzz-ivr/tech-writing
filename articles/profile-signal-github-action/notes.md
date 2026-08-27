# Notes — Profile Signal Release / Wiki / Preset配布

## Article focus

単にComposite Actionの書き方を説明する記事にはしない。

自分用のProfile README generatorを、**Release ZIPを自分のProfile Repositoryへ入れて使えるruntime**へ変えた実体験を中心にする。

外部Repositoryから `uses: owner/repo@v1` で直接呼ぶモデルは採用しない。

## Verified GitHub state — 2026-08-27

Merge済み:

- PR #18 TODAY Activity
- PR #19 Profile Signal Core
- PR #20 Visual Widgets
- PR #21 Operations / Project Health / CI Signal
- PR #22 History / DEV RECAP
- PR #23 config-driven local GitHub Action / Dogfooding
- PR #24 Release ZIP installation package
- PR #25 日本語Release Notes / License範囲 / Wiki source整備
- PR #26 `docs/wiki/` → GitHub Wiki同期Workflow
- PR #27 Wiki bootstrap handling
- PR #28 YAML Preset Registry
- PR #29 v0.2 Preset Pack

## Release

- `v0.1.0` 公開済み
- `v0.2.0` 公開済み
- `profile-signal-v0.2.0.zip` 公開済み
- Release本文は日本語
- Release Notes: `release-notes/v0.2.0.md`
- `Profile Signal release` workflow_dispatch run #11 success
- build / clean fixture smoke test / assets無しstaging / publish success
- digest: `sha256:f816bcdd8adf8f838a6839075380ef4f982b3dd89aa598b30df5612536c35e9c`

## Distribution decision

不採用:

```yaml
uses: mizzz-ivr/profile-signal@v1
```

採用:

```text
GitHub Release ZIP
        ↓
利用者の GitHub Profile Repository
        ↓
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
        ↓
uses: ./.profile-signal
```

Release ZIPを推奨導入経路とする。
Forkは完成形を参考にしたい場合の補助導線。

## Preset

v0.1互換:

- minimal
- standard
- full
- terminal

v0.2追加:

- compact
- developer
- activity
- oss

PR #29でYAML追加中心の拡張をDogfooding済み。

## License

Profile Signal runtime / Release packageはMIT License。
個人Profile README本文・画像・Screenshotなど配布元Repository固有コンテンツはMIT対象外。

## Wiki

- Home
- Installation
- Configuration
- Presets
- License

`docs/wiki/*.md` をSource of Truthとしてmain Merge後にGitHub Wikiへ自動同期する。

## Screenshot selection

採用:

1. `01-profile-overview.jpeg`
2. `02-release-package-ci-success.png`
3. `03-release-v0.2.0-top.png`
4. `04-release-v0.2.0-assets.png`
5. `05-repository-root.png`

不採用:

- `test-profile-signal-v0.2.0` 作業用tree

Releaseページは上下2枚に分け、本文を挟む。連結画像にはしない。
Release全文はGitHub URLへ誘導する。

## Before publish

- [x] Qiita #2公開
- [x] 第3弾からQiita #2へリンク
- [x] Release ZIP配布モデルへ記事を変更
- [x] `v0.2.0` Release公開
- [x] Release ZIP asset確認
- [x] 日本語Release Notes
- [x] GitHub Wiki公開 / 自動同期
- [x] MIT License境界整理
- [x] YAML Preset Registry / 8公式Preset
- [x] Screenshot撮影
- [x] Screenshot選定
- [x] article本文をv0.2.0へ追従
- [x] PR #11 mergeability確認
- [ ] Qiitaへ5枚Upload
- [ ] Qiita image Markdownをplaceholderへ反映
- [ ] Qiita Preview最終確認
- [ ] PR #11 Merge
- [ ] 公開

## Tags

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
