#!/usr/bin/env python3
"""Validate Qiita CLI article front matter without publishing anything."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


REQUIRED_KEYS = ("title", "tags", "private")
FRONT_MATTER_PATTERN = re.compile(
    r"\A---\n(?P<front_matter>.*?)\n---(?:\n|\Z)(?P<body>.*)\Z",
    re.DOTALL,
)


def parse_article(path: Path) -> tuple[dict[str, Any] | None, str, list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---\n"):
        return None, "", ["front matter must start with '---'"]

    match = FRONT_MATTER_PATTERN.match(text)
    if match is None:
        return None, "", ["front matter closing delimiter must be a standalone '---' line"]

    front_matter = match.group("front_matter")
    body = match.group("body")

    try:
        data = yaml.safe_load(front_matter)
    except yaml.YAMLError as exc:
        return None, "", [f"front matter is invalid YAML: {exc}"]

    if not isinstance(data, dict):
        return None, body, ["front matter must be a mapping"]

    return data, body, errors


def validate_article(path: Path) -> list[str]:
    data, body, errors = parse_article(path)
    if data is None:
        return errors

    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"missing required front matter key: {key}")

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("title must be a non-empty string")

    if not body.strip():
        errors.append("body must not be empty")

    tags = data.get("tags")
    if not isinstance(tags, list):
        errors.append("tags must be a list")
    else:
        if not 1 <= len(tags) <= 5:
            errors.append("tags must contain between 1 and 5 items")
        if any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            errors.append("tags must contain only non-empty strings")

    private = data.get("private")
    if not isinstance(private, bool):
        errors.append("private must be a boolean")

    for key in ("slide", "ignorePublish", "agreed_posting_campaign_term"):
        if key in data and not isinstance(data[key], bool):
            errors.append(f"{key} must be a boolean when specified")

    article_id = data.get("id")
    if "id" in data and article_id is not None and not isinstance(article_id, str):
        errors.append("id must be a string or null")

    organization = data.get("organization_url_name")
    if (
        "organization_url_name" in data
        and organization is not None
        and not isinstance(organization, str)
    ):
        errors.append("organization_url_name must be a string or null")

    if private is True and organization:
        errors.append("private articles cannot be linked to an Organization")

    campaign = data.get("posting_campaign_uuid")
    if campaign is not None and not isinstance(campaign, str):
        errors.append("posting_campaign_uuid must be a string or null")
    if campaign and data.get("agreed_posting_campaign_term") is not True:
        errors.append("posting campaigns require agreed_posting_campaign_term: true")
    if campaign and private is True:
        errors.append("private articles cannot be linked to a posting campaign")

    updated_at = data.get("updated_at")
    if "updated_at" in data and updated_at is not None and not isinstance(updated_at, str):
        errors.append("updated_at must be a string or null")

    return errors


def iter_articles(root: Path) -> list[Path]:
    public_dir = root / "public"
    if not public_dir.exists():
        return []
    return sorted(path for path in public_dir.rglob("*.md") if path.is_file())


def main() -> int:
    root = Path.cwd()
    articles = iter_articles(root)
    if not articles:
        print("No Qiita articles to validate.")
        return 0

    failed = False
    for article in articles:
        errors = validate_article(article)
        relative = article.relative_to(root)
        if errors:
            failed = True
            print(f"[ERROR] {relative}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[OK] {relative}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
