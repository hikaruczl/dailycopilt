import unittest
from unittest.mock import patch, MagicMock
import os

# Ensure the app module can be imported
import sys
# Add the parent directory (backend) to sys.path to allow direct import of app.llm_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import llm_service # Now this should work

class TestLLMService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Store original OPENAI_API_KEY value and set a dummy one for tests
        cls.original_api_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "test_api_key" # Needs to be non-empty for client init
        # Reload llm_service to re-initialize client with the test key if client is module-level
        # For this structure, llm_service.client would be initialized when llm_service is imported.
        # If client is None due to no key, some tests might behave differently.
        # A robust way is to ensure client can be re-initialized or mocked directly.
        # For simplicity, we assume the client will re-evaluate os.environ.get or is None.
        # If llm_service.client is initialized at module load, this reload is crucial.
        import importlib
        importlib.reload(llm_service)


    @classmethod
    def tearDownClass(cls):
        # Restore original OPENAI_API_KEY
        if cls.original_api_key is None:
            del os.environ["OPENAI_API_KEY"]
        else:
            os.environ["OPENAI_API_KEY"] = cls.original_api_key
        # Reload llm_service again to restore original client state if necessary
        import importlib
        importlib.reload(llm_service)

    # Patch the OpenAI client's chat.completions.create method
    @patch('openai.OpenAI')
    def test_call_llm_translate_success(self, MockOpenAI):
        # Configure the mock client and its response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Translated text"

        # Create a mock instance of the OpenAI client
        mock_openai_instance = MockOpenAI.return_value
        mock_openai_instance.chat.completions.create.return_value = mock_completion

        # Override the client in llm_service with our mocked instance
        with patch('app.llm_service.client', mock_openai_instance):
            prompt = "Translate this to Spanish: Hello"
            response = llm_service.call_llm(prompt, "translate")

            self.assertEqual(response, "Translated text")
            mock_openai_instance.chat.completions.create.assert_called_once()
            args, kwargs = mock_openai_instance.chat.completions.create.call_args
            self.assertEqual(kwargs['model'], "gpt-3.5-turbo")
            self.assertEqual(kwargs['messages'][-1]['content'], prompt)
            self.assertEqual(kwargs['messages'][0]['content'], "You are a helpful translation assistant.")

    @patch('openai.OpenAI')
    def test_call_llm_search_success(self, MockOpenAI):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Search result"
        mock_openai_instance = MockOpenAI.return_value
        mock_openai_instance.chat.completions.create.return_value = mock_completion

        with patch('app.llm_service.client', mock_openai_instance):
            prompt = "What is AI?"
            response = llm_service.call_llm(prompt, "search")

            self.assertEqual(response, "Search result")
            mock_openai_instance.chat.completions.create.assert_called_once()
            args, kwargs = mock_openai_instance.chat.completions.create.call_args
            self.assertEqual(kwargs['messages'][-1]['content'], f"Search or answer based on the following query: {prompt}")

    @patch('openai.OpenAI')
    def test_call_llm_analyze_document_success(self, MockOpenAI):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Document analysis"
        mock_openai_instance = MockOpenAI.return_value
        mock_openai_instance.chat.completions.create.return_value = mock_completion

        with patch('app.llm_service.client', mock_openai_instance):
            prompt = "This is a document."
            response = llm_service.call_llm(prompt, "analyze_document")

            self.assertEqual(response, "Document analysis")
            mock_openai_instance.chat.completions.create.assert_called_once()
            args, kwargs = mock_openai_instance.chat.completions.create.call_args
            # Check only a part of the prompt for analyze_document due to potential truncation in llm_service
            self.assertIn(prompt[:2000], kwargs['messages'][-1]['content'])


    @patch('openai.OpenAI')
    def test_call_llm_api_error(self, MockOpenAI):
        # Configure the mock client to raise an APIError
        mock_openai_instance = MockOpenAI.return_value
        mock_openai_instance.chat.completions.create.side_effect = llm_service.APIError("API Error", request=MagicMock(), body=None)

        with patch('app.llm_service.client', mock_openai_instance):
            response = llm_service.call_llm("Test prompt", "translate")
            self.assertTrue("Error interacting with LLM: API Error" in response)

    def test_call_llm_unrecognized_task(self):
        # This test does not need mocking of OpenAI client as it should be handled before API call
        response = llm_service.call_llm("Test prompt", "unknown_task")
        self.assertEqual(response, "LLM task not recognized by the new service.")

    def test_call_llm_no_client(self):
        # Test behavior when client is None (e.g., API key not set and client failed to initialize)
        with patch('app.llm_service.client', None):
            response = llm_service.call_llm("Test prompt", "translate")
            self.assertEqual(response, "Error: OpenAI client not initialized. Is OPENAI_API_KEY set?")

if __name__ == '__main__':
    unittest.main()
