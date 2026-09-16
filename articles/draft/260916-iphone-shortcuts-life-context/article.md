---
title: "iPhoneショートカットの朝ブリーフをChatGPTに直接作らせるのをやめた — WorkersとNotionでlifeへ端末コンテキストを渡す"
emoji: "📱"
type: "tech"
topics: ["iphone", "shortcuts", "cloudflare", "notion", "chatgpt"]
published: false
---

毎朝の予定や天気を、iPhoneのショートカットでまとめたくなりました。

最初に作ったのは、かなり素直な構成です。

```text
現在の日付
  ↓
現在地の天気
  ↓
今日の予定
  ↓
未完了リマインダー
  ↓
バッテリー残量
  ↓
ChatGPTを使用
  ↓
通知を表示
```

これだけでも「朝ブリーフ」っぽいものは作れます。

でも、自分が本当に欲しかったのはこれではありませんでした。

普段の生活管理はChatGPTの `life` というProjectを中心にしていて、NotionにはTasks、配送、契約、重要書類、クラウドの請求アラートなどを集めています。Google Calendarやメールも朝のブリーフに使っています。

つまり、iPhoneが持っている情報だけで新しい朝ブリーフをもう1個作ると、**同じ朝に別々の「今日やること」が2つできる**ことになります。

さらに、自分のiPhoneにあるShortcutsの `ChatGPTを使用` アクションを見ても、Projectとして `life` を選ぶ欄は見当たりませんでした。

そこで方針を変えました。

**iPhoneには判断させず、iPhoneでしか取れない情報だけを `life` へ送る。**

最終的には、こうなりました。

```text
iPhone Shortcut 06:55
  │
  ├─ 現在日時
  ├─ 市区町村程度のエリア
  ├─ 天気
  ├─ Apple Reminders
  └─ バッテリー
        ↓
   HTTPS POST
        ↓
Cloudflare Worker
        ↓
     Notion
📱 iPhone Context Inbox
        ↓
ChatGPT life 07:00
  ├─ Notion Tasks
  ├─ Google Calendar
  ├─ Mail
  ├─ Service Alerts
  ├─ 配送
  └─ iPhone Context
        ↓
    朝ブリーフ
```

この記事では、この構成に変えた理由と実装を書きます。

> **検証状態**
>
> Repository上のWorker実装とNotion側の受信DBまでは作成済みです。公開前に、実機Shortcut → Workers → Notion → 07:00ブリーフまでのE2E結果と、実際にハマった点を追記します。

## ChatGPTを2回使う必要はなかった

最初の構成では、Shortcutの最後に `ChatGPTを使用` を置いていました。

入力するのは、

- 日付
- 天気
- Calendar
- Reminders
- バッテリー

です。

一見すると自然です。

ただ、自分の環境ではGoogle Calendarはもともと `life` 側から取得できます。メールもNotionも同じです。

ShortcutからCalendarを取り出して、ChatGPTへ文字列として渡し直すのは二重管理でした。

一方で、`life` 側から直接は取っていなかったものがあります。

- Apple Reminders
- iPhoneのバッテリー残量
- Shortcut実行時点の現在地を使った天気
- 必要ならFocusなどの端末状態

だったら、iPhoneはこの差分だけ送ればいい。

この時点で、Shortcutの役割を「朝ブリーフを作るもの」から**端末コンテキストを収集するセンサー**へ変えました。

## Notionを中継地点にした

次に悩んだのが、iPhoneから `life` へどうデータを渡すかです。

今回はNotionに `📱 iPhone Context Inbox` というData Sourceを作りました。

持っている項目は小さくしています。

| Property | 内容 |
| --- | --- |
| Context | 受信レコードのタイトル |
| 取得日時 | Shortcutが取得した時刻 |
| エリア | 市区町村程度 |
| 天気 | 朝に必要な短い予報 |
| 未完了リマインダー | Reminderのタイトルだけ |
| バッテリー | 0〜100 |
| Focus | 取得できる場合だけ |
| デバイス | iPhoneなど |
| Shortcut Version | Payload変更時の切り分け用 |
| Source | `iOS Shortcut` |

ここで大事にしたのは、**Notionを位置履歴DBにしない**ことでした。

朝の天気に番地やGPS座標は必要ありません。

そのため、Shortcut側で必要なら位置情報を取得しても、送信するのは市区町村程度に丸めます。

ReminderもNotesや添付などを丸ごと送りません。朝の優先順位付けに必要なタイトルだけです。

## Notion TokenをiPhoneへ入れたくなかった

ShortcutからNotion APIへ直接POSTすることもできます。

