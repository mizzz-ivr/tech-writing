import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import article_layout
import writing_analytics as analytics


ARTICLE = """---
title: {title}
status: {status}
published_at: null
domains: []
languages: []
technologies: []
published:
  qiita: null
  zenn: null
---
body
"""


class ArticleLifecycleLayoutTests(unittest.TestCase):
    def write_article(self, root: Path, lifecycle: str, slug: str, status: str) -> Path:
        path = root / "articles" / lifecycle / slug / "article.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            ARTICLE.format(title=slug, status=status),
            encoding="utf-8",
        )
        return path

    def test_active_lifecycles_are_loaded_and_old_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            self.write_article(root, "draft", "draft-one", "draft")
            self.write_article(root, "review", "review-one", "review")
            self.write_article(root, "published", "published-one", "published")
            self.write_article(root, "old", "old-one", "draft")
            published_path = root / "published.md"
            published_path.write_text("", encoding="utf-8")

            with patch.object(analytics, "ROOT", root), patch.object(
                analytics, "ARTICLES_DIR", articles_dir
            ), patch.object(analytics, "PUBLISHED_PATH", published_path):
                loaded = article_layout.load_shared_articles(analytics)

        self.assertEqual(
            {article.slug for article in loaded},
            {"draft-one", "review-one", "published-one"},
        )

    def test_folder_and_front_matter_status_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            self.write_article(root, "draft", "wrong-status", "review")
            published_path = root / "published.md"
            published_path.write_text("", encoding="utf-8")

            with patch.object(analytics, "ROOT", root), patch.object(
                analytics, "ARTICLES_DIR", articles_dir
            ), patch.object(analytics, "PUBLISHED_PATH", published_path):
                with self.assertRaisesRegex(ValueError, "does not match"):
                    article_layout.load_shared_articles(analytics)

    def test_legacy_layout_delegates_to_existing_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir = Path(tmp) / "articles"
            articles_dir.mkdir()
            sentinel = object()

            with patch.object(analytics, "ARTICLES_DIR", articles_dir), patch.object(
                analytics, "load_articles", return_value=[sentinel]
            ) as legacy_loader:
                loaded = article_layout.load_shared_articles(analytics)

        self.assertEqual(loaded, [sentinel])
        legacy_loader.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
