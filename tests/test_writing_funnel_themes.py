import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_funnel as funnel
import writing_funnel_themes as themes


class FunnelThemeGroupingTests(unittest.TestCase):
    def policy(self) -> funnel.FunnelPolicy:
        return funnel.FunnelPolicy(
            repositories=("example/app", "example/other"),
            significant_issue_labels=frozenset({"feature"}),
            lookback_days=45,
            release_lookback_days=90,
            title_overlap_threshold=0.88,
            max_candidates=12,
        )

    def snapshot(self):
        return {
            "schema_version": 1,
            "as_of": "2026-08-28",
            "collected_at": "2026-08-28T00:00:00Z",
            "repositories": [
                {
                    "repository": "example/app",
                    "merged_pull_requests": [
                        {
                            "number": 10,
                            "title": "feat(ai): add runtime",
                            "url": "https://github.com/example/app/pull/10",
                            "merged_at": "2026-08-28T00:00:00Z",
                        },
                        {
                            "number": 11,
                            "title": "fix(ai): harden runtime",
                            "url": "https://github.com/example/app/pull/11",
                            "merged_at": "2026-08-28T01:00:00Z",
                        },
                        {
                            "number": 12,
                            "title": "security: rotate boundary",
                            "url": "https://github.com/example/app/pull/12",
                            "merged_at": "2026-08-28T02:00:00Z",
                        },
                    ],
                    "releases": [
                        {
                            "tag_name": "v1.0.0",
                            "name": "App v1.0.0",
                            "url": "https://github.com/example/app/releases/tag/v1.0.0",
                            "published_at": "2026-08-28T03:00:00Z",
                            "prerelease": False,
                        }
                    ],
                    "significant_issues": [],
                },
                {
                    "repository": "example/other",
                    "merged_pull_requests": [
                        {
                            "number": 20,
                            "title": "feat(ai): another runtime",
                            "url": "https://github.com/example/other/pull/20",
                            "merged_at": "2026-08-28T04:00:00Z",
                        }
                    ],
                    "releases": [],
                    "significant_issues": [],
                },
            ],
        }

    def test_explicit_scope_requires_conventional_commit_scope(self):
        self.assertEqual(themes.explicit_scope("feat(ai): add runtime"), "ai")
        self.assertEqual(themes.explicit_scope("FIX(Profile): repair"), "Profile")
        self.assertIsNone(themes.explicit_scope("security: rotate boundary"))
        self.assertIsNone(themes.explicit_scope("add runtime"))

    def test_same_repo_same_explicit_scope_is_grouped(self):
        payload = themes.build_theme_payload(
            [], [], policy=self.policy(), snapshot=self.snapshot()
        )
        ai_group = next(
            group
            for group in payload["theme_groups"]
            if group["repository"] == "example/app"
            and group["grouping"] == "explicit_scope"
            and group["scope"] == "ai"
        )
        self.assertEqual(ai_group["event_count"], 2)
        self.assertEqual(ai_group["representative"]["source_id"], "#11")

    def test_same_scope_never_crosses_repository_boundary(self):
        payload = themes.build_theme_payload(
            [], [], policy=self.policy(), snapshot=self.snapshot()
        )
        ai_groups = [
            group
            for group in payload["theme_groups"]
            if group["grouping"] == "explicit_scope" and group["scope"] == "ai"
        ]
        self.assertEqual({group["repository"] for group in ai_groups}, {"example/app", "example/other"})

    def test_unscoped_event_remains_singleton_and_release_is_independent(self):
        payload = themes.build_theme_payload(
            [], [], policy=self.policy(), snapshot=self.snapshot()
        )
        singleton = next(
            group
            for group in payload["theme_groups"]
            if group["grouping"] == "singleton"
        )
        release = next(
            group for group in payload["theme_groups"] if group["grouping"] == "release"
        )
        self.assertEqual(singleton["event_count"], 1)
        self.assertEqual(release["event_count"], 1)
        self.assertEqual(release["representative"]["source_id"], "v1.0.0")

    def test_tracked_evidence_is_not_counted_as_untracked_theme(self):
        article = SimpleNamespace(
            title="feat(ai): add runtime",
            effective_status="published",
        )
        payload = themes.build_theme_payload(
            [article], [], policy=self.policy(), snapshot=self.snapshot()
        )
        self.assertEqual(payload["untracked_theme_count"], 4)
        self.assertEqual(
            sum(group["event_count"] for group in payload["theme_groups"]),
            4,
        )


if __name__ == "__main__":
    unittest.main()
