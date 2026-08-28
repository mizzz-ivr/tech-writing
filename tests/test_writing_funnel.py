import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_funnel as funnel


class Article:
    def __init__(self, title: str, status: str = "published"):
        self.title = title
        self.effective_status = status


class Backlog:
    def __init__(self, title: str):
        self.title = title


class GitHubWritingFunnelTests(unittest.TestCase):
    def test_policy_rejects_private_self_monitoring_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yml"
            path.write_text(
                """schema_version: 1
repositories:
  - mizzz-ivr/tech-writing
""",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "cannot monitor itself"):
                funnel.load_policy(path)

    def test_collect_snapshot_keeps_only_recent_evidence_and_labeled_issues(self):
        policy = funnel.FunnelPolicy(
            repositories=("mizzz-ivr/example",),
            significant_issue_labels=frozenset({"security", "enhancement"}),
            lookback_days=45,
            release_lookback_days=90,
            title_overlap_threshold=0.88,
            max_candidates=12,
        )

        def fetcher(url: str):
            if url.endswith("/repos/mizzz-ivr/example"):
                return {"private": False, "archived": False}
            if "/pulls?" in url:
                return [
                    {
                        "number": 10,
                        "title": "feat: add runtime quota",
                        "html_url": "https://github.com/mizzz-ivr/example/pull/10",
                        "merged_at": "2026-08-20T00:00:00Z",
                    },
                    {
                        "number": 2,
                        "title": "old change",
                        "html_url": "https://github.com/mizzz-ivr/example/pull/2",
                        "merged_at": "2025-01-01T00:00:00Z",
                    },
                ]
            if "/releases?" in url:
                return [
                    {
                        "tag_name": "v1.0.0",
                        "name": "v1.0.0",
                        "html_url": "https://github.com/mizzz-ivr/example/releases/tag/v1.0.0",
                        "published_at": "2026-08-21T00:00:00Z",
                        "draft": False,
                        "prerelease": False,
                    }
                ]
            if "/issues?" in url:
                return [
                    {
                        "number": 7,
                        "title": "Harden secret boundary",
                        "html_url": "https://github.com/mizzz-ivr/example/issues/7",
                        "closed_at": "2026-08-22T00:00:00Z",
                        "labels": [{"name": "security"}],
                    },
                    {
                        "number": 8,
                        "title": "Unlabeled maintenance",
                        "html_url": "https://github.com/mizzz-ivr/example/issues/8",
                        "closed_at": "2026-08-22T00:00:00Z",
                        "labels": [],
                    },
                ]
            raise AssertionError(url)

        snapshot = funnel.collect_snapshot(
            policy,
            fetcher,
            as_of=date(2026, 8, 28),
            collected_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
        )
        funnel.validate_snapshot(snapshot, policy)
        repo = snapshot["repositories"][0]
        self.assertEqual([row["number"] for row in repo["merged_pull_requests"]], [10])
        self.assertEqual([row["tag_name"] for row in repo["releases"]], ["v1.0.0"])
        self.assertEqual([row["number"] for row in repo["significant_issues"]], [7])

    def test_payload_marks_only_explicit_title_overlap_as_tracked(self):
        policy = funnel.FunnelPolicy(
            repositories=("mizzz-ivr/example",),
            significant_issue_labels=frozenset(),
            lookback_days=45,
            release_lookback_days=90,
            title_overlap_threshold=0.88,
            max_candidates=12,
        )
        snapshot = {
            "schema_version": 1,
            "as_of": "2026-08-28",
            "collected_at": "2026-08-28T00:00:00Z",
            "repositories": [
                {
                    "repository": "mizzz-ivr/example",
                    "merged_pull_requests": [
                        {
                            "number": 1,
                            "title": "feat: GitHubプロフィールをライブな開発ダッシュボードにしてみた",
                            "url": "https://github.com/mizzz-ivr/example/pull/1",
                            "merged_at": "2026-08-27T00:00:00Z",
                        },
                        {
                            "number": 2,
                            "title": "Add zero-downtime deployment guard",
                            "url": "https://github.com/mizzz-ivr/example/pull/2",
                            "merged_at": "2026-08-28T00:00:00Z",
                        },
                    ],
                    "releases": [],
                    "significant_issues": [],
                }
            ],
        }
        payload = funnel.build_funnel_payload(
            [Article("GitHubプロフィールをライブな開発ダッシュボードにしてみた")],
            [Backlog("個人開発でもPRを切ってCIを通すようにしている理由")],
            policy=policy,
            snapshot=snapshot,
        )
        by_id = {row["source_id"]: row for row in payload["candidates"]}
        self.assertEqual(by_id["#1"]["tracking_status"], "tracked")
        self.assertEqual(by_id["#1"]["matched_source"], "article:published")
        self.assertEqual(by_id["#2"]["tracking_status"], "untracked")
        self.assertEqual(payload["untracked_count"], 1)

    def test_release_wins_duplicate_title_without_significance_score(self):
        rows = [
            funnel.Evidence("mizzz-ivr/example", "pull_request", "Ship v1", "pr", "2026-08-28T00:00:00Z", "#1"),
            funnel.Evidence("mizzz-ivr/example", "release", "Ship v1", "release", "2026-08-27T00:00:00Z", "v1"),
        ]
        selected = funnel.deduplicate_evidence(rows)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].kind, "release")


if __name__ == "__main__":
    unittest.main()
