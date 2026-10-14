import assert from "node:assert/strict";
import test from "node:test";

import worker from "../src/index.js";

const env = {
  INGEST_SECRET: "test-ingest-secret",
  NOTION_TOKEN: "test-notion-token",
  NOTION_DATA_SOURCE_ID: "test-data-source-id",
};

function request(path, init = {}) {
  return new Request(`https://example.test${path}`, init);
}

test("GET /health returns ok", async () => {
  const response = await worker.fetch(request("/health"), env);

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    ok: true,
    service: "life-iphone-context",
  });
});

test("POST requires bearer auth", async () => {
  const response = await worker.fetch(
    request("/life/iphone-context", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ captured_at: "2026-09-16T06:55:00+09:00" }),
    }),
    env,
  );

  assert.equal(response.status, 401);
  assert.equal((await response.json()).error, "unauthorized");
});

test("POST rejects malformed JSON", async () => {
  const response = await worker.fetch(
    request("/life/iphone-context", {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.INGEST_SECRET}`,
        "content-type": "application/json",
      },
      body: "{",
    }),
    env,
  );

  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, "invalid_json");
});

test("valid context is mapped to Notion properties", async (t) => {
  const originalFetch = globalThis.fetch;
  let notionRequest;

  globalThis.fetch = async (url, init) => {
    notionRequest = { url, init };
    return new Response(JSON.stringify({ id: "page-123" }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const payload = {
    captured_at: "2026-09-16T06:55:00+09:00",
    area: "市区町村程度",
    weather: "晴れ / 最高28℃ / 最低21℃ / 降水20%",
    reminders: ["記事レビュー", "郵便物を発送"],
    battery: 72,
    focus: "",
    device: "iPhone",
    shortcut_version: "1.0.0",
  };

  const response = await worker.fetch(
    request("/life/iphone-context", {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.INGEST_SECRET}`,
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    }),
    env,
  );

  assert.equal(response.status, 201);
  assert.deepEqual(await response.json(), {
    ok: true,
    page_id: "page-123",
    captured_at: payload.captured_at,
  });

  assert.equal(notionRequest.url, "https://api.notion.com/v1/pages");
  assert.equal(notionRequest.init.method, "POST");
  assert.equal(
    notionRequest.init.headers.authorization,
    `Bearer ${env.NOTION_TOKEN}`,
  );
  assert.equal(notionRequest.init.headers["notion-version"], "2026-03-11");

  const notionBody = JSON.parse(notionRequest.init.body);
  assert.deepEqual(notionBody.parent, {
    type: "data_source_id",
    data_source_id: env.NOTION_DATA_SOURCE_ID,
  });
  assert.equal(notionBody.properties["バッテリー"].number, 72);
  assert.equal(
    notionBody.properties["未完了リマインダー"].rich_text[0].text.content,
    "- 記事レビュー\n- 郵便物を発送",
  );
});
