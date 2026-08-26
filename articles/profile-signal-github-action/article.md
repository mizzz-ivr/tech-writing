---
title: "自作GitHubプロフィールWidgetをGitHub Actionとして配布できる形にしてみた"
status: draft
topics: [GitHubActions, GitHub, Python, OSS, 個人開発]
source_repositories: [mizzz-ivr/mizzz-ivr]
published:
  qiita: null
  zenn: null
---

# 自作GitHubプロフィールWidgetをGitHub Actionとして配布できる形にしてみた

GitHubプロフィールに `TODAY` を作って、そこから `LIVE SIGNAL`、`CURRENT FOCUS`、`DEV PULSE`、`NOW BUILDING`、`ACTIVITY STREAM`、`DEV RECAP` まで増やしていきました。

最初は完全に自分用でした。

でも、Widgetが増えてくると少し欲が出ました。

**これ、自分のREADME専用スクリプトではなく、好きなパーツだけ選んで他の人も使えるようにできないか。**

そこで今までプロフィールRepositoryに直接置いていたPythonスクリプトを、GitHub Actionとして切り出せる形へ変え始めました。

ただ、いきなり新しいRepositoryへコピーするのはやめました。

まず今動いている自分のプロフィール自身を、そのActionの最初の利用者にすることにしました。

```text
current Profile Signal scripts
        ↓
config-driven orchestrator
        ↓
local composite action
        ↓
mizzz-ivr/mizzz-ivr でDogfooding
        ↓
別Repositoryへ切り出す
```

この記事は、このDogfooding段階から実際に配布Repositoryへ移すまでを記録する予定です。

## そのままスクリプトを公開するだけでは足りなかった

Profile Signalは最初、自分のProfile Repositoryを前提に作っています。

例えばデータの保存先は固定です。

```text
data/activity/
data/weekly/
data/monthly/
data/profile-signal-state.json
assets/dev-pulse.svg
README.md
```

README Markerも自分の構成に合わせて増えていきました。

```md
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:START -->
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:END -->

<!-- PROFILE-SIGNAL:FOCUS:START -->
<!-- PROFILE-SIGNAL:FOCUS:END -->
```

このままコードだけコピーしても、使う人がPythonファイルを読んで自分用に書き換えないといけません。

それだと「配布」というより「ソースを置いただけ」です。

欲しかったのは、設定ファイルで次のように選べる形でした。

```yaml
preset: standard
theme: signal

widgets:
  activity_stream:
    enabled: false
  now_building:
    enabled: true
```

## 最初にPresetを4つにした

全部のWidgetを個別設定できるだけでも動きますが、初見で7個のON/OFFを決めるのは面倒です。

そこで最初にPresetを用意しました。

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

自分のプロフィールは `full` を使います。

```yaml
preset: full
theme: signal
```

そのうえで個別設定がPresetを上書きします。

```yaml
widgets:
  dev_recap:
    enabled: false
```

これなら、とりあえず `standard` で始めて、気になったものだけ変えられます。

## LIVE TERMINALはWidgetではなくThemeにした

最初の機能案には `LIVE TERMINAL` もありました。

でも実装を整理していくと、これはデータそのものではありません。

同じ `CURRENT FOCUS` でも、通常表示ならこうです。

```text
CURRENT FOCUS
mizzz-ivr/ivmz-home
34% weighted activity
```

Terminal風ならこうできます。

```text
mizzz@github:~$ current-focus
project  mizzz-ivr/ivmz-home
share    34%
score    117
```

なのでAction版では、WidgetとRendererを分ける方向にしました。

初期Themeは3つです。

```text
signal
minimal
terminal
```

まだデザインとして完成させる余地はありますが、config contractとして先に分けておくことにしました。

## Markerは利用者が全部手で置かなくてもいいようにした

Marker方式自体は、自動更新する範囲を限定できるので気に入っています。

一方で、導入手順に

> READMEへMarkerを7組コピーしてください

と書くのは微妙でした。

そこで、設定したWidgetのMarkerがREADMEに存在しなければ、自動挿入できるようにしました。

```yaml
readme:
  path: README.md
  auto_insert_markers: true
  insert_before: "## About me"
```

指定した見出しがあればその直前へ追加し、なければREADME末尾へ追加します。

逆に配置を完全に自分で決めたい場合は、

```yaml
auto_insert_markers: false
```

にできます。

### OFFにしてもMarker位置は残す

一度表示したWidgetをOFFにしたとき、Markerごと削除すると再度ONにしたときの配置が分からなくなります。

そのためデフォルトでは、

```md
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:START -->
<!-- PROFILE-SIGNAL:LIVE-SIGNAL:END -->
```

だけ残して中身を空にします。

再度有効化すれば、同じ場所へ戻せます。

