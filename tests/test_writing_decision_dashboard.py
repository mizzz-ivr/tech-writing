import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_decision_dashboard as dashboard


class DecisionDashboardTests(unittest.TestCase):
    def test_reaction_chart_excludes_page_views(self):
        model = {
            "reactions": {
                "observed_numeric_totals": {
                    "qiita": {
                        "likes": 1,
                        "stocks": 2,
                        "comments": 0,
                        "page_views": 999,
                    },
                    "zenn": {
                        "likes": 3,
                        "bookmarks": 4,
                        "comments": 1,
                        "page_views": 888,
                    },
                }
            }
        }

        entries = dict(dashboard.reaction_chart_entries(model))

        self.assertEqual(entries["qiita likes"], 1)
        self.assertEqual(entries["qiita stocks"], 2)
        self.assertEqual(entries["zenn bookmarks"], 4)
        self.assertNotIn("qiita page_views", entries)
        self.assertNotIn("zenn page_views", entries)

    def test_dashboard_published_kpi_comes_from_data_mart(self):
        model = {
            "as_of": "2026-08-28",
            "overview": {
                "published_articles": 4,
                "draft_articles": 1,
                "review_articles": 2,
                "last_published_at": "2026-08-27",
                "pipeline_only_coverage_gaps": 1,
            },
            "pipeline": {"draft": 1, "review": 2, "published": 4, "archived": 0},
            "trend_readiness": {
                "snapshot_count": 2,
                "first_snapshot_at": "2026-08-27",
                "last_snapshot_at": "2026-08-28",
                "observed_span_days": 1,
                "windows": {"7": False, "30": False, "90": False},
            },
            "coverage": {
                key: {"values": [], "pipeline_only_values": []}
                for key in ("topics", "domains", "languages", "technologies", "portfolio_signals")
            },
            "reactions": {
                "observed_numeric_totals": {},
                "observations": [],
            },
            "next_article_candidates": [],
            "data_quality": {"finding_count": 0, "findings": []},
        }

        rendered = dashboard.build_dashboard(model)
        dashboard.validate_dashboard(model, rendered)

        self.assertIn("| Published | **4** |", rendered)
        self.assertIn("7日Trendはまだ待機中", rendered)


if __name__ == "__main__":
    unittest.main()
