---
title: "自作GitHubプロフィールWidgetをReleaseで配布できる形にしてみた"
status: review
topics: [GitHubActions, GitHub, Python, OSS, 個人開発]
source_repositories: [mizzz-ivr/mizzz-ivr]
published:
  qiita: null
  zenn: null
---

# 自作GitHubプロフィールWidgetをReleaseで配布できる形にしてみた

前回の記事では、`TODAY` から始めたGitHubプロフィールを `LIVE SIGNAL`、`CURRENT FOCUS`、`DEV PULSE`、`NOW BUILDING`、`ACTIVITY STREAM`、`DEV RECAP` まで広げて、ライブな開発ダッシュボードにしました。

第2弾はこちらです。

https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630

<!-- QIITA_IMAGE: 01-profile-overview.jpg -->

実際のプロフィールは今もGitHub Actionsで更新し続けています。

https://github.com/mizzz-ivr

この仕組みは最初から配布目的で作っていたわけではありません。

完全に自分用でした。

でもWidgetが増えて、設定ファイルでPresetやThemeを切り替えられるようになると、次に考えたのが、

**これを他の人も自分のGitHub Profile Repositoryへ入れられる形にできないか**

ということでした。

最初はReusableなGitHub Actionとして、

```yaml
uses: owner/repo@v1
```

のように外部から呼ぶ形を考えていました。

ただ、Profile Signalの性質を整理すると、外部Actionよりも**利用者自身のProfile Repositoryへruntimeを置く方が合っている**と判断しました。

最終的には、GitHub ReleaseからZIPを取得し、自分のProfile Repositoryへ展開する配布方式にしています。

この記事では、その設計判断と、実際に `v0.2.0` までReleaseできる形にした過程を書きます。

## 最初は外部Actionとして配ろうとしていた

config-driven化した直後は、最終形を次のように想定していました。

```yaml
- uses: mizzz-ivr/profile-signal@v1
  with:
    config: .github/profile-signal.yml
```

一般的なGitHub Actionとしては自然です。

利用者はAction本体を持たず、versionだけ指定すれば使えます。

ただ、Profile SignalはCIで一度処理して終わる小さなActionではありません。

利用者のRepositoryへ継続的に、

```text
README.md
assets/dev-pulse.svg
data/activity/
data/weekly/
data/monthly/
data/profile-signal-state.json
```

を生成します。

README Markerや履歴JSONも利用者側へ残ります。

つまり、外部から一瞬だけ呼ぶ処理というより、**Profile Repositoryの一部として常駐するruntime**に近いです。

そこで配布モデルを考え直しました。

## Release ZIPを自分のRepositoryへ入れる方式にした

現在の構成は次のようになっています。

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

Workflowから呼ぶのは配布元Repositoryではありません。

```yaml
- uses: ./.profile-signal
  with:
    config: .github/profile-signal.yml
```

利用者自身のRepositoryへ展開されたlocal Composite Actionを実行します。

この方式にした理由は主に3つです。

### 実行コードを自分のRepositoryで確認できる

Profile READMEは公開物です。

何をGitHub APIから取得して、何をREADMEへ書いているかは利用者自身が確認できる方が分かりやすいです。

Release ZIP方式なら、実行されるPythonコードは自分のRepository内に残ります。

### 外部Repositoryへ毎回依存しない

Profile Signalは数時間ごとに長期間動かします。

一度取り込んだversionが自分のRepositoryに残る方が、今回の用途では扱いやすいと考えました。

### 更新前に差分を確認できる

新しいReleaseが出てもruntimeは勝手に更新しません。

新versionのZIPを取得し、`.profile-signal/` の差分を確認してからcommitできます。

プロフィールのように「動き続けるが、常に最新版へ即更新する必要はない」ものには、この更新方法が合っていました。

## runtimeは `.profile-signal/` に隔離した

