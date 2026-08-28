import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics
import writing_data_mart as data_mart
import writing_opportunities as opportunities


class WritingDataMartTests(unittest.TestCase):
    def article(self, slug, status, published_at=None, **extra):
        meta = {
            "title": slug,
            "status": status,
            "published_at": published_at,
            "topics": extra.pop("topics", []),
            "domains": extra.pop("domains", []),
            "languages": extra.pop("languages", []),
            "technologies": extra.pop("technologies", []),
            "portfolio_signals": extra.pop("portfolio_signals", []),
            "source_repositories": extra.pop("source_repositories", []),
            "published": extra.pop("published", {}),
            **extra,
        }
        return analytics.Article(
            slug=slug,
            path=Path(f"articles/{slug}/article.md"),
            meta=meta,
            registry=None,
        )

    def test_overview_pipeline_and_next_candidate_share_one_model(self):
        articles = [
            self.article(
                "published",
                "published",
                "2026-08-20",
                domains=["devops"],
                languages=["Python"],
                technologies=["GitHub Actions"],
                portfolio_signals=["automation"],
                published={"qiita": "https://qiita.com/example/items/00000000000000000000"},
            ),
            self.article(
                "candidate",
                "review",
                portfolio_signals=["communication"],
                source_repositories=["example/repo"],
            ),
            self.article("draft", "draft"),
        ]

        with patch.object(
            opportunities, "resolve_as_of", return_value=date(2026, 8, 28)
        ), patch.object(
            data_mart,
            "readable_snapshot_dates",
            return_value=[date(2026, 8, 27), date(2026, 8, 28)],
        ):
            payload = data_mart.build_data_mart(articles, None, [])

        data_mart.validate_data_mart(payload)
        self.assertEqual(payload["overview"]["tracked_articles"], 3)
        self.assertEqual(payload["overview"]["published_articles"], 1)
        self.assertEqual(payload["overview"]["review_articles"], 1)
        self.assertEqual(payload["overview"]["draft_articles"], 1)
        self.assertEqual(payload["pipeline"]["published"], 1)
        self.assertEqual(payload["next_article_candidates"][0]["slug"], "candidate")
        self.assertIn(
            "communication", payload["next_article_candidates"][0]["portfolio_gaps"]
        )
        self.assertFalse(payload["trend_readiness"]["windows"]["7"])

    def test_reactions_preserve_zero_null_and_missing_fields(self):
        snapshot = {
            "articles": [
                {
                    "title": "Example",
                    "platforms": {
                        "qiita": {
                            "url": "https://qiita.com/example/items/00000000000000000000",
                            "likes": 0,
                            "comments": 1,
                            "page_views": None,
                        }
                    },
                }
            ]
        }

        payload = data_mart.reaction_payload(snapshot)
        metrics = payload["observations"][0]["metrics"]

        self.assertEqual(metrics["likes"], 0)
        self.assertEqual(metrics["comments"], 1)
        self.assertIsNone(metrics["page_views"])
        self.assertNotIn("stocks", metrics)
        self.assertEqual(payload["observed_numeric_totals"]["qiita"]["likes"], 0)
        self.assertEqual(payload["observed_numeric_totals"]["qiita"]["comments"], 1)

    def test_trend_readiness_requires_real_observed_span(self):
        payload = data_mart.trend_readiness(
            [date(2026, 8, 1), date(2026, 8, 8), date(2026, 8, 28)]
        )

        self.assertEqual(payload["snapshot_count"], 3)
        self.assertEqual(payload["observed_span_days"], 27)
        self.assertTrue(payload["windows"]["7"])
        self.assertFalse(payload["windows"]["30"])
        self.assertFalse(payload["windows"]["90"])


if __name__ == "__main__":
    unittest.main()
