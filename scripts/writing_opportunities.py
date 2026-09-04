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

import article_layout
import writing_analytics as analytics

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
    """Load active shared articles plus published Zenn-native article files.

    Shared articles are discovered from the lifecycle directories via
    ``article_layout``. Zenn canonical files remain direct ``articles/<slug>.md``
    files and are included only when their title exists in ``ideas/published.md``;
    draft state is not inferred from Zenn's separate front matter schema.
    """

    articles = article_layout.load_shared_articles(analytics)
    registry = analytics.read_published_registry()
    known_paths = {article.path.resolve() for article in articles}

    for path in sorted(analytics.ARTICLES_DIR.glob("*.md")):
        if path.resolve() in known_paths:
            continue
        meta = analytics.read_frontmatter(path)
        title = str(meta.get("title") or path.stem)
        published_entry = registry.get(title)
        if published_entry is None:
            continue
        articles.append(
            analytics.Article(
                slug=path.stem,
                path=path,
                meta=meta,
                registry=published_entry,
            )
        )

    return sorted(articles, key=lambda article: article.path.as_posix())


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

        checkbox = re.match(r"^\s*-\s*\[([ xX])\]\s+(.+?)\s*$", line)
        if checkbox:
            flush()
            if checkbox.group(1).strip():
                continue
            title = checkbox.group(2).strip()
            item_section = section
            continue

        if title is not None:
            meta = re.match(r"^\s{2,}-\s+([^:：]+)[:：]\s*(.+?)\s*$", line)
            if meta:
                metadata[meta.group(1).strip()] = meta.group(2).strip()

    flush()
    return items


def load_backlog() -> list[BacklogItem]:
    if not BACKLOG_PATH.exists():
        return []
    return parse_backlog_text(BACKLOG_PATH.read_text(encoding="utf-8"))


def best_title_overlap(
    item: BacklogItem, title_pool: list[tuple[str, str]]
) -> tuple[str, str, float] | None:
    best: tuple[str, str, float] | None = None
    for status, title in title_pool:
        ratio = title_similarity(item.title, title)
        if best is None or ratio > best[2]:
            best = (status, title, ratio)
    return best if best and best[2] >= OVERLAP_THRESHOLD else None


def related_reaction_context(
    candidate: analytics.Article,
    articles: list[analytics.Article],
    snapshot: dict[str, Any] | None,
) -> int:
    notable_titles = {title for title, _, _, _ in analytics.notable_reaction_rows(snapshot)}
    candidate_terms = set(analytics.list_values(candidate.meta, "topics"))
    candidate_terms.update(analytics.list_values(candidate.meta, "domains"))
    if not notable_titles or not candidate_terms:
        return 0

    count = 0
    for article in analytics.published_articles(articles):
        if article.title not in notable_titles:
            continue
        terms = set(analytics.list_values(article.meta, "topics"))
        terms.update(analytics.list_values(article.meta, "domains"))
        if candidate_terms.intersection(terms):
            count += 1
    return count


def build_candidates(
    articles: list[analytics.Article],
    snapshot: dict[str, Any] | None,
    as_of: date,
) -> list[Candidate]:
    published_signals = published_values(articles, "portfolio_signals")
    coverage = {key: published_value_dates(articles, key) for key in GAP_KEYS}
    candidates: list[Candidate] = []

    for article in articles:
        if article.effective_status not in {"draft", "review"}:
            continue

        portfolio_gaps = tuple(
            value
            for value in analytics.list_values(article.meta, "portfolio_signals")
            if value not in published_signals
        )
        coverage_gaps: list[str] = []
        oldest_gap_age = 0
        for key in GAP_KEYS:
            if not analytics.has_explicit_classification(article.meta, key):
                continue
            for value in analytics.list_values(article.meta, key):
                dates = coverage[key].get(value, [])
                if not dates:
                    coverage_gaps.append(f"{key}:{value} (not yet published)")
                    oldest_gap_age = max(oldest_gap_age, UNPUBLISHED_GAP_AGE)
                    continue
                age = max(0, (as_of - max(dates)).days)
                if age > WINDOWS[0]:
                    coverage_gaps.append(f"{key}:{value} ({age}d since last post)")
                    oldest_gap_age = max(oldest_gap_age, age)

        sources = tuple(analytics.list_values(article.meta, "source_repositories"))
        missing = tuple(
            key
            for key in (*GAP_KEYS, "portfolio_signals", "source_repositories")
            if not analytics.has_explicit_classification(article.meta, key)
        )
        candidates.append(
            Candidate(
                article=article,
                portfolio_gaps=portfolio_gaps,
                coverage_gaps=tuple(coverage_gaps),
                oldest_gap_age=oldest_gap_age,
                sources=sources,
                reaction_context=related_reaction_context(article, articles, snapshot),
                missing_metadata=missing,
            )
        )

    def priority(candidate: Candidate) -> tuple[Any, ...]:
        readiness = 2 if candidate.article.effective_status == "review" else 1
        return (
            len(candidate.portfolio_gaps),
            bool(candidate.sources),
            len(candidate.coverage_gaps),
            candidate.oldest_gap_age,
            candidate.reaction_context,
            readiness,
            candidate.article.title.casefold(),
        )

    return sorted(candidates, key=priority, reverse=True)


