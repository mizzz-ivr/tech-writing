import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

MODULE_PATH = SCRIPTS_DIR / "writing_dashboard.py"
SPEC = importlib.util.spec_from_file_location("writing_dashboard", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
dashboard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = dashboard
SPEC.loader.exec_module(dashboard)

analytics = dashboard.analytics


class WritingDashboardTests(unittest.TestCase):
    def article(self, slug: str, status: str, published_at: str | None = None):
        meta = {
            "title": slug,
            "status": status,
            "published_at": published_at,
            "domains": ["devops"] if status == "published" else [],
            "languages": [],
            "technologies": ["GitHub Actions"] if status == "published" else [],
            "portfolio_signals": ["automation"] if status == "published" else [],
            "published": {
                "qiita": "https://qiita.com/example/items/00000000000000000000" if status == "published" else None,
                "zenn": None,
            },
        }
        return analytics.Article(
            slug=slug,
            path=Path(f"articles/{slug}/article.md"),
            meta=meta,
            registry=None,
        )

    def test_status_counts_keep_pipeline_states_separate(self):
        articles = [
            self.article("draft-one", "draft"),
            self.article("review-one", "review"),
            self.article("published-one", "published", "2026-08-27"),
        ]

        counts = dashboard.status_counts(articles)

        self.assertEqual(counts["draft"], 1)
        self.assertEqual(counts["review"], 1)
        self.assertEqual(counts["published"], 1)

    def test_reaction_totals_keep_observed_zero_but_skip_null_and_missing(self):
        snapshot = {
            "articles": [
                {
                    "title": "Example",
                    "platforms": {
                        "qiita": {
                            "url": "https://example.test/article",
                            "likes": 0,
                            "stocks": 2,
                            "comments": None,
                        }
                    },
                }
            ]
        }

        totals = dashboard.observed_reaction_counts(snapshot)

        self.assertIn("qiita likes", totals)
        self.assertEqual(totals["qiita likes"], 0)
        self.assertEqual(totals["qiita stocks"], 2)
        self.assertNotIn("qiita comments", totals)

    def test_svg_escapes_labels_and_renders_zero_as_observed_value(self):
        svg = dashboard.svg_bar_chart("A & B", [("x < y", 0), ("ok", 2)])

        self.assertIn("A &amp; B", svg)
        self.assertIn("x &lt; y", svg)
        self.assertIn(">0</text>", svg)
        self.assertIn(">2</text>", svg)

    def test_dashboard_refuses_to_invent_history_when_only_one_snapshot_exists(self):
        articles = [self.article("published-one", "published", "2026-08-27")]

        with patch.object(dashboard, "latest_snapshot_count", return_value=1):
            content = dashboard.build_dashboard(articles, None)

        self.assertIn("1 snapshot(s)", content)
        self.assertIn("intentionally not generated", content)
        self.assertIn("no interpolation or synthetic history", content)

    def test_chart_payloads_include_expected_visuals(self):
        articles = [self.article("published-one", "published", "2026-08-27")]

        charts = dashboard.chart_payloads(articles, None)

        self.assertEqual(
            set(charts),
            {
                "pipeline.svg",
                "domains.svg",
                "technologies.svg",
                "portfolio-signals.svg",
                "reactions.svg",
            },
        )
        self.assertIn("Published domains", charts["domains.svg"])


if __name__ == "__main__":
    unittest.main()
