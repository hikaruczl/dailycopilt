import time
import random

def call_llm(prompt: str, task: str) -> str:
    """
    Placeholder function to simulate a call to a Large Language Model.
    """
    print(f"LLM Service: Received task '{task}' with prompt: '{prompt[:50]}...'")

    # Simulate network latency and processing time
    time.sleep(random.uniform(0.5, 1.5))

    if task == "translate":
        return f"Translated: {prompt}" # Simple echo for now
    elif task == "search":
        return f"Search results for: {prompt}"
    elif task == "analyze_document":
        return f"Analysis of document content: {prompt[:100]}..."
    else:
        return "LLM task not recognized."

if __name__ == '__main__':
    # Example usage
    print(call_llm("Hello, how are you?", "translate"))
    print(call_llm("What is the capital of France?", "search"))
    print(call_llm("This is a test document.", "analyze_document"))
    print(call_llm("This is a test document.", "unknown_task"))
