import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add backend directory to sys.path to find 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm_qwen import QwenLLMService
# Import dashscope to mock its Generation.call method and Role attribute
import dashscope

class TestQwenLLMService(unittest.TestCase):

    def setUp(self):
        self.dummy_api_key = "test_qwen_api_key"
        # We will patch dashscope.Generation.call and potentially dashscope.api_key assignment
        # or ensure that setting dashscope.api_key in __init__ is testable.

    # Patch dashscope.Generation.call, which is the core interaction point
    # Also patch dashscope.api_key to control its value during tests if necessary,
    # or ensure QwenLLMService constructor correctly sets it for the mocked calls.
    # For simplicity, let's focus on mocking Generation.call and assume api_key setup in QwenLLMService works.
    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock) # Mock the module-level api_key attribute
    def test_translate_success(self, mock_dashscope_api_key_attr, mock_generation_call):
        # Configure the mock response from dashscope.Generation.call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = MagicMock()
        mock_response.output.choices = [MagicMock()]
        mock_response.output.choices[0].message = MagicMock()
        mock_response.output.choices[0].message.content = "Translated text from Qwen"
        mock_generation_call.return_value = mock_response

        service = QwenLLMService(api_key=self.dummy_api_key) # This sets dashscope.api_key
        response = service.translate("Hello", "Chinese")

        self.assertEqual(response, "Translated text from Qwen")
        # Verify dashscope.api_key was set by constructor (indirectly, or directly if we didn't mock it)
        # For this mocked setup, we assume it was set. We can check mock_dashscope_api_key_attr if it were assigned via the mock.
        # More importantly, check that Generation.call was called
        mock_generation_call.assert_called_once()
        args, kwargs = mock_generation_call.call_args
        self.assertEqual(kwargs['model'], "qwen-turbo") # Default model
        self.assertEqual(kwargs['messages'][-1]['role'], dashscope.api_entities.dashscope_response.Role.USER)
        self.assertIn("Translate the following text", kwargs['messages'][-1]['content'])
        self.assertIn("to Chinese", kwargs['messages'][-1]['content'])
        self.assertIn("Hello", kwargs['messages'][-1]['content'])


    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock)
    def test_analyze_text_summary_success(self, mock_api_key_attr, mock_generation_call):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = MagicMock()
        mock_response.output.choices = [MagicMock()]
        mock_response.output.choices[0].message = MagicMock()
        mock_response.output.choices[0].message.content = "This is a Qwen summary."
        mock_generation_call.return_value = mock_response

        service = QwenLLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Some very long text to summarize.", "summary")

        self.assertEqual(response, "This is a Qwen summary.")
        mock_generation_call.assert_called_once()
        args, kwargs = mock_generation_call.call_args
        self.assertIn("Summarize the following text concisely:", kwargs['messages'][-1]['content'])

    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock)
    def test_analyze_text_keywords_success(self, mock_api_key_attr, mock_generation_call):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = MagicMock()
        mock_response.output.choices = [MagicMock()]
        mock_response.output.choices[0].message = MagicMock()
        mock_response.output.choices[0].message.content = "qwen_keyword1, qwen_keyword2"
        mock_generation_call.return_value = mock_response

        service = QwenLLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Text for Qwen keywords.", "keywords")
        self.assertEqual(response, "qwen_keyword1, qwen_keyword2")

    def test_analyze_text_unsupported_type(self):
        service = QwenLLMService(api_key=self.dummy_api_key)
        with self.assertRaises(NotImplementedError):
            service.analyze_text("Some text.", "sentiment_analysis_qwen")

    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock)
    def test_generate_response_success(self, mock_api_key_attr, mock_generation_call):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = MagicMock()
        mock_response.output.choices = [MagicMock()]
        mock_response.output.choices[0].message = MagicMock()
        mock_response.output.choices[0].message.content = "Qwen generated response."
        mock_generation_call.return_value = mock_response

        service = QwenLLMService(api_key=self.dummy_api_key)
        response = service.generate_response("User prompt for Qwen")
        self.assertEqual(response, "Qwen generated response.")

    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock)
    def test_llm_api_error_handling(self, mock_api_key_attr, mock_generation_call):
        # Simulate an API error (non-200 status)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.code = "InternalError"
        mock_response.message = "Qwen API System Error"
        mock_generation_call.return_value = mock_response

        service = QwenLLMService(api_key=self.dummy_api_key)
        with self.assertRaisesRegex(ConnectionError, "Qwen API call failed after .* attempts: .*Qwen API System Error"):
            service.translate("Hello", "French")

    @patch('dashscope.Generation.call')
    @patch('dashscope.api_key', new_callable=MagicMock)
    def test_llm_sdk_exception_handling(self, mock_api_key_attr, mock_generation_call):
        # Simulate an SDK-level exception (e.g., network error)
        mock_generation_call.side_effect = Exception("Dashscope SDK Network Error")

        service = QwenLLMService(api_key=self.dummy_api_key)
        with self.assertRaisesRegex(ConnectionError, "Qwen API call failed after .* attempts: Dashscope SDK Network Error"):
            service.analyze_text("Some text for analysis")

    def test_init_no_api_key(self):
        with self.assertRaisesRegex(ValueError, "Qwen \(Dashscope\) API key not provided to service constructor."):
            QwenLLMService(api_key=None)
        with self.assertRaisesRegex(ValueError, "Qwen \(Dashscope\) API key not provided to service constructor."):
            QwenLLMService(api_key="")

    @patch('dashscope.api_key', new_callable=MagicMock) # Mock to check its value
    def test_init_api_key_assignment(self, mock_api_key_attr):
        # This test is a bit tricky because dashscope.api_key is a global module attribute.
        # The QwenLLMService constructor sets it.
        # We want to ensure it's set.
        # A more direct way might be to check dashscope.api_key after instantiation.
        # However, tests should be isolated.
        # For now, we assume if no error, it was set. A failure in other tests would indicate an issue.
        # A dedicated test might involve inspecting the mock_api_key_attr if it were used for assignment,
        # or checking dashscope.api_key directly if we control its state carefully across tests.
        # Given the current QwenLLMService structure, the constructor directly assigns to dashscope.api_key.
        # We can assert it was set.
        original_dashscope_key = dashscope.api_key # Store original
        try:
            service = QwenLLMService(api_key=self.dummy_api_key)
            self.assertEqual(dashscope.api_key, self.dummy_api_key)
        finally:
            dashscope.api_key = original_dashscope_key # Restore

if __name__ == '__main__':
    unittest.main()
