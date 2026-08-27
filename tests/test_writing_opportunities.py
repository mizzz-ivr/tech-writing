import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "writing_opportunities.py"
SPEC = importlib.util.spec_from_file_location("writing_opportunities", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
opportunities = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = opportunities
SPEC.loader.exec_module(opportunities)
analytics = opportunities.analytics


def article(slug: str, status: str, **meta):
    payload = {"title": meta.pop("title", slug), "status": status, **meta}
    return analytics.Article(
        slug=slug,
        path=analytics.ROOT / "articles" / slug / "article.md",
        meta=payload,
        registry=None,
    )


class BacklogParsingTests(unittest.TestCase):
    def test_only_unchecked_items_are_loaded_and_source_is_preserved(self):
        items = opportunities.parse_backlog_text(
            """
## Next
- [x] done
- [ ] pending
  - Source of Truth: ivRooom/Herta
"""
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "pending")
        self.assertEqual(opportunities.source_of_truth(items[0]), "ivRooom/Herta")

    def test_media_prefix_does_not_hide_existing_article_overlap(self):
        item = opportunities.BacklogItem(
            "Zenn: 生成AIを「APIを呼ぶだけ」で終わらせない — Secret・Quota・Kill Switchを分離したAI Runtime設計",
            "Next",
            {},
        )
        existing = "生成AIをAPI呼び出しで終わらせない — Secret・Quota・Kill Switchを分けるAI Runtime設計"

        overlap = opportunities.best_title_overlap(item, [("published", existing)])

        self.assertIsNotNone(overlap)
        assert overlap is not None
        self.assertEqual(overlap[0], "published")
        self.assertGreaterEqual(overlap[2], opportunities.OVERLAP_THRESHOLD)


class CoverageTests(unittest.TestCase):
    def test_coverage_uses_latest_publication_for_window_markers(self):
        articles = [
            article("old", "published", published_at="2026-01-01", domains=["devops"]),
            article("new", "published", published_at="2026-08-20", domains=["devops"]),
        ]

        rows = opportunities.coverage_rows(articles, "domains", date(2026, 8, 27))

        self.assertEqual(rows, [("devops", 2, date(2026, 8, 20), 7)])

    def test_explicit_empty_language_list_is_not_invented_as_gap(self):
        published = article(
            "published",
            "published",
            published_at="2026-08-20",
            domains=["devops"],
            languages=["Python"],
            technologies=["GitHub Actions"],
            portfolio_signals=["automation"],
        )
        pending = article(
            "pending",
            "draft",
            domains=["devops"],
            languages=[],
            technologies=["GitHub Actions"],
            portfolio_signals=["automation"],
            source_repositories=["example/repo"],
        )

        candidates = opportunities.build_candidates(
            [published, pending],
            snapshot=None,
            as_of=date(2026, 8, 27),
        )

        self.assertEqual(len(candidates), 1)
        self.assertFalse(any("languages:" in gap for gap in candidates[0].coverage_gaps))
        self.assertNotIn("languages", candidates[0].missing_metadata)


class RecommendationPriorityTests(unittest.TestCase):
    def test_portfolio_gap_precedes_readiness_and_reaction_context(self):
        published = article(
            "published",
            "published",
            title="Published",
            published_at="2026-08-20",
            topics=["GitHub"],
            domains=["devops"],
            languages=["Python"],
            technologies=["GitHub Actions"],
            portfolio_signals=["automation"],
        )
        portfolio_gap = article(
            "career-gap",
            "draft",
            title="Career gap",
            topics=["writing"],
            domains=["devops"],
            languages=[],
            technologies=["GitHub Actions"],
            portfolio_signals=["communication"],
            source_repositories=["example/repo"],
        )
        ready_reaction = article(
            "ready",
            "review",
            title="Ready",
            topics=["GitHub"],
            domains=["devops"],
            languages=["Python"],
            technologies=["GitHub Actions"],
            portfolio_signals=["automation"],
            source_repositories=["example/repo"],
        )
        snapshot = {"articles": []}

        with patch.object(
            analytics,
            "notable_reaction_rows",
            return_value=[("Published", "qiita", "https://example.test", {"likes": 1})],
        ):
            candidates = opportunities.build_candidates(
                [published, portfolio_gap, ready_reaction],
                snapshot=snapshot,
                as_of=date(2026, 8, 27),
            )

        self.assertEqual(candidates[0].article.slug, "career-gap")
        self.assertEqual(candidates[1].article.slug, "ready")

    def test_missing_metadata_is_reported_instead_of_guessed(self):
        pending = article("pending", "review", topics=["GitHub"])

        candidates = opportunities.build_candidates(
            [pending],
            snapshot=None,
            as_of=date(2026, 8, 27),
        )

        self.assertIn("domains", candidates[0].missing_metadata)
        self.assertIn("source_repositories", candidates[0].missing_metadata)
        self.assertEqual(candidates[0].sources, ())


if __name__ == "__main__":
    unittest.main()
