# Notes — Profile Signal Release / Wiki / Preset配布

## Article focus

単にComposite Actionの書き方を説明する記事にはしない。

自分用のProfile README generatorを、**Release ZIPを自分のProfile Repositoryへ入れて使えるruntime**へ変えた実体験を中心にする。

外部Repositoryから `uses: owner/repo@v1` で直接呼ぶモデルは採用しない。

## Verified GitHub state — 2026-08-27

### `mizzz-ivr/mizzz-ivr`

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
- PR #27 Wiki未初期化時のbootstrap handling
- PR #28 YAML Preset Registry
- PR #29 v0.2 Preset Pack

### Release

- `v0.1.0` 公開済み
- `v0.2.0` 公開済み
- `profile-signal-v0.2.0.zip` 公開済み
- Release本文は日本語
- Release Notesは `release-notes/v0.2.0.md` をSource of Truthとして管理
- `Profile Signal release` workflow_dispatch run #11 success
- Release package validation / clean fixture / assets無しstaging / Publish GitHub Release success
- GitHub Release asset digest: `sha256:f816bcdd8adf8f838a6839075380ef4f982b3dd89aa598b30df5612536c35e9c`

### Package validation

- Release ZIP build success
- ZIP integrity check success
- clean fixtureへ展開 → full runtime success
- README Marker / state schema v4 / SVG / CI / History検証 success
- `minimal`相当で`assets/`無しでもstaging success
- Existing Profile regression / Public API preview success

### GitHub Wiki

Repository Wikiは有効化・初期化済み。

Source of Truth:

```text
docs/wiki/
├─ Home.md
├─ Installation.md
├─ Configuration.md
├─ Presets.md
├─ License.md
└─ _Sidebar.md
```

`Sync Profile Signal wiki` workflowでmain Merge後に `.wiki.git` へ自動同期する。

実Wikiへのpushまで確認済み。

## Qiita series

公開済み:

1. GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
   - https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a
2. GitHubプロフィールをライブな開発ダッシュボードにしてみた
   - https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630

第3弾article冒頭から第2弾へ「前回の続き」としてリンク済み。

## Distribution decision

### 不採用

```yaml
uses: mizzz-ivr/profile-signal@v1
```

を利用者Repositoryから直接呼ぶ方式。

### 採用

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
Forkはshowcase全体を参考にしたい人向けの補助導線。

## Release package

```text
.profile-signal/
├─ action.yml
├─ LICENSE
├─ presets/
│  ├─ minimal.yml
│  ├─ standard.yml
│  ├─ full.yml
│  ├─ terminal.yml
│  ├─ compact.yml
│  ├─ developer.yml
│  ├─ activity.yml
│  └─ oss.yml
├─ src/
│  ├─ orchestrator.py
│  └─ preset_runtime.py
└─ scripts/
   ├─ update-profile-activity.py
   ├─ profile_signal.py
   ├─ update-profile-signal.py
   ├─ profile_signal_operations.py
   └─ profile_signal_history.py
```

Release ZIPにはREADME本体を含めない。
利用者の既存READMEを上書きしないことを最優先する。

## License

Profile Signal runtime / Release packageはMIT License。

MIT対象:

- `.profile-signal/**`
- Release packageの再利用可能コード
- generic config / workflow template
- 配布ドキュメント

MIT対象外:

- 個人Profile README本文
- Hero / Avatar / Screenshot
- 個人プロフィール固有Asset
- 第三者Logo / 商標 / 著作物

Repository root全体をMITにはしない。

## Preset contract

v0.1互換:

- minimal = live_signal + current_focus
- standard = live_signal + today + current_focus + dev_pulse
- full = all 7 widgets
- terminal = all 7 widgets + terminal theme default

v0.2追加:

- compact = today + current_focus / minimal theme
- developer = live_signal + current_focus + dev_pulse + now_building + activity_stream
- activity = today + dev_pulse + activity_stream + dev_recap
- oss = current_focus + now_building + activity_stream + dev_recap

PR #29で実際に4PresetをYAML追加中心で実装し、既存4Presetを変更せず拡張できることをDogfooding済み。

## Privacy

v0.xでは `privacy.public_only: true` が必須。
Private dataを取得して後段でmaskする設計にはしない。
Release ZIPのdefault運用ではAPI Secret不要。

## Screenshot strategy

採用5枚:

1. `01-profile-overview.jpeg`
   - 保存済みプロフィール全景を縮小プレビューとして使用
2. `02-release-package-ci-success.png`
   - `Profile Signal release #11` / Success
3. `03-release-v0.2.0-top.png`
   - Release title / Latest / 日本語説明上部
4. `04-release-v0.2.0-assets.png`
   - MIT / Wiki / Assets / ZIP
5. `05-repository-root.png`
   - `.profile-signal/` と `.github/` が確認できるRepository root

不採用:

- `test-profile-signal-v0.2.0` 作業用tree Screenshot
  - flattenした作業用ファイルが多く、導入構成と誤解されやすいため記事では使わない

Releaseページは上下を連結しない。
上部 → 説明 → 下部の2枚構成にする。
全文はRelease URLへ誘導する。

## Before publish

- [x] PR #23 Merge
- [x] main workflow_dispatchでlocal Action経由の更新成功
- [x] Qiita #2公開
- [x] 第3弾からQiita #2へリンク
- [x] PR #24 CI success / Merge
- [x] `v0.1.0` Release作成
- [x] Releaseページ日本語化
- [x] MIT License範囲整理
- [x] GitHub Wiki公開 / 自動同期
- [x] YAML Preset Registry実装 / PR #28 Merge
- [x] v0.2 Preset Pack / PR #29 Merge
- [x] `v0.2.0` Release作成
- [x] `profile-signal-v0.2.0.zip` asset確認
- [x] v0.2.0 Release package / smoke test / publish job success
- [x] Screenshot撮影
- [x] Screenshot選定 / file名確定
- [x] article本文をv0.2.0へ追従
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
