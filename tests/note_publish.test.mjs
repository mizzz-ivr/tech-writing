import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  NOTE_NEW_URL,
  findNoteCompatibilityWarnings,
  readNoteMarkdown,
  stripRepositoryFrontMatter,
  usage,
} from "../scripts/note_publish.mjs";

test("stripRepositoryFrontMatter removes repository metadata and preserves Markdown body", () => {
  const source = `---\ntitle: note draft\nstatus: draft\npublished:\n  note: null\n---\n\n# Heading\n\n- item 1\n- item 2\n\n\`\`\`js\nconsole.log("ok");\n\`\`\`\n`;
  const expected = `\n# Heading\n\n- item 1\n- item 2\n\n\`\`\`js\nconsole.log("ok");\n\`\`\`\n`;

  assert.equal(stripRepositoryFrontMatter(source), expected);
});

test("stripRepositoryFrontMatter leaves Markdown without front matter unchanged", () => {
  const source = "# Heading\n\nBody with **bold** and [link](https://example.com).\n";
  assert.equal(stripRepositoryFrontMatter(source), source);
});

test("stripRepositoryFrontMatter rejects malformed front matter", () => {
  assert.throws(
    () => stripRepositoryFrontMatter("---\ntitle: broken\n# body\n"),
    /no standalone closing '---' delimiter/,
  );
});

test("findNoteCompatibilityWarnings detects GitHub-style Markdown tables", () => {
  const markdown = `# Heading\n\n| Service | Role |\n| --- | --- |\n| Qiita | How |\n| note | Why |\n`;
  const warnings = findNoteCompatibilityWarnings(markdown);

  assert.equal(warnings.length, 1);
  assert.match(warnings[0], /Markdown table detected/);
  assert.match(warnings[0], /note does not support GitHub-style Markdown tables/);
});

test("findNoteCompatibilityWarnings ignores table-like text inside fenced code blocks", () => {
  const markdown = `# Heading\n\n\`\`\`md\n| Service | Role |\n| --- | --- |\n| Qiita | How |\n\`\`\`\n`;

  assert.deepEqual(findNoteCompatibilityWarnings(markdown), []);
});

test("readNoteMarkdown rejects missing files", () => {
  assert.throws(
    () => readNoteMarkdown("missing.md", os.tmpdir()),
    /Markdown file does not exist/,
  );
});

test("readNoteMarkdown reads UTF-8 Markdown and strips repository front matter", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "note-publish-"));
  const file = path.join(dir, "article.md");
  fs.writeFileSync(file, "---\ntitle: 日本語\n---\n\n# 本文\n", "utf8");

  try {
    const result = readNoteMarkdown(file);
    assert.equal(result.resolvedPath, file);
    assert.equal(result.markdown, "\n# 本文\n");
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("usage includes the official note new-post shortcut", () => {
  assert.equal(NOTE_NEW_URL, "https://note.com/new");
  assert.match(usage(), /https:\/\/note\.com\/new/);
  assert.match(usage(), /publish <markdown-file>/);
});
