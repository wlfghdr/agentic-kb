#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
TEMPLATES = [
    REPO / "plugins" / "kb" / "skills" / "kb-management" / "templates" / "report.html",
    REPO / "plugins" / "kb" / "skills" / "kb-setup" / "templates" / "presentation-template.html",
]
EXTERNAL_RESOURCE_RE = re.compile(
    r"<(?:script|link)[^>]*\s(?:src|href)\s*=\s*['\"](https?:|//)[^'\"]+['\"]",
    re.IGNORECASE,
)
EXTERNAL_CSS_IMPORT_RE = re.compile(r"@import\s+url\((['\"]?)(https?:|//)", re.IGNORECASE)


class HtmlTemplateTests(unittest.TestCase):
    def test_templates_are_self_contained(self) -> None:
        for path in TEMPLATES:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertNotRegex(content, EXTERNAL_RESOURCE_RE)
                self.assertNotRegex(content, EXTERNAL_CSS_IMPORT_RE)
                self.assertNotIn("fonts.googleapis.com", content)
                self.assertNotIn("fonts.gstatic.com", content)


if __name__ == "__main__":
    unittest.main()