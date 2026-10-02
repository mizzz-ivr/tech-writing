# iPhone Shortcuts → life Context Bridge notes

## Article status

- Medium: Qiita
- Status: implementation draft / E2E pending
- Publish only after real-device verification
- Source implementation: `examples/iphone-life-context-worker/`

## Story

Originally the iPhone Shortcut itself generated a morning brief via `ChatGPTを使用`.

Problem:

- the existing `life` workflow already reads Notion / Google Calendar / Mail
- generating another independent brief on iPhone duplicates prioritization
- on the user's current iOS Shortcuts UI, the ChatGPT action did not expose a Project selector for `life`

Decision:

- iPhone = sensor only
- Cloudflare Worker = narrow authenticated ingest boundary
- Notion = durable context bridge
- ChatGPT `life` = final synthesis / prioritization

Do not generalize the Project selector observation beyond the tested UI unless official docs explicitly confirm it.

## Real-device E2E checklist

- [ ] Create/select a Notion integration with access to `📱 iPhone Context Inbox`
- [ ] Set `NOTION_TOKEN` as Worker secret
- [ ] Set `NOTION_DATA_SOURCE_ID`
- [ ] Generate and set `INGEST_SECRET`
- [ ] Deploy Worker
- [ ] `/health` returns 200 JSON
- [ ] Invalid auth returns 401
- [ ] Invalid JSON returns 400
- [ ] Manual curl returns 201 and creates exactly one Notion row
- [ ] Manual iPhone Shortcut run returns success
- [ ] Notion row has `取得日時`, area, weather, reminders, battery
- [ ] No street address / coordinates stored
- [ ] No Reminder notes/body copied unintentionally
- [ ] 06:55 Personal Automation executes without confirmation
- [ ] 07:00 life brief uses a fresh Context
- [ ] 07:00 life brief ignores stale/missing Context
- [ ] Battery warning appears only when useful (initial policy: <30%)
- [ ] Apple Reminders are context only; no automatic Task duplication

## Capture for Qiita

Take screenshots only after masking or avoiding:

- Worker hostname if it reveals anything unwanted
- `INGEST_SECRET`
- Notion Integration Token
- exact location
- Reminder titles containing personal information
- private Notion URLs / IDs if unnecessary

Useful screenshots:

1. Shortcuts action sequence overview
2. Dictionary keys only, with dummy values
3. `URLの内容を取得` screen with endpoint/auth values masked
4. Notion Inbox row using dummy/harmless context
5. Final morning brief showing weather/reminders/battery behavior

## Details to add after E2E

Record actual facts rather than polishing them away:

- time from Shortcut start to Notion row creation
- whether Shortcuts serializes Reminder lists as expected
- how ISO 8601 formatting was configured in Shortcuts
- whether the Authorization header accepts a Text variable cleanly
- behavior when cellular network is unavailable
- behavior if Worker responds non-2xx
- whether Personal Automation ran while phone was locked
- any Notion property mismatch encountered
- any Wrangler secret/deploy gotcha

## Public references to verify before publish

- Cloudflare Workers secrets:
  https://developers.cloudflare.com/workers/configuration/secrets/
- Wrangler config:
  https://developers.cloudflare.com/workers/wrangler/configuration/
- Notion data APIs / create page under data source:
  https://developers.notion.com/guides/data-apis/working-with-databases
- Notion API versions:
  https://developers.notion.com/reference/changes-by-version

## Security decisions

- Notion token never stored in Shortcut
- Worker only accepts one POST endpoint for ingestion
- separate ingest secret for iPhone → Worker
- payload max 16 KiB
- server-side validation and string clipping
- no raw Notion error body returned to iPhone
- coarse area only
- Reminder titles only
- `.dev.vars` excluded from Git

## Potential follow-up article

If there is enough material, a Zenn article could focus on the boundary design rather than setup:

`Personal ContextをAIへ渡すとき、端末・Ingest・State・Reasoningをどう分離したか`

Do not duplicate the Qiita article body; focus on architecture, trust boundaries, stale-context handling and failure isolation.
