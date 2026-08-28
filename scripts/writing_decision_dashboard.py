#!/usr/bin/env python3
"""Generate a decision-oriented Writing Analytics dashboard."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import writing_analytics as analytics
import writing_catalog as catalog
import writing_data_mart as data_mart
import writing_dashboard as charts
import writing_opportunities as opportunities

DASHBOARD_PATH = analytics.ROOT / "reports" / "visual-dashboard.md"
ASSET_DIR = analytics.ROOT / "reports" / "assets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build and validate the dashboard in memory without writing files",
    )
    return parser.parse_args()


def coverage_chart_entries(
    model: dict[str, Any], key: str, limit: int = 8
) -> list[tuple[str, int]]:
    values = model["coverage"][key]["values"]
    return [
        (str(row["value"]), int(row["published_count"]))
        for row in values[:limit]
    ]


def reaction_chart_entries(model: dict[str, Any]) -> list[tuple[str, int]]:
    """Chart reaction fields only; page views remain available in the Data Mart detail."""

    entries: list[tuple[str, int]] = []
    for platform, metrics in model["reactions"]["observed_numeric_totals"].items():
        allowed = {key for key, _label in analytics.reaction_fields(platform)}
        for key, value in metrics.items():
            if key in allowed:
                entries.append((f"{platform} {key}", int(value)))
    return sorted(entries, key=lambda item: item[0].casefold())


def chart_payloads(model: dict[str, Any]) -> dict[str, str]:
    pipeline_order = ("draft", "review", "published", "archived")
    pipeline = model["pipeline"]
    pipeline_entries = [(status, int(pipeline.get(status, 0))) for status in pipeline_order]
    pipeline_entries.extend(
        (status, int(value))
        for status, value in pipeline.items()
        if status not in pipeline_order
    )

    return {
        "pipeline.svg": charts.svg_bar_chart(
            "Editorial pipeline", pipeline_entries, max_items=len(pipeline_entries)
        ),
        "domains.svg": charts.svg_bar_chart(
            "Published domains", coverage_chart_entries(model, "domains")
        ),
        "technologies.svg": charts.svg_bar_chart(
            "Technology coverage", coverage_chart_entries(model, "technologies")
        ),
        "portfolio-signals.svg": charts.svg_bar_chart(
            "Portfolio signals", coverage_chart_entries(model, "portfolio_signals")
        ),
        "reactions.svg": charts.svg_bar_chart(
            "Observed reactions", reaction_chart_entries(model)
        ),
    }


def pipeline_gap_lines(model: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in data_mart.COVERAGE_KEYS:
        values = model["coverage"][key]["pipeline_only_values"]
        if values:
            rendered = ", ".join(f"`{value}`" for value in values)
            lines.append(f"- **{key}:** {rendered}")
    return lines or ["- Pipeline-only gapはありません"]


def trend_status(model: dict[str, Any], window: int) -> str:
    return "Ready" if model["trend_readiness"]["windows"].get(str(window)) else "Waiting"


def build_dashboard(model: dict[str, Any]) -> str:
    overview = model["overview"]
    trend = model["trend_readiness"]
    quality = model["data_quality"]
    candidates = model["next_article_candidates"]
    next_candidate = candidates[0] if candidates else None

    if next_candidate:
        candidate_title = str(next_candidate["title"]).replace("|", "\\|")
        next_article = (
            f"[{candidate_title}](../{next_candidate['path']}) "
            f"(`{next_candidate['status']}`)"
        )
    else:
        next_article = "候補なし"

    quality_summary = (
        "問題なし"
        if quality["finding_count"] == 0
        else f"{quality['finding_count']}件 — 下のData Qualityを確認"
    )

    lines = [
        "# Writing Analytics — Decision Dashboard",
        "",
        f"> As of: {model['as_of']} · Derived from Repository metadata / publication registry / stored metric snapshots",
        "",
        "## まず見る",
        "",
        "| 判断軸 | 現在 |",
        "| --- | --- |",
        f"| Published | **{overview['published_articles']}** |",
        f"| Pipeline | Draft **{overview['draft_articles']}** / Review **{overview['review_articles']}** |",
        f"| Last published | **{overview['last_published_at'] or '-'}** |",
        f"| Metric snapshots | **{trend['snapshot_count']}** / observed span **{trend['observed_span_days']}d** |",
        f"| Data Quality | **{quality_summary}** |",
        f"| Pipeline-only coverage gaps | **{overview['pipeline_only_coverage_gaps']}** |",
        f"| 次の記事候補 | {next_article} |",
        "",
        "### 今の判断",
        "",
    ]

    if trend["windows"].get("7"):
        lines.append("- 7日Trendを実データだけで分析できる状態です。")
    else:
        lines.append(
            f"- 7日Trendはまだ待機中です。現在の実snapshot spanは **{trend['observed_span_days']}日** で、補間はしません。"
        )

    if quality["finding_count"]:
        lines.append(
            f"- Data Quality findingが **{quality['finding_count']}件** あります。記事追加より先に、必要ならmetadata整備対象として確認できます。"
        )
    else:
        lines.append("- Data Quality blockerはありません。")

    if next_candidate:
        gap_bits = list(next_candidate["portfolio_gaps"]) + list(next_candidate["coverage_gaps"])
        if gap_bits:
            lines.append(
                "- 次記事候補の主な根拠: " + ", ".join(f"`{item}`" for item in gap_bits[:4])
            )
        elif next_candidate["source_evidence_recorded"]:
            lines.append("- 次記事候補は実装Repositoryの根拠が記録済みです。")

    lines.extend(
        [
            "",
            "## Editorial Pipeline",
            "",
            "![Editorial pipeline](./assets/pipeline.svg)",
            "",
            "## Coverage Gaps",
            "",
            "draft / reviewにはあるが、公開済みPortfolioではまだ示せていないclassificationです。",
            "",
            *pipeline_gap_lines(model),
            "",
            "## Portfolio Coverage",
            "",
            "全classificationの詳細表は [Content Opportunities](./content-opportunities.md) に委譲し、ここでは分布だけを確認します。",
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
            "reaction chartはlikes / stocks / bookmarks / commentsのみを描画します。page viewsはData Martの観測値として保持します。`0` / `unavailable` / field missingは別状態で、単一のPopularity Scoreには集約しません。",
            "",
            "| Article | Platform | Reactions / observed metrics |",
            "| --- | --- | --- |",
        ]
    )

    observations = model["reactions"]["observations"]
    if observations:
        for row in observations:
            metrics = row["metrics"]
            summary_parts = []
            for key, value in metrics.items():
                if key == "error":
                    continue
                if value is None:
                    summary_parts.append(f"{key} unavailable")
                else:
                    summary_parts.append(f"{key} {value}")
            if metrics.get("error"):
                summary_parts.append("metrics error")
            title = str(row["title"]).replace("|", "\\|")
            url = row["url"]
            linked = f"[{title}]({url})" if url else title
            lines.append(
                f"| {linked} | {row['platform']} | {' · '.join(summary_parts) or 'not collected'} |"
            )
    else:
        lines.append("| - | - | Metrics snapshot is not available yet |")

    lines.extend(["", "## Trend Readiness", ""])
    lines.extend(
        [
            f"- Snapshot count: **{trend['snapshot_count']}**",
            f"- First snapshot: **{trend['first_snapshot_at'] or '-'}**",
            f"- Latest snapshot: **{trend['last_snapshot_at'] or '-'}**",
            f"- Observed span: **{trend['observed_span_days']} days**",
            "",
            "| Window | Status |",
            "| --- | --- |",
            f"| 7d | **{trend_status(model, 7)}** |",
            f"| 30d | **{trend_status(model, 30)}** |",
            f"| 90d | **{trend_status(model, 90)}** |",
            "",
            "履歴不足時は推測・直線補間・synthetic historyを作りません。",
            "",
            "## Data Quality",
            "",
        ]
    )

    if quality["findings"]:
        lines.extend(f"- {finding}" for finding in quality["findings"])
    else:
        lines.append("- No issues detected")

    lines.extend(
        [
            "",
            "## Analysis Data",
            "",
            "- [Normalized Writing Analytics Data Mart](../data/analytics/writing-analytics.json) — 集計・分析用の共通derived JSON",
            "- [Public Writing Portfolio JSON](../data/exports/writing-portfolio.json) — 外部公開向けstable schema",
            "- [Writing Profile](./writing-profile.md) — 詳細テキスト分析",
            "- [Content Opportunities](./content-opportunities.md) — coverage全件・次記事推薦の詳細",
            "",
            "## Source of Truth",
            "",
            "- Article metadata: `articles/**`",
            "- Publication registry: `ideas/published.md`",
            "- Raw external metrics: `data/metrics/YYYY-MM-DD.json`",
            "- Data Mart / Dashboard / reports: **derived / regeneratable**",
        ]
    )
    return "\n".join(lines) + "\n"


def validate_dashboard(model: dict[str, Any], dashboard: str) -> None:
    published = model["overview"]["published_articles"]
    if f"| Published | **{published}** |" not in dashboard:
        raise ValueError("dashboard published KPI does not match data mart")
    if "## まず見る" not in dashboard or "## Analysis Data" not in dashboard:
        raise ValueError("dashboard decision sections are missing")


def main() -> int:
    args = parse_args()
    try:
        articles = catalog.load_articles()
        snapshot = analytics.load_latest_snapshot()
        backlog = opportunities.load_backlog()
        model = data_mart.build_data_mart(articles, snapshot, backlog)
        data_mart.validate_data_mart(model)
        dashboard = build_dashboard(model)
        validate_dashboard(model, dashboard)
        assets = chart_payloads(model)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            "check completed: "
            f"{model['overview']['published_articles']} published, "
            f"{model['overview']['pipeline_only_coverage_gaps']} coverage gap(s), "
            f"{model['data_quality']['finding_count']} quality finding(s)",
            file=sys.stderr,
        )
        return 0

    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(dashboard, encoding="utf-8")
    for filename, content in assets.items():
        (ASSET_DIR / filename).write_text(content, encoding="utf-8")

    print(f"wrote {DASHBOARD_PATH.relative_to(analytics.ROOT)}")
    for filename in sorted(assets):
        print(f"wrote {(ASSET_DIR / filename).relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
