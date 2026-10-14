import unittest

from paxly_content import build_system_instruction, format_doc_to_html
from paxly_services import sanitize_google_doc_html


class ContentSafetyTests(unittest.TestCase):
    def test_plain_text_is_html_escaped(self):
        rendered = format_doc_to_html("# Rubrik\n1. <script>alert(1)</script>")

        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_exported_html_is_sanitized(self):
        rendered = sanitize_google_doc_html(
            '<p>Ok</p><script>alert(1)</script>'
            '<img src="javascript:alert(1)" onerror="alert(2)">'
        )

        self.assertNotIn("<script", rendered)
        self.assertNotIn("javascript:", rendered)
        self.assertNotIn("onerror", rendered)

    def test_system_instruction_contains_available_documents(self):
        instruction = build_system_instruction(["Första", "Andra"])

        self.assertIn("DOKUMENT 1", instruction)
        self.assertIn("DOKUMENT 2", instruction)
        self.assertIn("Första", instruction)


if __name__ == "__main__":
    unittest.main()
