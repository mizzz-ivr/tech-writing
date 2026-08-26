# Notes — Profile Signal Release / Fork配布

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

PR #23 Merge後:

- local Composite Action経由へWorkflow切替済み
- main workflow_dispatch success確認済み
- 24 tests success

PR #24:

- merged: 2026-08-27 JST
- `.profile-signal/` self-contained runtime追加
- Release ZIP builder追加
- generic config / workflow / install guide追加
- Package CI success
- clean fixtureへRelease ZIP展開 → full runtime実行 success
- `minimal`相当で`assets/`無しでもstaging可能なfixture success
- Existing Profile regression / Public API preview success
- Codex review 3件修正・resolve済み

次:

- `Profile Signal release` workflow_dispatchで `v0.1.0` を発行する
- Release ZIP assetを確認する

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

## PR #24 package

```text
.profile-signal/
├─ action.yml
├─ LICENSE
├─ src/orchestrator.py
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

## Preset contract

- minimal = live_signal + current_focus
- standard = live_signal + today + current_focus + dev_pulse
- full = all 7 widgets
- terminal = all 7 widgets + terminal theme default

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

## Package validation

PR #24で2種類のCIを通した。

### Existing profile regression

- existing unit tests
- real Public GitHub API preview
- README 7 Widget
- Weekly / Monthly / DEV RECAP
- SVG parse

### Release fixture smoke test

```text
build ZIP
  ↓
clean temporary directoryへextract
  ↓
README.mdを1行だけ作成
  ↓
usernameをmizzz-ivrへ置換
  ↓
presetをCIだけfullへ変更
  ↓
.profile-signal/src/orchestrator.py 実行
  ↓
7 README marker / state v4 / CI / history / SVG検証
```

さらに`minimal` preset相当で`assets/`が存在しない場合でも、配布Workflowのstagingが失敗しないfixtureを追加した。

これで「自分のRepositoryにたまたま依存して動いた」状態を避ける。

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

## Release publishing

`.github/workflows/profile-signal-release.yml` のworkflow_dispatchでversionを指定する。

例:

```text
v0.1.0
```

Workflowが:

- deterministic ZIP生成
- ZIP integrity check
- GitHub Release作成
- ZIP asset添付

まで行う。

## Screenshot strategy

保存済みのプロフィール全景Screenshotは縦長。
記事本文へ原寸で貼ると読みにくいので、次の扱いにする。

- 冒頭: 完成形の縮小プレビューとして1枚
- 本文: GitHubプロフィール本体へのリンクを併記
- 配布説明: Release / ZIP / CIの短いScreenshotを優先

### Required screenshots

1. 完成形Profile overview（保存済み画像）
2. PR #24 / package smoke test success
3. GitHub Release `v0.1.0` + ZIP asset
4. Release ZIPを展開したRepository tree / `uses: ./.profile-signal`

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
- [ ] `v0.1.0` Release作成
- [ ] Release ZIP asset確認
- [ ] mainで`.profile-signal` runtime経由のscheduled / workflow_dispatch更新を確認
- [ ] Screenshot追加

## Tags

第一候補:

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