小さい仕様ですが、「好きなパーツだけ使える」をやるなら必要でした。

## Public-onlyはconfigでも外せないようにした

Profile Signalは公開プロフィールへ出す情報なので、これまでと同じくPrivate Activityは対象にしません。

初期版ではconfigに、

```yaml
privacy:
  public_only: true
```

を持たせています。

現時点では `false` にするとエラーにしています。

これは設定項目というより、v0の契約を明示するために置いています。

Private Activityを取得してからRendererで隠すのではなく、最初からPublic APIだけを読む方針です。

## いきなり別Repositoryへ移さずLocal Actionにした

今回一番大きかった判断はここでした。

最終的には、

```yaml
- uses: mizzz-ivr/profile-signal@v1
```

で使える形にしたいです。

でも、いきなり今のスクリプトを新Repositoryへコピーすると、動いているプロフィールと配布版がすぐ別物になります。

そこで一度、現在のRepository内にComposite Actionを作りました。

```text
profile-signal-action/
├─ action.yml
├─ src/
│  └─ orchestrator.py
├─ examples/
│  ├─ minimal.yml
│  ├─ standard.yml
│  ├─ full.yml
│  └─ terminal.yml
└─ README.md
```

Workflow側は、今までの

```yaml
run: |
  python scripts/update-profile-activity.py
  python scripts/update-profile-signal.py
  python scripts/profile_signal_operations.py
  python scripts/profile_signal_history.py
```

から、

```yaml
- uses: ./profile-signal-action
  with:
    config: .github/profile-signal.yml
```

へ変更しました。

つまり自分のプロフィールが、配布前Actionの最初のConsumerです。

## 既存スクリプトを全部書き直さずOrchestratorを挟んだ

ここも少し悩みました。

本来ならCollector / Analytics / Rendererを綺麗にpackage化してからActionにする方が見た目は良いです。

ただ、Phase 1〜4まで実運用している処理を一気に書き直すと、Action化とリファクタリングの不具合を切り分けにくくなります。

そこで今回はOrchestratorを追加しました。

Orchestratorが、

- configを読む
- 必要な収集Phaseを判断する
- consumer workspaceへ出力先を向ける
- 既存Collector / Analyticsを呼ぶ
- 有効WidgetだけREADMEへ反映する

という役割を持ちます。

```text
profile-signal.yml
      ↓
Orchestrator
      ├─ TODAY Collector
      ├─ Profile Analytics
      ├─ Operations / CI
      └─ History
             ↓
      Widget Renderer
             ↓
      Consumer README
```

これで既存ロジックを保ったまま、配布時のcontractを先にDogfoodできます。

## Action経由で24 tests + 実APIまで通した

Action化すると、config parserだけunit testが通っていてもあまり安心できません。

実際にlocal ActionをWorkflowから実行しました。

PR上では、既存Phase 1〜4のテストにAction用テストを追加しています。

```text
24 tests
```

Action側で確認しているのは、

- Preset解決
- Widget override
- terminal preset
- public-only enforcement
- Marker自動挿入
- OFF時の空Marker

です。

さらにPR CIではlocal Actionそのものを実行し、Public GitHub APIから実データを取得しています。

```text
local composite action
        ↓
Public GitHub API
        ↓
Profile Signal state v4
        ↓
Daily / Weekly / Monthly
        ↓
README 7 widgets
        ↓
SVG parse
```

この状態でCIが通ってから、自分のScheduled WorkflowをAction経由へ切り替える予定にしています。

<!-- QIITA_IMAGE: 01-local-action-ci-success.jpg -->

## 導入手順は3ステップに寄せたい

最終版では、使う側の作業を次くらいにしたいです。

### 1. Configを置く

```text
.github/profile-signal.yml
```

### 2. WorkflowからActionを呼ぶ

```yaml
- uses: mizzz-ivr/profile-signal@v1
  with:
    config: .github/profile-signal.yml
```

### 3. 生成結果をCommitする

Action自体はまず「生成」に責務を絞り、Commit / Pushは利用側Workflowに残しています。

GitHub Actionsの権限やBranch protectionはRepositoryごとに違うので、初期版では分けた方が扱いやすいと判断しました。

## まだ「OSS化完了」ではない

この記事のSourceを書き始めた時点では、local ActionとしてのDogfoodingまでです。

残っているのは、

- `mizzz-ivr/profile-signal` Repository作成
- package移動
- external profile fixtureでのinstallation smoke test
- `v1` tag / release
- examples gallery
- config referenceの整理

です。

このあたりは実際に進めながら記事も更新します。

自分用の仕組みをOSSへ持っていくとき、コードを公開するだけではなく、**他のRepositoryから呼ばれる前提の境界を作るところが一番大きな作業だった**、というのが今のところの感想です。
