#!/usr/bin/env python3
"""Generate Content Gap / Next Article Opportunity reporting."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics
import writing_catalog as catalog

BACKLOG_PATH = analytics.ROOT / "ideas" / "backlog.md"
REPORT_PATH = analytics.ROOT / "reports" / "content-opportunities.md"
COVERAGE_KEYS = ("topics", "domains", "languages", "technologies", "portfolio_signals")
GAP_KEYS = ("domains", "languages", "technologies")
WINDOWS = (30, 90, 365)
OVERLAP_THRESHOLD = 0.88
UNPUBLISHED_GAP_AGE = WINDOWS[-1] + 1


@dataclass(frozen=True)
class BacklogItem:
    title: str
    section: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class Candidate:
    article: analytics.Article
    portfolio_gaps: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    oldest_gap_age: int
    sources: tuple[str, ...]
    reaction_context: int
    missing_metadata: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate source metadata and render the report in memory without writing",
    )
    return parser.parse_args()


def load_opportunity_articles() -> list[analytics.Article]:
    """Load the shared sidecar-aware article catalog used by all analytics products."""

    return catalog.load_articles()


def parse_iso_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def resolve_as_of(articles: list[analytics.Article]) -> date:
    if analytics.METRICS_DIR.exists():
        for path in reversed(sorted(analytics.METRICS_DIR.glob("*.json"))):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                snapshot_date = date.fromisoformat(path.stem)
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if isinstance(payload, dict) and isinstance(payload.get("articles"), list):
                return snapshot_date

    published_dates = [
        parsed
        for article in articles
        if (parsed := parse_iso_date(article.effective_published_at)) is not None
    ]
    return max(published_dates) if published_dates else date.today()


def published_value_dates(
    articles: list[analytics.Article], key: str
) -> dict[str, list[date]]:
    result: dict[str, list[date]] = {}
    for article in analytics.published_articles(articles):
        published_at = parse_iso_date(article.effective_published_at)
        if published_at is None or not analytics.has_explicit_classification(article.meta, key):
            continue
        for value in analytics.list_values(article.meta, key):
            result.setdefault(value, []).append(published_at)
    return result


def published_values(articles: list[analytics.Article], key: str) -> set[str]:
    return set(published_value_dates(articles, key))


def coverage_rows(
    articles: list[analytics.Article], key: str, as_of: date
) -> list[tuple[str, int, date, int]]:
    rows = []
    for value, dates in published_value_dates(articles, key).items():
        last = max(dates)
        rows.append((value, len(dates), last, max(0, (as_of - last).days)))
    return sorted(rows, key=lambda row: (-row[1], row[0].casefold()))


def normalize_title(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"^(?:zenn|qiita|note(?:\s*#\d+)?)\s*[:：]\s*", "", value)
    return re.sub(r"[\s「」『』【】（）()\[\]［］・:：—–\-_/]+", "", value)


def title_similarity(left: str, right: str) -> float:
    left_norm = normalize_title(left)
    right_norm = normalize_title(right)
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def parse_backlog_text(text: str) -> list[BacklogItem]:
    items: list[BacklogItem] = []
    section = "Unsectioned"
    title: str | None = None
    item_section = section
    metadata: dict[str, str] = {}

    def flush() -> None:
        nonlocal title, metadata
        if title is not None:
            items.append(BacklogItem(title, item_section, dict(metadata)))
        title = None
        metadata = {}

    for line in text.splitlines():
        heading = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if heading:
            flush()
            section = heading.group(1).strip()
            continue
        item = re.match(r"^- \[([ xX])\]\s+(.+?)\s*$", line)
        if item:
            flush()
            if item.group(1).casefold() == "x":
                continue
            title = item.group(2).strip()
            item_section = section
            continue
        if title is not None:
            detail = re.match(r"^\s{2,}-\s+([^:：]+)[:：]\s*(.+?)\s*$", line)
            if detail:
                metadata[detail.group(1).strip()] = detail.group(2).strip()
    flush()
    return items


def load_backlog(path: Path = BACKLOG_PATH) -> list[BacklogItem]:
    if not path.exists():
        return []
    return parse_backlog_text(path.read_text(encoding="utf-8"))


def source_of_truth(item: BacklogItem) -> str | None:
    for key, value in item.metadata.items():
        if key.casefold() in {"source of truth", "source", "repository", "repo"}:
            return value
    return None


def best_title_overlap(
    item: BacklogItem, article_titles: list[tuple[str, str]]
) -> tuple[str, str, float] | None:
    best: tuple[str, str, float] | None = None
    for status, title in article_titles:
        similarity = title_similarity(item.title, title)
        if best is None or similarity > best[2]:
            best = (status, title, similarity)
    if best and best[2] >= OVERLAP_THRESHOLD:
        return best
    return None


def explicit_values(article: analytics.Article, key: str) -> list[str] | None:
    if not analytics.has_explicit_classification(article.meta, key):
        return None
    return analytics.list_values(article.meta, key)


def missing_classification(article: analytics.Article) -> tuple[str, ...]:
    return tuple(
        key for key in COVERAGE_KEYS if not analytics.has_explicit_classification(article.meta, key)
    )


def candidate_sort_key(candidate: Candidate) -> tuple[Any, ...]:
    status_rank = 1 if candidate.article.effective_status == "review" else 0
    return (
        len(candidate.portfolio_gaps),
        bool(candidate.sources),
        len(candidate.coverage_gaps),
        candidate.oldest_gap_age,
        candidate.reaction_context,
        status_rank,
        candidate.article.title.casefold(),
    )


def build_candidates(
    articles: list[analytics.Article], snapshot: dict[str, Any] | None, as_of: date
) -> list[Candidate]:
    published = analytics.published_articles(articles)
    published_signals = published_values(published, "portfolio_signals")
    published_by_key = {
        key: published_value_dates(published, key) for key in GAP_KEYS
    }
    reaction_titles = {
        title
        for title, _, _, metrics in analytics.notable_reaction_rows(snapshot)
        if any((metrics.get(key) or 0) > 0 for key in metrics)
    }

    candidates = []
    for article in articles:
        if article.effective_status not in {"draft", "review"}:
            continue
        signals = explicit_values(article, "portfolio_signals")
        portfolio_gaps = tuple(
            value for value in (signals or []) if value not in published_signals
        )
        coverage_gaps: list[str] = []
        oldest_gap_age = 0
        for key in GAP_KEYS:
            values = explicit_values(article, key)
            if values is None:
                continue
            for value in values:
                dates = published_by_key[key].get(value, [])
                age = (
                    max(0, (as_of - max(dates)).days)
                    if dates
                    else UNPUBLISHED_GAP_AGE
                )
                if age > WINDOWS[0]:
                    coverage_gaps.append(f"{key}:{value}")
                    oldest_gap_age = max(oldest_gap_age, age)
        sources = tuple(analytics.list_values(article.meta, "source_repositories"))
        reaction_context = sum(
            1
            for published_article in published
            if published_article.title in reaction_titles
            and any(
                value in analytics.list_values(published_article.meta, key)
                for key in COVERAGE_KEYS
                for value in (explicit_values(article, key) or [])
            )
        )
        candidates.append(
            Candidate(
                article=article,
                portfolio_gaps=portfolio_gaps,
                coverage_gaps=tuple(coverage_gaps),
                oldest_gap_age=oldest_gap_age,
                sources=sources,
                reaction_context=reaction_context,
                missing_metadata=missing_classification(article),
            )
        )

    return sorted(candidates, key=candidate_sort_key, reverse=True)


def render_coverage(
    articles: list[analytics.Article], key: str, as_of: date
) -> list[str]:
    lines = [
        f"### {key}",
        "",
        "| Value | Published | Last published | Age | 30d | 90d | 365d |",
        "| --- | ---: | --- | ---: | :---: | :---: | :---: |",
    ]
    rows = coverage_rows(articles, key, as_of)
    if not rows:
        lines.append("| - | 0 | - | - | - | - | - |")
    for value, count, last, age in rows:
        markers = ["✓" if age <= window else "-" for window in WINDOWS]
        lines.append(
            f"| {value} | {count} | {last.isoformat()} | {age}d | {markers[0]} | {markers[1]} | {markers[2]} |"
        )
    lines.append("")
    return lines


def pipeline_only_values(
    articles: list[analytics.Article], key: str
) -> list[str]:
    published = published_values(articles, key)
    pending = set()
    for article in articles:
        if article.effective_status not in {"draft", "review"}:
            continue
        values = explicit_values(article, key)
        if values:
            pending.update(values)
    return sorted(pending - published, key=str.casefold)


def render_report(
    articles: list[analytics.Article],
    backlog: list[BacklogItem],
    snapshot: dict[str, Any] | None,
    as_of: date,
) -> str:
    published = analytics.published_articles(articles)
    candidates = build_candidates(articles, snapshot, as_of)
    lines = [
        "# Content Gap / Next Article Opportunities",
        "",
        f"> As of: {as_of.isoformat()}",
        "",
        "Repository metadataから再生成するderived reportです。本文やbacklog自由文から技術分類を推測せず、明示されたmetadataだけを使います。",
        "",
        "## Recommendation Policy",
        "",
        "候補は単一スコアへ潰さず、次の優先順位を辞書順に評価します。",
        "",
        "1. Portfolio / career coverage gap",
        "2. `source_repositories` 等で実装・検証根拠が明示されているか",
        "3. 未公開classification / 最終投稿日からのcoverage gap・recency",
        "4. 関連する公開記事のpositive reaction",
        "5. 同条件なら `review` を `draft` よりreadyとして扱う",
        "",
        "external reactionは4番目の補助情報で、反応が良いテーマだけを書く推薦にはしません。",
        "",
        "## Current Portfolio Coverage",
        "",
        f"- Tracked articles: **{len(articles)}**",
        f"- Published articles: **{len(published)}**",
        f"- Draft / review candidates: **{len(candidates)}**",
        f"- Unchecked backlog items: **{len(backlog)}**",
        "",
    ]

    for key in COVERAGE_KEYS:
        lines.extend(render_coverage(published, key, as_of))

    lines.extend(
        [
            "## Pipeline-only Coverage Gaps",
            "",
            "draft / reviewには存在するが、公開済み記事ではまだ示せていないclassificationです。",
            "",
        ]
    )
    any_gap = False
    for key in COVERAGE_KEYS:
        values = pipeline_only_values(articles, key)
        if values:
            any_gap = True
            lines.append(f"- **{key}:** " + ", ".join(f"`{value}`" for value in values))
    if not any_gap:
        lines.append("- None")
    lines.extend(["", "## Next Article Candidates", ""])

    if not candidates:
        lines.extend(["- None", ""])
    for index, candidate in enumerate(candidates, start=1):
        relative = candidate.article.path.relative_to(analytics.ROOT).as_posix()
        lines.extend(
            [
                f"### {index}. [{candidate.article.title}](../{relative})",
                "",
                f"- Status: `{candidate.article.effective_status}`",
                "- Portfolio gap: "
                + (", ".join(f"`{value}`" for value in candidate.portfolio_gaps) or "no new published portfolio signal detected"),
                "- Implementation evidence: "
                + (", ".join(f"`{value}`" for value in candidate.sources) or "not recorded"),
                "- Coverage gap / recency: "
                + (", ".join(f"`{value}`" for value in candidate.coverage_gaps) or "no >30d or unpublished domain/language/technology gap detected"),
                f"- Related positive-reaction context: {candidate.reaction_context} published article(s)",
            ]
        )
        if candidate.missing_metadata:
            lines.append(
                "- Metadata needed before stronger scoring: "
                + ", ".join(f"`{value}`" for value in candidate.missing_metadata)
            )
        lines.append("")

    article_titles = [
        (article.effective_status or "tracked", article.title) for article in articles
    ]
    overlaps = []
    unscored = []
    evidence_backlog = []
    for item in backlog:
        overlap = best_title_overlap(item, article_titles)
        if overlap:
            overlaps.append((item, overlap))
        elif source_of_truth(item):
            evidence_backlog.append(item)
        else:
            unscored.append(item)

    lines.extend(
        [
            "## Backlog Hygiene / Overlap",
            "",
            "backlog自由文にはclassificationを自動付与せず、タイトル類似度が高い既存記事だけを重複候補として可視化します。",
            "",
        ]
    )
    if overlaps:
        for item, (status, title, similarity) in overlaps:
            lines.append(
                f"- `{item.title}` → **{status}** `{title}` (title similarity {similarity:.2f}, section: {item.section})"
            )
    else:
        lines.append("- None")

    lines.extend(["", "### Evidence-backed backlog items not already tracked", ""])
    if evidence_backlog:
        for item in evidence_backlog:
            lines.append(
                f"- `{item.title}` — Source of Truth: `{source_of_truth(item)}` (section: {item.section})"
            )
    else:
        lines.append("- None")

    lines.extend(["", "### Backlog items intentionally left unscored", ""])
    lines.append(f"- Count: **{len(unscored)}**")
    lines.append(
        "- 理由: source repository / classificationが明示されていない自由文へ推測を入れないため。"
    )
    for item in unscored[:10]:
        lines.append(f"  - `{item.title}` ({item.section})")
    if len(unscored) > 10:
        lines.append(f"  - … and {len(unscored) - 10} more")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `30d / 90d / 365d` は公開済みclassificationの最終投稿日を基準にする。",
            "- Zenn-native `articles/*.md` は `ideas/published.md` に公開記録がある記事だけcoverageへ含める。draft状態は推測しない。",
            "- `not yet published` はtracked draft/review metadataにはあるが、公開済みcoverageにはまだ存在しない値。",
            "- `source_repositories` が無い候補は、実装根拠が無いと断定せず **not recorded** とする。",
            "- backlog自由文は分類推測しない。推薦精度を上げる場合はfront matterまたはbacklogへ根拠を明示する。",
            "- metricsが無い / positive reactionが無い場合も推薦自体は成立する。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        articles = load_opportunity_articles()
        backlog = load_backlog()
        snapshot = analytics.load_latest_snapshot()
        as_of = resolve_as_of(articles)
        rendered = render_report(articles, backlog, snapshot, as_of)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            f"check completed: {len(articles)} tracked articles, "
            f"{len(analytics.published_articles(articles))} published, "
            f"{len(load_backlog())} backlog item(s)",
            file=sys.stderr,
        )
        return 0

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
