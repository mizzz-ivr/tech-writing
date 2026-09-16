const NOTION_VERSION = "2026-03-11";
const MAX_BODY_BYTES = 16 * 1024;
const MAX_TEXT = 1800;

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

function text(value, max = MAX_TEXT) {
  if (value == null) return "";
  return String(value).trim().slice(0, max);
}

function remindersText(value) {
  if (Array.isArray(value)) {
    return value
      .slice(0, 20)
      .map((item) => text(item, 160))
      .filter(Boolean)
      .map((item) => `- ${item}`)
      .join("\n")
      .slice(0, MAX_TEXT);
  }
  return text(value);
}

function richText(content) {
  if (!content) return { rich_text: [] };
  return {
    rich_text: [
      {
        type: "text",
        text: { content },
      },
    ],
  };
}

function isValidCapturedAt(value) {
  if (typeof value !== "string" || value.length > 80) return false;
  const time = Date.parse(value);
  return Number.isFinite(time);
}

function normalizeBattery(value) {
  const battery = Number(value);
  if (!Number.isFinite(battery) || battery < 0 || battery > 100) return null;
  return Math.round(battery);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "life-iphone-context" });
    }

    if (request.method !== "POST" || url.pathname !== "/life/iphone-context") {
      return json({ ok: false, error: "not_found" }, 404);
    }

    const expectedAuth = `Bearer ${env.INGEST_SECRET ?? ""}`;
    if (!env.INGEST_SECRET || request.headers.get("authorization") !== expectedAuth) {
      return json({ ok: false, error: "unauthorized" }, 401);
    }

    const contentType = request.headers.get("content-type") ?? "";
    if (!contentType.toLowerCase().includes("application/json")) {
      return json({ ok: false, error: "content_type_must_be_json" }, 415);
    }

    const contentLength = Number(request.headers.get("content-length"));
    if (Number.isFinite(contentLength) && contentLength > MAX_BODY_BYTES) {
      return json({ ok: false, error: "payload_too_large" }, 413);
    }

    let raw;
    try {
      raw = await request.text();
      if (new TextEncoder().encode(raw).byteLength > MAX_BODY_BYTES) {
        return json({ ok: false, error: "payload_too_large" }, 413);
      }
    } catch {
      return json({ ok: false, error: "invalid_body" }, 400);
    }

    let payload;
    try {
      payload = JSON.parse(raw);
    } catch {
      return json({ ok: false, error: "invalid_json" }, 400);
    }

    if (!isValidCapturedAt(payload.captured_at)) {
      return json({ ok: false, error: "captured_at_is_required_iso8601" }, 400);
    }

    const battery = normalizeBattery(payload.battery);
    const area = text(payload.area, 120);
    const weather = text(payload.weather);
    const reminders = remindersText(payload.reminders);
    const focus = text(payload.focus, 120);
    const device = text(payload.device, 120) || "iPhone";
    const shortcutVersion = text(payload.shortcut_version, 40);

    if (!env.NOTION_TOKEN || !env.NOTION_DATA_SOURCE_ID) {
      return json({ ok: false, error: "worker_not_configured" }, 500);
    }

    const notionBody = {
      parent: {
        type: "data_source_id",
        data_source_id: env.NOTION_DATA_SOURCE_ID,
      },
      properties: {
        Context: {
          title: [
            {
              type: "text",
              text: { content: `${device} ${payload.captured_at}`.slice(0, 200) },
            },
          ],
        },
        "取得日時": {
          date: { start: payload.captured_at },
        },
        "エリア": richText(area),
        "天気": richText(weather),
        "未完了リマインダー": richText(reminders),
        "バッテリー": {
          number: battery,
        },
        Focus: richText(focus),
        "デバイス": richText(device),
        "Shortcut Version": richText(shortcutVersion),
        Source: {
          select: { name: "iOS Shortcut" },
        },
      },
    };

    let notionResponse;
    try {
      notionResponse = await fetch("https://api.notion.com/v1/pages", {
        method: "POST",
        headers: {
          authorization: `Bearer ${env.NOTION_TOKEN}`,
          "content-type": "application/json",
          "notion-version": NOTION_VERSION,
        },
        body: JSON.stringify(notionBody),
      });
    } catch (error) {
      console.error("notion_network_error", error);
      return json({ ok: false, error: "notion_unreachable" }, 502);
    }

    const notionText = await notionResponse.text();
    let notionJson = null;
    try {
      notionJson = JSON.parse(notionText);
    } catch {
      // Keep null. We intentionally do not send Notion's raw response to the iPhone.
    }

    if (!notionResponse.ok) {
      console.error(
        "notion_create_failed",
        notionResponse.status,
        notionJson?.code ?? "unknown",
        notionJson?.message ?? "unknown",
      );
      return json(
        {
          ok: false,
          error: "notion_create_failed",
          status: notionResponse.status,
          code: notionJson?.code ?? null,
        },
        502,
      );
    }

    return json(
      {
        ok: true,
        page_id: notionJson?.id ?? null,
        captured_at: payload.captured_at,
      },
      201,
    );
  },
};
