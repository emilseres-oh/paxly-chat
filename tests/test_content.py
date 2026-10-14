import unittest
from unittest.mock import MagicMock, patch

from paxly_content import DEFAULT_OPENAI_MODEL, build_system_instruction, format_doc_to_html
from paxly_services import GOOGLE_DOC_CACHE_TTL_SECONDS, sanitize_google_doc_html, send_to_slack


class ContentSafetyTests(unittest.TestCase):
    def test_google_doc_cache_refreshes_frequently(self):
        self.assertLessEqual(GOOGLE_DOC_CACHE_TTL_SECONDS, 300)

    def test_default_model_is_cost_optimized(self):
        self.assertEqual("gpt-6-luna", DEFAULT_OPENAI_MODEL)

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

    @patch("paxly_services.get_setting", return_value=None)
    def test_slack_send_fails_when_webhook_is_missing(self, _get_setting):
        self.assertFalse(send_to_slack("Fråga", "Svar"))

    @patch("paxly_services.urllib.request.urlopen")
    @patch("paxly_services.get_setting", return_value="https://hooks.slack.test/example")
    def test_slack_send_waits_for_successful_delivery(self, _get_setting, urlopen):
        response = MagicMock()
        response.getcode.return_value = 200
        response.read.return_value = b"ok"
        urlopen.return_value.__enter__.return_value = response

        self.assertTrue(send_to_slack("Fråga", "Svar"))
        urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
