#!/usr/bin/env python3
"""Lifecycle-aware entrypoint for Content Gap / Next Article Opportunity reporting."""

from __future__ import annotations

from pathlib import Path

import article_layout

_RUNTIME_NAME = __name__
_CORE_PATH = Path(__file__).with_name("writing_opportunities_core.py")

# Execute the existing implementation in this module namespace so its functions
# keep the same globals/patch boundary expected by the current test suite.
globals()["__name__"] = "writing_opportunities"
exec(compile(_CORE_PATH.read_text(encoding="utf-8"), str(_CORE_PATH), "exec"), globals())
globals()["__name__"] = _RUNTIME_NAME


def load_opportunity_articles() -> list[analytics.Article]:
    """Load active shared articles plus published Zenn-native article files."""

    articles = article_layout.load_shared_articles(analytics)
    registry = analytics.read_published_registry()
    known_paths = {article.path.resolve() for article in articles}

    for path in sorted(analytics.ARTICLES_DIR.glob("*.md")):
        if path.resolve() in known_paths:
            continue
        meta = analytics.read_frontmatter(path)
        title = str(meta.get("title") or path.stem)
        published_entry = registry.get(title)
        if published_entry is None:
            continue
        articles.append(
            analytics.Article(
                slug=path.stem,
                path=path,
                meta=meta,
                registry=published_entry,
            )
        )

    return sorted(articles, key=lambda article: article.path.as_posix())


if _RUNTIME_NAME == "__main__":
    raise SystemExit(main())
