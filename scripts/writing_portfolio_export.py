#!/usr/bin/env python3
"""Generate a stable public Writing Portfolio JSON export."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics
import writing_opportunities as opportunities

EXPORT_PATH = analytics.ROOT / "data" / "exports" / "writing-portfolio.json"
POLICY_PATH = analytics.ROOT / "config" / "portfolio-export.yml"
SCHEMA_VERSION = 1
COVERAGE_KEYS = ("domains", "languages", "technologies", "portfolio_signals")
WINDOWS = opportunities.WINDOWS
SENSITIVE_KEY_FRAGMENTS = ("token", "secret", "password", "cookie", "authorization", "api_key", "apikey")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Render and validate without writing the export")
    return parser.parse_args()


def load_policy() -> dict[str, Any]:
    data = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("config/portfolio-export.yml must be a mapping")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"portfolio export policy schema_version must be {SCHEMA_VERSION}")
    sources = data.get("public_source_repositories")
    if not isinstance(sources, list) or any(not isinstance(item, str) or not item.strip() for item in sources):
        raise ValueError("public_source_repositories must be a list of non-empty repository names")
    max_recent = data.get("max_recent_articles", 10)
    if not isinstance(max_recent, int) or isinstance(max_recent, bool) or max_recent < 1 or max_recent > 100:
        raise ValueError("max_recent_articles must be an integer between 1 and 100")
    return {
        "public_source_repositories": {item.strip() for item in sources},
        "max_recent_articles": max_recent,
    }


def exported_sources(article: analytics.Article, allowlist: set[str]) -> tuple[list[str], int]:
    declared = analytics.list_values(article.meta, "source_repositories")
    included = sorted({value for value in declared if value in allowlist}, key=str.casefold)
    return included, len([value for value in declared if value not in allowlist])


def article_payload(article: analytics.Article, allowlist: set[str]) -> tuple[dict[str, Any], int]:
    sources, omitted = exported_sources(article, allowlist)
    platforms = {
        platform: url
        for platform in analytics.PUBLICATION_PLATFORMS
        if (url := article.platform_url(platform))
    }
    payload = {
        "slug": article.slug,
        "title": article.title,
        "published_at": article.effective_published_at,
        "article_type": article.meta.get("article_type") or article.meta.get("type"),
        "level": article.meta.get("level"),
        "topics": analytics.list_values(article.meta, "topics"),
        "domains": analytics.list_values(article.meta, "domains"),
        "languages": analytics.list_values(article.meta, "languages"),
        "technologies": analytics.list_values(article.meta, "technologies"),
        "portfolio_signals": analytics.list_values(article.meta, "portfolio_signals"),
        "source_repositories": sources,
        "published": platforms,
    }
    return payload, omitted


def coverage_payload(articles: list[analytics.Article], key: str, as_of) -> list[dict[str, Any]]:
    rows = []
    for value, count, last, age in opportunities.coverage_rows(articles, key, as_of):
        rows.append(
            {
                "value": value,
                "published_count": count,
                "last_published_at": last.isoformat(),
                "days_since_last": age,
                "coverage": {str(window): age <= window for window in WINDOWS},
            }
        )
    return rows


def notable_payload(
    articles: list[analytics.Article], snapshot: dict[str, Any] | None
) -> list[dict[str, Any]]:
    by_title = {article.title: article for article in analytics.published_articles(articles)}
    result = []
    for title, platform, url, metrics in analytics.notable_reaction_rows(snapshot):
        article = by_title.get(title)
        if article is None:
            continue
        reactions = {
            key: metrics.get(key)
            for key, _ in analytics.reaction_fields(platform)
            if key in metrics and (metrics.get(key) is None or isinstance(metrics.get(key), (int, float)))
        }
        result.append(
            {
                "slug": article.slug,
                "title": article.title,
                "published_at": article.effective_published_at,
                "platform": platform,
                "url": url,
                "reactions": reactions,
            }
        )
    return result


def build_export(
    articles: list[analytics.Article],
    snapshot: dict[str, Any] | None,
    policy: dict[str, Any],
) -> dict[str, Any]:
    published = analytics.published_articles(articles)
    as_of = opportunities.resolve_as_of(articles)
    allowlist = set(policy["public_source_repositories"])
    max_recent = int(policy["max_recent_articles"])

    recent = []
    omitted_source_count = 0
    for article in published[:max_recent]:
        row, omitted = article_payload(article, allowlist)
        recent.append(row)
        omitted_source_count += omitted

    last_published = published[0].effective_published_at if published else None
    return {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "summary": {
            "published_articles": len(published),
            "last_published_at": last_published,
            "coverage_windows_days": list(WINDOWS),
        },
        "coverage": {key: coverage_payload(published, key, as_of) for key in COVERAGE_KEYS},
        "recent_articles": recent,
        "notable_articles": notable_payload(published, snapshot),
        "export_quality": {
            "omitted_non_allowlisted_source_repository_references": omitted_source_count,
        },
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


def validate_export(payload: dict[str, Any], allowlist: set[str]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected export schema_version")
    if sensitive_paths(payload):
        raise ValueError("public export contains sensitive-looking field names")

    for article in payload.get("recent_articles", []):
        for source in article.get("source_repositories", []):
            if source not in allowlist:
                raise ValueError("public export contains a source repository outside the explicit allowlist")
        for url in article.get("published", {}).values():
            if not isinstance(url, str) or not url.startswith("https://"):
                raise ValueError("published URLs in the public export must use HTTPS")

    for item in payload.get("notable_articles", []):
        url = item.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("notable article URLs in the public export must use HTTPS")
        if "page_views" in item.get("reactions", {}):
            raise ValueError("page views are intentionally excluded from the public export")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> int:
    args = parse_args()
    try:
        policy = load_policy()
        articles = opportunities.load_opportunity_articles()
        snapshot = analytics.load_latest_snapshot()
        payload = build_export(articles, snapshot, policy)
        validate_export(payload, set(policy["public_source_repositories"]))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            f"check completed: schema v{payload['schema_version']}, "
            f"{payload['summary']['published_articles']} published articles, "
            f"{len(payload['notable_articles'])} notable article(s)",
            file=sys.stderr,
        )
        return 0

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(render_json(payload), encoding="utf-8")
    print(f"wrote {EXPORT_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
