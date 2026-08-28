#!/usr/bin/env python3
"""Render Decision Dashboard with GitHub -> Writing Funnel evidence."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import writing_analytics as analytics
import writing_data_mart_funnel as mart
import writing_decision_dashboard as base


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
        f"> GitHub snapshot as of: **{payload['as_of'] or 'not available'}**",
        "",
        "最近のpublic Repository実装から、article/backlog titleと明示的に重複していないevidenceを確認します。意味的な重複や重要度は推測しません。",
        "",
        "| Repository | Kind | Evidence | Date | Tracking |",
        "| --- | --- | --- | --- | --- |",
    ]
    if not payload["candidates"]:
        lines.append("| - | - | Snapshot/evidence is not available yet | - | - |")
    for row in payload["candidates"]:
        title = md_escape(row["title"])
        evidence = f"[{title}]({row['url']})" if row.get("url") else title
        tracking = str(row["tracking_status"])
        if tracking == "tracked":
            tracking += f" → {md_escape(row.get('matched_source'))}"
        lines.append(
            f"| `{md_escape(row['repository'])}` | `{md_escape(row['kind'])}` | {evidence} | {str(row['occurred_at'])[:10] or '-'} | {tracking} |"
        )
    lines.extend(
        [
            "",
            "Priority: `release` → `pull_request` → labeled `issue` → recency。AI significance scoreは使いません。",
            "",
        ]
    )
    return "\n".join(lines)


def build_dashboard(model: dict[str, Any]) -> str:
    rendered = base.build_dashboard(model)
    funnel = model["github_writing_funnel"]

    next_row = "| 次の記事候補 |"
    index = rendered.find(next_row)
    if index < 0:
        raise ValueError("dashboard next-article KPI anchor is missing")
    funnel_kpi = (
        f"| GitHub → Writing Funnel | Untracked **{funnel['untracked_count']}** / Evidence **{funnel['evidence_count']}** |\n"
    )
    rendered = rendered[:index] + funnel_kpi + rendered[index:]

    judgment_anchor = "### 今の判断\n\n"
    if judgment_anchor not in rendered:
        raise ValueError("dashboard judgment anchor is missing")
    untracked = funnel["untracked_candidates"]
    if untracked:
        first = untracked[0]
        judgment = (
            f"- GitHub実装evidenceに未記事化候補が **{funnel['untracked_count']}件** あります。先頭候補: "
            f"`{md_escape(first['repository'])}` / {md_escape(first['title'])}。\n"
        )
    elif funnel["snapshot_available"]:
        judgment = "- GitHub Writing Funnelで未記事化evidenceは検出されていません。\n"
    else:
        judgment = "- GitHub Writing Funnel snapshotはまだありません。次回main/daily refresh後に候補が表示されます。\n"
    rendered = rendered.replace(judgment_anchor, judgment_anchor + judgment, 1)

    section_anchor = "## Source Freshness\n"
    if section_anchor not in rendered:
        raise ValueError("dashboard Source Freshness anchor is missing")
    rendered = rendered.replace(
        section_anchor, funnel_section(funnel) + "\n" + section_anchor, 1
    )

    source_anchor = "- Raw external metrics: `data/metrics/YYYY-MM-DD.json`\n"
    source_line = "- Raw GitHub writing evidence: `data/github-funnel/YYYY-MM-DD.json`\n"
    if source_anchor not in rendered:
        raise ValueError("dashboard Source of Truth metrics anchor is missing")
    rendered = rendered.replace(source_anchor, source_anchor + source_line, 1)
    return rendered


def validate_dashboard(model: dict[str, Any], rendered: str) -> None:
    base.validate_dashboard(model, rendered)
    funnel = model["github_writing_funnel"]
    expected = f"| GitHub → Writing Funnel | Untracked **{funnel['untracked_count']}** / Evidence **{funnel['evidence_count']}** |"
    if expected not in rendered:
        raise ValueError("dashboard GitHub funnel KPI does not match data mart")
    if "## GitHub → Writing Funnel" not in rendered:
        raise ValueError("dashboard GitHub funnel section is missing")
    if funnel["untracked_count"] and not funnel["untracked_candidates"]:
        raise ValueError("dashboard cannot represent non-zero untracked funnel evidence")


def main() -> int:
    args = parse_args()
    try:
        model = mart.build_data_mart()
        mart.validate_data_mart(model)
        rendered = build_dashboard(model)
        validate_dashboard(model, rendered)
        assets = base.chart_payloads(model)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            f"check completed: {model['github_writing_funnel']['untracked_count']} untracked GitHub evidence row(s)"
        )
        return 0

    base.DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    base.DASHBOARD_PATH.write_text(rendered, encoding="utf-8")
    base.ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in assets.items():
        (base.ASSET_DIR / filename).write_text(content, encoding="utf-8")
    print(f"wrote {base.DASHBOARD_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
