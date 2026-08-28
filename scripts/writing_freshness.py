#!/usr/bin/env python3
"""Validate and summarize article source-freshness metadata.

Freshness metadata is optional evidence. Existing articles are never assigned a
verification date or source commit implicitly; missing metadata is represented as
``needs_initial_verification`` for published articles.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

import writing_analytics as analytics
import writing_catalog as catalog

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def parse_verified_at(article: analytics.Article) -> date | None:
    raw = article.meta.get("verified_at")
    if raw is None or raw == "":
        return None
    if isinstance(raw, datetime):
        raise ValueError(
            f"{catalog.relative_path(article)}: `verified_at` must be YYYY-MM-DD, not datetime"
        )
    if isinstance(raw, date):
        return raw
    if not isinstance(raw, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise ValueError(
            f"{catalog.relative_path(article)}: `verified_at` must use YYYY-MM-DD"
        )
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(
            f"{catalog.relative_path(article)}: `verified_at` is not a valid date"
        ) from exc


def source_refs(article: analytics.Article) -> list[dict[str, str]]:
    raw = article.meta.get("source_refs")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(
            f"{catalog.relative_path(article)}: `source_refs` must be a list"
        )

    declared_repositories = set(
        analytics.list_values(article.meta, "source_repositories")
    )
    refs: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for index, item in enumerate(raw):
        prefix = f"{catalog.relative_path(article)}: `source_refs[{index}]`"
        if not isinstance(item, dict):
            raise ValueError(f"{prefix} must be a mapping")
        if set(item) != {"repository", "commit"}:
            raise ValueError(
                f"{prefix} must contain exactly `repository` and `commit`"
            )

        repository = item.get("repository")
        commit = item.get("commit")
        if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
            raise ValueError(f"{prefix}.repository must use owner/repository format")
        if repository not in declared_repositories:
            raise ValueError(
                f"{prefix}.repository must also exist in `source_repositories`"
            )
        if not isinstance(commit, str) or not COMMIT_SHA_RE.fullmatch(commit):
            raise ValueError(f"{prefix}.commit must be a 40-character commit SHA")

        normalized = (repository, commit.lower())
        if normalized in seen:
            raise ValueError(f"{prefix} duplicates an earlier source ref")
        seen.add(normalized)
        refs.append({"repository": repository, "commit": commit.lower()})

    return refs


def validate_article(
    article: analytics.Article, freshness_as_of: date
) -> tuple[date | None, list[dict[str, str]]]:
    verified_at = parse_verified_at(article)
    refs = source_refs(article)
    if refs and verified_at is None:
        raise ValueError(
            f"{catalog.relative_path(article)}: `source_refs` requires `verified_at`"
        )
    if verified_at is not None and verified_at > freshness_as_of:
        raise ValueError(
            f"{catalog.relative_path(article)}: `verified_at` cannot be in the future relative to {freshness_as_of.isoformat()}"
        )
    return verified_at, refs


def freshness_payload(
    articles: list[analytics.Article], as_of: date | None = None
) -> dict[str, Any]:
    """Return freshness state using a date independent from metric snapshots.

    Source freshness ages with calendar time even when the latest external metric
    snapshot is older. Tests may inject ``as_of``; production defaults to today's
    date in the repository's configured JST timezone.
    """

    freshness_as_of = as_of or datetime.now(analytics.JST).date()
    validated: dict[str, tuple[date | None, list[dict[str, str]]]] = {}
    for article in articles:
        validated[article.slug] = validate_article(article, freshness_as_of)

    rows: list[dict[str, Any]] = []
    for article in analytics.published_articles(articles):
        verified_at, refs = validated[article.slug]
        age = (
            (freshness_as_of - verified_at).days
            if verified_at is not None
            else None
        )
        rows.append(
            {
                "slug": article.slug,
                "title": article.title,
                "path": catalog.relative_path(article),
                "status": (
                    "verified" if verified_at is not None else "needs_initial_verification"
                ),
                "verified_at": verified_at.isoformat() if verified_at else None,
                "days_since_verified": age,
                "source_ref_count": len(refs),
            }
        )

    rows.sort(
        key=lambda row: (
            0 if row["status"] == "needs_initial_verification" else 1,
            -(row["days_since_verified"] or 0),
            str(row["title"]).casefold(),
        )
    )
    verified_ages = [
        int(row["days_since_verified"])
        for row in rows
        if row["days_since_verified"] is not None
    ]
    initial = sum(
        1 for row in rows if row["status"] == "needs_initial_verification"
    )

    return {
        "as_of": freshness_as_of.isoformat(),
        "published_articles": len(rows),
        "verified_articles": len(rows) - initial,
        "needs_initial_verification": initial,
        "oldest_verification_age_days": max(verified_ages) if verified_ages else None,
        "articles": rows,
    }
