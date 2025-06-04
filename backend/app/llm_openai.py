import os
from openai import OpenAI, APIError
from .llm_interfaces import AbstractLLMService

class OpenAILLMService(AbstractLLMService):
    """
    LLM Service implementation for OpenAI models.
    """

    def __init__(self, api_key: str, **kwargs):
        """
        Initializes the OpenAI service client.

        Args:
            api_key (str): The OpenAI API key.
            **kwargs: Additional options (not currently used by OpenAI client directly here).
        """
        super().__init__(api_key, **kwargs) # Though AbstractLLMService.__init__ is simple
        if not api_key:
            raise ValueError("OpenAI API key not provided.")

        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            # Log this error appropriately in a real application
            print(f"Error initializing OpenAI client: {e}")
            raise ConnectionError(f"Failed to initialize OpenAI client: {e}")

    def _get_model(self, model_preference: str = None) -> str:
        """ Helper to determine model, can be expanded later """
        # For now, default to gpt-3.5-turbo, allow override if needed by specific tasks
        return model_preference if model_preference else "gpt-3.5-turbo"

    def translate(self, text: str, target_language: str, source_language: str = "auto", model_preference: str = None) -> str:
        """
        Translate text using OpenAI.
        """
        model = self._get_model(model_preference)
        system_message = f"You are a helpful translation assistant. Translate the following text from {source_language if source_language != 'auto' else 'the detected language'} to {target_language}."
        user_message = text

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=250  # Adjust as needed
            )
            if completion.choices and len(completion.choices) > 0:
                message = completion.choices[0].message
                if message and message.content:
                    return message.content.strip()
            return "Error: LLM returned no valid translation."
        except APIError as e:
            self._handle_api_error(e) # This will re-raise a generic Exception
        except Exception as e: # Catch other potential errors
            print(f"An unexpected error occurred during OpenAI translation: {e}")
            raise

    def analyze_text(self, text: str, analysis_type: str = "summary", model_preference: str = None) -> str:
        """
        Analyze text using OpenAI (e.g., summarize, extract keywords).
        """
        model = self._get_model(model_preference)

        if analysis_type == "summary":
            system_message = "You are a helpful assistant. Summarize the following text concisely."
        elif analysis_type == "keywords":
            system_message = "You are a helpful assistant. Extract the main keywords from the following text, comma-separated."
        # Add more analysis types as needed
        else:
            raise NotImplementedError(f"Analysis type '{analysis_type}' is not supported by OpenAI service.")

        user_message = text[:8000] # Limit prompt length for safety/cost with OpenAI

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5, # Lower temperature for more factual tasks
                max_tokens=300   # Adjust for expected summary/keyword list length
            )
            if completion.choices and len(completion.choices) > 0:
                message = completion.choices[0].message
                if message and message.content:
                    return message.content.strip()
            return f"Error: LLM returned no valid {analysis_type}."
        except APIError as e:
            self._handle_api_error(e)
        except Exception as e:
            print(f"An unexpected error occurred during OpenAI text analysis: {e}")
            raise

    def generate_response(self, prompt: str, context: str = None, model_preference: str = None) -> str:
        """
        Generate a response to a prompt using OpenAI (for search/Q&A).
        """
        model = self._get_model(model_preference)
        system_message = "You are an intelligent assistant. Provide a concise and relevant answer to the user's query."

        user_messages = []
        if context:
            # Simple way to add context, could be more sophisticated
            user_messages.append({"role": "system", "content": f"Consider the following context: {context[:4000]}"})
        user_messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message}
                ] + user_messages, # Combine system message with user prompt(+context)
                temperature=0.7,
                max_tokens=350
            )
            if completion.choices and len(completion.choices) > 0:
                message = completion.choices[0].message
                if message and message.content:
                    return message.content.strip()
            return "Error: LLM returned no valid response."
        except APIError as e:
            self._handle_api_error(e)
        except Exception as e:
            print(f"An unexpected error occurred during OpenAI response generation: {e}")
            raise

if __name__ == '__main__':
    # Example Usage (Requires OPENAI_API_KEY to be set in environment or .env for load_dotenv to work)
    # For direct testing, ensure .env is loaded if API key is not in direct environment
    from dotenv import load_dotenv
    # Assuming .env is in backend/, and this file is in backend/app/
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found. Skipping OpenAILLMService example.")
    else:
        try:
            openai_service = OpenAILLMService(api_key=api_key)

            print("--- Translation Example (OpenAI) ---")
            translation = openai_service.translate("Hello, how are you today?", "French")
            print(f"Translation: {translation}")

            print("\n--- Analysis Example (OpenAI) ---")
            analysis = openai_service.analyze_text("Python is a versatile programming language. It is known for its readability and large standard library.", "summary")
            print(f"Summary: {analysis}")

            keywords = openai_service.analyze_text("Python is a versatile programming language. It is known for its readability and large standard library.", "keywords")
            print(f"Keywords: {keywords}")

            print("\n--- Generation Example (OpenAI) ---")
            response = openai_service.generate_response("What is the capital of France?")
            print(f"Response: {response}")

        except ConnectionError as e:
            print(f"Connection Error: {e}")
        except ValueError as e:
            print(f"Value Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
