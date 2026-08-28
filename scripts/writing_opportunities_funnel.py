#!/usr/bin/env python3
"""Render Content Opportunities with stored GitHub writing-funnel evidence."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import writing_analytics as analytics
import writing_funnel as funnel
import writing_opportunities as opportunities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def funnel_section(payload: dict[str, Any]) -> str:
    lines = [
        "## GitHub → Writing Funnel",
        "",
        "configured public repositoryのstored GitHub snapshotから、まだarticle/backlog titleと明示的に重複しない実装evidenceを可視化します。title overlap以外の意味的重複や重要度は推測しません。",
        "",
        f"- Snapshot: **{payload['as_of'] or 'not available'}**",
        f"- Monitored repositories: **{len(payload['monitored_repositories'])}**",
        f"- Evidence rows: **{payload['evidence_count']}**",
        f"- Untracked evidence: **{payload['untracked_count']}**",
        f"- Tracked by explicit title overlap: **{payload['tracked_count']}**",
        "",
        "| Repository | Kind | Evidence | Date | Tracking |",
        "| --- | --- | --- | --- | --- |",
    ]
    candidates = payload["candidates"]
    if not candidates:
        lines.append("| - | - | Snapshot/evidence is not available yet | - | - |")
    for row in candidates:
        title = md_escape(row["title"])
        evidence = f"[{title}]({row['url']})" if row.get("url") else title
        tracking = str(row["tracking_status"])
        if tracking == "tracked":
            tracking += f" → {md_escape(row.get('matched_source'))}: {md_escape(row.get('matched_title'))}"
        lines.append(
            f"| `{md_escape(row['repository'])}` | `{md_escape(row['kind'])}` | {evidence} | {str(row['occurred_at'])[:10] or '-'} | {tracking} |"
        )
    lines.extend(
        [
            "",
            "Priorityは `release` → `pull_request` → labeled `issue` → recency の明示ルールです。単一のAI significance scoreは作りません。",
            "",
        ]
    )
    return "\n".join(lines)


def build_report() -> tuple[str, dict[str, Any]]:
    articles = opportunities.load_opportunity_articles()
    backlog = opportunities.load_backlog()
    snapshot = analytics.load_latest_snapshot()
    as_of = opportunities.resolve_as_of(articles)
    base = opportunities.build_report(articles, backlog, snapshot, as_of).rstrip()
    payload = funnel.build_funnel_payload(articles, backlog)
    return base + "\n\n" + funnel_section(payload), payload


def validate_report(report: str, payload: dict[str, Any]) -> None:
    if "## GitHub → Writing Funnel" not in report:
        raise ValueError("GitHub writing funnel section is missing")
    if f"- Untracked evidence: **{payload['untracked_count']}**" not in report:
        raise ValueError("GitHub writing funnel summary does not match payload")


def main() -> int:
    args = parse_args()
    try:
        report, payload = build_report()
        validate_report(report, payload)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.check:
        print(f"check completed: {payload['untracked_count']} untracked GitHub evidence row(s)")
        return 0
    opportunities.REPORT_PATH.write_text(report + "\n", encoding="utf-8")
    print(f"wrote {opportunities.REPORT_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
