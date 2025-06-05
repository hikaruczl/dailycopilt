import os
from .llm_interfaces import AbstractLLMService
from .llm_openai import OpenAILLMService
from .llm_google import GoogleLLMService
from .llm_qwen import QwenLLMService # Use the actual QwenLLMService

# All placeholder classes have been removed.

# Global variable to cache the LLM service instance
_llm_service_instance = None

def get_llm_service() -> AbstractLLMService:
    """
    Factory function to get the configured LLM service instance.
    It reads the LLM_PROVIDER and relevant API key from environment variables
    (which should be loaded from .env by python-dotenv in the main app).

    Caches the service instance to avoid re-initialization on every call.
    """
    global _llm_service_instance
    if _llm_service_instance is not None:
        return _llm_service_instance

    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    api_key = None
    service_class = None

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        service_class = OpenAILLMService
    elif provider == "google":
        api_key = os.environ.get("GOOGLE_API_KEY")
        service_class = GoogleLLMService
    elif provider == "qwen":
        api_key = os.environ.get("QWEN_API_KEY")
        service_class = QwenLLMService # Use the actual implementation
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers are 'openai', 'google', 'qwen'.")

    if not api_key:
        raise ValueError(f"API key for {provider} not found. Please set the appropriate environment variable (e.g., OPENAI_API_KEY, GOOGLE_API_KEY, QWEN_API_KEY).")

    if not service_class:
        # This case should ideally be caught by the provider check above,
        # but as a safeguard if a provider is added to .env but not here.
        raise NotImplementedError(f"LLM service for provider '{provider}' is not implemented in the factory.")

    _llm_service_instance = service_class(api_key=api_key)
    return _llm_service_instance

if __name__ == '__main__':
    # Example of using the factory.
    # This requires .env to be loaded or environment variables to be set.
    # For direct testing of this file, you might need to call load_dotenv() here.
    from dotenv import load_dotenv
    # Load from backend/.env
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    print(f"Attempting to get LLM service for provider: {os.environ.get('LLM_PROVIDER')}")

    try:
        service_instance = get_llm_service()
        print(f"Successfully got service: {type(service_instance)}")
        print(service_instance.translate("Hello", "French"))

        # Example of switching provider (by changing env var and clearing cache)
        # This is for demonstration; in a real app, env vars are set at startup.
        print("\n--- Switching provider example (for demo) ---")
        os.environ["LLM_PROVIDER"] = "google"
        os.environ["GOOGLE_API_KEY"] = "fake_google_key" # Ensure key exists for demo
        _llm_service_instance = None # Clear cache
        service_instance_google = get_llm_service()
        print(f"Successfully got service: {type(service_instance_google)}")
        print(service_instance_google.translate("Hello", "German"))

        os.environ["LLM_PROVIDER"] = "qwen" # Switch to Qwen
        os.environ["QWEN_API_KEY"] = "fake_qwen_key" # Ensure key exists
        _llm_service_instance = None # Clear cache
        service_instance_qwen = get_llm_service()
        print(f"Successfully got service: {type(service_instance_qwen)}")
        print(service_instance_qwen.analyze_text("Some document text"))


    except ValueError as e:
        print(f"Configuration Error: {e}")
    except NotImplementedError as e:
        print(f"Implementation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