自分用の初期実装では、Profile Signal用コードとRepository側のscriptが混ざっていました。

配布するなら利用者側の既存ファイルと衝突しない方がよいので、runtimeをhidden directoryへまとめています。

`v0.2.0` では次のような構成です。

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

Composite ActionからPreset Registryのentrypointを呼びます。

```yaml
runs:
  using: composite
  steps:
    - name: Set up Python
      uses: actions/setup-python@v6
      with:
        python-version: "3.12"

    - name: Generate Profile Signal
      shell: bash
      run: python "${{ github.action_path }}/src/preset_runtime.py"
```

`preset_runtime.py` がPreset YAMLを検証し、Orchestratorが同じ `.profile-signal/` 配下のruntimeを実行します。

親Repository側のPython fileへ依存しない構成です。

## 自分のプロフィールも配布版runtimeで動かす

配布用のコードだけを別管理すると、本番で使っているものとRelease packageが少しずつズレる可能性があります。

そこで自分のProfile Repositoryも、配布版と同じruntimeを利用しています。

```yaml
- name: Update profile through installed Profile Signal runtime
  uses: ./.profile-signal
  with:
    config: .github/profile-signal.yml
```

自分自身が最初の利用者としてDogfoodingし続ける形です。

## runtimeと利用者設定を分ける

配布runtimeと利用者が編集する設定は分離しています。

```text
.profile-signal/
→ Releaseで更新するruntime

.github/profile-signal.yml
→ 利用者が保持する設定
```

設定例です。

```yaml
version: 1

profile:
  username: YOUR_GITHUB_USERNAME
  timezone: Asia/Tokyo

privacy:
  public_only: true

preset: developer
theme: signal

widgets: {}

readme:
  path: README.md
  auto_insert_markers: true
  insert_before: ""
  empty_disabled: true
```

Release更新時は基本的に `.profile-signal/` を差し替え、利用者が調整した `.github/profile-signal.yml` は維持します。

## Presetはv0.2.0で8種類になった

初回Releaseでは次の4Presetから始めました。

```text
minimal
standard
full
terminal
```

`v0.2.0` では用途別に4つ追加しています。

```text
compact
  TODAY + CURRENT FOCUS

developer
  現在の開発状況・Active Repository・Activity Stream中心

activity
  TODAY / DEV PULSE / ACTIVITY STREAM / DEV RECAP中心

oss
  Public Repositoryでの開発状況・履歴中心
```

既存の `minimal / standard / full / terminal` の意味は変更していません。

Presetを選んだ後でも、`widgets` で個別にON/OFFできます。

```yaml
preset: standard

widgets:
  activity_stream:
    enabled: true
  now_building:
    enabled: true
```

Themeは現在、

```text
signal
minimal
terminal
```

を使えます。

Presetは「どのWidgetを使うか」、Themeは「どう見せるか」と責務を分けています。

## Preset定義もYAMLへ分離した

Preset数を増やすたびにPythonへ、

```python
if preset == "compact":
    ...
```

のような分岐を追加したくなかったため、Preset定義を `.profile-signal/presets/*.yml` へ分離しました。

例えば `compact.yml` は次のような定義です。

```yaml
version: 1
id: compact
description: Compact profile template.
theme: minimal
widgets:
  - today
  - current_focus
```

Registry loaderでは、

- schema version
- ファイル名とPreset IDの一致
- unknown Widget
- Widget重複
- 対応Theme
- 既存互換Presetの欠落

などを検証します。

CIでは既存PresetのWidget contractも固定しています。

今回 `compact / developer / activity / oss` を実際にYAML追加中心で実装できたので、Preset Registryを分離した狙いも確認できました。

`portfolio` のようなPresetも候補にはありますが、現状のProfile Signalは動的な開発Activity Widgetが中心です。静的な代表作品まで生成しない段階で「portfolio」を名乗るのは責務が広すぎるため、今は追加していません。

## READMEはRelease ZIPに含めない

