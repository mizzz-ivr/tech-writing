#!/usr/bin/env python3
"""Generate a visual Writing Analytics dashboard and SVG charts."""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics

DASHBOARD_PATH = analytics.ROOT / "reports" / "visual-dashboard.md"
ASSET_DIR = analytics.ROOT / "reports" / "assets"
PIPELINE_STATUS_ORDER = ("draft", "review", "published", "archived")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that committed dashboard and chart files match the deterministic rendering",
    )
    return parser.parse_args()


def status_counts(articles: list[analytics.Article]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for article in articles:
        counts[article.effective_status] += 1
    return counts


def pipeline_rows(counts: Counter[str]) -> list[tuple[str, int]]:
    """Render every tracked status while keeping common states in a stable order."""
    rows = [(status, counts.get(status, 0)) for status in PIPELINE_STATUS_ORDER]
    known = set(PIPELINE_STATUS_ORDER)
    rows.extend((status, counts[status]) for status in sorted(counts) if status not in known)
    return rows


def observed_reaction_counts(snapshot: dict | None) -> dict[str, int]:
    """Return only observed numeric values; null/missing values are not coerced to zero."""
    totals: dict[str, int] = {}
    if not snapshot:
        return totals

    for _title, platform, _url, metrics in analytics.reaction_rows(snapshot):
        for key, label in analytics.reaction_fields(platform):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            name = f"{platform} {label}"
            totals[name] = totals.get(name, 0) + int(value)
    return totals


def svg_bar_chart(title: str, entries: Iterable[tuple[str, int]], *, max_items: int = 8) -> str:
    rows = list(entries)[:max_items]
    width = 920
    left = 250
    right = 80
    top = 76
    row_height = 42
    bottom = 36
    height = top + max(1, len(rows)) * row_height + bottom
    chart_width = width - left - right
    max_value = max((value for _, value in rows), default=0)
    scale_max = max(max_value, 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(title)}</title>',
        f'<desc id="desc">Horizontal bar chart for {html.escape(title)}</desc>',
        '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
        f'<text x="28" y="38" fill="#f0f6fc" font-family="system-ui,sans-serif" font-size="22" font-weight="700">{html.escape(title)}</text>',
    ]

    if not rows:
        parts.append(
            '<text x="28" y="92" fill="#8b949e" font-family="system-ui,sans-serif" font-size="16">No observed data</text>'
        )
    else:
        for index, (label, value) in enumerate(rows):
            y = top + index * row_height
            bar_width = 0 if value <= 0 else max(4, int(chart_width * value / scale_max))
            parts.append(
                f'<text x="{left - 16}" y="{y + 21}" text-anchor="end" fill="#c9d1d9" font-family="system-ui,sans-serif" font-size="14">{html.escape(str(label))}</text>'
            )
            parts.append(
                f'<rect x="{left}" y="{y + 7}" width="{chart_width}" height="20" rx="5" fill="#21262d"/>'
            )
            if bar_width:
                parts.append(
                    f'<rect x="{left}" y="{y + 7}" width="{bar_width}" height="20" rx="5" fill="#58a6ff"/>'
                )
            parts.append(
                f'<text x="{left + chart_width + 14}" y="{y + 22}" fill="#f0f6fc" font-family="ui-monospace,monospace" font-size="14">{value}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def chart_payloads(articles: list[analytics.Article], snapshot: dict | None) -> dict[str, str]:
    published = analytics.published_articles(articles)
    pipeline = status_counts(articles)
    pipeline_entries = pipeline_rows(pipeline)
    domains = analytics.count_field(published, "domains")
    technologies = analytics.count_field(published, "technologies")
    signals = analytics.count_field(published, "portfolio_signals")
    reactions = observed_reaction_counts(snapshot)

    return {
        "pipeline.svg": svg_bar_chart(
            "Editorial pipeline", pipeline_entries, max_items=len(pipeline_entries)
        ),
        "domains.svg": svg_bar_chart("Published domains", domains.most_common(8)),
        "technologies.svg": svg_bar_chart("Technology coverage", technologies.most_common(8)),
        "portfolio-signals.svg": svg_bar_chart("Portfolio signals", signals.most_common(8)),
        "reactions.svg": svg_bar_chart("Observed reactions", sorted(reactions.items())),
    }


def is_readable_metric_snapshot(path: Path) -> bool:
    """Accept only parseable snapshot files with the fields required for history analysis."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    if not isinstance(payload, dict):
        return False
    if not isinstance(payload.get("articles"), list):
        return False
    collected_at = payload.get("collected_at")
    if not isinstance(collected_at, str) or not collected_at.strip():
        return False
    return True


def latest_snapshot_count() -> int:
    if not analytics.METRICS_DIR.exists():
        return 0
    return sum(
        1
        for path in analytics.METRICS_DIR.glob("*.json")
        if is_readable_metric_snapshot(path)
    )


def snapshot_source_time(snapshot: dict | None) -> str:
    """Return a deterministic display time from the persisted metric snapshot."""
    if not snapshot:
        return "unavailable"
    raw = snapshot.get("collected_at")
    if not raw:
        return "unavailable"

    value = str(raw)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        return value
    return parsed.astimezone(analytics.JST).strftime("%Y-%m-%d %H:%M JST")


def build_dashboard(articles: list[analytics.Article], snapshot: dict | None) -> str:
    published = analytics.published_articles(articles)
    last_date, avg_gap = analytics.cadence_summary(published)
    quality = analytics.data_quality(articles)
    rows = analytics.reaction_rows(snapshot)
    snapshots = latest_snapshot_count()
    source_snapshot = snapshot_source_time(snapshot)

    lines = [
        "# Writing Analytics Visual Dashboard",
        "",
        f"> Source snapshot: {source_snapshot}",
        "",
        "Repository metadata and metric snapshots remain the Source of Truth. This page and the SVG files are derived/generated views.",
        "",
        "## Overview",
        "",
        "| KPI | Value |",
        "| --- | ---: |",
        f"| Published | **{len(published)}** |",
        f"| Tracked | **{len(articles)}** |",
        f"| Last published | **{last_date}** |",
        f"| Average interval | **{avg_gap}** |",
        f"| Data quality findings | **{len(quality)}** |",
        f"| Metric snapshots | **{snapshots}** |",
        "",
        "## Editorial Pipeline",
        "",
        "![Editorial pipeline](./assets/pipeline.svg)",
        "",
        "## Portfolio Coverage",
        "",
        "### Domains",
        "",
        "![Published domains](./assets/domains.svg)",
        "",
        "### Technologies",
        "",
        "![Technology coverage](./assets/technologies.svg)",
        "",
        "### Portfolio Signals",
        "",
        "![Portfolio signals](./assets/portfolio-signals.svg)",
        "",
        "## Reactions",
        "",
        "![Observed reactions](./assets/reactions.svg)",
        "",
        "The reaction chart contains only observed numeric values. `unavailable` and `not collected` are omitted rather than converted to zero.",
        "",
        "| Article | Platform | Reactions |",
        "| --- | --- | --- |",
    ]

    if rows:
        for title, platform, url, metrics in rows:
            lines.append(
                f"| {analytics.md_link(title, url)} | {platform} | {analytics.reaction_summary(platform, metrics, include_page_views=True)} |"
            )
    else:
        lines.append("| - | - | Metrics snapshot is not available yet |")

    lines.extend(["", "## Recent Publications", ""])
    if published:
        for article in published[:8]:
            url = article.platform_url("qiita") or article.platform_url("zenn")
            lines.append(
                f"- **{article.effective_published_at or '-'}** — `{article.slug}` — {analytics.md_link(article.title, url)}"
            )
    else:
        lines.append("- No published articles")

    lines.extend(["", "## Trend Readiness", ""])
    if snapshots < 2:
        lines.extend(
            [
                f"- Historical trend chart is intentionally not generated yet: **{snapshots} snapshot(s)** available.",
                "- 7 / 30 / 90 day trend starts only after real snapshots accumulate; no interpolation or synthetic history is used.",
            ]
        )
    else:
        lines.extend(
            [
                f"- **{snapshots} snapshots** are available.",
                "- Time-series trend visualization can be generated from actual stored snapshots.",
            ]
        )

    lines.extend(["", "## Data Quality", ""])
    if quality:
        lines.extend(f"- {item}" for item in quality)
    else:
        lines.append("- **No issues detected**")

    lines.extend(
        [
            "",
            "## Source of Truth",
            "",
            "- Article metadata: `articles/*/article.md`",
            "- Publication registry: `ideas/published.md`",
            "- Raw external metrics: `data/metrics/YYYY-MM-DD.json`",
            "- Detailed text report: [`writing-profile.md`](./writing-profile.md)",
            "- Visual assets: `reports/assets/*.svg`",
            "",
        ]
    )
    return "\n".join(lines)


def render() -> tuple[str, dict[str, str]]:
    articles = analytics.load_articles()
    snapshot = analytics.load_latest_snapshot()
    return build_dashboard(articles, snapshot), chart_payloads(articles, snapshot)


def generated_file_mismatches(dashboard: str, charts: dict[str, str]) -> list[Path]:
    """Return generated files that are missing or differ from the deterministic rendering."""
    mismatches: list[Path] = []
    if not DASHBOARD_PATH.exists() or DASHBOARD_PATH.read_text(encoding="utf-8") != dashboard:
        mismatches.append(DASHBOARD_PATH)

    for filename, expected in charts.items():
        path = ASSET_DIR / filename
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            mismatches.append(path)
    return mismatches


def display_path(path: Path) -> str:
    try:
        return path.relative_to(analytics.ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    args = parse_args()
    try:
        dashboard, charts = render()
    except Exception as exc:  # keep CI output actionable without hiding the underlying error
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        mismatches = generated_file_mismatches(dashboard, charts)
        if mismatches:
            for path in mismatches:
                print(f"ERROR: stale generated file: {display_path(path)}", file=sys.stderr)
            print("Run `python scripts/writing_dashboard.py` and commit the generated changes.", file=sys.stderr)
            return 1
        print(f"check completed: {len(charts)} generated chart files are current", file=sys.stderr)
        return 0

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in charts.items():
        (ASSET_DIR / filename).write_text(content, encoding="utf-8")
    DASHBOARD_PATH.write_text(dashboard, encoding="utf-8")
    print(f"wrote {DASHBOARD_PATH.relative_to(analytics.ROOT)}")
    print(f"wrote {len(charts)} chart assets to {ASSET_DIR.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
