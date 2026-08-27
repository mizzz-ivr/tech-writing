#!/usr/bin/env python3
"""Run Writing Analytics against the unified article catalog."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import yaml

import writing_analytics as analytics
import writing_catalog as catalog

PORTFOLIO_EXPORT_PATH = analytics.ROOT / "data" / "exports" / "writing-portfolio.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-metrics",
        action="store_true",
        help="Fetch Qiita/Zenn metrics and write today's snapshot when not checking",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and render in memory without writing generated files",
    )
    return parser.parse_args()


def expected_portfolio_published_count() -> int | None:
    if not PORTFOLIO_EXPORT_PATH.exists():
        return None
    try:
        payload: Any = json.loads(PORTFOLIO_EXPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return None
    value = summary.get("published_articles")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def validate_universe(articles: list[analytics.Article]) -> None:
    expected = expected_portfolio_published_count()
    if expected is None:
        return
    actual = len(analytics.published_articles(articles))
    if actual != expected:
        raise ValueError(
            "analytics published universe does not match public Portfolio Export: "
            f"analytics={actual}, portfolio={expected}"
        )


def main() -> int:
    args = parse_args()
    try:
        articles = catalog.load_articles()
        validate_universe(articles)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    snapshot = None
    if args.refresh_metrics:
        snapshot = analytics.refresh_metrics(articles)
        if not args.check:
            path = analytics.write_metric_snapshot(snapshot)
            print(f"wrote {path.relative_to(analytics.ROOT)}")
        for error in snapshot.get("errors", []):
            print(
                f"WARNING: metrics {error['platform']} {error['slug']}: {error['error']}",
                file=sys.stderr,
            )
    else:
        snapshot = analytics.load_latest_snapshot()

    report = analytics.build_report(articles, snapshot)
    readme = analytics.README_PATH.read_text(encoding="utf-8")
    next_readme = analytics.update_readme(
        readme, analytics.build_readme_section(articles, snapshot)
    )

    if args.check:
        published = analytics.published_articles(articles)
        quality = analytics.data_quality(articles)
        print(report)
        print(
            "check completed: "
            f"{len(articles)} tracked, {len(published)} published, "
            f"{len(quality)} data-quality finding(s)",
            file=sys.stderr,
        )
        return 0

    analytics.REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    analytics.REPORT_PATH.write_text(report, encoding="utf-8")
    analytics.README_PATH.write_text(next_readme, encoding="utf-8")
    print(f"wrote {analytics.REPORT_PATH.relative_to(analytics.ROOT)}")
    print(f"updated {analytics.README_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
