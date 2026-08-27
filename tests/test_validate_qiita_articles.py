from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_qiita_articles import validate_article


class QiitaArticleValidatorTests(unittest.TestCase):
    def write_article(self, content: str) -> Path:
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "article.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_accepts_valid_article(self):
        path = self.write_article(
            """---
title: Valid article
tags:
  - GitHub
  - Python
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Article body
"""
        )

        self.assertEqual(validate_article(path), [])

    def test_rejects_missing_title_empty_body_and_invalid_tags(self):
        path = self.write_article(
            """---
tags:
  - ""
  - one
  - two
  - three
  - four
  - five
private: false
---
"""
        )

        errors = validate_article(path)
        self.assertIn("missing required front matter key: title", errors)
        self.assertIn("title must be a non-empty string", errors)
        self.assertIn("body must not be empty", errors)
        self.assertIn("tags must contain between 1 and 5 items", errors)
        self.assertIn("tags must contain only non-empty strings", errors)

    def test_rejects_private_article_with_organization(self):
        path = self.write_article(
            """---
title: Private organization article
tags:
  - GitHub
private: true
organization_url_name: ivrooom
---
Article body
"""
        )

        self.assertIn(
            "private articles cannot be linked to an Organization",
            validate_article(path),
        )

    def test_rejects_campaign_without_agreement(self):
        path = self.write_article(
            """---
title: Campaign article
tags:
  - GitHub
private: false
posting_campaign_uuid: 12345678-1234-1234-1234-123456789abc
agreed_posting_campaign_term: false
---
Article body
"""
        )

        self.assertIn(
            "posting campaigns require agreed_posting_campaign_term: true",
            validate_article(path),
        )

    def test_rejects_non_standalone_closing_delimiter(self):
        path = self.write_article(
            """---
title: Invalid delimiter
tags:
  - GitHub
private: false
---oops
Article body
"""
        )

        self.assertIn(
            "front matter closing delimiter must be a standalone '---' line",
            validate_article(path),
        )


if __name__ == "__main__":
    unittest.main()
