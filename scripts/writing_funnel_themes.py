#!/usr/bin/env python3
"""Deterministic theme grouping for GitHub -> Writing Funnel evidence.

The grouping layer intentionally avoids semantic inference. It uses only explicit
Conventional Commit scopes already present in GitHub titles. Releases remain
independent themes, and unscoped events remain singletons.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

import writing_funnel as funnel

SCOPE_RE = re.compile(
    r"^(?:build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"\((?P<scope>[^)]+)\)\s*[:：]\s*",
    re.IGNORECASE,
)
THEME_PRIORITY = {"release": 3, "explicit_scope": 2, "singleton": 1}


def explicit_scope(title: str) -> str | None:
    match = SCOPE_RE.match(str(title).strip())
    if not match:
        return None
    scope = re.sub(r"\s+", " ", match.group("scope").strip())
    return scope or None


def all_candidate_rows(
    articles: Iterable[Any],
    backlog: Iterable[Any],
    *,
    policy: funnel.FunnelPolicy,
    snapshot: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    titles = funnel.tracking_titles(articles, backlog)
    rows = funnel.deduplicate_evidence(funnel.flatten_evidence(snapshot))
    candidates: list[dict[str, Any]] = []

    for row in rows:
        best: tuple[str, str, float] | None = None
        for source, title in titles:
            similarity = funnel.title_similarity(row.title, title)
            if best is None or similarity > best[2]:
                best = (source, title, similarity)
        tracked = bool(best and best[2] >= policy.title_overlap_threshold)
        candidates.append(
            {
                "repository": row.repository,
                "kind": row.kind,
                "source_id": row.source_id,
                "title": row.title,
                "url": row.url,
                "occurred_at": row.occurred_at,
                "tracking_status": "tracked" if tracked else "untracked",
                "matched_source": best[0] if tracked and best else None,
                "matched_title": best[1] if tracked and best else None,
                "title_similarity": round(best[2], 3) if best else 0.0,
            }
        )

    candidates.sort(key=funnel.candidate_sort_key, reverse=True)
    return candidates


def _group_identity(row: dict[str, Any]) -> tuple[str, str, str]:
    repository = str(row["repository"])
    if row["kind"] == "release":
        return ("release", repository, str(row["source_id"]))
    if scope := explicit_scope(str(row["title"])):
        return ("explicit_scope", repository, scope.casefold())
    return (
        "singleton",
        repository,
        f"{row['kind']}:{row['source_id']}",
    )


def _theme_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        THEME_PRIORITY.get(str(row["grouping"]), 0),
        int(row["event_count"]),
        str(row["latest_at"]),
        str(row["repository"]),
        str(row["label"]),
    )


def build_theme_payload(
    articles: Iterable[Any],
    backlog: Iterable[Any],
    *,
    policy: funnel.FunnelPolicy | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or funnel.load_policy()
    snapshot = snapshot if snapshot is not None else funnel.load_latest_snapshot(policy)
    rows = all_candidate_rows(
        articles,
        backlog,
        policy=policy,
        snapshot=snapshot,
    )
    untracked = [row for row in rows if row["tracking_status"] == "untracked"]

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in untracked:
        grouped.setdefault(_group_identity(row), []).append(row)

    themes: list[dict[str, Any]] = []
    for (grouping, repository, identity), evidence_rows in grouped.items():
        ordered = sorted(evidence_rows, key=funnel.candidate_sort_key, reverse=True)
        representative = ordered[0]
        scope = explicit_scope(str(representative["title"])) if grouping == "explicit_scope" else None
        label = (
            str(representative["title"])
            if grouping in {"release", "singleton"}
            else str(scope)
        )
        themes.append(
            {
                "repository": repository,
                "grouping": grouping,
                "scope": scope,
                "label": label,
                "event_count": len(ordered),
                "latest_at": max(str(row["occurred_at"]) for row in ordered),
                "kinds": sorted({str(row["kind"]) for row in ordered}),
                "representative": {
                    "kind": representative["kind"],
                    "source_id": representative["source_id"],
                    "title": representative["title"],
                    "url": representative["url"],
                    "occurred_at": representative["occurred_at"],
                },
                "evidence": [
                    {
                        "kind": row["kind"],
                        "source_id": row["source_id"],
                        "title": row["title"],
                        "url": row["url"],
                        "occurred_at": row["occurred_at"],
                    }
                    for row in ordered[:3]
                ],
                "identity": identity,
            }
        )

    themes.sort(key=_theme_sort_key, reverse=True)
    theme_count = len(themes)
    compression_ratio = (
        round(len(untracked) / theme_count, 2) if theme_count else None
    )
    return {
        "untracked_theme_count": theme_count,
        "compression_ratio": compression_ratio,
        "theme_groups": themes[: policy.max_candidates],
    }


def validate_theme_payload(payload: dict[str, Any], *, untracked_count: int) -> None:
    count = payload.get("untracked_theme_count")
    groups = payload.get("theme_groups")
    if not isinstance(count, int) or count < 0:
        raise ValueError("GitHub writing funnel untracked_theme_count must be a non-negative integer")
    if not isinstance(groups, list):
        raise ValueError("GitHub writing funnel theme_groups must be a list")
    if untracked_count and not groups:
        raise ValueError("non-zero untracked evidence must expose a theme group")
    if count > untracked_count:
        raise ValueError("theme count cannot exceed untracked evidence count")

    for group in groups:
        if group.get("grouping") not in THEME_PRIORITY:
            raise ValueError("invalid GitHub writing funnel theme grouping")
        if not isinstance(group.get("event_count"), int) or group["event_count"] < 1:
            raise ValueError("theme event_count must be positive")
        if group["grouping"] == "explicit_scope" and not group.get("scope"):
            raise ValueError("explicit_scope theme must expose scope")
        if group["grouping"] == "singleton" and group["event_count"] != 1:
            raise ValueError("singleton theme must contain exactly one event")
