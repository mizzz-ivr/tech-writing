#!/usr/bin/env python3
"""Generate a normalized Writing Analytics data mart.

Raw article metadata, publication registry entries and metric snapshots remain the
Source of Truth. This JSON is deterministic derived data intended for analysis,
visualization and downstream consumers.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from statistics import mean
from typing import Any

import writing_analytics as analytics
import writing_catalog as catalog
import writing_freshness as freshness
import writing_opportunities as opportunities

DATA_MART_PATH = analytics.ROOT / "data" / "analytics" / "writing-analytics.json"
SCHEMA_VERSION = 1
COVERAGE_KEYS = ("topics", "domains", "languages", "technologies", "portfolio_signals")
TREND_WINDOWS = (7, 30, 90)
SENSITIVE_KEY_FRAGMENTS = (
    "token",
    "secret",
    "password",
    "cookie",
    "authorization",
    "api_key",
    "apikey",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build and validate the data mart in memory without writing it",
    )
    return parser.parse_args()


def parse_iso_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def average_interval_days(articles: list[analytics.Article]) -> float | None:
    dates = sorted(
        parsed
        for article in analytics.published_articles(articles)
        if (parsed := parse_iso_date(article.effective_published_at)) is not None
    )
    if len(dates) < 2:
        return None
    gaps = [(dates[index] - dates[index - 1]).days for index in range(1, len(dates))]
    return round(mean(gaps), 1)


def readable_snapshot_dates() -> list[date]:
    if not analytics.METRICS_DIR.exists():
        return []

    result: list[date] = []
    for path in sorted(analytics.METRICS_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            snapshot_date = date.fromisoformat(path.stem)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        if not isinstance(payload.get("articles"), list):
            continue
        collected_at = payload.get("collected_at")
        if not isinstance(collected_at, str) or not collected_at.strip():
            continue
        result.append(snapshot_date)
    return result


def trend_readiness(snapshot_dates: list[date]) -> dict[str, Any]:
    if not snapshot_dates:
        return {
            "snapshot_count": 0,
            "first_snapshot_at": None,
            "last_snapshot_at": None,
            "observed_span_days": 0,
            "windows": {str(window): False for window in TREND_WINDOWS},
        }

    first = min(snapshot_dates)
    last = max(snapshot_dates)
    span = max(0, (last - first).days)
    return {
        "snapshot_count": len(snapshot_dates),
        "first_snapshot_at": first.isoformat(),
        "last_snapshot_at": last.isoformat(),
        "observed_span_days": span,
        "windows": {str(window): span >= window for window in TREND_WINDOWS},
    }


def status_payload(articles: list[analytics.Article]) -> dict[str, int]:
    counts = Counter(article.effective_status for article in articles)
    known = ("draft", "review", "published", "archived")
    payload = {status: counts.get(status, 0) for status in known}
    for status in sorted(counts):
        if status not in payload:
            payload[status] = counts[status]
    return payload


def coverage_payload(
    articles: list[analytics.Article], key: str, as_of: date
) -> dict[str, Any]:
    published = analytics.published_articles(articles)
    rows = [
        {
            "value": value,
            "published_count": count,
            "last_published_at": last.isoformat(),
            "days_since_last": age,
            "windows": {
                "30": age <= 30,
                "90": age <= 90,
                "365": age <= 365,
            },
        }
        for value, count, last, age in opportunities.coverage_rows(published, key, as_of)
    ]
    unclassified = analytics.count_field(published, key).get("Unclassified", 0)
    return {
        "values": rows,
        "unclassified_published_articles": unclassified,
        "pipeline_only_values": opportunities.pipeline_only_values(articles, key),
    }


def normalized_article(article: analytics.Article) -> dict[str, Any]:
    platforms = [
        platform
        for platform in analytics.PUBLICATION_PLATFORMS
        if article.platform_url(platform)
    ]
    return {
        "slug": article.slug,
        "path": catalog.relative_path(article),
        "title": article.title,
        "status": article.effective_status,
        "published_at": article.effective_published_at,
        "article_type": article.meta.get("article_type") or article.meta.get("type"),
        "level": article.meta.get("level"),
        "publication_platforms": platforms,
        "classifications": {
            key: analytics.list_values(article.meta, key) for key in COVERAGE_KEYS
        },
        "source_evidence": {
            "repository_count": len(
                analytics.list_values(article.meta, "source_repositories")
            ),
            "recorded": bool(
                analytics.list_values(article.meta, "source_repositories")
            ),
        },
    }


def reaction_payload(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    totals: dict[str, dict[str, int]] = {}

    for title, platform, url, metrics in analytics.reaction_rows(snapshot):
        values: dict[str, Any] = {}
        for key, _label in analytics.reaction_fields(platform):
            if key in metrics:
                values[key] = metrics.get(key)
        if "page_views" in metrics:
            values["page_views"] = metrics.get("page_views")
        if metrics.get("error"):
            values["error"] = True

        observations.append(
            {
                "title": title,
                "platform": platform,
                "url": url,
                "metrics": values,
            }
        )

        platform_totals = totals.setdefault(platform, {})
        for key, value in values.items():
            if key == "error" or isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            platform_totals[key] = platform_totals.get(key, 0) + int(value)

    return {
        "observed_numeric_totals": totals,
        "observations": observations,
        "notable_observation_count": len(analytics.notable_reaction_rows(snapshot)),
    }


def candidate_payload(candidate: opportunities.Candidate) -> dict[str, Any]:
    return {
        "slug": candidate.article.slug,
        "title": candidate.article.title,
        "status": candidate.article.effective_status,
        "path": catalog.relative_path(candidate.article),
        "portfolio_gaps": list(candidate.portfolio_gaps),
        "coverage_gaps": list(candidate.coverage_gaps),
        "oldest_gap_age_days": candidate.oldest_gap_age,
        "source_evidence_recorded": bool(candidate.sources),
        "source_repository_count": len(candidate.sources),
        "related_positive_reaction_articles": candidate.reaction_context,
        "missing_metadata": list(candidate.missing_metadata),
    }


def build_data_mart(
    articles: list[analytics.Article],
    snapshot: dict[str, Any] | None,
    backlog: list[opportunities.BacklogItem],
) -> dict[str, Any]:
    published = analytics.published_articles(articles)
    as_of = opportunities.resolve_as_of(articles)
    quality = analytics.data_quality(articles)
    candidates = opportunities.build_candidates(articles, snapshot, as_of)
    statuses = status_payload(articles)
    last_published = published[0].effective_published_at if published else None
    freshness_model = freshness.freshness_payload(articles, as_of)

    coverage = {
        key: coverage_payload(articles, key, as_of) for key in COVERAGE_KEYS
    }
    pipeline_gap_count = sum(
        len(section["pipeline_only_values"]) for section in coverage.values()
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "overview": {
            "tracked_articles": len(articles),
            "published_articles": len(published),
            "draft_articles": statuses.get("draft", 0),
            "review_articles": statuses.get("review", 0),
            "last_published_at": last_published,
            "average_publish_interval_days": average_interval_days(articles),
            "data_quality_findings": len(quality),
            "pipeline_only_coverage_gaps": pipeline_gap_count,
            "freshness_needs_initial_verification": freshness_model[
                "needs_initial_verification"
            ],
            "backlog_items": len(backlog),
        },
        "pipeline": statuses,
        "trend_readiness": trend_readiness(readable_snapshot_dates()),
        "freshness": freshness_model,
        "coverage": coverage,
        "reactions": reaction_payload(snapshot),
        "next_article_candidates": [
            candidate_payload(candidate) for candidate in candidates[:5]
        ],
        "data_quality": {
            "finding_count": len(quality),
            "findings": quality,
        },
        "articles": [normalized_article(article) for article in articles],
    }


def sensitive_paths(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            normalized = str(key).casefold().replace("-", "_")
            if any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
                findings.append(path)
            findings.extend(sensitive_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            findings.extend(sensitive_paths(nested, f"{prefix}[{index}]"))
    return findings


def validate_data_mart(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected analytics data mart schema_version")
    overview = payload.get("overview")
    if not isinstance(overview, dict):
        raise ValueError("analytics data mart overview must be a mapping")
    if overview.get("tracked_articles") != len(payload.get("articles", [])):
        raise ValueError("tracked article count does not match normalized article rows")
    published_rows = [
        row for row in payload.get("articles", []) if row.get("status") == "published"
    ]
    if overview.get("published_articles") != len(published_rows):
        raise ValueError("published article count does not match normalized article rows")

    freshness_model = payload.get("freshness")
    if not isinstance(freshness_model, dict):
        raise ValueError("analytics data mart freshness must be a mapping")
    if freshness_model.get("published_articles") != len(published_rows):
        raise ValueError("freshness published count does not match normalized article rows")
    verified = freshness_model.get("verified_articles")
    initial = freshness_model.get("needs_initial_verification")
    if not isinstance(verified, int) or not isinstance(initial, int):
        raise ValueError("freshness summary counts must be integers")
    if verified + initial != len(published_rows):
        raise ValueError("freshness summary counts do not cover all published articles")
    if overview.get("freshness_needs_initial_verification") != initial:
        raise ValueError("overview freshness count does not match freshness summary")

    if sensitive_paths(payload):
        raise ValueError("analytics data mart contains sensitive-looking field names")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> int:
    args = parse_args()
    try:
        articles = catalog.load_articles()
        snapshot = analytics.load_latest_snapshot()
        backlog = opportunities.load_backlog()
        payload = build_data_mart(articles, snapshot, backlog)
        validate_data_mart(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            "check completed: "
            f"schema v{payload['schema_version']}, "
            f"{payload['overview']['published_articles']} published, "
            f"{payload['overview']['tracked_articles']} tracked, "
            f"{payload['freshness']['needs_initial_verification']} need initial verification",
            file=sys.stderr,
        )
        return 0

    DATA_MART_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_MART_PATH.write_text(render_json(payload), encoding="utf-8")
    print(f"wrote {DATA_MART_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