でも、その場合はNotion Integration TokenをiPhone側へ持たせることになります。

Shortcutは自分しか使わないとしても、認証情報を端末側のWorkflowへ直接埋め込む構成にはしたくありませんでした。

そこで、間にCloudflare Workersを置きました。

```text
iPhone
  │  INGEST_SECRET
  ▼
Cloudflare Worker
  │  NOTION_TOKEN
  ▼
Notion API
```

iPhoneが知っているのは、Workerへ送るための `INGEST_SECRET` だけです。

Notion TokenはWorker SecretとしてCloudflare側に置きます。

Cloudflare WorkersではSecretをWorkerの `env` から参照できます。また現在のWranglerでは、必要なSecret名を `wrangler.jsonc` の `secrets.required` へ宣言できます。

```json
{
  "secrets": {
    "required": [
      "NOTION_TOKEN",
      "NOTION_DATA_SOURCE_ID",
      "INGEST_SECRET"
    ]
  }
}
```

ローカル開発では `.dev.vars`、デプロイ先では `wrangler secret put` を使います。

Cloudflare公式:

- https://developers.cloudflare.com/workers/configuration/secrets/
- https://developers.cloudflare.com/workers/wrangler/configuration/

## Workerは薄くした

WorkerでAI処理はしていません。

やることは、

1. Endpointを限定する
2. Bearer Secretを確認する
3. JSONであることを確認する
4. Payload sizeを制限する
5. 値の型・長さを最低限検証する
6. Notion APIへ書く

だけです。

Repositoryでは次に置いています。

```text
examples/iphone-life-context-worker/
├─ src/
│  └─ index.js
├─ .dev.vars.example
├─ .gitignore
├─ package.json
├─ README.md
└─ wrangler.jsonc
```

Endpointは2つです。

```text
GET  /health
POST /life/iphone-context
```

受け取るJSONはこうしました。

```json
{
  "captured_at": "2026-09-16T06:55:00+09:00",
  "area": "市区町村程度",
  "weather": "晴れ / 最高28℃ / 最低21℃ / 降水20%",
  "reminders": [
    "記事レビュー",
    "郵便物を発送"
  ],
  "battery": 72,
  "focus": "",
  "device": "iPhone",
  "shortcut_version": "1.0.0"
}
```

Worker側では、たとえばバッテリーなら0〜100以外を弾きます。

```js
function normalizeBattery(value) {
  const battery = Number(value);

  if (!Number.isFinite(battery) || battery < 0 || battery > 100) {
    return null;
  }

  return Math.round(battery);
}
```

Bodyも16KBに制限しました。

これは強固なAPI Gatewayを作るためではありません。

**個人用ShortcutがNotionへ何でも書ける入口にならないように、用途を狭くしておく**ためです。

実装全体はRepositoryの `examples/iphone-life-context-worker` に置いています。

## Notion APIはData Source IDへ書く

今回のNotion APIは `2026-03-11` を使用しています。

Notionの現在のAPIでは、Data SourceへPageを追加するときは `parent.type = data_source_id` としてPOSTします。

```js
const notionBody = {
  parent: {
    type: "data_source_id",
    data_source_id: env.NOTION_DATA_SOURCE_ID,
  },
  properties: {
    // ...
  },
};

await fetch("https://api.notion.com/v1/pages", {
  method: "POST",
  headers: {
    authorization: `Bearer ${env.NOTION_TOKEN}`,
    "content-type": "application/json",
    "notion-version": "2026-03-11",
  },
  body: JSON.stringify(notionBody),
});
```

Notion公式:

- https://developers.notion.com/guides/data-apis/working-with-databases
- https://developers.notion.com/reference/changes-by-version

## Workerをデプロイする

実装ディレクトリへ移動します。

```bash
cd examples/iphone-life-context-worker
npm install
```

Cloudflareへログインします。

```bash
npx wrangler login
```

Secretを設定します。

```bash
npx wrangler secret put NOTION_TOKEN
npx wrangler secret put NOTION_DATA_SOURCE_ID
npx wrangler secret put INGEST_SECRET
```

そのあとデプロイします。

```bash
npm run deploy
```

`wrangler.jsonc` には `secrets.required` を書いているため、必要なSecretが欠けた状態を検出しやすくしています。

Worker URLが決まったら、まず `/health` を確認します。

```bash
curl https://<worker>.workers.dev/health
```

```json
{"ok":true,"service":"life-iphone-context"}
```

## iPhone Shortcut側

ここからiPhone側を変えます。

元のShortcutには最後に、

```text
ChatGPTを使用
↓
通知を表示
```

