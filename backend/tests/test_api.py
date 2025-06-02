import unittest
from unittest.mock import patch
import json

# Add backend directory to sys.path to find 'app'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app # Your Flask app instance

class TestAPI(unittest.TestCase):

    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        # Propagate exceptions to the test client
        app.config['TESTING'] = True
        app.config['DEBUG'] = False # Ensure debug is False for testing typical error handling

    @patch('app.main.call_llm') # Patch call_llm where it's used in app.main
    def test_translate_api_success(self, mock_call_llm):
        mock_call_llm.return_value = "Texte traduit"
        payload = {"text": "Hello", "target_language": "French"}
        response = self.app.post('/api/translate',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['translated_text'], "Texte traduit")
        mock_call_llm.assert_called_once_with(
            prompt="Translate the following text to French: Hello",
            task="translate"
        )

    def test_translate_api_missing_fields(self):
        payload = {"text": "Hello"} # Missing target_language
        response = self.app.post('/api/translate',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("Missing 'text' or 'target_language'", data['error'])

    @patch('app.main.call_llm')
    def test_search_api_success(self, mock_call_llm):
        mock_call_llm.return_value = "Search results for AI"
        payload = {"query": "What is AI?"}
        response = self.app.post('/api/search',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['results'], "Search results for AI")
        mock_call_llm.assert_called_once_with(prompt="What is AI?", task="search")

    def test_search_api_missing_query(self):
        payload = {} # Missing query
        response = self.app.post('/api/search',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("Missing 'query'", data['error'])

    @patch('app.main.call_llm')
    def test_convert_document_api_success(self, mock_call_llm):
        mock_call_llm.return_value = "Document analysis complete."
        # Simulate file upload
        from io import BytesIO
        payload = {
            'document': (BytesIO(b"This is a test txt file."), 'test.txt')
        }
        # For file uploads, content_type should be multipart/form-data
        response = self.app.post('/api/convert-document',
                                 data=payload,
                                 content_type='multipart/form-data')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['analysis_preview'], "Document analysis complete.")
        self.assertEqual(data['filename'], 'test.txt')
        # Ensure call_llm was called with the content of the file
        mock_call_llm.assert_called_once_with(prompt="This is a test txt file.", task="analyze_document")

    def test_convert_document_api_no_file(self):
        response = self.app.post('/api/convert-document',
                                 content_type='multipart/form-data') # No file in data
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("No document file provided", data['error'])

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Backend server is running!")

if __name__ == '__main__':
    unittest.main()
