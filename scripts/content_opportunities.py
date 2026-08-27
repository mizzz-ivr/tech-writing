#!/usr/bin/env python3
"""Generate content-gap, portfolio-coverage, and next-article opportunity reports."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from writing_analytics import Article, JST, ROOT, list_values, load_articles

BACKLOG_PATH = ROOT / "ideas" / "backlog.md"
GOALS_PATH = ROOT / "data" / "portfolio-coverage-goals.yml"
METRICS_DIR = ROOT / "data" / "metrics"
REPORT_PATH = ROOT / "reports" / "content-opportunities.md"

CLASSIFICATION_FIELDS = ("topics", "domains", "languages", "technologies", "portfolio_signals")
PIPELINE_METADATA_FIELDS = (
    "domains",
    "languages",
    "technologies",
    "article_type",
    "level",
    "portfolio_signals",
    "source_repositories",
)
GOAL_SELECTOR_FIELDS = {
    "topics",
    "domains",
    "languages",
    "technologies",
    "portfolio_signals",
    "article_type",
    "level",
}


@dataclass(frozen=True)
class PortfolioGoal:
    goal_id: str
    label: str
    selectors: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class BacklogItem:
    section: str
    title: str
    checked: bool
    order: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate and render without writing the report")
    return parser.parse_args()


def normalize_token(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def normalize_title_key(title: str) -> str:
    title = re.sub(r"^(?:qiita|zenn)\s*:\s*", "", title.strip(), flags=re.IGNORECASE)
    return normalize_token(title)


def load_portfolio_goals(path: Path = GOALS_PATH) -> list[PortfolioGoal]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("portfolio coverage goals must use schema_version: 1")

    raw_goals = data.get("goals")
    if not isinstance(raw_goals, list) or not raw_goals:
        raise ValueError("portfolio coverage goals must contain a non-empty goals list")

    goals: list[PortfolioGoal] = []
    seen_ids: set[str] = set()
    for raw in raw_goals:
        if not isinstance(raw, dict):
            raise ValueError("each portfolio coverage goal must be a mapping")
        goal_id = str(raw.get("id") or "").strip()
        label = str(raw.get("label") or "").strip()
        selectors = raw.get("selectors")
        if not goal_id or not label or not isinstance(selectors, dict) or not selectors:
            raise ValueError("each portfolio coverage goal requires id, label, and selectors")
        if goal_id in seen_ids:
            raise ValueError(f"duplicate portfolio coverage goal id: {goal_id}")
        seen_ids.add(goal_id)

        normalized_selectors: dict[str, tuple[str, ...]] = {}
        for field, values in selectors.items():
            if field not in GOAL_SELECTOR_FIELDS:
                raise ValueError(f"unsupported portfolio goal selector field: {field}")
            if not isinstance(values, list) or not values:
                raise ValueError(f"selector {field} for {goal_id} must be a non-empty list")
            cleaned = tuple(str(value).strip() for value in values if str(value).strip())
            if not cleaned:
                raise ValueError(f"selector {field} for {goal_id} has no usable values")
            normalized_selectors[field] = cleaned

        goals.append(PortfolioGoal(goal_id=goal_id, label=label, selectors=normalized_selectors))
    return goals


def parse_backlog(path: Path = BACKLOG_PATH) -> list[BacklogItem]:
    section = ""
    items: list[BacklogItem] = []
    order = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = re.match(r"^- \[([ xX])\] (.+)$", line)
        if not match:
            continue
        items.append(
            BacklogItem(
                section=section,
                title=match.group(2).strip(),
                checked=match.group(1).lower() == "x",
                order=order,
            )
        )
        order += 1
    return items


def article_values(article: Article, field: str) -> set[str]:
    return {normalize_token(value) for value in list_values(article.meta, field)}


def article_matches_goal(article: Article, goal: PortfolioGoal) -> bool:
    for field, selector_values in goal.selectors.items():
        values = article_values(article, field)
        if values.intersection(normalize_token(value) for value in selector_values):
            return True
    return False


def article_date(article: Article) -> date | None:
    value = article.effective_published_at
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def published_articles(articles: list[Article]) -> list[Article]:
    return [article for article in articles if article.effective_status == "published"]


def pipeline_articles(articles: list[Article]) -> list[Article]:
    return [article for article in articles if article.effective_status in {"draft", "review"}]


def goal_evidence(
    articles: list[Article], goal: PortfolioGoal
) -> tuple[list[Article], list[Article]]:
    public = [article for article in published_articles(articles) if article_matches_goal(article, goal)]
    pipeline = [article for article in pipeline_articles(articles) if article_matches_goal(article, goal)]
    return public, pipeline


def coverage_rows(articles: list[Article], field: str, as_of: date) -> list[dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = {}
    for article in published_articles(articles):
        values = list_values(article.meta, field)
        published_at = article_date(article)
        for value in values:
            row = aggregates.setdefault(value, {"value": value, "count": 0, "last": None})
            row["count"] += 1
            if published_at and (row["last"] is None or published_at > row["last"]):
                row["last"] = published_at

    rows: list[dict[str, Any]] = []
    for value in sorted(aggregates, key=lambda item: item.casefold()):
        item = aggregates[value]
        last = item["last"]
        age_days = (as_of - last).days if last else None
        rows.append(
            {
                "value": value,
                "count": item["count"],
                "last": last.isoformat() if last else None,
                "age_days": age_days,
                "within_30": age_days is not None and 0 <= age_days <= 30,
                "within_90": age_days is not None and 0 <= age_days <= 90,
                "within_365": age_days is not None and 0 <= age_days <= 365,
            }
        )
    return rows


def pipeline_missing_metadata(article: Article) -> list[str]:
    return [field for field in PIPELINE_METADATA_FIELDS if field not in article.meta or article.meta.get(field) is None]


def article_link(article: Article) -> str:
    public_url = article.platform_url("qiita") or article.platform_url("zenn")
    url = public_url or f"../articles/{article.slug}/article.md"
    title = article.title.replace("|", "\\|")
    return f"[{title}]({url})"


def article_index(articles: list[Article]) -> dict[str, Article]:
    return {normalize_title_key(article.title): article for article in articles}


def backlog_duplicates(items: list[BacklogItem]) -> dict[str, list[BacklogItem]]:
    grouped: dict[str, list[BacklogItem]] = defaultdict(list)
    for item in items:
        if not item.checked:
            grouped[normalize_title_key(item.title)].append(item)
    return {key: value for key, value in grouped.items() if len(value) > 1}


def uncovered_goals_for_article(
    article: Article, articles: list[Article], goals: list[PortfolioGoal]
) -> list[PortfolioGoal]:
    matches: list[PortfolioGoal] = []
    for goal in goals:
        public, _ = goal_evidence(articles, goal)
        if not public and article_matches_goal(article, goal):
            matches.append(goal)
    return matches


def choose_next_opportunity(
    items: list[BacklogItem], articles: list[Article], goals: list[PortfolioGoal]
) -> tuple[BacklogItem | None, Article | None, list[PortfolioGoal], str]:
    candidates = [item for item in items if item.section == "次に着手" and not item.checked]
    index = article_index(articles)

    enriched: list[tuple[BacklogItem, Article | None, list[PortfolioGoal], bool]] = []
    for item in candidates:
        article = index.get(normalize_title_key(item.title))
        gaps = uncovered_goals_for_article(article, articles, goals) if article else []
        has_source = bool(article and list_values(article.meta, "source_repositories"))
        enriched.append((item, article, gaps, has_source))

    for item, article, gaps, has_source in enriched:
        if article and article.effective_status in {"draft", "review"} and gaps and has_source:
            return item, article, gaps, "coverage gap + source evidence"
    for item, article, gaps, _ in enriched:
        if article and article.effective_status in {"draft", "review"} and gaps:
            return item, article, gaps, "coverage gap"
    for item, article, gaps, has_source in enriched:
        if article and article.effective_status in {"draft", "review"} and has_source:
            return item, article, gaps, "source evidence"
    if enriched:
        item, article, gaps, _ = enriched[0]
        return item, article, gaps, "backlog priority"
    return None, None, [], "no candidate"


def metric_snapshot_count(metrics_dir: Path = METRICS_DIR) -> int:
    if not metrics_dir.exists():
        return 0
    return len(list(metrics_dir.glob("*.json")))


def yn(value: bool) -> str:
    return "Yes" if value else "No"


def render_recency_table(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- No published values"]
    lines = [
        "| Value | Published | Last published | 30d | 90d | 365d |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        value = str(row["value"]).replace("|", "\\|")
        lines.append(
            f"| {value} | {row['count']} | {row['last'] or '-'} | "
            f"{yn(row['within_30'])} | {yn(row['within_90'])} | {yn(row['within_365'])} |"
        )
    return lines


def build_report(
    articles: list[Article],
    backlog: list[BacklogItem],
    goals: list[PortfolioGoal],
    as_of: date,
    snapshot_count: int,
) -> str:
    published = published_articles(articles)
    pipeline = pipeline_articles(articles)
    statuses = Counter(article.effective_status for article in articles)

    goal_rows: list[tuple[PortfolioGoal, str, list[Article], list[Article]]] = []
    for goal in goals:
        public, queued = goal_evidence(articles, goal)
        status = "published" if public else "pipeline" if queued else "gap"
        goal_rows.append((goal, status, public, queued))

    goal_status_counts = Counter(status for _, status, _, _ in goal_rows)
    open_backlog = [item for item in backlog if not item.checked]
    next_item, next_article, next_gaps, decision_reason = choose_next_opportunity(backlog, articles, goals)

    lines = [
        "# Content Opportunities / Portfolio Coverage",
        "",
        f"> As of: {as_of.isoformat()}",
        "",
        "## Decision Summary",
        "",
        f"- Published articles: **{len(published)}**",
        f"- Editorial pipeline: **{len(pipeline)}** "
        f"(draft {statuses.get('draft', 0)} / review {statuses.get('review', 0)})",
        f"- Open backlog items: **{len(open_backlog)}**",
        f"- Portfolio goals: **{goal_status_counts.get('published', 0)} published / "
        f"{goal_status_counts.get('pipeline', 0)} pipeline / {goal_status_counts.get('gap', 0)} gaps**",
        f"- Metric snapshot dates available: **{snapshot_count}**",
        "",
    ]

    if next_item:
        lines.append(f"- Next editorial priority: **{next_item.title}**")
    else:
        lines.append("- Next editorial priority: **No candidate in `次に着手`**")

    lines.extend(
        [
            "",
            "## Portfolio Coverage Goals",
            "",
            "Coverage is credited only from explicit article metadata matched by the configured selectors. "
            "A pipeline match is not counted as published portfolio evidence.",
            "",
            "| Goal | Status | Published evidence | Pipeline evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for goal, status, public, queued in goal_rows:
        public_text = ", ".join(article_link(article) for article in public) or "-"
        pipeline_text = ", ".join(article_link(article) for article in queued) or "-"
        lines.append(f"| {goal.label} | **{status}** | {public_text} | {pipeline_text} |")

    lines.extend(["", "## Topic Recency Matrix", ""])
    for field, label in (
        ("topics", "Topics"),
        ("domains", "Domains"),
        ("languages", "Languages"),
        ("technologies", "Technologies"),
        ("portfolio_signals", "Portfolio Signals"),
    ):
        lines.extend([f"### {label}", "", *render_recency_table(coverage_rows(articles, field, as_of)), ""])

    lines.extend(["## Editorial Pipeline", ""])
    if pipeline:
        for article in sorted(pipeline, key=lambda item: (item.effective_status, item.title.casefold())):
            missing = pipeline_missing_metadata(article)
            missing_text = ", ".join(f"`{field}`" for field in missing) if missing else "complete"
            sources = ", ".join(list_values(article.meta, "source_repositories")) or "not declared"
            lines.append(
                f"- {article_link(article)} — **{article.effective_status}** — "
                f"source repositories: {sources} — metadata: {missing_text}"
            )
    else:
        lines.append("- No draft/review articles")

    lines.extend(["", "## Backlog Alignment", ""])
    next_items = [item for item in backlog if item.section == "次に着手" and not item.checked]
    index = article_index(articles)
    if next_items:
        for item in next_items:
            article = index.get(normalize_title_key(item.title))
            if article:
                lines.append(f"- {item.title} — source article: {article_link(article)} — status **{article.effective_status}**")
            else:
                lines.append(f"- {item.title} — source article: **not linked by exact normalized title**")
    else:
        lines.append("- No open items in `次に着手`")

    duplicates = backlog_duplicates(backlog)
    lines.extend(["", "### Duplicate open backlog titles", ""])
    if duplicates:
        for grouped in duplicates.values():
            sections = ", ".join(item.section or "(no section)" for item in grouped)
            lines.append(f"- {grouped[0].title} — sections: {sections}")
    else:
        lines.append("- None")

    lines.extend(["", "## Next Article Opportunity", ""])
    if next_item:
        lines.append(f"**Decision: {next_item.title}**")
        lines.append("")
        lines.append(f"- Selection basis: **{decision_reason}**")
        if next_article:
            lines.append(f"- Current source: {article_link(next_article)} — **{next_article.effective_status}**")
            sources = list_values(next_article.meta, "source_repositories")
            lines.append(f"- Source repository evidence: {', '.join(sources) if sources else 'not declared'}")
            if next_gaps:
                lines.append(
                    "- Unpublished portfolio goals supported by explicit metadata: "
                    + ", ".join(f"**{goal.label}**" for goal in next_gaps)
                )
            else:
                lines.append("- Unpublished portfolio goals supported by explicit metadata: none")
            missing = pipeline_missing_metadata(next_article)
            if missing:
                lines.append(
                    "- Metadata to classify before publication: "
                    + ", ".join(f"`{field}`" for field in missing)
                )
        else:
            lines.append("- Matching draft/review article: not found by exact normalized title")
        if snapshot_count < 2:
            lines.append(
                f"- External reaction trend: not used for this decision because only {snapshot_count} snapshot date(s) exist"
            )
        else:
            lines.append("- External reaction trend: secondary input only; it does not override coverage/evidence")
    else:
        lines.append("- No candidate can be selected because `次に着手` has no open item")

    lines.extend(
        [
            "",
            "## Method / Guardrails",
            "",
            "- Published coverage and pipeline coverage are kept separate.",
            "- `[]` remains explicit N/A; missing metadata is not inferred or backfilled.",
            "- Portfolio goal matching uses only selectors declared in `data/portfolio-coverage-goals.yml`.",
            "- Backlog-to-article linking uses exact normalized titles only; no fuzzy semantic matching is performed.",
            "- 30 / 90 / 365 day coverage uses actual `published_at` dates only.",
            "- External reactions are not converted into a cross-platform score and are lower priority than portfolio coverage and source evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        articles = load_articles()
        backlog = parse_backlog()
        goals = load_portfolio_goals()
        as_of = datetime.now(JST).date()
        report = build_report(articles, backlog, goals, as_of, metric_snapshot_count())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(report)
        print(
            f"check completed: {len(articles)} articles, {len(backlog)} backlog items, {len(goals)} portfolio goals",
            file=sys.stderr,
        )
        return 0

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
