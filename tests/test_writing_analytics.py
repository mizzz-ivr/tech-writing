import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "writing_analytics.py"
SPEC = importlib.util.spec_from_file_location("writing_analytics", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
analytics = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = analytics
SPEC.loader.exec_module(analytics)


class CadenceSummaryTests(unittest.TestCase):
    def article(self, slug: str, published_at: str):
        return analytics.Article(
            slug=slug,
            path=Path(f"articles/{slug}/article.md"),
            meta={"title": slug, "status": "published", "published_at": published_at},
            registry=None,
        )

    def test_same_day_publications_are_preserved(self):
        articles = [
            self.article("a", "2026-01-01"),
            self.article("b", "2026-01-01"),
            self.article("c", "2026-01-11"),
        ]

        last, average = analytics.cadence_summary(articles)

        self.assertEqual(last, "2026-01-11")
        self.assertEqual(average, "5.0日")


class ClassificationTests(unittest.TestCase):
    def test_explicit_empty_list_is_not_unclassified(self):
        article = analytics.Article(
            slug="language-agnostic",
            path=Path("articles/language-agnostic/article.md"),
            meta={
                "title": "language agnostic",
                "status": "published",
                "published_at": "2026-01-01",
                "domains": ["ai"],
                "languages": [],
                "technologies": ["GitHub"],
                "published": {"qiita": "https://qiita.com/example/items/00000000000000000000"},
            },
            registry=None,
        )

        issues = analytics.data_quality([article])
        languages = analytics.count_field([article], "languages")

        self.assertFalse(any("`languages` が未分類" in issue for issue in issues))
        self.assertNotIn("Unclassified", languages)
        self.assertEqual(sum(languages.values()), 0)

    def test_missing_classification_remains_unclassified(self):
        article = analytics.Article(
            slug="missing-language",
            path=Path("articles/missing-language/article.md"),
            meta={
                "title": "missing language",
                "status": "published",
                "published_at": "2026-01-01",
                "domains": ["ai"],
                "technologies": ["GitHub"],
                "published": {"qiita": "https://qiita.com/example/items/00000000000000000000"},
            },
            registry=None,
        )

        issues = analytics.data_quality([article])
        languages = analytics.count_field([article], "languages")

        self.assertTrue(any("`languages` が未分類" in issue for issue in issues))
        self.assertEqual(languages["Unclassified"], 1)


class ExternalMetricHardeningTests(unittest.TestCase):
    def test_unexpected_zenn_schema_becomes_platform_error(self):
        article = analytics.Article(
            slug="zenn-schema-test",
            path=Path("articles/zenn-schema-test/article.md"),
            meta={
                "title": "schema test",
                "status": "published",
                "published_at": "2026-01-01",
                "published": {"zenn": "https://zenn.dev/mizzz/articles/example"},
            },
            registry=None,
        )

        with patch.object(analytics, "api_json", return_value=[]):
            result = analytics.refresh_metrics([article])

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["platform"], "zenn")
        self.assertIn("error", result["articles"][0]["platforms"]["zenn"])


class ReactionAnalyticsTests(unittest.TestCase):
    def test_metric_display_distinguishes_zero_null_and_missing(self):
        metrics = {"likes": 0, "page_views": None}

        self.assertEqual(analytics.metric_display(metrics, "likes"), "0")
        self.assertEqual(analytics.metric_display(metrics, "page_views"), "unavailable")
        self.assertEqual(analytics.metric_display(metrics, "stocks"), "not collected")

    def test_stock_reaction_is_notable_even_when_likes_are_zero(self):
        snapshot = {
            "articles": [
                {
                    "title": "Stocked article",
                    "platforms": {
                        "qiita": {
                            "url": "https://example.test/article",
                            "likes": 0,
                            "stocks": 2,
                            "comments": 0,
                            "page_views": None,
                        }
                    },
                }
            ]
        }

        rows = analytics.notable_reaction_rows(snapshot)

        self.assertEqual(len(rows), 1)
        self.assertIn("stocks 2", analytics.reaction_summary(rows[0][1], rows[0][3]))

    def test_all_zero_reactions_do_not_create_fake_notable_order(self):
        snapshot = {
            "articles": [
                {
                    "title": "Zero article",
                    "platforms": {
                        "qiita": {
                            "url": "https://example.test/article",
                            "likes": 0,
                            "stocks": 0,
                            "comments": 0,
                            "page_views": None,
                        }
                    },
                }
            ]
        }

        self.assertEqual(analytics.notable_reaction_rows(snapshot), [])

    def test_platform_specific_fields_are_not_normalized(self):
        qiita = analytics.reaction_summary("qiita", {"likes": 1, "stocks": 2, "comments": 3})
        zenn = analytics.reaction_summary("zenn", {"likes": 1, "bookmarks": 2, "comments": 3})

        self.assertIn("stocks 2", qiita)
        self.assertNotIn("bookmarks", qiita)
        self.assertIn("bookmarks 2", zenn)
        self.assertNotIn("stocks", zenn)

    def test_page_views_null_is_normal_renderable_state(self):
        summary = analytics.reaction_summary(
            "qiita",
            {"likes": 0, "stocks": 0, "comments": 0, "page_views": None},
            include_page_views=True,
        )

        self.assertIn("page views unavailable", summary)
        self.assertNotIn("metrics error", summary)

    def test_report_uses_reactions_and_notable_instead_of_popular_ranking(self):
        snapshot = {
            "articles": [
                {
                    "title": "Stocked article",
                    "platforms": {
                        "qiita": {
                            "url": "https://example.test/article",
                            "likes": 0,
                            "stocks": 2,
                            "comments": 0,
                            "page_views": None,
                        }
                    },
                }
            ]
        }

        report = analytics.build_report([], snapshot)

        self.assertIn("## Reactions", report)
        self.assertIn("### Notable", report)
        self.assertIn("stocks 2", report)
        self.assertIn("page views unavailable", report)
        self.assertNotIn("## Popular Articles", report)


class ReadmeUpdateTests(unittest.TestCase):
    def test_marker_replacement_preserves_details_wrapper(self):
        original = "\n".join(
            [
                "# repo",
                "",
                "<details>",
                "<summary>Analytics</summary>",
                "",
                analytics.README_START,
                "old analytics",
                analytics.README_END,
                "",
                "</details>",
            ]
        )
        replacement = "\n".join(
            [
                analytics.README_START,
                "new analytics",
                analytics.README_END,
            ]
        )

        updated = analytics.update_readme(original, replacement)

        self.assertIn("<details>", updated)
        self.assertIn("<summary>Analytics</summary>", updated)
        self.assertIn("new analytics", updated)
        self.assertNotIn("old analytics", updated)
        self.assertLess(updated.index("<details>"), updated.index(analytics.README_START))
        self.assertLess(updated.index(analytics.README_END), updated.index("</details>"))


if __name__ == "__main__":
    unittest.main()
