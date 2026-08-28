#!/usr/bin/env python3
"""Generate the normalized Writing Analytics data mart with GitHub funnel data."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import writing_analytics as analytics
import writing_catalog as catalog
import writing_data_mart as base
import writing_funnel as funnel
import writing_opportunities as opportunities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def build_data_mart() -> dict[str, Any]:
    articles = catalog.load_articles()
    snapshot = analytics.load_latest_snapshot()
    backlog = opportunities.load_backlog()
    payload = base.build_data_mart(articles, snapshot, backlog)
    github_funnel = funnel.build_funnel_payload(articles, backlog)
    payload["overview"]["github_untracked_evidence"] = github_funnel["untracked_count"]
    payload["github_writing_funnel"] = github_funnel
    return payload


def validate_data_mart(payload: dict[str, Any]) -> None:
    base.validate_data_mart(payload)
    github_funnel = payload.get("github_writing_funnel")
    if not isinstance(github_funnel, dict):
        raise ValueError("analytics data mart GitHub writing funnel must be a mapping")
    candidates = github_funnel.get("candidates")
    untracked_candidates = github_funnel.get("untracked_candidates")
    if not isinstance(candidates, list):
        raise ValueError("GitHub writing funnel candidates must be a list")
    if not isinstance(untracked_candidates, list):
        raise ValueError("GitHub writing funnel untracked_candidates must be a list")
    if payload["overview"].get("github_untracked_evidence") != github_funnel.get("untracked_count"):
        raise ValueError("overview GitHub funnel count does not match funnel summary")
    if github_funnel.get("untracked_count", 0) and not untracked_candidates:
        raise ValueError("non-zero GitHub untracked count must expose an untracked candidate")
    allowed = set(github_funnel.get("monitored_repositories", []))
    for row in [*candidates, *untracked_candidates]:
        if row.get("repository") not in allowed:
            raise ValueError("GitHub writing funnel candidate is outside monitored repositories")
        if row.get("tracking_status") not in {"tracked", "untracked"}:
            raise ValueError("invalid GitHub writing funnel tracking_status")
    if any(row.get("tracking_status") != "untracked" for row in untracked_candidates):
        raise ValueError("GitHub writing funnel untracked_candidates contains tracked evidence")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> int:
    args = parse_args()
    try:
        payload = build_data_mart()
        validate_data_mart(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            "check completed: "
            f"{payload['overview']['published_articles']} published, "
            f"{payload['github_writing_funnel']['untracked_count']} untracked GitHub evidence row(s)"
        )
        return 0

    base.DATA_MART_PATH.parent.mkdir(parents=True, exist_ok=True)
    base.DATA_MART_PATH.write_text(render_json(payload), encoding="utf-8")
    print(f"wrote {base.DATA_MART_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
