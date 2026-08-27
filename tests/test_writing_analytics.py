import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "writing_analytics.py"
SPEC = importlib.util.spec_from_file_location("writing_analytics", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
analytics = importlib.util.module_from_spec(SPEC)
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


if __name__ == "__main__":
    unittest.main()
