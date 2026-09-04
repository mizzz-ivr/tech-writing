#!/usr/bin/env python3
"""Normalize metadata for the three articles published before Writing Analytics v1.

This migration is intentionally explicit and idempotent. Values are curated from the
article bodies and ideas/published.md; it does not infer metadata dynamically.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTICLES_DIR = ROOT / "articles"
PUBLISHED_ARTICLES_DIR = ARTICLES_DIR / "published"

CURATED: dict[str, dict[str, Any]] = {
    "github-profile-daily-activity": {
        "status": "published",
        "published_at": "2026-08-26",
        "article_type": "case-study",
        "level": "intermediate",
        "domains": ["devops", "developer-productivity"],
        "languages": ["Python"],
        "technologies": ["GitHub Actions", "GitHub API", "GitHub Search API"],
        "portfolio_signals": ["automation", "ci-cd"],
        "published": {
            "qiita": "https://qiita.com/mizzz-ivr/items/73bd3a3874aa8adacc1a",
            "zenn": None,
        },
    },
    "github-profile-live-dashboard": {
        "status": "published",
        "published_at": "2026-08-27",
        "article_type": "case-study",
        "level": "intermediate",
        "domains": ["devops", "developer-productivity"],
        "languages": ["Python"],
        "technologies": ["GitHub Actions", "GitHub API", "GitHub Events API"],
        "portfolio_signals": ["automation", "architecture"],
        "published": {
            "qiita": "https://qiita.com/mizzz-ivr/items/b5cc51f17c9d9e69f630",
            "zenn": None,
        },
    },
    "repository-is-source-of-truth": {
        "status": "published",
        "published_at": "2026-08-24",
        "article_type": "case-study",
        "level": "intermediate",
        "domains": ["ai", "developer-productivity"],
        # This article describes a development workflow, not a language-specific implementation.
        "languages": [],
        "technologies": ["GitHub", "GitHub Issues", "GitHub Pull Requests", "GitHub Actions"],
        "portfolio_signals": ["development-process", "ai-assisted-development"],
        "source_repositories": ["ivRooom/Herta"],
        "published": {
            "qiita": "https://qiita.com/mizzz-ivr/items/44cd3077d732eea1bf6e",
            "zenn": None,
        },
    },
}

PREFERRED_ORDER = [
    "title",
    "status",
    "published_at",
    "article_type",
    "level",
    "topics",
    "domains",
    "languages",
    "technologies",
    "portfolio_signals",
    "source_repositories",
    "published",
]


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("front matter is missing")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("front matter is not closed")
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise ValueError("front matter must be a mapping")
    return meta, parts[2].lstrip("\n")


def ordered(meta: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in PREFERRED_ORDER:
        if key in meta:
            result[key] = meta[key]
    for key, value in meta.items():
        if key not in result:
            result[key] = value
    return result


def render(meta: dict[str, Any], body: str) -> str:
    dumped = yaml.safe_dump(
        ordered(meta),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    ).rstrip()
    return f"---\n{dumped}\n---\n\n{body.rstrip()}\n"


def normalize(slug: str, updates: dict[str, Any], check: bool) -> bool:
    path = PUBLISHED_ARTICLES_DIR / slug / "article.md"
    text = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)
    next_meta = dict(meta)
    next_meta.update(updates)
    next_text = render(next_meta, body)
    changed = next_text != text
    if changed and not check:
        path.write_text(next_text, encoding="utf-8")
    print(f"{'would update' if check and changed else 'updated' if changed else 'unchanged'}: {path.relative_to(ROOT)}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed = 0
    for slug, updates in CURATED.items():
        changed += int(normalize(slug, updates, args.check))

    print(f"metadata migration: {changed} file(s) {'would change' if args.check else 'changed'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
