import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

ANALYTICS_SPEC = importlib.util.spec_from_file_location("writing_analytics", SCRIPTS / "writing_analytics.py")
assert ANALYTICS_SPEC is not None and ANALYTICS_SPEC.loader is not None
analytics = importlib.util.module_from_spec(ANALYTICS_SPEC)
sys.modules[ANALYTICS_SPEC.name] = analytics
ANALYTICS_SPEC.loader.exec_module(analytics)

EXPORT_SPEC = importlib.util.spec_from_file_location("writing_portfolio_export", SCRIPTS / "writing_portfolio_export.py")
assert EXPORT_SPEC is not None and EXPORT_SPEC.loader is not None
portfolio_export = importlib.util.module_from_spec(EXPORT_SPEC)
sys.modules[EXPORT_SPEC.name] = portfolio_export
EXPORT_SPEC.loader.exec_module(portfolio_export)


class NoteRegistryTests(unittest.TestCase):
    def test_six_column_registry_reads_note_url(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "published.md"
            path.write_text(
                "| 公開日 | タイトル | Qiita | Zenn | note | その他 |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| 2026-08-28 | Note only | - | - | https://note.com/example/n/n123 | - |\n",
                encoding="utf-8",
            )
            with patch.object(analytics, "PUBLISHED_PATH", path):
                registry = analytics.read_published_registry()

        self.assertEqual(registry["Note only"].note, "https://note.com/example/n/n123")
        self.assertIsNone(registry["Note only"].qiita)
        self.assertIsNone(registry["Note only"].zenn)

    def test_legacy_five_column_other_is_not_treated_as_note(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "published.md"
            path.write_text(
                "| 公開日 | タイトル | Qiita | Zenn | その他 |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| 2026-08-28 | Legacy | - | - | https://example.com/other |\n",
                encoding="utf-8",
            )
            with patch.object(analytics, "PUBLISHED_PATH", path):
                registry = analytics.read_published_registry()

        self.assertIsNone(registry["Legacy"].note)


class NotePublicationBehaviorTests(unittest.TestCase):
    @staticmethod
    def note_article() -> object:
        return analytics.Article(
            slug="note-only",
            path=Path("articles/note-only/article.md"),
            meta={
                "title": "Note only",
                "status": "published",
                "published_at": "2026-08-28",
                "domains": [],
                "languages": [],
                "technologies": [],
                "published": {"note": "https://note.com/example/n/n123"},
            },
            registry=None,
        )

    def test_note_only_article_has_representative_url_and_no_missing_url_error(self):
        article = self.note_article()

        self.assertEqual(
            analytics.preferred_publication_url(article),
            "https://note.com/example/n/n123",
        )
        self.assertFalse(any("公開URLがない" in issue for issue in analytics.data_quality([article])))

    def test_note_is_not_added_to_external_metric_collection(self):
        article = self.note_article()

        with patch.object(analytics, "api_json") as api_json:
            snapshot = analytics.refresh_metrics([article])

        api_json.assert_not_called()
        self.assertEqual(snapshot["errors"], [])
        self.assertEqual(snapshot["articles"][0]["platforms"], {})

    def test_report_and_readme_link_note_only_publication(self):
        article = self.note_article()

        report = analytics.build_report([article], snapshot=None)
        readme = analytics.build_readme_section([article], snapshot=None)

        self.assertIn("[Note only](https://note.com/example/n/n123)", report)
        self.assertIn("[Note only](https://note.com/example/n/n123)", readme)

    def test_public_portfolio_export_includes_note_url(self):
        article = self.note_article()

        payload, omitted = portfolio_export.article_payload(article, set())

        self.assertEqual(omitted, 0)
        self.assertEqual(
            payload["published"],
            {"note": "https://note.com/example/n/n123"},
        )


if __name__ == "__main__":
    unittest.main()
