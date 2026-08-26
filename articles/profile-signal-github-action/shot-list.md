# Shot List — Profile Signal GitHub Action

Qiita #3用。

## Required

### 01. PR #23 local Action CI success

見せたいもの:

- `Generate Profile Signal preview through local action` success
- validation success
- Secret / Tokenが映らない範囲

目的:

- Python直呼びではなくComposite Action経由で実データ生成まで通っていることを示す。

### 02. `.github/profile-signal.yml`

見せたい部分:

```yaml
preset: full
theme: signal
widgets:
  ...
```

Screenshotよりコードブロックで十分なら省略可。

### 03. Preset examples

Repository treeで:

```text
examples/minimal.yml
examples/standard.yml
examples/full.yml
examples/terminal.yml
```

が見える状態。

### 04. External install

`mizzz-ivr/profile-signal`切り出し後に必須。

Consumer側Workflow:

```yaml
uses: mizzz-ivr/profile-signal@v1
```

が見える画面。

### 05. External profile result

Sample / fixture Profile READMEで、Action導入後のWidget表示。

自分のProfile Screenshotだけだと「自分専用」から脱した証明にならないため、v1公開記事では優先度高。

## Optional

### 06. Theme comparison

signal / minimal / terminalを並べる。

Qiita記事内で縦に3枚置くより、1枚の比較画像へまとめられると良い。

### 07. Marker auto insert before/after

導入前READMEと、Action初回実行後READMEのdiff。

## Safety

- [ ] Token / Secretなし
- [ ] Private Repositoryなし
- [ ] third-party notificationなし
- [ ] test consumerに個人情報なし
- [ ] `GITHUB_TOKEN`値やAuthorization headerなし
