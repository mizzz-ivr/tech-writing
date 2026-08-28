#!/usr/bin/env python3
"""Collect and derive GitHub -> Writing Funnel evidence.

Dynamic GitHub state is stored as a dated raw snapshot. Derived analytics consume
only stored snapshots so reports remain reproducible and PR validation does not
require network access.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo

import yaml

import writing_analytics as analytics

CONFIG_PATH = analytics.ROOT / "config" / "github-writing-funnel.yml"
SNAPSHOT_DIR = analytics.ROOT / "data" / "github-funnel"
SCHEMA_VERSION = 1
JST = ZoneInfo("Asia/Tokyo")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
KIND_PRIORITY = {"release": 3, "pull_request": 2, "issue": 1}
PAGE_SIZE = 100


@dataclass(frozen=True)
class FunnelPolicy:
    repositories: tuple[str, ...]
    significant_issue_labels: frozenset[str]
    lookback_days: int
    release_lookback_days: int
    title_overlap_threshold: float
    max_candidates: int


@dataclass(frozen=True)
class Evidence:
    repository: str
    kind: str
    title: str
    url: str
    occurred_at: str
    source_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def load_policy(path: Path = CONFIG_PATH) -> FunnelPolicy:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected GitHub writing funnel config schema_version")

    repositories = data.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("GitHub writing funnel repositories must be a non-empty list")
    normalized_repositories: list[str] = []
    for value in repositories:
        repo = str(value).strip()
        if not REPO_RE.fullmatch(repo):
            raise ValueError(f"invalid repository name: {repo}")
        if repo == "mizzz-ivr/tech-writing":
            raise ValueError("tech-writing cannot monitor itself")
        if repo in normalized_repositories:
            raise ValueError(f"duplicate repository: {repo}")
        normalized_repositories.append(repo)

    labels = data.get("significant_issue_labels", [])
    if not isinstance(labels, list):
        raise ValueError("significant_issue_labels must be a list")
    normalized_labels = frozenset(
        str(value).casefold().strip() for value in labels if str(value).strip()
    )

    lookback_days = int(data.get("lookback_days", 45))
    release_lookback_days = int(data.get("release_lookback_days", 90))
    threshold = float(data.get("title_overlap_threshold", 0.88))
    max_candidates = int(data.get("max_candidates", 12))
    if lookback_days < 1 or release_lookback_days < 1:
        raise ValueError("lookback days must be positive")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("title_overlap_threshold must be between 0 and 1")
    if max_candidates < 1 or max_candidates > 100:
        raise ValueError("max_candidates must be between 1 and 100")

    return FunnelPolicy(
        repositories=tuple(normalized_repositories),
        significant_issue_labels=normalized_labels,
        lookback_days=lookback_days,
        release_lookback_days=release_lookback_days,
        title_overlap_threshold=threshold,
        max_candidates=max_candidates,
    )


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def recent_enough(value: Any, cutoff: datetime) -> bool:
    parsed = parse_timestamp(value)
    return parsed is not None and parsed >= cutoff


def github_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mizzz-ivr-tech-writing-funnel/1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise OSError(f"GitHub API request failed for {url}: {exc}") from exc


def repo_api(repository: str, suffix: str = "") -> str:
    encoded = "/".join(
        urllib.parse.quote(part, safe="") for part in repository.split("/")
    )
    return f"https://api.github.com/repos/{encoded}{suffix}"


def paginated_collection(
    repository: str,
    endpoint: str,
    params: dict[str, str],
    fetcher: Callable[[str], Any],
    *,
    cutoff: datetime,
    ordering_timestamp: Callable[[dict[str, Any]], Any],
) -> list[dict[str, Any]]:
    """Fetch all pages that can still contain events inside the cutoff.

    PR and Issue endpoints are sorted by ``updated``. An item merged/closed inside
    the lookback necessarily has ``updated_at >= event time``, so once the final
    row on a full page has ``updated_at < cutoff`` later pages cannot contain a
    relevant event. Releases are returned newest first and use publication time.
    """

    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        query = dict(params)
        query["per_page"] = str(PAGE_SIZE)
        query["page"] = str(page)
        url = repo_api(repository, f"/{endpoint}?{urllib.parse.urlencode(query)}")
        payload = fetcher(url)
        if not isinstance(payload, list):
            raise ValueError(
                f"unexpected GitHub collection response: {repository}/{endpoint}"
            )
        typed_page = [item for item in payload if isinstance(item, dict)]
        rows.extend(typed_page)
        if len(payload) < PAGE_SIZE:
            break
        if typed_page:
            last_clock = parse_timestamp(ordering_timestamp(typed_page[-1]))
            if last_clock is not None and last_clock < cutoff:
                break
        page += 1
    return rows


def collect_snapshot(
    policy: FunnelPolicy,
    fetcher: Callable[[str], Any] = github_json,
    *,
    as_of: date | None = None,
    collected_at: datetime | None = None,
) -> dict[str, Any]:
    as_of = as_of or datetime.now(JST).date()
    collected_at = collected_at or datetime.now(timezone.utc)
    cutoff = datetime.combine(
        as_of - timedelta(days=policy.lookback_days),
        datetime.min.time(),
        tzinfo=JST,
    ).astimezone(timezone.utc)
    release_cutoff = datetime.combine(
        as_of - timedelta(days=policy.release_lookback_days),
        datetime.min.time(),
        tzinfo=JST,
    ).astimezone(timezone.utc)

    repositories: list[dict[str, Any]] = []
    for repository in policy.repositories:
        repo_meta = fetcher(repo_api(repository))
        if not isinstance(repo_meta, dict):
            raise ValueError(f"repository metadata is not a mapping: {repository}")
        if repo_meta.get("private") is not False:
            raise ValueError(f"refusing non-public repository: {repository}")
        if repo_meta.get("archived") is True:
            raise ValueError(f"refusing archived repository: {repository}")

        pulls = paginated_collection(
            repository,
            "pulls",
            {"state": "closed", "sort": "updated", "direction": "desc"},
            fetcher,
            cutoff=cutoff,
            ordering_timestamp=lambda item: item.get("updated_at"),
        )
        releases = paginated_collection(
            repository,
            "releases",
            {},
            fetcher,
            cutoff=release_cutoff,
            ordering_timestamp=lambda item: item.get("published_at")
            or item.get("created_at"),
        )
        issues = paginated_collection(
            repository,
            "issues",
            {"state": "closed", "sort": "updated", "direction": "desc"},
            fetcher,
            cutoff=cutoff,
            ordering_timestamp=lambda item: item.get("updated_at"),
        )

        merged_pull_requests = []
        for item in pulls:
            merged_at = item.get("merged_at")
            if not recent_enough(merged_at, cutoff):
                continue
            merged_pull_requests.append(
                {
                    "number": int(item["number"]),
                    "title": str(item.get("title") or "").strip(),
                    "url": str(item.get("html_url") or ""),
                    "merged_at": str(merged_at),
                }
            )

        recent_releases = []
        for item in releases:
            if item.get("draft"):
                continue
            published_at = item.get("published_at") or item.get("created_at")
            if not recent_enough(published_at, release_cutoff):
                continue
            recent_releases.append(
                {
                    "tag_name": str(item.get("tag_name") or "").strip(),
                    "name": str(
                        item.get("name") or item.get("tag_name") or ""
                    ).strip(),
                    "url": str(item.get("html_url") or ""),
                    "published_at": str(published_at),
                    "prerelease": bool(item.get("prerelease")),
                }
            )

        significant_issues = []
        for item in issues:
            if "pull_request" in item:
                continue
            closed_at = item.get("closed_at")
            if not recent_enough(closed_at, cutoff):
                continue
            item_labels = {
                str(label.get("name") or "").casefold().strip()
                for label in item.get("labels", [])
                if isinstance(label, dict)
            }
            matched = sorted(
                item_labels.intersection(policy.significant_issue_labels)
            )
            if not matched:
                continue
            significant_issues.append(
                {
                    "number": int(item["number"]),
                    "title": str(item.get("title") or "").strip(),
                    "url": str(item.get("html_url") or ""),
                    "closed_at": str(closed_at),
                    "matched_labels": matched,
                }
            )

        repositories.append(
            {
                "repository": repository,
                "merged_pull_requests": merged_pull_requests,
                "releases": recent_releases,
                "significant_issues": significant_issues,
            }
        )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "collected_at": collected_at.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "repositories": repositories,
    }
    validate_snapshot(payload, policy, enforce_current_allowlist=True)
    return payload


def validate_snapshot(
    payload: dict[str, Any],
    policy: FunnelPolicy | None = None,
    *,
    enforce_current_allowlist: bool = False,
) -> None:
    """Validate snapshot structure without rewriting historical policy."""

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected GitHub writing funnel snapshot schema_version")
    try:
        date.fromisoformat(str(payload["as_of"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid GitHub writing funnel snapshot as_of") from exc
    if parse_timestamp(payload.get("collected_at")) is None:
        raise ValueError("invalid GitHub writing funnel snapshot collected_at")

    repositories = payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("GitHub writing funnel repositories must be a list")
    seen: set[str] = set()
    current = set(policy.repositories) if policy is not None else set()
    for row in repositories:
        if not isinstance(row, dict):
            raise ValueError("GitHub writing funnel repository row must be a mapping")
        repository = str(row.get("repository") or "")
        if not REPO_RE.fullmatch(repository):
            raise ValueError(f"invalid snapshot repository name: {repository}")
        if enforce_current_allowlist and repository not in current:
            raise ValueError(
                f"snapshot repository is outside current allowlist: {repository}"
            )
        if repository in seen:
            raise ValueError(f"duplicate snapshot repository: {repository}")
        seen.add(repository)
        for key in ("merged_pull_requests", "releases", "significant_issues"):
            if not isinstance(row.get(key), list):
                raise ValueError(f"snapshot {key} must be a list for {repository}")


def snapshot_paths() -> list[Path]:
    if not SNAPSHOT_DIR.exists():
        return []
    return sorted(SNAPSHOT_DIR.glob("*.json"))


def snapshot_for_current_policy(
    payload: dict[str, Any], policy: FunnelPolicy
) -> dict[str, Any]:
    current = set(policy.repositories)
    filtered = dict(payload)
    filtered["repositories"] = [
        row
        for row in payload.get("repositories", [])
        if isinstance(row, dict) and row.get("repository") in current
    ]
    validate_snapshot(filtered, policy, enforce_current_allowlist=True)
    return filtered


def load_latest_snapshot(policy: FunnelPolicy | None = None) -> dict[str, Any] | None:
    policy = policy or load_policy()
    for path in reversed(snapshot_paths()):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                continue
            validate_snapshot(payload)
            return snapshot_for_current_policy(payload, policy)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return None


def normalize_title(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(
        r"^(?:feat|fix|chore|docs|refactor|perf|test)(?:\([^)]*\))?\s*[:：]\s*",
        "",
        value,
    )
    return re.sub(r"[\s「」『』【】（）()\[\]［］・:：—–\-_/]+", "", value)


def title_similarity(left: str, right: str) -> float:
    left_norm, right_norm = normalize_title(left), normalize_title(right)
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def flatten_evidence(snapshot: dict[str, Any] | None) -> list[Evidence]:
    if not snapshot:
        return []
    result: list[Evidence] = []
    for repo in snapshot.get("repositories", []):
        repository = str(repo.get("repository") or "")
        for item in repo.get("merged_pull_requests", []):
            result.append(
                Evidence(
                    repository,
                    "pull_request",
                    str(item.get("title") or ""),
                    str(item.get("url") or ""),
                    str(item.get("merged_at") or ""),
                    f"#{item.get('number')}",
                )
            )
        for item in repo.get("releases", []):
            title = str(item.get("name") or item.get("tag_name") or "")
            result.append(
                Evidence(
                    repository,
                    "release",
                    title,
                    str(item.get("url") or ""),
                    str(item.get("published_at") or ""),
                    str(item.get("tag_name") or ""),
                )
            )
        for item in repo.get("significant_issues", []):
            result.append(
                Evidence(
                    repository,
                    "issue",
                    str(item.get("title") or ""),
                    str(item.get("url") or ""),
                    str(item.get("closed_at") or ""),
                    f"#{item.get('number')}",
                )
            )
    return result


def deduplicate_evidence(rows: Iterable[Evidence]) -> list[Evidence]:
    selected: dict[tuple[str, str], Evidence] = {}
    for row in rows:
        key = (row.repository, normalize_title(row.title))
        current = selected.get(key)
        if current is None:
            selected[key] = row
            continue
        current_key = (KIND_PRIORITY.get(current.kind, 0), current.occurred_at)
        candidate_key = (KIND_PRIORITY.get(row.kind, 0), row.occurred_at)
        if candidate_key > current_key:
            selected[key] = row
    return list(selected.values())


def tracking_titles(
    articles: Iterable[Any], backlog: Iterable[Any]
) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for article in articles:
        title = str(getattr(article, "title", "") or "").strip()
        if title:
            status = str(
                getattr(article, "effective_status", "article") or "article"
            )
            result.append((f"article:{status}", title))
    for item in backlog:
        title = str(getattr(item, "title", "") or "").strip()
        if title:
            result.append(("backlog", title))
    return result


def candidate_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        KIND_PRIORITY.get(str(row["kind"]), 0),
        str(row["occurred_at"]),
        str(row["repository"]),
        str(row["title"]),
    )


def build_funnel_payload(
    articles: Iterable[Any],
    backlog: Iterable[Any],
    *,
    policy: FunnelPolicy | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or load_policy()
    snapshot = snapshot if snapshot is not None else load_latest_snapshot(policy)
    titles = tracking_titles(articles, backlog)
    rows = deduplicate_evidence(flatten_evidence(snapshot))
    candidates: list[dict[str, Any]] = []

    for row in rows:
        best: tuple[str, str, float] | None = None
        for source, title in titles:
            similarity = title_similarity(row.title, title)
            if best is None or similarity > best[2]:
                best = (source, title, similarity)
        tracked = bool(best and best[2] >= policy.title_overlap_threshold)
        candidates.append(
            {
                "repository": row.repository,
                "kind": row.kind,
                "source_id": row.source_id,
                "title": row.title,
                "url": row.url,
                "occurred_at": row.occurred_at,
                "tracking_status": "tracked" if tracked else "untracked",
                "matched_source": best[0] if tracked and best else None,
                "matched_title": best[1] if tracked and best else None,
                "title_similarity": round(best[2], 3) if best else 0.0,
            }
        )

    candidates.sort(key=candidate_sort_key, reverse=True)
    untracked = [
        row for row in candidates if row["tracking_status"] == "untracked"
    ]
    tracked = [row for row in candidates if row["tracking_status"] == "tracked"]
    return {
        "as_of": snapshot.get("as_of") if snapshot else None,
        "snapshot_available": snapshot is not None,
        "monitored_repositories": list(policy.repositories),
        "evidence_count": len(candidates),
        "untracked_count": len(untracked),
        "tracked_count": len(tracked),
        "candidates": candidates[: policy.max_candidates],
        "untracked_candidates": untracked[: policy.max_candidates],
    }


def write_snapshot(policy: FunnelPolicy) -> Path:
    today = datetime.now(JST).date()
    target = SNAPSHOT_DIR / f"{today.isoformat()}.json"
    if target.exists():
        payload = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"snapshot must be a mapping: {target}")
        validate_snapshot(payload)
        return target
    payload = collect_snapshot(policy, as_of=today)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target


def validate_existing_snapshots(policy: FunnelPolicy) -> int:
    # Historical snapshots stay valid even if today's allowlist changes.
    count = 0
    for path in snapshot_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"snapshot must be a mapping: {path}")
        validate_snapshot(payload)
        count += 1
    return count


def main() -> int:
    args = parse_args()
    try:
        policy = load_policy()
        count = validate_existing_snapshots(policy)
        if args.refresh:
            path = write_snapshot(policy)
            print(
                f"GitHub writing funnel snapshot: {path.relative_to(analytics.ROOT)}"
            )
        else:
            payload = build_funnel_payload([], [], policy=policy)
            print(
                "GitHub writing funnel check: "
                f"{len(policy.repositories)} repositories, {count} snapshots, "
                f"{payload['evidence_count']} evidence rows"
            )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
