import os
import google.generativeai as genai
from .llm_interfaces import AbstractLLMService

# Helper to map analysis types to specific prompts for Gemini
GEMINI_ANALYSIS_PROMPTS = {
    "summary": "Summarize the following text concisely: ",
    "keywords": "Extract the main keywords from the following text, comma-separated: ",
    # Add more analysis types and their specific prompts here
}

class GoogleLLMService(AbstractLLMService):
    """
    LLM Service implementation for Google Gemini models.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initializes the Google Gemini service client.

        Args:
            api_key (str): The Google API key for Gemini.
            **kwargs: Additional options.
        """
        super().__init__(api_key, **kwargs)
        if not api_key:
            raise ValueError("Google API key not provided.")

        try:
            genai.configure(api_key=self.api_key)
            # Model selection can be done per-method or a default here
            # For now, methods will select their model or use a passed preference
        except Exception as e:
            print(f"Error configuring Google GenAI client: {e}")
            raise ConnectionError(f"Failed to configure Google GenAI client: {e}")

    def _get_model_name(self, model_preference: str = None, task_type: str = "general") -> str:
        """ Helper to determine model based on preference or task """
        if model_preference:
            return model_preference

        # Default model (Gemini 1.0 Pro is a good general purpose model)
        # Gemini 1.5 Flash is faster and cheaper, good for many tasks.
        # Consider task_type for more specific defaults if needed in future.
        return "gemini-1.5-flash-latest"


    def _generate_content_with_retry(self, model_name: str, prompt_parts: list, max_retries: int = 1):
        """
        Generates content using the specified Gemini model with basic retry logic.
        The 'prompt_parts' argument should be a list, as expected by model.generate_content().
        """
        model = genai.GenerativeModel(model_name)
        attempts = 0
        last_exception = None
        while attempts <= max_retries:
            try:
                response = model.generate_content(prompt_parts)
                # Add safety check for response structure if needed by specific Gemini versions/models
                if response and hasattr(response, 'text'):
                    return response
                else: # Handle cases where response might be empty or not have 'text' as expected
                    # This could be due to safety settings, blocked prompts, etc.
                    print(f"Gemini API call attempt {attempts + 1} returned an unexpected response structure: {response}")
                    # Check for prompt_feedback if available
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        print(f"Prompt Feedback: {response.prompt_feedback}")
                        # Depending on the feedback, you might not want to retry.
                        # For simplicity here, we'll let it retry or fail through.
                    # If no text and no clear feedback, treat as an issue for retry or failure.
                    # last_exception = ValueError("Gemini response missing 'text' attribute or content.")
                    # For now, let it retry or raise based on outer logic for simplicity if it's not an outright API error.
                    # If it's a specific non-retryable issue (e.g. safety block), this should be handled more gracefully.
                    # For this example, we assume 'text' should usually be there on success.
                    if attempts >= max_retries: # If it's the last attempt and still no text
                         raise ValueError(f"Gemini response missing 'text' attribute or content after {attempts + 1} attempts. Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")


            except Exception as e: # Catching a broad exception, can be refined
                last_exception = e
                print(f"Gemini API call attempt {attempts + 1} failed: {e}")
                attempts += 1
                if attempts > max_retries:
                    print(f"Max retries reached for Gemini API call.")
                    raise ConnectionError(f"Gemini API call failed after {max_retries + 1} attempts: {last_exception}") from last_exception
        # Fallback if loop finishes unexpectedly (should be caught by raise in loop)
        raise ConnectionError("Gemini API call failed due to an unexpected issue in retry logic.")


    def translate(self, text: str, target_language: str, source_language: str = "auto", model_preference: str = None) -> str:
        """
        Translate text using Google Gemini.
        """
        model_name = self._get_model_name(model_preference, task_type="translate")

        source_lang_instruction = f"from {source_language}" if source_language and source_language.lower() != "auto" else "from the detected language"
        prompt = f"Translate the following text {source_lang_instruction} to {target_language}: \"{text}\""

        try:
            response = self._generate_content_with_retry(model_name, [prompt])
            if response and response.text: # Ensure response.text is checked after retry logic
                return response.text.strip()
            # If _generate_content_with_retry now raises on persistent lack of .text, this might not be reached.
            return "Error: Gemini returned no valid translation."
        except Exception as e:
            print(f"An unexpected error occurred during Google translation: {e}")
            # self._handle_api_error(e) # Use if you want the generic error from base class
            raise

    def analyze_text(self, text: str, analysis_type: str = "summary", model_preference: str = None) -> str:
        """
        Analyze text using Google Gemini.
        """
        model_name = self._get_model_name(model_preference, task_type="analyze")

        if analysis_type not in GEMINI_ANALYSIS_PROMPTS:
            raise NotImplementedError(f"Analysis type '{analysis_type}' is not supported by Google Gemini service or not defined in GEMINI_ANALYSIS_PROMPTS.")

        prompt_template = GEMINI_ANALYSIS_PROMPTS[analysis_type]
        full_prompt = prompt_template + text

        try:
            response = self._generate_content_with_retry(model_name, [full_prompt])
            if response and response.text:
                return response.text.strip()
            return f"Error: Gemini returned no valid {analysis_type}."
        except Exception as e:
            print(f"An unexpected error occurred during Google text analysis: {e}")
            raise

    def generate_response(self, prompt: str, context: str = None, model_preference: str = None) -> str:
        """
        Generate a response to a prompt using Google Gemini.
        """
        model_name = self._get_model_name(model_preference, task_type="generate")

        full_prompt_parts = []
        if context:
            full_prompt_parts.append(f"Based on this context: \"{context}\"\n\n")
        full_prompt_parts.append(f"Respond to this query: \"{prompt}\"")

        final_prompt = "".join(full_prompt_parts)

        try:
            response = self._generate_content_with_retry(model_name, [final_prompt])
            if response and response.text:
                return response.text.strip()
            return "Error: Gemini returned no valid response."
        except Exception as e:
            print(f"An unexpected error occurred during Google response generation: {e}")
            raise

if __name__ == '__main__':
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found. Skipping GoogleLLMService example.")
    else:
        try:
            google_service = GoogleLLMService(api_key=api_key)

            print("--- Translation Example (Google Gemini) ---")
            translation = google_service.translate("Hello, how are you today?", "French")
            print(f"Translation: {translation}")

            print("\n--- Analysis Example (Google Gemini) ---")
            summary = google_service.analyze_text("Python is a versatile programming language. It is known for its readability and large standard library.", "summary")
            print(f"Summary: {summary}")

            keywords = google_service.analyze_text("Python is a versatile programming language. It is known for its readability and large standard library.", "keywords")
            print(f"Keywords: {keywords}")

            print("\n--- Generation Example (Google Gemini) ---")
            response = google_service.generate_response("What is the capital of France?")
            print(f"Response: {response}")

        except ConnectionError as e:
            print(f"Connection Error: {e}")
        except ValueError as e:
            print(f"Value Error: {e}")
        except NotImplementedError as e:
            print(f"NotImplementedError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
