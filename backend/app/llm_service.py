# OpenAI API Key Requirement:
# This service requires an OpenAI API key to function.
# The API key should be placed in a file named .env in the 'backend' directory.
# Create this file by copying backend/.env.example to backend/.env and entering your key.
# Example content for backend/.env:
# OPENAI_API_KEY='your_actual_api_key_here'
#
# The key is loaded from this .env file. If an environment variable OPENAI_API_KEY is
# also set, it might take precedence depending on the system and python-dotenv behavior (usually, existing env vars are not overwritten by default).
# Ensure this key is kept secret and the .env file is not committed to version control.

import os
from openai import OpenAI, APIError
from dotenv import load_dotenv

# Construct the path to the .env file located in the backend directory
# __file__ is llm_service.py, dirname(__file__) is app/, dirname(dirname()) is backend/
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Initialize the OpenAI client.
# It's good practice to handle the API key not being set.
try:
    api_key_value = os.environ.get("OPENAI_API_KEY")
    if not api_key_value:
        print("Warning: OPENAI_API_KEY not found in environment or .env file. LLM calls will fail.")
        client = None
    else:
        client = OpenAI(api_key=api_key_value)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None # Ensure client is None if initialization fails

def call_llm(prompt: str, task: str) -> str:
    """
    Function to call the OpenAI LLM.
    """
    if not client:
        return "Error: OpenAI client not initialized. Is OPENAI_API_KEY set?"

    print(f"LLM Service: Received task '{task}' with prompt: '{prompt[:70]}...'")

    try:
        if task == "translate":
            # The prompt for translation should ideally be structured with original text and target language.
            # Assuming the prompt is already formatted like "Translate the following text to {target_language}: {text_to_translate}"
            system_message = "You are a helpful translation assistant."
            user_message = prompt
        elif task == "search":
            system_message = "You are an intelligent search assistant. Provide concise and relevant search results or answers."
            user_message = f"Search or answer based on the following query: {prompt}"
        elif task == "analyze_document":
            system_message = "You are a document analysis assistant. Summarize or provide key insights from the provided text."
            user_message = f"Analyze the following document content: {prompt[:2000]}" # Limit prompt length for safety/cost
        else:
            return "LLM task not recognized by the new service."

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or consider "gpt-4o-mini" or other models
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7, # Adjust for creativity vs. determinism
            max_tokens=250  # Adjust based on expected output length
        )

        # Enhanced response access
        if completion.choices and len(completion.choices) > 0:
            message = completion.choices[0].message
            if message and message.content:
                return message.content.strip()
            else:
                return "Error: LLM returned an empty message content."
        else:
            return "Error: LLM returned no choices."

    except APIError as e:
        print(f"OpenAI API Error: {e}")
        return f"Error interacting with LLM: {e}"
    except Exception as e:
        print(f"An unexpected error occurred in call_llm: {e}")
        return f"An unexpected error occurred: {str(e)}"

if __name__ == '__main__':
    # Example Usage (Requires OPENAI_API_KEY to be set in environment or .env file)
    if not os.environ.get("OPENAI_API_KEY"): # This check remains valid as dotenv loads it into os.environ
        print("Cannot run examples: OPENAI_API_KEY environment variable is not set directly or via backend/.env.")
    else:
        print("Attempting example LLM calls...")
        print("\n--- Translation Example ---")
        translation_prompt = "Translate the following text to French: Hello, how are you today?"
        print(f"Input: {translation_prompt}")
        print(f"Output: {call_llm(translation_prompt, 'translate')}")

        print("\n--- Search Example ---")
        search_prompt = "What is the main benefit of using a version control system like Git?"
        print(f"Input: {search_prompt}")
        print(f"Output: {call_llm(search_prompt, 'search')}")

        print("\n--- Document Analysis Example ---")
        doc_content = "Python is a versatile and widely-used programming language known for its readability and extensive libraries. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming. Python's simple syntax makes it an excellent choice for beginners, while its power and flexibility cater to the needs of experienced developers in fields like web development, data science, artificial intelligence, and scientific computing."
        print(f"Input (first 70 chars): {doc_content[:70]}...")
        print(f"Output: {call_llm(doc_content, 'analyze_document')}")
