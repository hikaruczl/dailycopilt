import os
import dashscope # Alibaba Qwen SDK
from dashscope.api_entities.dashscope_response import Role
from .llm_interfaces import AbstractLLMService

# Helper to map analysis types to specific prompts for Qwen
QWEN_ANALYSIS_PROMPTS = {
    "summary": "Summarize the following text concisely: ",
    "keywords": "Extract the main keywords from the following text, comma-separated: ",
}

class QwenLLMService(AbstractLLMService):
    """
    LLM Service implementation for Alibaba Qwen (Tongyi) models.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initializes the Qwen service.
        The Dashscope SDK primarily uses an API key set as an environment variable (DASHSCOPE_API_KEY).
        This 'api_key' parameter is for interface consistency but also checked.
        The SDK might also be configured directly if preferred: dashscope.api_key = api_key

        Args:
            api_key (str): The Dashscope API key for Qwen.
            **kwargs: Additional options.
        """
        super().__init__(api_key, **kwargs)
        if not api_key:
            raise ValueError("Qwen (Dashscope) API key not provided to service constructor.")

        # Dashscope SDK typically expects DASHSCOPE_API_KEY env var.
        # We can also set it directly:
        dashscope.api_key = self.api_key

        # Check if the key is effectively set for the SDK (optional check)
        if not dashscope.api_key: # or check a specific config if available
             raise ConnectionError("Failed to configure Qwen (Dashscope) client: API key not effectively set.")


    def _get_model_name(self, model_preference: str = None, task_type: str = "general") -> str:
        """ Helper to determine model based on preference or task """
        if model_preference:
            return model_preference
        # Default Qwen model (e.g., qwen-turbo, qwen-plus, qwen-max)
        # qwen-turbo is generally a good starting point.
        return "qwen-turbo"

    def _call_qwen_with_retry(self, model_name: str, messages: list, max_retries: int = 1):
        """
        Calls the Qwen model with retry logic.
        'messages' should be a list of message dicts, e.g., [{"role": "user", "content": "Hello"}]
        """
        attempts = 0
        last_exception = None
        while attempts <= max_retries:
            try:
                response = dashscope.Generation.call(
                    model=model_name,
                    messages=messages,
                    result_format='message',  # Get result in message format
                    # stream=False, # Set to True for streaming
                    # top_p=0.8 # Example of other parameters
                )
                if response.status_code == 200 and response.output and response.output.choices:
                    return response
                else:
                    # Handle non-200 status or unexpected response structure
                    error_message = f"Qwen API call failed with status {response.status_code}. Code: {response.code if hasattr(response, 'code') else 'N/A'}, Message: {response.message if hasattr(response, 'message') else 'N/A'}"
                    print(error_message)
                    last_exception = ValueError(error_message) # Store as last exception
                    # Don't retry on all errors, but for simplicity here we do.
                    # Specific error codes could determine retry eligibility.

            except Exception as e: # Catch SDK errors or network issues
                last_exception = e
                print(f"Qwen API call attempt {attempts + 1} raised an exception: {e}")

            attempts += 1
            if attempts > max_retries:
                print(f"Max retries reached for Qwen API call.")
                raise ConnectionError(f"Qwen API call failed after {max_retries + 1} attempts: {last_exception}") from last_exception

        # Fallback if loop finishes unexpectedly
        raise ConnectionError("Qwen API call failed due to an unexpected issue in retry logic.")


    def translate(self, text: str, target_language: str, source_language: str = "auto", model_preference: str = None) -> str:
        """
        Translate text using Qwen.
        """
        model_name = self._get_model_name(model_preference, task_type="translate")

        source_lang_instruction = f"from {source_language}" if source_language and source_language.lower() != "auto" else "from the detected language"
        # Qwen models are generally good with direct instructions.
        prompt = f"Translate the following text {source_lang_instruction} to {target_language}. Output only the translated text, without any additional explanations or conversation. Text to translate: \"{text}\""

        messages = [{'role': Role.SYSTEM, 'content': 'You are a helpful translation assistant.'},
                    {'role': Role.USER, 'content': prompt}]
        try:
            response = self._call_qwen_with_retry(model_name, messages)
            # Assuming response.output.choices[0].message.content contains the translation
            if response.output.choices[0].message.content:
                return response.output.choices[0].message.content.strip()
            return "Error: Qwen returned no valid translation."
        except Exception as e:
            print(f"An unexpected error occurred during Qwen translation: {e}")
            raise

    def analyze_text(self, text: str, analysis_type: str = "summary", model_preference: str = None) -> str:
        """
        Analyze text using Qwen.
        """
        model_name = self._get_model_name(model_preference, task_type="analyze")

        if analysis_type not in QWEN_ANALYSIS_PROMPTS:
            raise NotImplementedError(f"Analysis type '{analysis_type}' is not supported by Qwen service or not defined in QWEN_ANALYSIS_PROMPTS.")

        prompt_template = QWEN_ANALYSIS_PROMPTS[analysis_type]
        full_prompt = prompt_template + text

        messages = [{'role': Role.SYSTEM, 'content': 'You are a helpful text analysis assistant.'},
                    {'role': Role.USER, 'content': full_prompt}]
        try:
            response = self._call_qwen_with_retry(model_name, messages)
            if response.output.choices[0].message.content:
                return response.output.choices[0].message.content.strip()
            return f"Error: Qwen returned no valid {analysis_type}."
        except Exception as e:
            print(f"An unexpected error occurred during Qwen text analysis: {e}")
            raise

    def generate_response(self, prompt: str, context: str = None, model_preference: str = None) -> str:
        """
        Generate a response to a prompt using Qwen.
        """
        model_name = self._get_model_name(model_preference, task_type="generate")

        user_content = prompt
        if context:
            user_content = f"Context: \"{context}\"\n\nQuery: \"{prompt}\""

        messages = [{'role': Role.SYSTEM, 'content': 'You are an intelligent and helpful assistant.'},
                    {'role': Role.USER, 'content': user_content}]
        try:
            response = self._call_qwen_with_retry(model_name, messages)
            if response.output.choices[0].message.content:
                return response.output.choices[0].message.content.strip()
            return "Error: Qwen returned no valid response."
        except Exception as e:
            print(f"An unexpected error occurred during Qwen response generation: {e}")
            raise

