import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import writing_analytics as analytics
import writing_catalog as catalog


class UnifiedArticleCatalogTests(unittest.TestCase):
    def test_published_zenn_native_article_is_normalized_into_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            articles_dir.mkdir()

            common_dir = articles_dir / "common"
            common_dir.mkdir()
            (common_dir / "article.md").write_text(
                """---
title: Common article
status: published
published_at: '2026-08-26'
domains: []
languages: []
technologies: []
published:
  qiita: https://qiita.com/example/items/00000000000000000000
---
body
""",
                encoding="utf-8",
            )

            (articles_dir / "native.md").write_text(
                """---
title: Native Zenn article
type: tech
topics: [typescript]
published: true
---
body
""",
                encoding="utf-8",
            )

            published_path = root / "published.md"
            published_path.write_text(
                """| 公開日 | タイトル | Qiita | Zenn | note | その他 |
| --- | --- | --- | --- | --- | --- |
| 2026-08-27 | Native Zenn article | - | https://zenn.dev/example/articles/native | - | - |
""",
                encoding="utf-8",
            )
            sidecar = root / "platform-native-analytics.yml"
            sidecar.write_text("schema_version: 1\narticles: {}\n", encoding="utf-8")

            with patch.object(analytics, "ARTICLES_DIR", articles_dir), patch.object(
                analytics, "PUBLISHED_PATH", published_path
            ), patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                articles = catalog.load_articles()

        by_slug = {article.slug: article for article in articles}
        self.assertEqual(set(by_slug), {"common", "native"})
        native = by_slug["native"]
        self.assertEqual(native.effective_status, "published")
        self.assertEqual(native.effective_published_at, "2026-08-27")
        self.assertEqual(
            native.platform_url("zenn"), "https://zenn.dev/example/articles/native"
        )
        self.assertEqual(native.meta["article_type"], "tech")

    def test_native_sidecar_adds_evidence_without_overriding_platform_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            articles_dir.mkdir()
            (articles_dir / "native.md").write_text(
                """---
title: Native Zenn article
type: tech
topics: [typescript]
published: true
---
body
""",
                encoding="utf-8",
            )
            published_path = root / "published.md"
            published_path.write_text(
                """| 公開日 | タイトル | Qiita | Zenn | note | その他 |
| --- | --- | --- | --- | --- | --- |
| 2026-08-27 | Native Zenn article | - | https://zenn.dev/example/articles/native | - | - |
""",
                encoding="utf-8",
            )
            sidecar = root / "platform-native-analytics.yml"
            sidecar.write_text(
                """schema_version: 1
articles:
  articles/native.md:
    source_repositories:
      - example/repo
    verified_at: '2026-08-28'
    source_refs:
      - repository: example/repo
        commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
""",
                encoding="utf-8",
            )

            with patch.object(analytics, "ARTICLES_DIR", articles_dir), patch.object(
                analytics, "PUBLISHED_PATH", published_path
            ), patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                native = catalog.load_articles()[0]

        self.assertEqual(native.title, "Native Zenn article")
        self.assertEqual(native.effective_status, "published")
        self.assertEqual(native.effective_published_at, "2026-08-27")
        self.assertEqual(native.meta["source_repositories"], ["example/repo"])
        self.assertEqual(native.meta["verified_at"], "2026-08-28")
        self.assertEqual(len(native.meta["source_refs"]), 1)
        self.assertEqual(
            native.platform_url("zenn"), "https://zenn.dev/example/articles/native"
        )

    def test_native_sidecar_cannot_override_publication_or_title_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            sidecar = Path(tmp) / "platform-native-analytics.yml"
            sidecar.write_text(
                """schema_version: 1
articles:
  articles/native.md:
    status: draft
""",
                encoding="utf-8",
            )
            with patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                with self.assertRaisesRegex(ValueError, "unsupported.*status"):
                    catalog.load_native_analytics_metadata()

    def test_native_sidecar_only_targets_direct_platform_native_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            sidecar = Path(tmp) / "platform-native-analytics.yml"
            sidecar.write_text(
                """schema_version: 1
articles:
  articles/common/article.md:
    verified_at: '2026-08-28'
""",
                encoding="utf-8",
            )
            with patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                with self.assertRaisesRegex(ValueError, "direct `articles/<slug>.md`"):
                    catalog.load_native_analytics_metadata()

    def test_sidecar_entry_for_unpublished_native_article_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            articles_dir.mkdir()
            (articles_dir / "native-draft.md").write_text(
                """---
title: Native draft
type: tech
topics: [python]
published: false
---
body
""",
                encoding="utf-8",
            )
            published_path = root / "published.md"
            published_path.write_text("", encoding="utf-8")
            sidecar = root / "platform-native-analytics.yml"
            sidecar.write_text(
                """schema_version: 1
articles:
  articles/native-draft.md:
    verified_at: '2026-08-28'
""",
                encoding="utf-8",
            )

            with patch.object(analytics, "ARTICLES_DIR", articles_dir), patch.object(
                analytics, "PUBLISHED_PATH", published_path
            ), patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                with self.assertRaisesRegex(ValueError, "outside the published native catalog"):
                    catalog.load_articles()

    def test_unregistered_native_file_is_not_inferred_as_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles_dir = root / "articles"
            articles_dir.mkdir()
            (articles_dir / "native-draft.md").write_text(
                """---
title: Native draft
type: tech
topics: [python]
published: false
---
body
""",
                encoding="utf-8",
            )
            published_path = root / "published.md"
            published_path.write_text("", encoding="utf-8")
            sidecar = root / "platform-native-analytics.yml"
            sidecar.write_text("schema_version: 1\narticles: {}\n", encoding="utf-8")

            with patch.object(analytics, "ARTICLES_DIR", articles_dir), patch.object(
                analytics, "PUBLISHED_PATH", published_path
            ), patch.object(catalog, "NATIVE_ANALYTICS_PATH", sidecar):
                articles = catalog.load_articles()

        self.assertEqual(articles, [])


if __name__ == "__main__":
    unittest.main()
