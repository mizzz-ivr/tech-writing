---
title: 自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた
tags:
  - GitHubActions
  - GitHub
  - Python
  - OSS
  - 個人開発
private: true
updated_at: '2026-08-28T09:27:51+09:00'
id: f20a2d58f623097a5904
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# 自作GitHubプロフィールWidgetをStandalone OSSとして配布してみた

前回は、GitHubプロフィールREADMEを `LIVE SIGNAL`、`CURRENT FOCUS`、`DEV PULSE`、`ACTIVITY STREAM` などを使った開発ダッシュボードへ広げました。

https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630

実際のプロフィールはこちらです。

https://github.com/mizzz-ivr

今回は、その自分用の仕組みを **他の人も自分のGitHub Profile Repositoryへ入れられるStandalone OSS** にした話です。

Source of Truthは次のRepositoryです。

https://github.com/mizzz-ivr/profile-signal

## 自分用コードをそのまま配るのは難しかった

最初は、一般的なGitHub Actionのように、

```yaml
- uses: mizzz-ivr/profile-signal@v1
```

と外部Repositoryから直接呼ぶ形を考えていました。

ただ、Profile SignalはREADMEを書き換えるだけではありません。

- Activity履歴
- 計算済みstate
- SVG
- Preset / Theme設定

などをProfile Repository側へ継続して残します。

そのため、外部Actionというより **Profile Repositoryの中で動き続けるruntime** に近いと考えました。

## Release ZIP + local runtimeにした

最終的な配布方法はこうしました。

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

Workflowからは、利用者Repository内へ展開したruntimeを実行します。

```yaml
- uses: ./.profile-signal
  with:
    config: .github/profile-signal.yml
```

この方式にした理由はシンプルです。

- 実行コードを自分のRepository内で確認できる
- 導入versionを固定できる
- 新Releaseへ更新する前にdiffを確認できる
- 利用者設定とruntimeを分離しやすい

プロフィールのように長期間動かすものでは、勝手に最新版へ追従するより扱いやすいと判断しました。

## OSS本体を専用Repositoryへ分離した

最初は `mizzz-ivr/mizzz-ivr` の中で開発していましたが、runtime、tests、Release、Wikiまで増えてきたため、`v0.3.0` で専用Repositoryへ分離しました。

```text
mizzz-ivr/profile-signal
→ OSS本体 / CI / Release / Wiki

mizzz-ivr/mizzz-ivr
→ Consumer / Live Demo / Dogfooding
```

![IMG_3770.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4394245/a0ce3241-e6a0-44ce-89dc-bd2724ce7b84.jpeg)

これで「配布するOSS」と「自分のプロフィール固有コンテンツ」の境界がかなり分かりやすくなりました。

## runtimeと利用者設定を分けた

runtimeは `.profile-signal/`、利用者が触る設定は `.github/profile-signal.yml` に分けています。

```yaml
version: 1

profile:
  username: YOUR_GITHUB_USERNAME
  timezone: Asia/Tokyo

privacy:
  public_only: true

preset: developer
theme: signal
```

現在は8種類のPresetを用意しています。

```text
minimal / standard / full / terminal
compact / developer / activity / oss
```

標準構成はpublic-onlyで、PATやAPI Keyは不要です。

## v0.4.0で「重い更新」と「最新表示」を分けた

Profile全体を毎回更新すると、履歴集計やCI取得まで毎回走ります。

そこで `v0.4.0` では更新を2つに分けました。

```text
profile-signal.yml
→ 3時間ごとのFull refresh
→ TODAY / DEV PULSE / CI / History / DEV RECAP など

profile-signal-stream.yml
→ 30分ごとのLatest Signals refresh
→ LIVE SIGNAL / CURRENT FOCUS / ACTIVITY STREAM
```

Latest Signals側では、重いAnalytics stateを壊さず、表示に変化がある場合だけcommitします。

GitHub Public EventsやGitHub Actions scheduleには遅延があり得るため、リアルタイム保証ではなく「取得できた最新の公開Signal」として扱っています。

## 現在の最新版はv0.4.0

現在のReleaseは `v0.4.0` です。

https://github.com/mizzz-ivr/profile-signal/releases/tag/v0.4.0

Release assetは `profile-signal-v0.4.0.zip` です。

ZIPは作って終わりではなく、CIで展開してruntimeを実行するsmoke testも入れています。

## 導入後の見た目はSample Profileで確認できる

実際のConsumer Repositoryは個人プロフィール固有の内容が多いため、Standalone Repository側に固定データのSample Profileを用意しました。

https://github.com/mizzz-ivr/profile-signal/tree/main/examples/sample-profile

![IMG_3774.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4394245/bc017304-a056-4bc1-9096-436fc4177385.jpeg)

`LIVE SIGNAL`、`TODAY`、`CURRENT FOCUS`、`DEV PULSE`、`NOW BUILDING`、`ACTIVITY STREAM`、`DEV RECAP` をGitHub上で確認できます。

値はすべてサンプルなので、導入前の確認やドキュメントにも使えます。

## 導入は5ステップ

1. `<username>/<username>` のProfile Repositoryを用意する
2. Release ZIPをRepository rootへ展開する
3. `.github/profile-signal.yml` のusernameとPresetを変更する
4. commit / pushする
5. Actionsから `Profile Signal` を一度手動実行する

以降はFull refreshとLatest Signals refreshがscheduleで動きます。

## まとめ

今回やったことは、Widgetを増やすことよりも **自分専用コードの前提を外すこと** でした。

特に重要だったのは、

- OSS本体とConsumerを分ける
- runtimeと利用者設定を分ける
- Release ZIPでversionを固定する
- public-onlyを初期contractにする
- 重い集計とLatest Signalsを分ける

という境界です。

現在は、Standalone Repository、Release ZIP、8 Preset、Wiki、Sample Profile、Full / Latest Signals分離まで整いました。

自分のGitHubプロフィールをLive Demoとして使いながら、Profile Signal本体はStandalone OSSとして育てていきます。
