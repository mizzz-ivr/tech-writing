import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

MODULE_PATH = SCRIPTS_DIR / "content_opportunities.py"
SPEC = importlib.util.spec_from_file_location("content_opportunities", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
opportunities = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = opportunities
SPEC.loader.exec_module(opportunities)

analytics = sys.modules["writing_analytics"]


def article(slug: str, status: str, **meta):
    return analytics.Article(
        slug=slug,
        path=Path(f"articles/{slug}/article.md"),
        meta={"title": meta.pop("title", slug), "status": status, **meta},
        registry=None,
    )


class ContentOpportunityTests(unittest.TestCase):
    def test_recency_windows_use_actual_published_dates(self):
        articles = [
            article(
                "recent",
                "published",
                published_at="2026-08-20",
                domains=["devops"],
                languages=[],
                technologies=["GitHub Actions"],
            ),
            article(
                "old",
                "published",
                published_at="2026-04-01",
                domains=["devops"],
                languages=[],
                technologies=["Docker"],
            ),
        ]

        rows = opportunities.coverage_rows(articles, "domains", date(2026, 8, 27))

        self.assertEqual(rows[0]["count"], 2)
        self.assertEqual(rows[0]["last"], "2026-08-20")
        self.assertTrue(rows[0]["within_30"])
        self.assertTrue(rows[0]["within_90"])
        self.assertTrue(rows[0]["within_365"])

    def test_portfolio_goal_distinguishes_published_pipeline_and_gap(self):
        goals = [
            opportunities.PortfolioGoal("architecture", "Architecture", {"portfolio_signals": ("architecture",)}),
            opportunities.PortfolioGoal("security", "Security", {"topics": ("セキュリティ",)}),
            opportunities.PortfolioGoal("testing", "Testing", {"portfolio_signals": ("testing",)}),
        ]
        articles = [
            article("public", "published", published_at="2026-08-20", portfolio_signals=["architecture"]),
            article("queued", "review", topics=["セキュリティ"]),
        ]

        public_arch, pipeline_arch = opportunities.goal_evidence(articles, goals[0])
        public_sec, pipeline_sec = opportunities.goal_evidence(articles, goals[1])
        public_test, pipeline_test = opportunities.goal_evidence(articles, goals[2])

        self.assertEqual([item.slug for item in public_arch], ["public"])
        self.assertEqual(pipeline_arch, [])
        self.assertEqual(public_sec, [])
        self.assertEqual([item.slug for item in pipeline_sec], ["queued"])
        self.assertEqual(public_test, [])
        self.assertEqual(pipeline_test, [])

    def test_goal_matching_does_not_infer_from_article_title(self):
        goal = opportunities.PortfolioGoal("security", "Security", {"portfolio_signals": ("security",)})
        titled_only = article("security-title", "review", title="Security hardening without metadata")

        self.assertFalse(opportunities.article_matches_goal(titled_only, goal))

    def test_explicit_topic_can_match_configured_goal(self):
        goal = opportunities.PortfolioGoal("security", "Security", {"topics": ("セキュリティ", "security")})
        queued = article("ai-runtime", "review", topics=["TypeScript", "セキュリティ"])

        self.assertTrue(opportunities.article_matches_goal(queued, goal))

    def test_backlog_parser_keeps_top_level_section_and_detects_duplicates(self):
        text = """# Backlog

## 次に着手
- [ ] Article A
  - detail
- [x] Done

## Other
- [ ] Article A
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "backlog.md"
            path.write_text(text, encoding="utf-8")
            items = opportunities.parse_backlog(path)

        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].section, "次に着手")
        self.assertFalse(items[0].checked)
        self.assertEqual(len(opportunities.backlog_duplicates(items)), 1)

    def test_next_opportunity_prefers_explicit_gap_with_source_evidence(self):
        goals = [
            opportunities.PortfolioGoal("security", "Security", {"topics": ("セキュリティ",)}),
            opportunities.PortfolioGoal("ci-cd", "CI/CD", {"topics": ("ci",)}),
        ]
        articles = [
            article("ci-public", "published", published_at="2026-08-20", topics=["ci"]),
            article(
                "ai-runtime",
                "review",
                title="AI Runtime",
                topics=["セキュリティ"],
                source_repositories=["ivRooom/Herta"],
            ),
            article("ci-review", "review", title="PR CI", topics=["ci"]),
        ]
        items = [
            opportunities.BacklogItem("次に着手", "AI Runtime", False, 0),
            opportunities.BacklogItem("次に着手", "PR CI", False, 1),
        ]

        item, source, gaps, reason = opportunities.choose_next_opportunity(items, articles, goals)

        self.assertEqual(item.title, "AI Runtime")
        self.assertEqual(source.slug, "ai-runtime")
        self.assertEqual([goal.label for goal in gaps], ["Security"])
        self.assertEqual(reason, "coverage gap + source evidence")

    def test_report_separates_pipeline_from_published_and_does_not_use_reaction_score(self):
        goals = [
            opportunities.PortfolioGoal("security", "Security", {"topics": ("セキュリティ",)}),
        ]
        articles = [
            article(
                "ai-runtime",
                "review",
                title="AI Runtime",
                topics=["セキュリティ"],
                source_repositories=["ivRooom/Herta"],
            )
        ]
        backlog = [opportunities.BacklogItem("次に着手", "AI Runtime", False, 0)]

        report = opportunities.build_report(articles, backlog, goals, date(2026, 8, 27), 1)

        self.assertIn("**0 published / 1 pipeline / 0 gaps**", report)
        self.assertIn("coverage gap + source evidence", report)
        self.assertIn("only 1 snapshot date(s) exist", report)
        self.assertNotIn("Popularity Score", report)


if __name__ == "__main__":
    unittest.main()
