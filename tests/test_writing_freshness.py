import json
import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics
import writing_freshness as freshness


class WritingFreshnessTests(unittest.TestCase):
    def article(self, slug="example", status="published", **extra):
        meta = {
            "title": slug,
            "status": status,
            "published_at": "2026-08-20" if status == "published" else None,
            "source_repositories": extra.pop("source_repositories", []),
            "published": {"qiita": "https://qiita.com/example/items/00000000000000000000"}
            if status == "published"
            else {},
            **extra,
        }
        return analytics.Article(
            slug=slug,
            path=Path(f"articles/{slug}/article.md"),
            meta=meta,
            registry=None,
        )

    def test_missing_metadata_is_initial_verification_not_inferred(self):
        payload = freshness.freshness_payload(
            [self.article()], date(2026, 8, 28)
        )

        self.assertEqual(payload["published_articles"], 1)
        self.assertEqual(payload["verified_articles"], 0)
        self.assertEqual(payload["needs_initial_verification"], 1)
        self.assertEqual(payload["as_of"], "2026-08-28")
        row = payload["articles"][0]
        self.assertEqual(row["status"], "needs_initial_verification")
        self.assertIsNone(row["verified_at"])
        self.assertIsNone(row["days_since_verified"])

    def test_verified_article_reports_age_and_ref_count_without_exposing_ref(self):
        repository = "private-looking/example"
        commit = "a" * 40
        payload = freshness.freshness_payload(
            [
                self.article(
                    verified_at="2026-08-25",
                    source_repositories=[repository],
                    source_refs=[{"repository": repository, "commit": commit}],
                )
            ],
            date(2026, 8, 28),
        )

        row = payload["articles"][0]
        self.assertEqual(row["status"], "verified")
        self.assertEqual(row["verified_at"], "2026-08-25")
        self.assertEqual(row["days_since_verified"], 3)
        self.assertEqual(row["source_ref_count"], 1)
        rendered = json.dumps(payload)
        self.assertNotIn(repository, rendered)
        self.assertNotIn(commit, rendered)

    def test_same_slug_different_layouts_keep_independent_freshness(self):
        shared = self.article(verified_at="2026-08-20")
        native = self.article(verified_at="2026-08-27")
        native.path = Path("articles/example.md")

        payload = freshness.freshness_payload(
            [shared, native], date(2026, 8, 28)
        )
        rows = {row["path"]: row for row in payload["articles"]}

        self.assertEqual(payload["published_articles"], 2)
        self.assertEqual(rows["articles/example/article.md"]["days_since_verified"], 8)
        self.assertEqual(rows["articles/example.md"]["days_since_verified"], 1)

    def test_invalid_verified_at_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "verified_at"):
            freshness.freshness_payload(
                [self.article(verified_at="2026/08/25")], date(2026, 8, 28)
            )

    def test_future_verified_at_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot be in the future"):
            freshness.freshness_payload(
                [self.article(verified_at="2026-08-29")], date(2026, 8, 28)
            )

    def test_malformed_commit_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "40-character commit SHA"):
            freshness.freshness_payload(
                [
                    self.article(
                        verified_at="2026-08-25",
                        source_repositories=["example/repo"],
                        source_refs=[{"repository": "example/repo", "commit": "abc"}],
                    )
                ],
                date(2026, 8, 28),
            )

    def test_source_ref_repository_must_match_source_repositories(self):
        with self.assertRaisesRegex(ValueError, "source_repositories"):
            freshness.freshness_payload(
                [
                    self.article(
                        verified_at="2026-08-25",
                        source_repositories=["example/other"],
                        source_refs=[
                            {"repository": "example/repo", "commit": "b" * 40}
                        ],
                    )
                ],
                date(2026, 8, 28),
            )

    def test_source_refs_require_verified_at(self):
        with self.assertRaisesRegex(ValueError, "requires `verified_at`"):
            freshness.freshness_payload(
                [
                    self.article(
                        source_repositories=["example/repo"],
                        source_refs=[
                            {"repository": "example/repo", "commit": "c" * 40}
                        ],
                    )
                ],
                date(2026, 8, 28),
            )


if __name__ == "__main__":
    unittest.main()
