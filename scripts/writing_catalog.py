#!/usr/bin/env python3
"""Unified article catalog for Writing Analytics.

This module normalizes the two article layouts currently used by the repository:

- ``articles/<slug>/article.md`` for shared/note-oriented metadata
- ``articles/<slug>.md`` for Zenn-native articles

Only Zenn-native files with a matching entry in ``ideas/published.md`` are added to
the analytics universe. Publication state for those files is normalized from the
registry instead of guessing from Zenn's separate ``published: true`` schema.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import writing_analytics as analytics


def normalized_native_meta(
    meta: dict[str, Any], registry: analytics.RegistryEntry
) -> dict[str, Any]:
    """Normalize a published Zenn-native front matter mapping for analytics."""

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


def load_articles() -> list[analytics.Article]:
    """Return the complete tracked article universe with normalized publication metadata."""

    registry = analytics.read_published_registry()
    articles = analytics.load_articles()
    known_paths = {article.path.resolve() for article in articles}

    for path in sorted(analytics.ARTICLES_DIR.glob("*.md")):
        if path.resolve() in known_paths:
            continue

        raw_meta = analytics.read_frontmatter(path)
        title = str(raw_meta.get("title") or path.stem)
        published_entry = registry.get(title)
        if published_entry is None:
            # Do not infer draft/review state from Zenn's independent schema.
            continue

        articles.append(
            analytics.Article(
                slug=path.stem,
                path=path,
                meta=normalized_native_meta(raw_meta, published_entry),
                registry=published_entry,
            )
        )

    return sorted(articles, key=lambda article: article.path.as_posix())


def published_articles() -> list[analytics.Article]:
    return analytics.published_articles(load_articles())


def relative_path(article: analytics.Article) -> str:
    try:
        return article.path.relative_to(analytics.ROOT).as_posix()
    except ValueError:
        return Path(article.path).as_posix()
