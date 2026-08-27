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

でもWidgetが増えて、設定ファイルで `minimal / standard / full / terminal` を切り替えられるようになると、少し欲が出ました。

**これ、自分のREADMEだけで終わらせず、他の人も自分のGitHubプロフィールへ入れられる形にできないか。**

最初は「ReusableなGitHub Actionにして `uses: owner/repo@v1` で呼べばよい」と考えていました。

ただ、実際に配布方法まで考えると少し違和感が出ました。

最終的には、外部Actionとして呼ぶのではなく、**Release ZIPを利用者自身のProfile Repositoryへ展開して使う方式**に変えました。

今回はその判断と、実際に配布可能な形へ変えていったところを書きます。

## 最初は外部Actionとして配ろうとしていた

Profile Signalをconfig-drivenにした時点では、最終形をこんなWorkflowにするつもりでした。

```yaml
- uses: mizzz-ivr/profile-signal@v1
  with:
    config: .github/profile-signal.yml
```

普通のGitHub Actionとして考えると自然です。

利用者はAction本体を自分のRepositoryへ置かず、versionだけ指定すれば使えます。

でもProfile Signalの性質を考えると、少し違いました。

これはCI用の小さな処理ではありません。

実際には利用者のProfile Repositoryへ、次のようなものを生成し続けます。

```text
README.md
assets/dev-pulse.svg
data/activity/
data/weekly/
data/monthly/
data/profile-signal-state.json
```

さらに、README Markerの配置や履歴JSONも利用者側に残ります。

つまりProfile Signalは、外から一瞬だけ処理を呼び出すActionというより、**Profile Repositoryの一部として常駐するruntime**に近いです。

そこで配布モデルを考え直しました。

## Release ZIPを自分のRepositoryへ入れる方式にした

最終的な構成はこうしました。

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

Workflowから呼ぶのは外部Repositoryではありません。

```yaml
- uses: ./.profile-signal
  with:
    config: .github/profile-signal.yml
```

利用者自身のRepositoryに入っているlocal Composite Actionを実行します。

この方がProfile Signalには合っていると判断しました。

### 実行コードを自分のRepositoryで確認できる

Profile READMEは公開物です。

何をGitHub APIから取得して、何をREADMEへ書いているかは利用者自身が確認できる方が安心です。

Release ZIP方式なら、実際に実行されるPythonコードはすべて自分のRepositoryにあります。

### 外部Repositoryへ毎回依存しない

外部Action方式だと、実行時には配布元Repositoryのtagを参照します。

もちろん一般的なGitHub Actionでは普通のことですが、Profile Signalは数時間ごとに長期間動かす予定です。

一度取り込んだversionが自分のRepository内に残る方が、今回の用途では扱いやすいと感じました。

### 更新前に差分を見られる

新versionが出ても自動では置き換わりません。

ReleaseをDownloadして `.profile-signal/` を更新し、差分を見てからcommitできます。

プロフィールのように「動き続けるけど急いで更新する必要はない」ものには、このくらいの更新速度がちょうど良いです。

## runtimeは `.profile-signal/` に閉じ込めた

最初のDogfooding版では、次のような構成でした。

```text
profile-signal-action/
scripts/
```

自分のRepositoryだけなら問題ありません。

でもこれをそのまま配布すると、利用者がすでに `scripts/` を使っている場合に混ざります。

そこで配布版ではruntimeを完全に隔離しました。

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
```

GitHubプロフィールで普段触る必要がないruntimeなので、hidden directoryにしています。

Composite Actionの`action.yml`からは、同じディレクトリ内のPreset Registry entrypointを実行します。

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

`preset_runtime.py` がPreset YAMLを検証してからOrchestratorへ渡し、Orchestrator側は `.profile-signal/scripts/` のruntimeを実行します。

親RepositoryのPythonファイルへ依存しない構成です。

## 自分のプロフィールも配布版runtimeを使うようにした

配布用ファイルを別に作るだけだと、本番で動かしているものと配布物が少しずつズレます。

そこで自分のプロフィールWorkflowも、配布予定のdirectoryへ切り替えました。

```yaml
- name: Update profile through installed Profile Signal runtime
  uses: ./.profile-signal
  with:
    config: .github/profile-signal.yml
```

つまり自分自身も、Release ZIPを展開した利用者とほぼ同じ構成で動かします。

Dogfoodingを続けながら配布物を育てる形です。

## 設定はProfile Repository側に残す

runtimeとユーザー設定は分けています。

```text
.profile-signal/
→ 配布されるruntime

.github/profile-signal.yml
→ 利用者が編集する設定
```

例えば標準設定は次のようになります。

```yaml
version: 1

profile:
  username: YOUR_GITHUB_USERNAME
  timezone: Asia/Tokyo

privacy:
  public_only: true

preset: standard
theme: signal

widgets: {}

readme:
  path: README.md
  auto_insert_markers: true
  insert_before: ""
  empty_disabled: true
```

Update時は基本的に `.profile-signal/` だけ置き換えます。

自分で調整したconfigはそのまま残せます。

## PresetとThemeはそのまま使える

最初に作ったPresetは配布版でも維持しています。

```text
minimal
  LIVE SIGNAL
  CURRENT FOCUS

