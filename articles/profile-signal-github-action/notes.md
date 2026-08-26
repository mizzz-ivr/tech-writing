# Notes — Profile Signal GitHub Action OSS化

## Article focus

単にComposite Actionの書き方を説明する記事にはしない。

自分用のProfile README generatorを、他Repositoryから使えるcontractへ変えていった実体験を中心にする。

## Verified GitHub state — 2026-08-27

### `mizzz-ivr/mizzz-ivr`

Merge済み:

- PR #18 TODAY Activity
- PR #19 Profile Signal Core
- PR #20 Visual Widgets
- PR #21 Operations / Project Health / CI Signal
- PR #22 History / DEV RECAP
- PR #23 config-driven local GitHub Action / Dogfooding

PR #23:

- merged: 2026-08-27 JST
- local Composite Action経由へWorkflow切替済み
- PR CI success
- 24 tests success

### Qiita series

公開済み:

1. GitHubプロフィールREADMEに「今日の開発活動」を自動表示してみた
   - https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a
2. GitHubプロフィールをライブな開発ダッシュボードにしてみた
   - https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630

第3弾article冒頭から第2弾へ「前回の続き」としてリンクする。

## PR #23 implementation

Added:

```text
.github/profile-signal.yml
profile-signal-action/action.yml
profile-signal-action/src/orchestrator.py
profile-signal-action/README.md
profile-signal-action/examples/minimal.yml
profile-signal-action/examples/standard.yml
profile-signal-action/examples/full.yml
profile-signal-action/examples/terminal.yml
tests/test_profile_signal_action.py
```

Workflowのgeneratorは4 script直呼びからlocal actionへ変更。

```yaml
uses: ./profile-signal-action
with:
  config: .github/profile-signal.yml
```

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

## Widgets

- live_signal
- today
- current_focus
- dev_pulse
- now_building
- activity_stream
- dev_recap

Configのwidget overrideがpresetより優先。

## Marker UX

- enabled markerがない → `auto_insert_markers: true` なら指定anchor前へ自動追加
- disabled markerがある → defaultでは中身だけ空にしてpairを維持
- 再enable時に同じ位置へ復帰可能

## Privacy

v0では `privacy.public_only: true` が必須。

falseはエラー。

Private dataを取得して後段でmaskする設計にはしない。

## CI proof

PR #23 CI:

- 24 tests success
- local composite action step success
- Public API preview success
- Profile Signal state schema v4
- Daily snapshots
- Weekly reports
- Monthly reports
- DEV RECAP
- README seven sections
- SVG parse

Action log:

```text
Profile Signal action refreshed:
user=mizzz-ivr
preset=full
theme=signal
widgets=live_signal,today,current_focus,dev_pulse,now_building,activity_stream,dev_recap
```

## Distribution target

第一候補:

```text
mizzz-ivr/profile-signal
```

理由:

- 個人Profile READMEから発展したOSS
- Qiita authorとownerが揃う
- ProfileからLive Demoへ直接辿れる
- ivRooom org固有のプロダクトに見せすぎない

2026-08-27時点ではRepository未作成。

## Connector limitation

現在のGitHub連携では新規Repository creation actionが提供されていない。

そのためChatGPT側では、current repo内でportable staging packageまで実装済み。Repository作成後に移行する。

記事ではこの制約は必須説明ではない。OSS設計の判断として「先にlocal actionでdogfoodした」を中心にする。

## Before publish

- [x] PR #23 Merge
- [ ] main scheduled / workflow_dispatchでlocal Action経由の更新成功
- [ ] `mizzz-ivr/profile-signal` Repository作成
- [ ] Action package移行
- [ ] external installation smoke test
- [ ] `v1` tag / release
- [ ] README / config reference更新
- [ ] 実際のexternal `uses: mizzz-ivr/profile-signal@v1` screenshot
- [ ] Action Marketplace対応をするか判断

## Tags

第一候補:

1. GitHubActions
2. GitHub
3. Python
4. OSS
5. 個人開発
