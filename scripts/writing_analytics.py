#!/usr/bin/env python3
"""Repository-layout aware facade for Writing Analytics.

The analytics implementation lives in ``writing_analytics_core``. This facade owns
how shared article folders are discovered so repository layout can evolve without
mixing lifecycle policy into the analytics/reporting implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import writing_analytics_core as _core

ACTIVE_ARTICLE_LIFECYCLES = ("draft", "review", "published")


def managed_article_paths() -> Iterator[Path]:
    """Yield active shared article sources; ``old`` is intentionally excluded."""

    for lifecycle in ACTIVE_ARTICLE_LIFECYCLES:
        lifecycle_dir = _core.ARTICLES_DIR / lifecycle
        if not lifecycle_dir.exists():
            continue
        yield from lifecycle_dir.glob("*/article.md")


def load_articles() -> list[_core.Article]:
    """Load shared articles and enforce folder/front-matter lifecycle alignment."""

    registry = _core.read_published_registry()
    articles: list[_core.Article] = []
    seen_slugs: set[str] = set()

    for path in sorted(managed_article_paths()):
        meta = _core.read_frontmatter(path)
        relative = path.relative_to(_core.ARTICLES_DIR)
        lifecycle = relative.parts[0]
        slug = path.parent.name
        status = str(meta.get("status") or "draft")

        if status != lifecycle:
            raise ValueError(
                f"{relative.as_posix()}: lifecycle folder `{lifecycle}` does not match "
                f"front matter `status: {status}`"
            )
        if slug in seen_slugs:
            raise ValueError(f"duplicate active article slug: {slug}")
        seen_slugs.add(slug)

        title = str(meta.get("title") or slug)
        articles.append(_core.Article(slug, path, meta, registry.get(title)))

    return articles


# Expose one shared module object to existing imports/tests. This keeps patches of
# constants such as ARTICLES_DIR working exactly as before while only replacing
# article discovery with the lifecycle-aware loader above.
_core.ACTIVE_ARTICLE_LIFECYCLES = ACTIVE_ARTICLE_LIFECYCLES
_core.managed_article_paths = managed_article_paths
_core.load_articles = load_articles

if __name__ == "__main__":
    raise SystemExit(_core.main())

sys.modules[__name__] = _core
