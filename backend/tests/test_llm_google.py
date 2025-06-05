import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add backend directory to sys.path to find 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm_google import GoogleLLMService
# Import google.generativeai itself to mock specific exceptions if needed,
# or to type hint for mocked objects if strict about that.
# For now, we'll primarily mock at the point of genai.configure and genai.GenerativeModel
import google.generativeai as genai # Used for genai.GenerativeModel and potentially errors

class TestGoogleLLMService(unittest.TestCase):

    def setUp(self):
        self.dummy_api_key = "test_google_api_key"
        # It's important that genai.configure is callable without error in tests,
        # or that it's patched if it makes actual checks during configure.
        # For these tests, we'll assume genai.configure itself doesn't fail with a dummy key
        # and we primarily mock the model generation part.

    # Patch genai.configure and genai.GenerativeModel
    # Patching multiple targets requires careful handling or nested patches.
    # Let's patch 'google.generativeai.GenerativeModel' as it's the primary interaction point after configure.
    # We also need to ensure 'genai.configure' doesn't cause issues.
    @patch('google.generativeai.configure') # Mock configure to prevent actual configuration
    @patch('google.generativeai.GenerativeModel') # Mock the GenerativeModel class
    def test_translate_success(self, MockGenerativeModel, mock_genai_configure):
        # Configure the mock model instance
        mock_model_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "Translated text from Google"
        mock_model_instance.generate_content.return_value = mock_response

        service = GoogleLLMService(api_key=self.dummy_api_key)
        response = service.translate("Hello", "Spanish")

        self.assertEqual(response, "Translated text from Google")
        mock_genai_configure.assert_called_once_with(api_key=self.dummy_api_key)
        MockGenerativeModel.assert_called_once_with("gemini-1.5-flash-latest") # Default model
        mock_model_instance.generate_content.assert_called_once()
        # Check the prompt structure passed to generate_content
        args, _ = mock_model_instance.generate_content.call_args
        self.assertIn("Translate the following text", args[0][0]) # args[0] is the list of prompt_parts
        self.assertIn("to Spanish", args[0][0])
        self.assertIn("Hello", args[0][0])

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_text_summary_success(self, MockGenerativeModel, mock_genai_configure):
        mock_model_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "This is a Google summary."
        mock_model_instance.generate_content.return_value = mock_response

        service = GoogleLLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Some long text.", "summary")

        self.assertEqual(response, "This is a Google summary.")
        mock_genai_configure.assert_called_once_with(api_key=self.dummy_api_key)
        MockGenerativeModel.assert_called_once_with("gemini-1.5-flash-latest")
        mock_model_instance.generate_content.assert_called_once()
        args, _ = mock_model_instance.generate_content.call_args
        self.assertIn("Summarize the following text concisely:", args[0][0])

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_text_keywords_success(self, MockGenerativeModel, mock_genai_configure):
        mock_model_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "google_keyword1, google_keyword2"
        mock_model_instance.generate_content.return_value = mock_response

        service = GoogleLLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Some long text for keywords.", "keywords")
        self.assertEqual(response, "google_keyword1, google_keyword2")

    def test_analyze_text_unsupported_type(self):
        service = GoogleLLMService(api_key=self.dummy_api_key) # configure is not called if method isn't
        with self.assertRaises(NotImplementedError):
            service.analyze_text("Some text.", "sentiment") # Assuming 'sentiment' is not in GEMINI_ANALYSIS_PROMPTS

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_response_success(self, MockGenerativeModel, mock_genai_configure):
        mock_model_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "Google generated response."
        mock_model_instance.generate_content.return_value = mock_response

        service = GoogleLLMService(api_key=self.dummy_api_key)
        response = service.generate_response("User prompt for Google")
        self.assertEqual(response, "Google generated response.")

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_llm_api_error_handling(self, MockGenerativeModel, mock_genai_configure):
        mock_model_instance = MockGenerativeModel.return_value
        # Simulate an API error from google.generativeai
        # The specific exception type might vary, using a generic one for mock
        mock_model_instance.generate_content.side_effect = Exception("Google API Error")

        service = GoogleLLMService(api_key=self.dummy_api_key)
        # The _generate_content_with_retry re-raises as ConnectionError
        with self.assertRaisesRegex(ConnectionError, "Gemini API call failed after .* attempts: Google API Error"):
            service.translate("Hello", "French")

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_llm_empty_response_text_handling(self, MockGenerativeModel, mock_genai_configure):
        mock_model_instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = None # Simulate empty text in response
        mock_response.prompt_feedback = "BLOCK_REASON_SAFETY" # Example feedback
        mock_model_instance.generate_content.return_value = mock_response

        service = GoogleLLMService(api_key=self.dummy_api_key)
        # The _generate_content_with_retry re-raises as ValueError
        with self.assertRaisesRegex(ValueError, "Gemini response missing 'text' attribute or content after .* attempts. Feedback: BLOCK_REASON_SAFETY"):
            service.translate("Risky prompt", "French")


    def test_init_no_api_key(self):
        with self.assertRaisesRegex(ValueError, "Google API key not provided."):
            GoogleLLMService(api_key=None)
        with self.assertRaisesRegex(ValueError, "Google API key not provided."):
            GoogleLLMService(api_key="")

    @patch('google.generativeai.configure', side_effect=Exception("Config Error"))
    def test_init_configure_failure(self, mock_genai_configure):
        with self.assertRaisesRegex(ConnectionError, "Failed to configure Google GenAI client: Config Error"):
            GoogleLLMService(api_key=self.dummy_api_key)

if __name__ == '__main__':
    unittest.main()