def pipeline_only_values(articles: list[analytics.Article], key: str) -> list[str]:
    published = published_values(articles, key)
    pending: set[str] = set()
    for article in articles:
        if article.effective_status in {"draft", "review"}:
            pending.update(analytics.list_values(article.meta, key))
    return sorted(pending - published, key=str.casefold)


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def article_link(article: analytics.Article) -> str:
    relative = article.path.relative_to(analytics.ROOT).as_posix()
    return f"[{md_escape(article.title)}](../{relative})"


def source_of_truth(item: BacklogItem) -> str | None:
    for key in ("Source of Truth", "Source repository", "Source Repository"):
        if item.metadata.get(key):
            return item.metadata[key]
    return None


def build_report(
    articles: list[analytics.Article],
    backlog: list[BacklogItem],
    snapshot: dict[str, Any] | None,
    as_of: date,
) -> str:
    published = analytics.published_articles(articles)
    candidates = build_candidates(articles, snapshot, as_of)
    title_pool = [("published", title) for title in analytics.read_published_registry()]
    title_pool.extend((article.effective_status, article.title) for article in articles)

    overlaps: list[tuple[BacklogItem, tuple[str, str, float]]] = []
    evidence_backlog: list[BacklogItem] = []
    unscored_backlog: list[BacklogItem] = []
    for item in backlog:
        overlap = best_title_overlap(item, title_pool)
        if overlap:
            overlaps.append((item, overlap))
        elif source_of_truth(item):
            evidence_backlog.append(item)
        else:
            unscored_backlog.append(item)

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
        lines.extend(
            [
                f"### {key}",
                "",
                "| Value | Published | Last published | Age | 30d | 90d | 365d |",
                "| --- | ---: | --- | ---: | :---: | :---: | :---: |",
            ]
        )
        rows = coverage_rows(articles, key, as_of)
        if not rows:
            lines.append("| - | 0 | - | - | - | - | - |")
        for value, count, last, age in rows:
            marks = ["✓" if age <= window else "—" for window in WINDOWS]
            lines.append(
                f"| {md_escape(value)} | {count} | {last.isoformat()} | {age}d | "
                f"{marks[0]} | {marks[1]} | {marks[2]} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Pipeline-only Coverage Gaps",
            "",
            "draft / reviewには存在するが、公開済み記事ではまだ示せていないclassificationです。",
            "",
        ]
    )
    found_gap = False
    for key in COVERAGE_KEYS:
        values = pipeline_only_values(articles, key)
        if values:
            found_gap = True
            lines.append(f"- **{key}:** {', '.join(f'`{value}`' for value in values)}")
    if not found_gap:
        lines.append("- No pipeline-only classifications")
    lines.append("")

    lines.extend(["## Next Article Candidates", ""])
    if not candidates:
        lines.append("- No draft/review article candidates")
    for index, candidate in enumerate(candidates, start=1):
        lines.extend(
            [
                f"### {index}. {article_link(candidate.article)}",
                "",
                f"- Status: `{candidate.article.effective_status}`",
                "- Portfolio gap: "
                + (
                    ", ".join(f"`{value}`" for value in candidate.portfolio_gaps)
                    if candidate.portfolio_gaps
                    else "no new published portfolio signal detected"
                ),
                "- Implementation evidence: "
                + (
                    ", ".join(f"`{value}`" for value in candidate.sources)
                    if candidate.sources
                    else "not recorded"
                ),
                "- Coverage gap / recency: "
                + (
                    "; ".join(candidate.coverage_gaps)
                    if candidate.coverage_gaps
                    else "no >30d or unpublished domain/language/technology gap detected"
                ),
                f"- Related positive-reaction context: {candidate.reaction_context} published article(s)",
            ]
        )
        if candidate.missing_metadata:
            lines.append(
                "- Metadata needed before stronger scoring: "
                + ", ".join(f"`{key}`" for key in candidate.missing_metadata)
            )
        lines.append("")

    lines.extend(
        [
            "## Backlog Hygiene / Overlap",
            "",
            "backlog自由文にはclassificationを自動付与せず、タイトル類似度が高い既存記事だけを重複候補として可視化します。",
            "",
        ]
    )
    if overlaps:
        for item, (status, title, ratio) in sorted(overlaps, key=lambda row: row[1][2], reverse=True):
            lines.append(
                f"- `{item.title}` → **{status}** `{title}` "
                f"(title similarity {ratio:.2f}, section: {item.section})"
            )
    else:
        lines.append("- No likely backlog overlaps detected")

    lines.extend(["", "### Evidence-backed backlog items not already tracked", ""])
    if evidence_backlog:
        for item in evidence_backlog:
            lines.append(
                f"- `{item.title}` — source: `{source_of_truth(item)}` — section: {item.section}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "### Backlog items intentionally left unscored",
            "",
            f"- Count: **{len(unscored_backlog)}**",
            "- 理由: source repository / classificationが明示されていない自由文へ推測を入れないため。",
        ]
    )
    for item in unscored_backlog[:10]:
        lines.append(f"  - `{item.title}` ({item.section})")
    if len(unscored_backlog) > 10:
        lines.append(f"  - … and {len(unscored_backlog) - 10} more")

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
        report = build_report(articles, backlog, snapshot, resolve_as_of(articles))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            f"check completed: {len(articles)} articles, {len(backlog)} backlog items, "
            f"{len(report)} report chars",
            file=sys.stderr,
        )
        return 0

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(analytics.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