if __name__ == '__main__':
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path) # Load .env from backend directory

    api_key = os.environ.get("QWEN_API_KEY") # Dashscope SDK uses DASHSCOPE_API_KEY
                                           # but we pass QWEN_API_KEY to constructor for consistency.
                                           # The constructor sets dashscope.api_key.

    # For direct testing, you might need to ensure DASHSCOPE_API_KEY is also set if
    # the SDK strictly relies on it despite dashscope.api_key = self.api_key
    # or if some SDK parts read it directly.
    # For now, we assume dashscope.api_key = self.api_key is sufficient.

    if not api_key: # Check the key we are passing to constructor
        print("QWEN_API_KEY (for Dashscope) not found in .env. Skipping QwenLLMService example.")
    else:
        # To be absolutely sure for local testing, also set DASHSCOPE_API_KEY if Qwen SDK needs it
        # os.environ['DASHSCOPE_API_KEY'] = api_key
        print(f"Attempting to use Qwen with API key starting: {api_key[:5]}...")
        try:
            qwen_service = QwenLLMService(api_key=api_key) # This sets dashscope.api_key

            print("--- Translation Example (Qwen) ---")
            translation = qwen_service.translate("Hello, how are you today?", "French")
            print(f"Qwen Translation: {translation}")

            print("\n--- Analysis Example (Qwen) ---")
            summary = qwen_service.analyze_text("Alibaba Cloud's Qwen model is a powerful large language model.", "summary")
            print(f"Qwen Summary: {summary}")

            keywords = qwen_service.analyze_text("The Qwen series includes models of various sizes like Qwen-Turbo, Qwen-Plus, and Qwen-Max.", "keywords")
            print(f"Qwen Keywords: {keywords}")

            print("\n--- Generation Example (Qwen) ---")
            response = qwen_service.generate_response("What are the main features of the Qwen model series?")
            print(f"Qwen Response: {response}")

        except ConnectionError as e:
            print(f"Connection Error: {e}")
        except ValueError as e:
            print(f"Value Error: {e}")
        except NotImplementedError as e:
            print(f"NotImplementedError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
