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

### Release

- `v0.1.0` 公開済み
- `profile-signal-v0.1.0.zip` 公開済み
- Release本文は日本語へ同期済み
- Release Notesは `release-notes/v0.1.0.md` をSource of Truthとして管理

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

実Wikiへのpush:

```text
mizzz-ivr/mizzz-ivr.wiki.git
HEAD -> master
Profile Signal wiki synchronized
```

まで確認済み。

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

理由:

- Profile Signalは汎用CI ActionというよりProfile Repositoryに常駐するruntime / templateに近い
- 利用者自身のRepository内に実行コードがある方が透明性が高い
- 外部Repository availabilityへ毎回依存しない
- Release単位で更新内容を確認してから取り込める
- Fork / Release配布の方がREADME customizationと相性が良い

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

Forkはshowcase全体を参考にしたい人向けの補助導線。個人プロフィール固有の文章・画像まで入るため、初回導入の推奨にはしない。

## Release package

```text
.profile-signal/
├─ action.yml
├─ LICENSE
├─ presets/
│  ├─ minimal.yml
│  ├─ standard.yml
│  ├─ full.yml
│  └─ terminal.yml
├─ src/
│  ├─ orchestrator.py
│  └─ preset_runtime.py
└─ scripts/
   ├─ update-profile-activity.py
   ├─ profile_signal.py
   ├─ update-profile-signal.py
   ├─ profile_signal_operations.py
   └─ profile_signal_history.py

distribution/
├─ profile-signal.yml
├─ profile-signal-workflow.yml
└─ INSTALL.md
```

Release builder:

```text
scripts/build-profile-signal-release.py
```

Release ZIPにはREADME本体を含めない。
利用者の既存READMEを上書きしないことを最優先する。

## Release ZIP install contract

1. Release ZIPをDownload
2. Profile Repository rootへ展開
3. `.github/profile-signal.yml` のusernameを変更
4. preset / theme / widgetを選ぶ
5. commit / push
6. `Actions → Profile Signal → Run workflow`
7. README / assets / dataの生成を確認

Workflowでは:

```yaml
uses: ./.profile-signal
```

を使う。

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

v0.1互換のbuilt-in contract:

- minimal = live_signal + current_focus
- standard = live_signal + today + current_focus + dev_pulse
- full = all 7 widgets
- terminal = all 7 widgets + terminal theme default

## YAML Preset Registry

PR #28でPresetをruntimeコードから分離。

```text
.profile-signal/presets/*.yml
```

例:

```yaml
version: 1
id: standard
description: Balanced default profile signal.
theme: signal
widgets:
  - live_signal
  - today
  - current_focus
  - dev_pulse
```

新しい公式PresetはYAML追加中心で定義できる。

Registry validation:

- YAML mapping
- schema version
- filename / id一致
- non-empty widgets
- unknown widget rejection
- duplicate widget rejection
- supported theme validation
- built-in 4Preset欠落検知

CIでは既存PresetのWidget contractを固定。

将来候補:

- compact
- developer
- portfolio
- activity
- oss

名称とWidget構成は実利用を見ながら決める。

利用者独自Presetは現状 `.profile-signal/` 更新時に消える可能性があるため、まず `widgets` overrideを推奨する。

## Themes

- signal
- minimal
- terminal

Themeはデータ収集ではなくRenderer concernとして扱う。

## Marker UX

- enabled markerがない → `auto_insert_markers: true` なら自動追加
- release configの`insert_before`は空をdefaultにする
  - 利用者READMEの見出しを勝手に推測しない
  - defaultではREADME末尾へ追加
- disabled markerがある → 中身だけ空にしてpairを維持
- 再enable時に同じ位置へ復帰可能

## Privacy

v0では `privacy.public_only: true` が必須。
falseはエラー。

Private dataを取得して後段でmaskする設計にはしない。
Release ZIPのdefault運用ではAPI Secret不要。

## Review fixes

PR #24のCodex Reviewで見つかった内容:

1. workflow_dispatchをfeature branchから実行した場合にmainへ誤pushし得る
2. `minimal` presetで`assets/`が無いと`git add assets`が失敗する
3. `0.1.0`入力時にbuilderだけ`v0.1.0`へ正規化され、後段のarchive pathとズレる

対応:

- consumer repositoryのdefault branchをcheckout / push targetとして利用
- generated pathは存在するものだけstage
- release versionをWorkflowの最初に1回正規化し、build / release / asset pathで共通利用

3 threadともresolve済み。

## Documentation

GitHub Wikiへ以下を公開する。

- Home
- Installation
- Configuration
- Presets
- License

Wikiは直接編集ではなく `docs/wiki/*.md` をSource of Truthにする。
PRで必須ページと内部リンクをvalidationし、main Merge後に自動同期する。

## Screenshot strategy

保存済みのプロフィール全景Screenshotは縦長。
記事本文へ原寸で貼ると読みにくいので、次の扱いにする。

- 冒頭: 完成形の縮小プレビューとして1枚
- 本文: GitHubプロフィール本体へのリンクを併記
- 配布説明: Release / ZIP / CIの短いScreenshotを優先

### Required screenshots

1. 完成形Profile overview（保存済み画像）
2. package smoke test success
3. GitHub Release `v0.1.0` + ZIP asset + 日本語説明
4. Release ZIPを展開したRepository tree / `uses: ./.profile-signal`

Optional:

5. Wiki Home / Sidebar
6. `.profile-signal/presets/` tree

外部Action呼び出しScreenshotは不要。

## Before publish

- [x] PR #23 Merge
- [x] main workflow_dispatchでlocal Action経由の更新成功
- [x] Qiita #2公開
- [x] 第3弾からQiita #2へリンク
- [x] PR #24 CI success
- [x] PR #24 Merge
- [x] Release ZIPをclean fixtureへ導入した結果を確認
- [x] 記事をRelease/Forkモデルへ更新
- [x] `v0.1.0` Release作成
- [x] Release ZIP asset確認
- [x] Releaseページ日本語化
- [x] MIT License範囲整理
- [x] GitHub Wiki公開 / 自動同期
- [x] YAML Preset Registry実装 / PR #28 Merge
- [ ] Screenshot追加
- [ ] Qiita Preview最終確認
- [ ] 公開

## Tags

第一候補:

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
