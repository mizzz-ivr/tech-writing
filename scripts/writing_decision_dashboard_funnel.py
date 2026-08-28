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


def theme_label(group: dict[str, Any]) -> str:
    if group.get("grouping") == "explicit_scope":
        return f"scope `{md_escape(group.get('scope') or '-')}`"
    if group.get("grouping") == "release":
        return "release"
    return "single event"


def funnel_section(payload: dict[str, Any]) -> str:
    lines = [
        "## GitHub → Writing Funnel",
        "",
        f"> GitHub snapshot as of: **{payload['as_of'] or 'not available'}**",
        "",
        "最近のpublic Repository実装を、明示的なConventional Commit scopeだけでtheme groupingして表示します。scopeが無いeventは無理にまとめません。tracked evidenceを含む監査用全件はContent Opportunities / Data Martで確認します。意味的な重複や重要度は推測しません。",
        "",
        "| Repository | Theme | Events | Representative evidence | Latest |",
        "| --- | --- | ---: | --- | --- |",
    ]
    groups = payload["theme_groups"]
    if not groups:
        message = (
            "No untracked themes detected"
            if payload["snapshot_available"]
            else "Snapshot/evidence is not available yet"
        )
        lines.append(f"| - | - | - | {message} | - |")
    for group in groups:
        representative = group["representative"]
        title = md_escape(representative["title"])
        evidence = (
            f"[{title}]({representative['url']})"
            if representative.get("url")
            else title
        )
        lines.append(
            f"| `{md_escape(group['repository'])}` | {theme_label(group)} | **{group['event_count']}** | {evidence} | {str(group['latest_at'])[:10] or '-'} |"
        )
    lines.extend(
        [
            "",
            f"Raw untracked evidence **{payload['untracked_count']}件** → deterministic theme **{payload['untracked_theme_count']}件**。Compression: **{payload['compression_ratio'] or '-'}x**。",
            "",
            "Grouping: `release`は独立theme、`feat(scope)` / `fix(scope)`等は同一Repository内の明示scopeでgrouping、scope無しはsingleton。AI semantic clustering / significance scoreは使いません。",
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
        f"| GitHub → Writing Funnel | Themes **{funnel['untracked_theme_count']}** / Events **{funnel['untracked_count']}** |\n"
    )
    rendered = rendered[:index] + funnel_kpi + rendered[index:]

    judgment_anchor = "### 今の判断\n\n"
    if judgment_anchor not in rendered:
        raise ValueError("dashboard judgment anchor is missing")
    groups = funnel["theme_groups"]
    if groups:
        first = groups[0]
        representative = first["representative"]
        judgment = (
            f"- GitHub実装の未記事化evidence **{funnel['untracked_count']}件** を、明示scopeで **{funnel['untracked_theme_count']} themes** に整理しています。先頭theme: "
            f"`{md_escape(first['repository'])}` / {md_escape(first['label'])}（{first['event_count']} events、代表: {md_escape(representative['title'])}）。\n"
        )
    elif funnel["snapshot_available"]:
        judgment = "- GitHub Writing Funnelで未記事化themeは検出されていません。\n"
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
    expected = f"| GitHub → Writing Funnel | Themes **{funnel['untracked_theme_count']}** / Events **{funnel['untracked_count']}** |"
    if expected not in rendered:
        raise ValueError("dashboard GitHub funnel KPI does not match data mart")
    if "## GitHub → Writing Funnel" not in rendered:
        raise ValueError("dashboard GitHub funnel section is missing")
    if funnel["untracked_count"] and not funnel["theme_groups"]:
        raise ValueError("dashboard cannot represent non-zero untracked funnel evidence")
    for group in funnel["theme_groups"]:
        representative = group["representative"]
        if md_escape(representative["title"]) not in rendered:
            raise ValueError("dashboard is missing a GitHub theme representative")


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
            f"check completed: {model['github_writing_funnel']['untracked_count']} untracked GitHub evidence row(s), "
            f"{model['github_writing_funnel']['untracked_theme_count']} theme(s)"
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
