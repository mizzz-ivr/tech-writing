---
title: "自作GitHubプロフィールWidgetをStandalone OSSとしてRelease配布できる形にしてみた"
status: review
topics: [GitHubActions, GitHub, Python, OSS, 個人開発]
source_repositories: [mizzz-ivr/profile-signal, mizzz-ivr/mizzz-ivr]
published:
  qiita: null
  zenn: null
---

# 自作GitHubプロフィールWidgetをStandalone OSSとしてRelease配布できる形にしてみた

前回の記事では、`TODAY` から始めたGitHubプロフィールを `LIVE SIGNAL`、`CURRENT FOCUS`、`DEV PULSE`、`NOW BUILDING`、`ACTIVITY STREAM`、`DEV RECAP` まで広げて、ライブな開発ダッシュボードにしました。

第2弾はこちらです。

https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630

<!-- QIITA_IMAGE: 01-profile-overview.jpg -->

実際のプロフィールは今もProfile Signalを使って更新しています。

https://github.com/mizzz-ivr

この仕組みは最初から配布目的で作っていたわけではありません。

完全に自分用でした。

Widgetが増え、PresetやThemeを設定ファイルで切り替えられるようになったところで、次に考えたのが、

**これを他の人も自分のGitHub Profile Repositoryへ入れられる形にできないか**

ということでした。

最初は外部GitHub Actionとして、

```yaml
uses: owner/repo@v1
```

のように呼ぶ形も考えました。

ただ、Profile SignalはREADMEを書き換えるだけではなく、履歴JSONやSVG、計算済みstateを利用者側へ継続的に残します。

そこで最終的には、

- OSS本体は専用Repositoryへ分離する
- GitHub Release ZIPとして配布する
- 利用者自身のProfile Repositoryへruntimeを展開する
- Workflowからは `uses: ./.profile-signal` でlocal runtimeを実行する

という形にしました。

現在のSource of Truthは次のRepositoryです。

https://github.com/mizzz-ivr/profile-signal

この記事では、自分専用のプロフィール生成処理を、`v0.4.0` までStandalone OSSとして配布できる形へ持っていった過程を書きます。

## 最初は外部Actionとして配ろうとしていた

config-driven化した直後は、最終形を次のように想定していました。

```yaml
- uses: mizzz-ivr/profile-signal@v1
  with:
    config: .github/profile-signal.yml
```

一般的なGitHub Actionとしては自然です。

ただ、Profile SignalはCIの中で一度処理して終わる小さなActionではありません。

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

現在の導入構成は次のようになっています。

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

何をGitHub APIから取得し、何をREADMEへ書くのかは利用者自身が確認できる方が分かりやすいです。

Release ZIP方式なら、実際に動くPythonコードは自分のRepository内に残ります。

### 外部Repositoryへ毎回依存しない

Profile Signalは定期的に長期間動かします。

一度取り込んだversionが自分のRepositoryへ固定されるため、配布元のmain変更で挙動が急に変わりません。

### 更新前に差分を確認できる

新しいReleaseが出てもruntimeは勝手に更新しません。

新versionのZIPを取得し、`.profile-signal/` の差分を確認してからcommitできます。

プロフィールのように「長く動かすが、常に最新版へ即追従する必要はない」ものには、この更新方法が合っていました。

## OSS本体をProfile Repositoryから分離した

最初のReleaseは自分のGitHub Profile Repository `mizzz-ivr/mizzz-ivr` の中で作っていました。

ただ、配布物が育つにつれて、

- runtime
- tests
- Release builder
- Release Notes
- Wiki source
- Preset Registry

まで個人プロフィールのRepositoryへ同居する状態になりました。

そこで `v0.3.0` で開発・配布のSource of Truthを専用Repositoryへ移しました。

```text
mizzz-ivr/profile-signal
→ OSS本体 / tests / CI / Release / Wiki / 配布Source

mizzz-ivr/mizzz-ivr
→ Consumer / Live Demo / Dogfooding
```

この分離によって、OSSコードと個人プロフィール固有コンテンツの境界もかなり分かりやすくなりました。

<!-- QIITA_IMAGE: 02-standalone-repository.jpg -->

## runtimeは `.profile-signal/` に隔離する

Release ZIPへ入れるruntimeは `.profile-signal/` にまとめています。

`v0.4.0` のRelease builderでは、最低限次のruntimeを必須ファイルとして検証しています。

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
│  ├─ preset_runtime.py
│  └─ stream_runtime.py
└─ scripts/
   ├─ update-profile-activity.py
   ├─ profile_signal.py
   ├─ update-profile-signal.py
   ├─ profile_signal_operations.py
   └─ profile_signal_history.py
