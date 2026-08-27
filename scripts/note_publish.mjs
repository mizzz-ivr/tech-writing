#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const NOTE_NEW_URL = "https://note.com/new";

export function stripRepositoryFrontMatter(markdown) {
  const text = markdown.replace(/^\uFEFF/, "");
  if (!text.startsWith("---\n") && !text.startsWith("---\r\n")) {
    return text;
  }

  const closingDelimiter = /\r?\n---(?:\r?\n|$)/g;
  closingDelimiter.lastIndex = text.indexOf("\n") + 1;
  const match = closingDelimiter.exec(text);

  if (!match) {
    throw new Error(
      "YAML front matter starts with '---' but has no standalone closing '---' delimiter.",
    );
  }

  return text.slice(match.index + match[0].length);
}

export function readNoteMarkdown(filePath, cwd = process.cwd()) {
  if (!filePath) {
    throw new Error("Markdown file path is required.");
  }

  const resolvedPath = path.resolve(cwd, filePath);
  if (!fs.existsSync(resolvedPath)) {
    throw new Error(`Markdown file does not exist: ${resolvedPath}`);
  }

  const stat = fs.statSync(resolvedPath);
  if (!stat.isFile()) {
    throw new Error(`Markdown path is not a file: ${resolvedPath}`);
  }

  const markdown = fs.readFileSync(resolvedPath, "utf8");
  const noteMarkdown = stripRepositoryFrontMatter(markdown);

  if (!noteMarkdown.trim()) {
    throw new Error(`Markdown body is empty: ${resolvedPath}`);
  }

  return { resolvedPath, markdown: noteMarkdown };
}

function runCommand(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: ["pipe", "pipe", "pipe"],
    ...options,
  });

  if (result.error) {
    return { ok: false, error: result.error };
  }
  if (result.status !== 0) {
    return {
      ok: false,
      error: new Error(result.stderr?.trim() || `${command} exited with ${result.status}`),
    };
  }

  return { ok: true };
}

function copyWithPowerShell(markdown) {
  return runCommand(
    "powershell.exe",
    [
      "-NoProfile",
      "-NonInteractive",
      "-Command",
      "[Console]::In.ReadToEnd() | Set-Clipboard",
    ],
    { input: markdown },
  );
}

export function copyMarkdownToClipboard(markdown, platform = process.platform) {
  if (platform === "win32") {
    const result = copyWithPowerShell(markdown);
    if (!result.ok) throw result.error;
    return "PowerShell Set-Clipboard";
  }

  if (platform === "darwin") {
    const result = runCommand("pbcopy", [], { input: markdown });
    if (!result.ok) throw result.error;
    return "pbcopy";
  }

  if (platform === "linux") {
    if (process.env.WSL_DISTRO_NAME || process.env.WSL_INTEROP) {
      const powershell = copyWithPowerShell(markdown);
      if (powershell.ok) return "PowerShell Set-Clipboard (WSL)";
    }

    const candidates = [
      ["wl-copy", []],
      ["xclip", ["-selection", "clipboard"]],
      ["xsel", ["--clipboard", "--input"]],
    ];

    for (const [command, args] of candidates) {
      const result = runCommand(command, args, { input: markdown });
      if (result.ok) return command;
    }

    throw new Error(
      "No supported clipboard command is available. Install wl-copy, xclip, or xsel.",
    );
  }

  throw new Error(`Clipboard copy is not supported on platform: ${platform}`);
}

export function openNoteEditor(platform = process.platform) {
  if (platform === "win32") {
    const result = runCommand("powershell.exe", [
      "-NoProfile",
      "-NonInteractive",
      "-Command",
      `Start-Process '${NOTE_NEW_URL}'`,
    ]);
    if (!result.ok) throw result.error;
    return;
  }

  if (platform === "darwin") {
    const result = runCommand("open", [NOTE_NEW_URL]);
    if (!result.ok) throw result.error;
    return;
  }

  if (platform === "linux") {
    if (process.env.WSL_DISTRO_NAME || process.env.WSL_INTEROP) {
      const powershell = runCommand("powershell.exe", [
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        `Start-Process '${NOTE_NEW_URL}'`,
      ]);
      if (powershell.ok) return;
    }

    const result = runCommand("xdg-open", [NOTE_NEW_URL]);
    if (!result.ok) throw result.error;
    return;
  }

  throw new Error(`Opening the note editor is not supported on platform: ${platform}`);
}

export function usage() {
  return `Usage:\n  node scripts/note_publish.mjs copy <markdown-file>\n  node scripts/note_publish.mjs open\n  node scripts/note_publish.mjs publish <markdown-file>\n\nCommands:\n  copy     Copy Markdown body to the clipboard. Repository YAML front matter is removed.\n  open     Open ${NOTE_NEW_URL} in the default browser.\n  publish  Copy Markdown body, then open ${NOTE_NEW_URL}.`;
}

export function run(argv = process.argv.slice(2)) {
  const [command, filePath] = argv;

  if (!command || command === "--help" || command === "-h") {
    console.log(usage());
    return 0;
  }

  if (command === "open") {
    openNoteEditor();
    console.log(`Opened note editor: ${NOTE_NEW_URL}`);
    return 0;
  }

  if (command !== "copy" && command !== "publish") {
    throw new Error(`Unknown command: ${command}\n\n${usage()}`);
  }

  const { resolvedPath, markdown } = readNoteMarkdown(filePath);
  const clipboardProvider = copyMarkdownToClipboard(markdown);
  console.log(`Copied Markdown body: ${resolvedPath}`);
  console.log(`Clipboard provider: ${clipboardProvider}`);

  if (command === "publish") {
    openNoteEditor();
    console.log(`Opened note editor: ${NOTE_NEW_URL}`);
  }

  return 0;
}

const isDirectExecution =
  process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isDirectExecution) {
  try {
    process.exitCode = run();
  } catch (error) {
    console.error(`[note-publish] ${error.message}`);
    process.exitCode = 1;
  }
}