Release ZIPには利用者の既存READMEを上書きする `README.md` を含めていません。

展開して追加される主なファイルは、

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
PROFILE_SIGNAL_INSTALL.md
PROFILE_SIGNAL_VERSION
```

です。

最初のWorkflow実行時に、必要なREADME Markerを自動追加します。

Release版のdefault設定は、

```yaml
insert_before: ""
```

です。

利用者READMEの見出し名を勝手に推測せず、指定がなければ末尾へ追加します。

任意の見出し前へ置きたい場合は、

```yaml
readme:
  insert_before: "## About me"
```

のように変更できます。

## Public-onlyを初期contractにした

Profile Signal v0.xでは、

```yaml
privacy:
  public_only: true
```

を必須にしています。

Private Repository情報を取得してからRendererで隠す設計ではありません。

最初からPublic GitHub APIだけをCollection対象にします。

標準構成ではAPI KeyやPATも不要です。

プロフィールへ公開するツールなので、初期版では安全側へ寄せています。

## Release ZIPは再現可能に生成する

Release ZIPは手作業で作らず、Python builderで生成しています。

```text
scripts/build-profile-signal-release.py
```

対象を固定し、Releaseごとに必要なruntime・config・workflow・install guideをpackageします。

同じSourceから同じversionをbuildしやすいよう、ZIP entryのtimestampも固定しています。

## ZIPを作るだけではなく、展開して動かすCIを入れた

配布物で一番避けたかったのは、

> 自分のRepositoryでは動くが、Release ZIPだけ持っていくと動かない

という状態です。

そこでRelease Workflowでは、archiveを作った後にclean fixtureへ展開して実際にruntimeを動かします。

```text
build ZIP
   ↓
clean temporary directory
   ↓
最小READMEを作成
   ↓
configをtest用に設定
   ↓
Profile Signal runtime実行
   ↓
README / state / SVGを検証
```

<!-- QIITA_IMAGE: 02-release-package-ci-success.jpg -->

`v0.2.0` を発行した `Profile Signal release #11` でも、

- Build release archive
- Smoke test extracted install
- Validate installed workflow staging without assets
- Publish GitHub Release

まで成功しました。

## GitHub ReleaseもWorkflowから発行する

配布Workflowは `workflow_dispatch` でversionを指定して実行します。

例えば、

```text
v0.2.0
```

を指定すると、

1. Release ZIP生成
2. package validation
3. 日本語Release Notes準備
4. GitHub Release作成
5. ZIP asset添付

まで行います。

<!-- QIITA_IMAGE: 03-release-v0.2.0-top.jpg -->

現在の最新版は `v0.2.0` です。

https://github.com/mizzz-ivr/mizzz-ivr/releases/tag/v0.2.0

初回の `v0.1.0` から、Preset Registryと用途別Presetを追加したReleaseになっています。

Release Notesも日本語で用意し、変更点・導入・互換性・License・Wikiへの導線がReleaseページだけでも分かるようにしています。

Release assetは、

```text
profile-signal-v0.2.0.zip
```

です。

<!-- QIITA_IMAGE: 04-release-v0.2.0-assets.jpg -->

Release Notes本文は、

```text
release-notes/v0.2.0.md
```

をSource of Truthにしています。

Releaseページ全文は長くなるため、記事では要点だけをスクリーンショットで見せ、詳細はReleaseページへ誘導します。

## 導入手順はかなり短い

### 1. Profile Repositoryを用意

GitHubプロフィールREADME用の、

```text
<username>/<username>
```

Repositoryを使います。

### 2. v0.2.0のRelease ZIPを展開

Release Assetsから、

```text
profile-signal-v0.2.0.zip
```

を取得してRepository rootへ展開します。

### 3. usernameとPresetを変更

```yaml
profile:
  username: YOUR_GITHUB_USERNAME

preset: developer
```

のように設定します。

