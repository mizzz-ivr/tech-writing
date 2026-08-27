#!/usr/bin/env python3
"""Generate writing analytics reports and optional external metric snapshots."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
PUBLISHED_PATH = ROOT / "ideas" / "published.md"
REPORT_PATH = ROOT / "reports" / "writing-profile.md"
METRICS_DIR = ROOT / "data" / "metrics"
README_PATH = ROOT / "README.md"
README_START = "<!-- WRITING_ANALYTICS:START -->"
README_END = "<!-- WRITING_ANALYTICS:END -->"
JST = ZoneInfo("Asia/Tokyo")
USER_AGENT = "mizzz-ivr-tech-writing-analytics/1.0"


@dataclass
class RegistryEntry:
    published_at: str
    title: str
    qiita: str | None
    zenn: str | None


@dataclass
class Article:
    slug: str
    path: Path
    meta: dict[str, Any]
    registry: RegistryEntry | None

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.slug)

    @property
    def effective_status(self) -> str:
        status = str(self.meta.get("status") or "draft")
        if self.registry and status != "published":
            return "published"
        return status

    @property
    def effective_published_at(self) -> str | None:
        value = self.meta.get("published_at")
        if isinstance(value, (date, datetime)):
            return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
        if value:
            return str(value)
        return self.registry.published_at if self.registry else None

    def platform_url(self, platform: str) -> str | None:
        published = self.meta.get("published") or {}
        if isinstance(published, dict):
            value = published.get(platform)
            if value:
                return str(value)
        if self.registry:
            return getattr(self.registry, platform, None)
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-metrics", action="store_true", help="Fetch Qiita/Zenn metrics and write today's snapshot")
    parser.add_argument("--check", action="store_true", help="Validate and render in memory without writing generated files")
    return parser.parse_args()


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)}: front matter is missing")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.relative_to(ROOT)}: front matter is not closed")
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: front matter must be a mapping")
    return data


def clean_cell(value: str) -> str | None:
    value = value.strip()
    if not value or value == "-":
        return None
    return value


def read_published_registry() -> dict[str, RegistryEntry]:
    if not PUBLISHED_PATH.exists():
        return {}
    registry: dict[str, RegistryEntry] = {}
    for raw_line in PUBLISHED_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.startswith("|"):
            continue
        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) < 4 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[0]):
            continue
        entry = RegistryEntry(
            published_at=cells[0],
            title=cells[1],
            qiita=clean_cell(cells[2]),
            zenn=clean_cell(cells[3]),
        )
        registry[entry.title] = entry
    return registry


def load_articles() -> list[Article]:
    registry = read_published_registry()
    articles: list[Article] = []
    for path in sorted(ARTICLES_DIR.glob("*/article.md")):
        meta = read_frontmatter(path)
        title = str(meta.get("title") or path.parent.name)
        articles.append(Article(path.parent.name, path, meta, registry.get(title)))
    return articles


def list_values(meta: dict[str, Any], key: str) -> list[str]:
    value = meta.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def api_json(url: str, token: str | None = None) -> Any:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def fetch_qiita(url: str, token: str | None) -> dict[str, Any]:
    match = re.search(r"/items/([0-9a-f]{20})(?:$|[/?#])", url)
    if not match:
        raise ValueError("unsupported Qiita item URL")
    payload = api_json(f"https://qiita.com/api/v2/items/{match.group(1)}", token)
    return {
        "likes": payload.get("likes_count"),
        "stocks": payload.get("stocks_count"),
        "comments": payload.get("comments_count"),
        "page_views": payload.get("page_views_count"),
    }


def fetch_zenn(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 3 or parts[1] != "articles":
        raise ValueError("unsupported Zenn article URL")
    username, slug = parts[0], parts[2]
    page = 1
    while page <= 20:
        query = urllib.parse.urlencode({"username": username, "order": "latest", "page": page})
        payload = api_json(f"https://zenn.dev/api/articles?{query}")
        for item in payload.get("articles", []):
            if item.get("slug") == slug:
                return {
                    "likes": item.get("liked_count"),
                    "bookmarks": item.get("bookmarked_count"),
                    "comments": item.get("comments_count"),
                    "page_views": None,
                }
        next_page = payload.get("next_page")
        if not next_page:
            break
        page = int(next_page)
    raise LookupError("article was not returned by Zenn article list endpoint")


def refresh_metrics(articles: list[Article]) -> dict[str, Any]:
    token = os.getenv("QIITA_TOKEN") or None
    collected_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result: dict[str, Any] = {
        "schema_version": 1,
        "collected_at": collected_at,
        "articles": [],
        "errors": [],
    }

    for article in articles:
        if article.effective_status != "published":
            continue
        row: dict[str, Any] = {
            "slug": article.slug,
            "title": article.title,
            "published_at": article.effective_published_at,
            "platforms": {},
        }
        for platform in ("qiita", "zenn"):
            url = article.platform_url(platform)
            if not url:
                continue
            try:
                if platform == "qiita":
                    metrics = fetch_qiita(url, token)
                else:
                    metrics = fetch_zenn(url)
                row["platforms"][platform] = {"url": url, **metrics}
            except (ValueError, LookupError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
                row["platforms"][platform] = {"url": url, "error": str(exc)}
                result["errors"].append({"slug": article.slug, "platform": platform, "error": str(exc)})
        result["articles"].append(row)

    return result


def write_metric_snapshot(snapshot: dict[str, Any]) -> Path:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(JST).date().isoformat()
    path = METRICS_DIR / f"{day}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_latest_snapshot() -> dict[str, Any] | None:
    files = sorted(METRICS_DIR.glob("*.json")) if METRICS_DIR.exists() else []
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def data_quality(articles: list[Article]) -> list[str]:
    issues: list[str] = []
    for article in articles:
        status = str(article.meta.get("status") or "draft")
        published = article.meta.get("published") if isinstance(article.meta.get("published"), dict) else {}
        if article.registry and status != "published":
            issues.append(f"`{article.slug}`: published.mdでは公開済みだがfront matterは `status: {status}`")
        if article.registry:
            for platform in ("qiita", "zenn"):
                registry_url = getattr(article.registry, platform)
                meta_url = published.get(platform) if isinstance(published, dict) else None
                if registry_url and not meta_url:
                    issues.append(f"`{article.slug}`: published.mdに{platform} URLがあるがfront matterは空")
                elif registry_url and meta_url and str(meta_url) != registry_url:
                    issues.append(f"`{article.slug}`: {platform} URLがpublished.mdとfront matterで不一致")
        if article.effective_status == "published" and not article.effective_published_at:
            issues.append(f"`{article.slug}`: 公開済みだが `published_at` を特定できない")
        if status == "published" and not any(article.platform_url(name) for name in ("qiita", "zenn")):
            issues.append(f"`{article.slug}`: `status: published` だが公開URLがない")
        for key in ("domains", "languages", "technologies"):
            if article.effective_status == "published" and not list_values(article.meta, key):
                issues.append(f"`{article.slug}`: `{key}` が未分類")
    return issues


def count_field(articles: list[Article], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for article in articles:
        if article.effective_status != "published":
            continue
        values = list_values(article.meta, key)
        if not values:
            counter["Unclassified"] += 1
        else:
            counter.update(values)
    return counter


def format_counter(counter: Counter[str], limit: int = 10) -> str:
    if not counter:
        return "-"
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common(limit))


def published_articles(articles: list[Article]) -> list[Article]:
    return sorted(
        [article for article in articles if article.effective_status == "published"],
        key=lambda item: item.effective_published_at or "0000-00-00",
        reverse=True,
    )


def cadence_summary(articles: list[Article]) -> tuple[str, str]:
    dates = sorted({article.effective_published_at for article in articles if article.effective_published_at})
    if not dates:
        return "-", "-"
    last = dates[-1]
    if len(dates) < 2:
        return last, "-"
    parsed = [date.fromisoformat(item) for item in dates]
    gaps = [(parsed[index] - parsed[index - 1]).days for index in range(1, len(parsed))]
    return last, f"{mean(gaps):.1f}日"


def latest_metric_rows(snapshot: dict[str, Any] | None) -> list[tuple[int, str, str, str]]:
    if not snapshot:
        return []
    rows: list[tuple[int, str, str, str]] = []
    for article in snapshot.get("articles", []):
        for platform, metrics in article.get("platforms", {}).items():
            likes = metrics.get("likes")
            if isinstance(likes, int):
                rows.append((likes, str(article.get("title") or article.get("slug")), platform, str(metrics.get("url") or "")))
    return sorted(rows, reverse=True)


def md_link(title: str, url: str | None) -> str:
    title = title.replace("|", "\\|")
    return f"[{title}]({url})" if url else title


def build_report(articles: list[Article], snapshot: dict[str, Any] | None) -> str:
    published = published_articles(articles)
    last_date, avg_gap = cadence_summary(published)
    quality = data_quality(articles)
    counters = {key: count_field(published, key) for key in ("topics", "domains", "languages", "technologies", "portfolio_signals")}
    generated_at = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    lines = [
        "# Writing Profile / Analytics",
        "",
        f"> Generated: {generated_at}",
        "",
        "## Overview",
        "",
        f"- Published articles: **{len(published)}**",
        f"- Last published: **{last_date}**",
        f"- Average publish interval: **{avg_gap}**",
        f"- Tracked article drafts/reviews/published: **{len(articles)}**",
        "",
        "## Technology Mix",
        "",
        f"- Topics: {format_counter(counters['topics'])}",
        f"- Domains: {format_counter(counters['domains'])}",
        f"- Languages: {format_counter(counters['languages'])}",
        f"- Technologies: {format_counter(counters['technologies'])}",
        f"- Portfolio signals: {format_counter(counters['portfolio_signals'])}",
        "",
        "## Recent Articles",
        "",
    ]

    if not published:
        lines.append("- No published articles")
    else:
        for article in published[:5]:
            url = article.platform_url("qiita") or article.platform_url("zenn")
            lines.append(f"- {article.effective_published_at or '-'} — {md_link(article.title, url)}")

    lines.extend(["", "## Popular Articles", ""])
    metric_rows = latest_metric_rows(snapshot)
    if metric_rows:
        for likes, title, platform, url in metric_rows[:5]:
            lines.append(f"- {md_link(title, url)} — {likes} likes ({platform})")
    else:
        lines.append("- Metrics snapshot is not available yet")

    lines.extend(["", "## Data Quality", ""])
    if quality:
        lines.extend(f"- {issue}" for issue in quality)
    else:
        lines.append("- No issues detected")

    lines.extend([
        "",
        "## Review Hints",
        "",
        "- `Unclassified` が多い軸は、次回の記事更新時にfront matterを整備する",
        "- 30/90日単位でtopic / domain / languageの偏りを見る",
        "- metrics snapshotが蓄積したら、likesの絶対値だけでなく7日/30日の増分を見る",
        "- Portfolio用途では、記事数より `portfolio_signals` とsource repositoryの対応を重視する",
        "",
    ])
    return "\n".join(lines)


def build_readme_section(articles: list[Article], snapshot: dict[str, Any] | None) -> str:
    published = published_articles(articles)
    last_date, avg_gap = cadence_summary(published)
    topics = count_field(published, "topics")
    domains = count_field(published, "domains")
    languages = count_field(published, "languages")
    recent_lines = []
    for article in published[:3]:
        url = article.platform_url("qiita") or article.platform_url("zenn")
        recent_lines.append(f"- {article.effective_published_at or '-'} — {md_link(article.title, url)}")
    if not recent_lines:
        recent_lines = ["- No published articles"]

    popular = latest_metric_rows(snapshot)
    popular_lines = [f"- {md_link(title, url)} — {likes} likes ({platform})" for likes, title, platform, url in popular[:3]]
    if not popular_lines:
        popular_lines = ["- 外部メトリクスはまだ未取得"]

    return "\n".join([
        README_START,
        "### Writing Profile",
        "",
        f"**{len(published)} published** · Last post **{last_date}** · Avg interval **{avg_gap}**",
        "",
        f"- Topics: {format_counter(topics, 5)}",
        f"- Domains: {format_counter(domains, 5)}",
        f"- Languages: {format_counter(languages, 5)}",
        "",
        "#### Recent",
        "",
        *recent_lines,
        "",
        "#### Popular",
        "",
        *popular_lines,
        "",
        "詳細: [Writing Profile / Analytics](./reports/writing-profile.md) · [運用設計](./docs/WRITING_ANALYTICS.md)",
        README_END,
    ])


def update_readme(original: str, section: str) -> str:
    pattern = re.compile(re.escape(README_START) + r".*?" + re.escape(README_END), re.DOTALL)
    if pattern.search(original):
        return pattern.sub(section, original)
    suffix = "" if original.endswith("\n") else "\n"
    return original + suffix + "\n## Writing Analytics\n\n" + section + "\n"


def main() -> int:
    args = parse_args()
    try:
        articles = load_articles()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    snapshot = None
    if args.refresh_metrics:
        snapshot = refresh_metrics(articles)
        if not args.check:
            path = write_metric_snapshot(snapshot)
            print(f"wrote {path.relative_to(ROOT)}")
        for error in snapshot.get("errors", []):
            print(f"WARNING: metrics {error['platform']} {error['slug']}: {error['error']}", file=sys.stderr)
    else:
        snapshot = load_latest_snapshot()

    report = build_report(articles, snapshot)
    readme = README_PATH.read_text(encoding="utf-8")
    next_readme = update_readme(readme, build_readme_section(articles, snapshot))

    if args.check:
        print(report)
        quality = data_quality(articles)
        print(f"check completed: {len(articles)} articles, {len(quality)} data-quality findings", file=sys.stderr)
        return 0

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    README_PATH.write_text(next_readme, encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"updated {README_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
