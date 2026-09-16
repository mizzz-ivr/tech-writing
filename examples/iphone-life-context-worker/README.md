# iPhone Context → Notion Worker

iOS Shortcuts から朝の端末コンテキストを受け取り、Notion の `📱 iPhone Context Inbox` に保存する Cloudflare Worker です。

## 役割

```text
iPhone Shortcut
  ↓ POST /life/iphone-context
Cloudflare Worker
  ↓ Notion API
📱 iPhone Context Inbox
  ↓
ChatGPT life Daily Brief
```

Shortcut に Notion Integration Token を置かず、Worker 側の Secret に閉じ込めるのが目的です。

## 必要な Secret

- `NOTION_TOKEN`
- `NOTION_DATA_SOURCE_ID`
- `INGEST_SECRET`

`INGEST_SECRET` は Shortcut → Worker 間だけで使う長いランダム文字列です。

## Notion 側

対象 Data Source には次のプロパティが必要です。

- `Context` title
- `取得日時` date
- `エリア` rich text
- `天気` rich text
- `未完了リマインダー` rich text
- `バッテリー` number
- `Focus` rich text
- `デバイス` rich text
- `Shortcut Version` rich text
- `Source` select（`iOS Shortcut`）

Notion Integration へ対象 Data Source のアクセス権を付与してください。

## ローカル確認

```bash
cd examples/iphone-life-context-worker
npm install
cp .dev.vars.example .dev.vars
# .dev.vars を編集
npm run dev
```

別ターミナルから:

```bash
curl -i http://localhost:8787/life/iphone-context \
  -H 'Authorization: Bearer YOUR_INGEST_SECRET' \
  -H 'Content-Type: application/json' \
  --data '{
    "captured_at":"2026-09-16T06:55:00+09:00",
    "area":"東京都内",
    "weather":"晴れ / 最高28℃ / 最低21℃ / 降水20%",
    "reminders":["記事レビュー","郵便物を発送"],
    "battery":72,
    "focus":"",
    "device":"iPhone",
    "shortcut_version":"1.0.0"
  }'
```

成功すると HTTP `201` と `{"ok":true,...}` が返り、Notion に1行追加されます。

## Cloudflare へ deploy

Cloudflare の公式 Wrangler を使います。

```bash
npm install
npx wrangler login
npx wrangler secret put NOTION_TOKEN
npx wrangler secret put NOTION_DATA_SOURCE_ID
npx wrangler secret put INGEST_SECRET
npm run deploy
```

デプロイ後、`https://<worker>.workers.dev/health` で `{"ok":true}` が返ることを確認します。

## iOS Shortcuts

Shortcut 側では JSON を作成し、`URLの内容を取得` で送信します。

- URL: `https://<worker>.workers.dev/life/iphone-context`
- Method: `POST`
- Request Body: `JSON`
- Header `Content-Type`: `application/json`
- Header `Authorization`: `Bearer <INGEST_SECRET>`

Payload:

```json
{
  "captured_at": "2026-09-16T06:55:00+09:00",
  "area": "市区町村程度",
  "weather": "晴れ / 最高28℃ / 最低21℃ / 降水20%",
  "reminders": ["未完了Reminder 1", "未完了Reminder 2"],
  "battery": 72,
  "focus": "",
  "device": "iPhone",
  "shortcut_version": "1.0.0"
}
```

### 推奨実行時刻

- 06:55: iPhone Personal Automation
- 07:00: life Daily Brief

07:00 側では、最新 Context が十分新しい場合だけ利用します。取得に失敗した日は、iPhone Context を推測で補完しません。

## Security / Privacy

- Notion Token を Shortcut に保存しない。
- 正確な GPS・番地は送らず、市区町村程度へ丸める。
- Worker は Bearer Secret・Content-Type・payload size・型を検証する。
- Reminder は必要なタイトルだけ送り、Notes などの本文を不要に送らない。
- Worker の Secret は `vars` ではなく Cloudflare Secret に保存する。
- Notion API の raw error response は iPhone へ返さない。

## API

### `GET /health`

認証不要の簡易 health check。

### `POST /life/iphone-context`

`Authorization: Bearer <INGEST_SECRET>` が必須です。

Notion API version は `2026-03-11` を使用しています。
