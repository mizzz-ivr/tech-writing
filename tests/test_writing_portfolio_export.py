import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "writing_portfolio_export.py"
SPEC = importlib.util.spec_from_file_location("writing_portfolio_export", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
portfolio = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = portfolio
SPEC.loader.exec_module(portfolio)
analytics = portfolio.analytics


def article(slug: str, title: str, **meta):
    payload = {"title": title, "status": "published", "published_at": "2026-08-20", **meta}
    return analytics.Article(
        slug=slug,
        path=analytics.ROOT / "articles" / slug / "article.md",
        meta=payload,
        registry=None,
    )


class PublicSourceBoundaryTests(unittest.TestCase):
    def test_only_allowlisted_source_repositories_are_exported(self):
        item = article(
            "example",
            "Example",
            source_repositories=["public/repo", "private/repo"],
            published={"qiita": "https://qiita.com/example/items/00000000000000000000"},
        )

        payload, omitted = portfolio.article_payload(item, {"public/repo"})

        self.assertEqual(payload["source_repositories"], ["public/repo"])
        self.assertEqual(omitted, 1)
        self.assertNotIn("private/repo", portfolio.render_json({"article": payload}))

    def test_validator_rejects_source_outside_allowlist(self):
        payload = {
            "schema_version": 1,
            "recent_articles": [
                {
                    "source_repositories": ["private/repo"],
                    "published": {"qiita": "https://qiita.com/example/items/00000000000000000000"},
                }
            ],
            "notable_articles": [],
        }

        with self.assertRaises(ValueError):
            portfolio.validate_export(payload, {"public/repo"})


class PublicMetricBoundaryTests(unittest.TestCase):
    def test_notable_export_keeps_reactions_but_excludes_page_views(self):
        item = article(
            "example",
            "Example",
            topics=["GitHub"],
            published={"qiita": "https://qiita.com/example/items/00000000000000000000"},
        )
        snapshot = {
            "articles": [
                {
                    "title": "Example",
                    "platforms": {
                        "qiita": {
                            "url": "https://qiita.com/example/items/00000000000000000000",
                            "likes": 1,
                            "stocks": 2,
                            "comments": 0,
                            "page_views": 123,
                        }
                    },
                }
            ]
        }

        rows = portfolio.notable_payload([item], snapshot)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reactions"], {"likes": 1, "stocks": 2, "comments": 0})
        self.assertNotIn("page_views", rows[0]["reactions"])


class StableSchemaTests(unittest.TestCase):
    def test_build_export_contains_stable_top_level_shape(self):
        item = article(
            "example",
            "Example",
            domains=["devops"],
            languages=["Python"],
            technologies=["GitHub Actions"],
            portfolio_signals=["automation"],
            source_repositories=["public/repo"],
            published={"qiita": "https://qiita.com/example/items/00000000000000000000"},
        )
        policy = {"public_source_repositories": {"public/repo"}, "max_recent_articles": 10}

        payload = portfolio.build_export([item], snapshot=None, policy=policy)

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["summary"]["published_articles"], 1)
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "as_of",
                "summary",
                "coverage",
                "recent_articles",
                "notable_articles",
                "export_quality",
            },
        )
        self.assertEqual(set(payload["coverage"]), {"domains", "languages", "technologies", "portfolio_signals"})

    def test_sensitive_field_names_are_rejected_recursively(self):
        payload = {"schema_version": 1, "nested": {"api_token": "redacted"}, "recent_articles": [], "notable_articles": []}

        with self.assertRaises(ValueError):
            portfolio.validate_export(payload, set())


if __name__ == "__main__":
    unittest.main()