### 4. commit / push

runtime・config・Workflowをcommitします。

### 5. Actionsから一度手動実行

```text
Actions
→ Profile Signal
→ Run workflow
```

初回結果を確認します。

<!-- QIITA_IMAGE: 05-repository-root.jpg -->

Repository内では `.profile-signal/` と `.github/profile-signal.yml`、Workflowを確認できます。

その後はscheduleで自動更新されます。

## 導入手順はGitHub Wikiにもまとめた

Releaseページだけへ長い説明を詰め込まず、継続的なドキュメントはGitHub Wikiへ分けています。

https://github.com/mizzz-ivr/mizzz-ivr/wiki

現在は、

- Home
- Installation
- Configuration
- Presets
- License

を用意しています。

ただしWikiをGitHub UIだけで更新すると、Repository側のドキュメントとズレやすくなります。

そこで編集元は、

```text
docs/wiki/*.md
```

です。

Pull Requestで必須ページと内部リンクを検証し、mainへMergeすると `Sync Profile Signal wiki` Workflowが `.wiki.git` へ自動pushします。

実Wikiへの同期まで確認済みです。

## MIT Licenseの対象も分けた

Release ZIP内のProfile Signal runtimeはMIT Licenseです。

一方、配布元は自分自身のGitHub Profile Repositoryでもあります。

Repository root全体をMITにすると、

- 個人Profile README本文
- Hero / Avatar画像
- Screenshot
- 個人用の文章
- 第三者Logoや商標

まで同じLicense対象に見えやすくなります。

そのためMITの対象は、

```text
.profile-signal/**
Release packageの再利用可能コード
generic config / workflow template
配布ドキュメント
```

へ明確に寄せています。

個人プロフィール固有コンテンツはMIT対象外です。

## Forkは補助的な導線にする

Forkで配布する方法もあります。

ただ、自分のProfile RepositoryにはProfile Signal以外にも、

- 自己紹介
- Featured Project
- Links
- Hero画像
- 個人用文章

が含まれます。

そのため現在は、

```text
Release ZIP
→ 既存Profileへ機能だけ追加したい人向け / 推奨

Fork
→ 完成形のRepository構成を丸ごと参考にしたい人向け
```

と役割を分けています。

## 更新はruntimeだけ差し替えるのが基本

新Releaseへ更新するときは、基本的に、

```text
.profile-signal/
```

を新しいruntimeへ差し替えます。

`.github/profile-signal.yml` は利用者設定なので維持します。

Workflow templateに変更があるReleaseだけ、Release Notesを確認して更新します。

Profile Signalでは自動updateよりも、利用者がdiffを見てからruntimeを更新できることを優先しています。

## OSS化して一番変わったのはコードより境界だった

今回、CollectorやWidgetの計算ロジック自体を全面的に作り直したわけではありません。

それより時間を使ったのは、

- runtimeをどこへ置くか
- user configと何を分離するか
- READMEを上書きしない方法
- defaultの挿入位置
- Update時に何を残すか
- Private dataをどこで遮断するか
- Release ZIPだけで本当に起動できるか
- 配布コードと個人プロフィールのLicense境界
- WikiとRepository内ドキュメントをどう同期するか
- Presetをどう増やせるようにするか

といった境界でした。

自分専用スクリプトなら、「自分のRepositoryではこうだから」で済みます。

配布しようとすると、その前提を一つずつ外す必要があります。

外部ActionではなくRelease ZIP方式へ変えたのも、その過程でProfile Signalの性質を見直した結果でした。

現在は、

- `v0.2.0` Release公開
- Release ZIP配布
- 日本語Release Notes
- clean fixture smoke test
- GitHub Wiki
- MIT License境界
- YAML Preset Registry
- 8種類の公式Preset

まで整っています。

今後も自分のプロフィールでDogfoodingしながら、Profile SignalのThemeや用途別Presetを増やしていく予定です。
