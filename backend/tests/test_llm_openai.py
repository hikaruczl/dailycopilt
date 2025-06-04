import unittest
from unittest.mock import patch, MagicMock
import os # Keep for potential path manipulation if needed, or api key checks

# Adjust path for imports if running tests from root or specific test runner context
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm_openai import OpenAILLMService
from openai import APIError # For testing exception handling

class TestOpenAILLMService(unittest.TestCase):

    def setUp(self):
        # Each test will get a fresh service instance with a dummy key
        self.dummy_api_key = "sk-dummy_test_key"
        # We will mock the client *after* instantiation of OpenAILLMService
        # or mock OpenAI() itself before instantiation.
        # Let's try mocking the client on the instance.

    @patch('openai.OpenAI') # Mocks the OpenAI class itself
    def test_translate_success(self, MockOpenAI):
        # Configure the mock OpenAI client instance
        mock_openai_client_instance = MockOpenAI.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Translated text"
        mock_openai_client_instance.chat.completions.create.return_value = mock_completion

        # Instantiate the service; it will use the mocked OpenAI client if MockOpenAI is used right
        service = OpenAILLMService(api_key=self.dummy_api_key)

        response = service.translate("Hello", "Spanish")
        self.assertEqual(response, "Translated text")

        # Check that chat.completions.create was called with correct args
        mock_openai_client_instance.chat.completions.create.assert_called_once()
        _, kwargs = mock_openai_client_instance.chat.completions.create.call_args
        self.assertEqual(kwargs['model'], "gpt-3.5-turbo") # Default model
        self.assertEqual(kwargs['messages'][-1]['content'], "Hello")
        self.assertIn("Spanish", kwargs['messages'][0]['content'])


    @patch('openai.OpenAI')
    def test_analyze_text_summary_success(self, MockOpenAI):
        mock_openai_client_instance = MockOpenAI.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "This is a summary."
        mock_openai_client_instance.chat.completions.create.return_value = mock_completion

        service = OpenAILLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Some long text.", "summary")
        self.assertEqual(response, "This is a summary.")
        mock_openai_client_instance.chat.completions.create.assert_called_once()
        _, kwargs = mock_openai_client_instance.chat.completions.create.call_args
        self.assertIn("Summarize the following text concisely.", kwargs['messages'][0]['content'])

    @patch('openai.OpenAI')
    def test_analyze_text_keywords_success(self, MockOpenAI):
        mock_openai_client_instance = MockOpenAI.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "keyword1, keyword2"
        mock_openai_client_instance.chat.completions.create.return_value = mock_completion

        service = OpenAILLMService(api_key=self.dummy_api_key)
        response = service.analyze_text("Some long text.", "keywords")
        self.assertEqual(response, "keyword1, keyword2")
        mock_openai_client_instance.chat.completions.create.assert_called_once()
        _, kwargs = mock_openai_client_instance.chat.completions.create.call_args
        self.assertIn("Extract the main keywords", kwargs['messages'][0]['content'])


    def test_analyze_text_unsupported_type(self):
        service = OpenAILLMService(api_key=self.dummy_api_key)
        with self.assertRaises(NotImplementedError):
            service.analyze_text("Some text.", "sentiment_analysis")

    @patch('openai.OpenAI')
    def test_generate_response_success(self, MockOpenAI):
        mock_openai_client_instance = MockOpenAI.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Generated response."
        mock_openai_client_instance.chat.completions.create.return_value = mock_completion

        service = OpenAILLMService(api_key=self.dummy_api_key)
        response = service.generate_response("User prompt")
        self.assertEqual(response, "Generated response.")
        mock_openai_client_instance.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_llm_api_error_handling(self, MockOpenAI):
        mock_openai_client_instance = MockOpenAI.return_value
        # Configure the mock to raise APIError for any of the methods
        # Note: The actual APIError constructor might need specific arguments if your version of openai lib is strict.
        # For openai >v1.0, APIError(name="...", status_code=xxx, ...) is more typical.
        # However, the mock just needs to raise an instance of APIError.
        # The 'response' argument for APIError was problematic before, let's use a simple message.
        # The `_handle_api_error` in `OpenAILLMService` catches `APIError as e` and then `raise Exception(f"An error occurred with the LLM provider: {str(e)}")`
        # So the text we check for should match that.
        error_message = "Simulated OpenAI API Error"
        mock_openai_client_instance.chat.completions.create.side_effect = APIError(error_message, response=MagicMock(), body=None)


        service = OpenAILLMService(api_key=self.dummy_api_key)
        with self.assertRaisesRegex(Exception, f"An error occurred with the LLM provider: {error_message}"):
            service.translate("Hello", "French")
        with self.assertRaisesRegex(Exception, f"An error occurred with the LLM provider: {error_message}"):
            service.analyze_text("Some text")
        with self.assertRaisesRegex(Exception, f"An error occurred with the LLM provider: {error_message}"):
            service.generate_response("A prompt")

    def test_init_no_api_key(self):
        with self.assertRaisesRegex(ValueError, "OpenAI API key not provided."):
            OpenAILLMService(api_key=None)
        with self.assertRaisesRegex(ValueError, "OpenAI API key not provided."):
            OpenAILLMService(api_key="")

# if __name__ == '__main__':
#     unittest.main() # Usually run tests via discover