```

利用者Repository側のPython fileへ依存しない、自己完結したruntimeとして扱っています。

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

## Presetは8種類をYAML Registryで管理する

現在の公式Presetは8種類です。

```text
minimal
standard
full
terminal
compact
developer
activity
oss
```

Preset数を増やすたびにPythonへ分岐を追加したくなかったので、Preset定義を `.profile-signal/presets/*.yml` へ分離しました。

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

Presetは「どのWidgetを使うか」、Themeは「どう見せるか」と責務を分けています。

## READMEはRelease ZIPに含めない

Release ZIPには利用者の既存READMEを上書きする `README.md` を含めていません。

builderがpackageする主なファイルは次のとおりです。

```text
.profile-signal/
.github/profile-signal.yml
.github/workflows/profile-signal.yml
.github/workflows/profile-signal-stream.yml
PROFILE_SIGNAL_INSTALL.md
PROFILE_SIGNAL_VERSION
```

最初のWorkflow実行時に必要なREADME Markerを追加します。

利用者READMEの見出しを勝手に推測しないため、指定がなければ末尾へ挿入する設計です。

## Public-onlyを初期contractにした

Profile Signal v0.xでは、

```yaml
privacy:
  public_only: true
```

を基本契約にしています。

Private Repository情報を取得してからRendererで隠す設計ではありません。

最初からPublic GitHub APIだけをCollection対象にします。

標準構成ではPATやAPI Keyも不要です。

プロフィールへ公開するツールなので、初期版は安全側へ寄せています。

## ZIPを作るだけではなく、展開して動かすCIを入れた

配布物で一番避けたかったのは、

> 自分のRepositoryでは動くが、Release ZIPだけ持っていくと動かない

という状態です。

そこでRelease Workflowでは、archiveを作った後にclean fixtureへ展開し、実際にruntimeを動かして検証します。

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

Release ZIP自体もbuilderで再現可能に生成し、ZIP entryのtimestampを固定しています。

<!-- QIITA_IMAGE: 03-release-package-ci-success.jpg -->

## v0.4.0ではLatest Signalsを軽量更新へ分けた

最初はProfile全体を同じWorkflowで更新していました。

ただ、`ACTIVITY STREAM` や `CURRENT FOCUS` のような「今」に近い表示まで、重い履歴集計と同じ周期で待たせる必要はありません。

そこで `v0.4.0` では更新責務を分けました。

```text
profile-signal.yml
→ 3時間ごとのFull refresh
→ TODAY / DEV PULSE / CI / History / DEV RECAP など

profile-signal-stream.yml
→ 30分ごとのlightweight refresh
→ LIVE SIGNAL / CURRENT FOCUS / ACTIVITY STREAM
```

軽量runtimeはCIやHistoryなどの既存stateを再計算・破棄せず、live-facingな公開Event由来stateだけを更新します。

表示内容に実質変更がなければcommitもしません。

GitHub Public EventsやGitHub Actionsのschedule自体には遅延があり得るため、ここはリアルタイム保証ではなく「取得できた最新の公開Signal」として扱っています。

## 現在の最新版はv0.4.0

現在のReleaseは `v0.4.0` です。

https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0

Release assetは、

```text
profile-signal-v0.4.0.zip
```

です。

`v0.3.0` でStandalone Repositoryへ移行し、`v0.4.0` でLatest Signalsの軽量更新を追加しました。

<!-- QIITA_IMAGE: 04-release-v0.4.0.jpg -->

Release NotesもRepository内の `release-notes/v0.4.0.md` を元に管理しています。

## 導入手順はかなり短い

### 1. Profile Repositoryを用意

GitHubプロフィールREADME用の、

```text
<username>/<username>
```

Repositoryを使います。

### 2. v0.4.0のRelease ZIPを展開

Release Assetsから、

```text
profile-signal-v0.4.0.zip
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

<!-- QIITA_IMAGE: 05-installed-repository.jpg -->

その後はFull refreshとLatest Signals refreshがscheduleで動きます。

## GitHub WikiもStandalone Repositoryへ移した

継続的なドキュメントはGitHub Wikiへ分けています。

https://github.com/mizzz-ivr/profile-signal/wiki

現在は英語をdefaultにし、日本語ページも用意しています。

Wiki SourceはRepository内の、

```text
docs/wiki/*.md
```

で管理します。

Pull Requestで必須ページや内部リンクを検証し、main更新後にGitHub Wikiへ同期します。

## Standalone化でLicense境界もきれいになった

旧構成ではOSS runtimeと個人Profile README・画像が同じRepositoryに入っていたため、Licenseの適用範囲を慎重に分ける必要がありました。

Standalone化後の `mizzz-ivr/profile-signal` はRepository全体をMIT Licenseとして扱えます。

一方、Consumer側の `mizzz-ivr/mizzz-ivr` にある、

- 個人Profile README本文
- Hero / Avatar画像
- Screenshot
- 個人用文章

などへStandalone OSSのMIT Licenseを自動適用するわけではありません。

OSSと個人コンテンツをRepositoryごと分けたことで、この境界も説明しやすくなりました。

## 更新はruntime差し替えを基本にする

新Releaseへ更新するときは、基本的に、

```text
.profile-signal/
```

を新しいruntimeへ差し替えます。

`.github/profile-signal.yml` は利用者設定なので維持します。

Workflow templateに変更があるReleaseでは、Release Notesを確認して `.github/workflows/` 側も更新します。

自動updateよりも、利用者がdiffを見てからruntimeを更新できることを優先しています。

## OSS化して一番変わったのはコードより境界だった

今回、CollectorやWidgetの計算ロジック自体を全面的に作り直したわけではありません。

それより時間を使ったのは、

- runtimeをどこへ置くか
- user configと何を分離するか
- READMEを上書きしない方法
- Update時に何を残すか
- Private dataをどこで遮断するか
- Release ZIPだけで本当に起動できるか
- 配布コードと個人プロフィールをどう分離するか
- WikiとRepository内ドキュメントをどう同期するか
- Presetをどう増やせるようにするか
- Full refreshとLatest Signalsの責務をどう分けるか

といった境界でした。

自分専用スクリプトなら、「自分のRepositoryではこうだから」で済みます。

配布しようとすると、その前提を一つずつ外す必要があります。

現在は、

- Standalone OSS Repository
- `v0.4.0` Release
- Release ZIP配布
- clean fixture smoke test
- English / 日本語 GitHub Wiki
- MIT License
- YAML Preset Registry
- 8種類の公式Preset
- Full refresh / Latest Signals分離

まで整いました。

自分のプロフィールをConsumer / Live DemoとしてDogfoodingしながら、Profile Signal本体は専用Repositoryで育てる形にしています。