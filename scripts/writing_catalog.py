#!/usr/bin/env python3
"""Unified article catalog for Writing Analytics.

This module normalizes the two article layouts currently used by the repository:

- ``articles/<slug>/article.md`` for shared/note-oriented metadata
- ``articles/<slug>.md`` for platform-native articles (currently Zenn)

Only platform-native files with a matching entry in ``ideas/published.md`` are
added to the analytics universe. Publication state for those files is normalized
from the registry instead of guessing from the platform's separate front matter
schema.

Analytics-only evidence for platform-native files is read from
``metadata/platform-native-analytics.yml`` so platform-owned front matter does not
need unsupported custom keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import writing_analytics as analytics

NATIVE_ANALYTICS_PATH = analytics.ROOT / "metadata" / "platform-native-analytics.yml"
NATIVE_ANALYTICS_SCHEMA_VERSION = 1
NATIVE_ANALYTICS_KEYS = frozenset(
    {"source_repositories", "verified_at", "source_refs"}
)


def normalized_native_meta(
    meta: dict[str, Any], registry: analytics.RegistryEntry
) -> dict[str, Any]:
    """Normalize a published platform-native front matter mapping for analytics."""

    normalized = dict(meta)
    normalized["status"] = "published"
    normalized["published_at"] = registry.published_at
    normalized["article_type"] = meta.get("article_type") or meta.get("type")
    normalized["published"] = {
        platform: url
        for platform in analytics.PUBLICATION_PLATFORMS
        if (url := getattr(registry, platform, None))
    }
    return normalized


def load_native_analytics_metadata() -> dict[str, dict[str, Any]]:
    """Load strict analytics-only metadata for platform-native article files."""

    if not NATIVE_ANALYTICS_PATH.exists():
        return {}

    data = yaml.safe_load(NATIVE_ANALYTICS_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("metadata/platform-native-analytics.yml must be a mapping")
    if data.get("schema_version") != NATIVE_ANALYTICS_SCHEMA_VERSION:
        raise ValueError(
            f"platform-native analytics schema_version must be {NATIVE_ANALYTICS_SCHEMA_VERSION}"
        )

    raw_articles = data.get("articles", {})
    if not isinstance(raw_articles, dict):
        raise ValueError("platform-native analytics `articles` must be a mapping")

    result: dict[str, dict[str, Any]] = {}
    for raw_path, raw_meta in raw_articles.items():
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("platform-native analytics article path must be non-empty")
        normalized_path = Path(raw_path.strip()).as_posix()
        parts = Path(normalized_path).parts
        if (
            len(parts) != 2
            or parts[0] != "articles"
            or not parts[1].endswith(".md")
            or parts[1] in {".", ".."}
        ):
            raise ValueError(
                "platform-native analytics entries must target direct `articles/<slug>.md` files"
            )
        if not isinstance(raw_meta, dict):
            raise ValueError(f"{normalized_path}: analytics metadata must be a mapping")

        unknown = set(raw_meta) - NATIVE_ANALYTICS_KEYS
        if unknown:
            rendered = ", ".join(sorted(unknown))
            raise ValueError(
                f"{normalized_path}: unsupported platform-native analytics field(s): {rendered}"
            )

        sources = raw_meta.get("source_repositories")
        if sources is not None and (
            not isinstance(sources, list)
            or any(not isinstance(item, str) or not item.strip() for item in sources)
        ):
            raise ValueError(
                f"{normalized_path}: `source_repositories` must be a list of non-empty strings"
            )

        result[normalized_path] = dict(raw_meta)

    return result


def load_articles() -> list[analytics.Article]:
    """Return the complete tracked article universe with normalized publication metadata."""

    registry = analytics.read_published_registry()
    articles = analytics.load_articles()
    known_paths = {article.path.resolve() for article in articles}
    native_metadata = load_native_analytics_metadata()
    consumed_native_metadata: set[str] = set()

    for path in sorted(analytics.ARTICLES_DIR.glob("*.md")):
        if path.resolve() in known_paths:
            continue

        raw_meta = analytics.read_frontmatter(path)
        title = str(raw_meta.get("title") or path.stem)
        published_entry = registry.get(title)
        if published_entry is None:
            # Do not infer draft/review state from a platform's independent schema.
            continue

        relative = f"articles/{path.name}"
        normalized = normalized_native_meta(raw_meta, published_entry)
        if override := native_metadata.get(relative):
            normalized.update(override)
            consumed_native_metadata.add(relative)

        articles.append(
            analytics.Article(
                slug=path.stem,
                path=path,
                meta=normalized,
                registry=published_entry,
            )
        )

    unused = sorted(set(native_metadata) - consumed_native_metadata)
    if unused:
        raise ValueError(
            "platform-native analytics metadata references article(s) outside the published native catalog: "
            + ", ".join(unused)
        )

    return sorted(articles, key=lambda article: article.path.as_posix())


def published_articles() -> list[analytics.Article]:
    return analytics.published_articles(load_articles())


def relative_path(article: analytics.Article) -> str:
    try:
        return article.path.relative_to(analytics.ROOT).as_posix()
    except ValueError:
        return Path(article.path).as_posix()