がありました。

新しい構成では、この2つは朝のContext収集Shortcutから外します。

最終判断は07:00の `life` ブリーフが担当するからです。

Shortcutは次の順番にします。

```text
現在の日付
↓
天気予報
↓
必要なら現在地 → 市区町村だけ取得
↓
リマインダーを検索
  完了済みではない
  期限が今日以前
↓
バッテリー残量を取得
↓
辞書を作る
↓
URLの内容を取得
```

### `辞書` のキー

| Key | Value |
| --- | --- |
| captured_at | 現在日時をISO 8601形式へ整形 |
| area | 市区町村程度 |
| weather | 天気の短いテキスト |
| reminders | Reminder一覧 |
| battery | バッテリー残量 |
| focus | 任意 |
| device | `iPhone` |
| shortcut_version | `1.0.0` |

### `URLの内容を取得`

設定は次の通りです。

```text
URL
https://<worker>.workers.dev/life/iphone-context

メソッド
POST

リクエスト本文
JSON

ヘッダ
Content-Type: application/json
Authorization: Bearer <INGEST_SECRET>
```

ここでもNotion Tokenは使いません。

## 06:55と07:00を分けた

Shortcutを07:00、ChatGPT側のブリーフも07:00にすると、どちらが先に実行されるかを気にすることになります。

そこで5分ずらしました。

```text
06:55 iPhone Shortcut
      ↓
   Notion保存
      ↓
07:00 life Daily Brief
```

life側では、最新Contextが十分新しい場合だけ読みます。

たとえば07:00実行なら、06:55のContextは使う。

前日のContextしかなければ使わない。

この**鮮度チェック**を入れておくと、Shortcutの実行に失敗した日に、古いバッテリーや天気を「今日の情報」として扱わずに済みます。

そしてiPhone Contextが無くても、Calendar、Notion Tasks、メールなどから通常のブリーフは作れます。

ここは自分の中ではかなり重要でした。

Shortcutが落ちたら朝ブリーフ全体も落ちる、という依存関係にはしていません。

## Apple RemindersとNotion Tasksも自動同期しない

もう1つ、最初にやりそうになってやめたことがあります。

Apple Remindersで見つかった項目を、そのままNotion Tasksへ自動登録することです。

自分の運用ではNotion Tasksが正式なTaskのSource of Truthです。

一方、Apple RemindersはiPhone上で一時的に入れるものもあります。

そのため今回のContextでは、Remindersは**朝の優先順位を考えるための補助情報**として扱うだけにしました。

```text
Apple Reminders
  ↓
朝ブリーフでは見る
  ↓
Notion Tasksへ勝手に複製しない
```

必要ならあとで明示的な同期ルールを作れますが、最初から全部同期しない方が自分の運用には合っていました。

## バッテリーは30%未満のときだけ見せる

端末情報も、毎日全部表示するとノイズになります。

そこで最終ブリーフでは、バッテリーが30%以上なら基本的に表示しないことにしました。

外出予定があり、朝の時点で18%なら、

```text
📱 バッテリー
外出前に充電しておいた方がよさそう。
```

と出す。

72%なら何も出さない。

データを取れることと、毎回ユーザーへ見せることは分けています。

## 作ってみて変わったこと

最初は「iPhone ShortcutからChatGPTを呼び出す」が主役でした。

作っている途中で、主役が逆になりました。

```text
Before
iPhone → ChatGPT → 朝ブリーフ

After
iPhone → Contextを提供
             ↓
         lifeが判断
```

CalendarやMailをShortcut側へ寄せなかったことで、iPhoneを使っていない時でも `life` 自体は動けます。

逆にiPhoneでしか取れないものだけが追加Contextになる。

自分の環境では、この境界の方がかなり扱いやすそうです。

## 公開前に確認すること

実機で次を通してから記事を公開します。

- [ ] Shortcutを手動実行してWorkerが201を返す
- [ ] Notionに1件だけContextが追加される
- [ ] 位置情報が市区町村より細かく保存されていない
- [ ] Reminderの不要な本文が保存されていない
- [ ] 06:55 Personal Automationで自動実行される
- [ ] 07:00ブリーフが当日のContextを使う
- [ ] Contextが古い/存在しない日は無視される
- [ ] バッテリー30%以上なら不要な警告を出さない
- [ ] Secretや実URLがスクリーンショット・記事に入っていない

ここで実際に詰まったところが出たら、その内容も追記します。

少なくとも今のところ、朝ブリーフを増やすのではなく、**1つのブリーフへ端末固有Contextを足す**方向にしたのは良かったと思っています。
