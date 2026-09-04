#!/usr/bin/env python3
"""Shared article lifecycle discovery for Writing Analytics consumers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ACTIVE_LIFECYCLES = ("draft", "review", "published")
OLD_LIFECYCLE = "old"


def has_lifecycle_layout(articles_dir: Path) -> bool:
    return any((articles_dir / lifecycle).exists() for lifecycle in ACTIVE_LIFECYCLES)


def load_shared_articles(analytics: Any) -> list[Any]:
    """Load active shared articles while preserving legacy/test compatibility.

    Repositories using lifecycle directories are scanned from
    ``articles/{draft,review,published}/*/article.md``. ``articles/old`` is
    intentionally excluded. If lifecycle directories do not exist, delegate to
    the legacy ``analytics.load_articles`` loader so isolated tests and older
    checkouts keep their existing behavior.
    """

    articles_dir = analytics.ARTICLES_DIR
    if not has_lifecycle_layout(articles_dir):
        return analytics.load_articles()

    registry = analytics.read_published_registry()
    articles: list[Any] = []
    seen_slugs: set[str] = set()

    for lifecycle in ACTIVE_LIFECYCLES:
        lifecycle_dir = articles_dir / lifecycle
        if not lifecycle_dir.exists():
            continue

        for path in sorted(lifecycle_dir.glob("*/article.md")):
            meta = analytics.read_frontmatter(path)
            slug = path.parent.name
            status = str(meta.get("status") or "draft")

            if status != lifecycle:
                relative = path.relative_to(analytics.ROOT).as_posix()
                raise ValueError(
                    f"{relative}: lifecycle folder `{lifecycle}` does not match "
                    f"front matter `status: {status}`"
                )
            if slug in seen_slugs:
                raise ValueError(f"duplicate active article slug: {slug}")
            seen_slugs.add(slug)

            title = str(meta.get("title") or slug)
            articles.append(
                analytics.Article(
                    slug=slug,
                    path=path,
                    meta=meta,
                    registry=registry.get(title),
                )
            )

    return sorted(articles, key=lambda article: article.path.as_posix())