standard
  LIVE SIGNAL
  TODAY
  CURRENT FOCUS
  DEV PULSE

full
  全Widget

terminal
  全Widget + terminal theme
```

例えば、とりあえず少なめに始めたい場合は、

```yaml
preset: minimal
```

だけで済みます。

Presetを使ったうえで個別Widgetだけ変更できます。

```yaml
preset: standard

widgets:
  activity_stream:
    enabled: true
  now_building:
    enabled: true
```

Themeも、

```yaml
theme: signal
```

から、

```text
signal
minimal
terminal
```

を選べます。

## Preset定義もYAMLへ分離した

最初は `minimal / standard / full / terminal` の組み合わせをPythonの辞書に直接書いていました。

でも今後プロフィール用テンプレートを増やすたびに、OrchestratorへPreset名の分岐を増やしたくありません。

そこでPresetを `.profile-signal/presets/*.yml` へ分離しました。

例えば `standard` は次のように定義します。

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

新しい公式Presetなら、基本的にはYAMLを追加するだけです。

```text
.profile-signal/presets/compact.yml
```

のように追加し、

```yaml
version: 1
id: compact
description: Compact profile template.
theme: minimal
widgets:
  - today
  - current_focus
```

と定義できます。

Registry loaderでは、

- schema version
- ファイル名とPreset IDの一致
- unknown Widget
- Widget重複
- 対応Theme
- 既存4Presetの欠落

を検証します。

CIでは既存 `minimal / standard / full / terminal` のWidget構成も固定しています。

これで今後 `compact / developer / portfolio / activity / oss` のような用途別Presetを増やしても、CollectorやAnalyticsへPreset固有の分岐を持ち込まずに済みます。

利用者独自Presetについては、現状 `.profile-signal/` がRelease更新時に差し替わる領域なので、まずは `widgets` overrideを推奨しています。

## READMEはRelease ZIPに含めない

ここはかなり重要でした。

Profile Signalの完成形を見せるために、自分のREADMEをそのまま配布する方法もあります。

でも利用者がすでにProfile READMEを持っている場合、上書きしたくありません。

そのためRelease ZIPにはREADMEを入れません。

展開して追加されるのは、基本的に次だけです。

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
PROFILE_SIGNAL_INSTALL.md
```

最初のWorkflow実行時に、Profile SignalがMarkerを追加します。

Release版のdefault設定では、

```yaml
insert_before: ""
```

にしています。

利用者のREADMEにどんな見出しがあるか分からないため、勝手に`## About me`などを推測しません。

空の場合は末尾へ追加します。

自分で配置を決めたい場合は、例えば、

```yaml
readme:
  insert_before: "## About me"
```

と変更できます。

## Public-onlyは配布版でも固定した

Profile Signal v0では、

```yaml
privacy:
  public_only: true
```

が必須です。

`false`にするとエラーにしています。

Private Repositoryの情報を取得してからRendererで隠す設計にはしていません。

最初からPublic GitHub APIだけをCollection対象にします。

Release ZIPの標準構成ではAPI KeyやPATも不要です。

プロフィールへ公開するツールなので、この制約は機能不足というより初期版の安全側のcontractとして残しています。

## Release ZIPはPythonで再現可能に生成する

手動でdirectoryをZIPにすると、毎回入れるファイルが微妙に変わりそうだったのでbuilderを作りました。

```text
scripts/build-profile-signal-release.py
```

生成対象を固定しています。

```text
.profile-signal/
distribution/profile-signal.yml
distribution/profile-signal-workflow.yml
distribution/INSTALL.md
```

Release ZIP内では次の配置になります。

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
PROFILE_SIGNAL_INSTALL.md
PROFILE_SIGNAL_VERSION
```

同じSourceから同じversionをbuildしやすいよう、ZIP entryのtimestampも固定しています。

## ZIPを作るだけではなく、展開して実際に動かすCIを入れた

配布物で一番怖かったのは、

> 自分のRepositoryでは動くけど、ZIPだけ持っていくと動かない

という状態です。

そこでRelease用Workflowでは、archiveを作ったあと、temporary directoryへ展開します。

```text
build ZIP
   ↓
clean temporary directory
   ↓
README.md を1行だけ作る
   ↓
configのusernameをtest用に設定
   ↓
.profile-signal/src/preset_runtime.py を実行
   ↓
README / state / SVGを検証
```

<!-- QIITA_IMAGE: 02-release-package-ci-success.jpg -->

このfixtureには自分のProfile RepositoryのREADMEや既存dataを持ち込みません。

そこでPublic APIからデータを集めて、

- README Marker
- `data/profile-signal-state.json`
- schema v4
- `assets/dev-pulse.svg`

まで作れれば、少なくとも配布物だけで起動できることが確認できます。

## GitHub Release自体もWorkflowから作れるようにした

配布用Workflowには`workflow_dispatch`を追加しました。

versionを、

```text
v0.1.0
```

のように指定して実行します。

Workflow側で、

1. Release ZIP生成
2. ZIP integrity check
3. GitHub Release作成
4. ZIP asset添付

まで行います。

<!-- QIITA_IMAGE: 03-release-v0.1.0.jpg -->

`v0.1.0` は実際に公開済みです。

https://github.com/mizzz-ivr/mizzz-ivr/releases/tag/v0.1.0

Release assetには、

```text
profile-signal-v0.1.0.zip
```

を置いています。

Release本文も日本語にし、導入方法・Privacy・LicenseがReleaseページだけでも分かるようにしました。

Release Notes本文は `release-notes/v0.1.0.md` をSource of Truthとして、Workflowから公開済みReleaseへ同期します。

## 導入手順はかなり短くできた

### 1. Profile Repositoryを用意

GitHubプロフィールREADME用の、

```text
<username>/<username>
```

Repositoryを使います。

### 2. Release ZIPを展開

Releaseページから、例えば、

```text
profile-signal-v0.1.0.zip
```

をDownloadしてRepository rootへ展開します。

### 3. usernameを変更

```yaml
profile:
  username: YOUR_GITHUB_USERNAME
```

を自分のloginへ変更します。

### 4. commit / push

runtime・config・Workflowをcommitします。

### 5. Actionsから一度手動実行

```text
Actions
→ Profile Signal
→ Run workflow
```

初回結果を確認します。

<!-- QIITA_IMAGE: 04-installed-tree.jpg -->

ここまでで、その後はscheduleで自動更新されます。

## 導入手順はGitHub Wikiにもまとめた

Releaseページだけに長い説明を詰め込まず、継続的なドキュメントはGitHub Wikiへ分けました。

https://github.com/mizzz-ivr/mizzz-ivr/wiki

Wikiには、

- Home
- Installation
- Configuration
- Presets
- License

を用意しています。

ただしWikiをGitHub UIだけで編集すると、Repository側のドキュメントと内容がズレやすくなります。

そこで編集元は、

```text
docs/wiki/*.md
```

にしました。

Pull Requestでは必須ページと内部リンクを検証し、mainへMergeすると `Sync Profile Signal wiki` Workflowが `.wiki.git` へ自動pushします。

実際に初期Wikiを作成したあと、

```text
mizzz-ivr/mizzz-ivr.wiki.git
HEAD -> master
Profile Signal wiki synchronized
```

まで動作確認しました。

## MIT Licenseの対象も分けた

Release ZIP内のProfile Signal runtimeはMIT Licenseにしています。

一方で、配布元は自分自身のGitHub Profile Repositoryです。

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

個人プロフィール固有コンテンツは別扱いです。

「OSS化するコード」と「自分のプロフィールそのもの」を同じRepositoryに置いているからこそ、License境界も明記する必要がありました。

## Forkは補助的な導線にする

Forkで配布する案も考えています。

ただ、自分のProfile Repositoryには当然ですが、

- 自己紹介
- Featured Project
- Links
- Hero画像
- 個人用の文章

が入っています。

そのままForkを推奨すると、Profile Signal以外の個人要素まで大量についてきます。

なので今の方針では、

```text
Release ZIP
→ 既存Profileへ機能だけ追加したい人向け / 推奨

Fork
→ 完成形のRepository構成を丸ごと参考にしたい人向け
```

と役割を分けます。

## 更新も「runtimeだけ差し替える」を基本にした

新しいReleaseが出たときは、毎回設定を作り直す必要はありません。

基本は、

```text
.profile-signal/
```

だけ新しいversionへ置き換えます。

`.github/profile-signal.yml`は自分の設定なので維持します。

Workflow templateに変更があるReleaseだけ、Release Notesを見て手動で更新します。

自動updateまで最初から入れなかったのは、プロフィールのようなものなら「勝手にruntimeが更新される」より、自分でdiffを見て更新したいと思ったからです。

## OSS化して一番変わったのはコードより境界だった

今回、CollectorやWidgetの計算ロジック自体を大きく作り直したわけではありません。

それより時間を使ったのは、

- runtimeをどこへ置くか
- user configと何を分離するか
- READMEを上書きしない方法
- defaultの挿入位置をどうするか
- Update時に何を残すか
- Private dataをどこで遮断するか
- 配布ZIPだけで本当に起動できるか
- 配布コードと個人プロフィールのLicense境界
- WikiとRepository内ドキュメントをどう同期するか
- Presetをどう増やせるようにするか

といった境界でした。

自分専用スクリプトなら「自分のRepositoryではこうだから」で済みます。

配布しようとすると、その前提を一つずつ外す必要があります。

今回外部ActionではなくRelease ZIP方式へ変えたのも、その過程でProfile Signalの性質を見直した結果でした。

今のところ、**GitHubプロフィールを自動化するruntimeは、自分のProfile Repositoryに見える形で置いておく方が自分の狙いには合っている**と感じています。

`v0.1.0` のRelease公開、Wiki、MIT License、YAML Preset Registryまで整いました。

次は実際のDogfoodingを続けながら、用途別PresetとThemeを増やしていく予定です。