import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .llm_factory import get_llm_service
# Removed: from .llm_service import call_llm

# Load .env file from backend directory (e.g., backend/.env)
# __file__ is main.py, dirname is app/, dirname(dirname()) is backend/
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if not load_dotenv(dotenv_path=dotenv_path):
    # This print is for server-side logging. Actual user feedback should be through API responses.
    print(f"Warning: Could not load .env file from {dotenv_path}. LLM_PROVIDER and API keys must be set directly in environment if .env is not used.")
# Note: llm_factory.py and llm_openai.py also call load_dotenv for their __main__ examples,
# but it's good practice for the main app to ensure it's loaded early.
# load_dotenv doesn't overwrite existing env vars by default.

app = Flask(__name__)

@app.route('/')
def home():
    return "Backend server is running!"

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    if not data or 'text' not in data or 'target_language' not in data:
        return jsonify({"error": "Missing 'text' or 'target_language' in request"}), 400

    text_to_translate = data['text']
    target_language = data['target_language']
    # The source_language parameter from AbstractLLMService.translate is not used here yet.
    # Could be added as an optional field in the JSON payload if needed.

    try:
        llm_service = get_llm_service()
        translated_text_content = llm_service.translate(
            text=text_to_translate,
            target_language=target_language
            # source_language="auto" # Could be passed if available
        )

        return jsonify({
            "original_text": text_to_translate,
            "target_language": target_language,
            "translated_text": translated_text_content
        })
    except Exception as e:
        print(f"Error during translation: {e}") # Server-side log
        return jsonify({"error": f"LLM service error: {str(e)}"}), 500

@app.route('/api/convert-document', methods=['POST'])
def convert_document_format():
    if 'document' not in request.files:
        return jsonify({"error": "No document file provided"}), 400

    file = request.files['document']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename
    _ , file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()

    prompt_content = ""
    max_file_size_bytes = 2 * 1024 * 1024 # 2MB limit for text extraction
    supported_text_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.csv', '.json', '.xml']

    if file_extension in supported_text_extensions:
        try:
            file_bytes = file.read(max_file_size_bytes + 1)
            if len(file_bytes) > max_file_size_bytes:
                prompt_content = f"File content is too large (over {max_file_size_bytes // (1024*1024)}MB). Processing only the first {max_file_size_bytes // (1024*1024)}MB.\n\n"
                file_bytes = file_bytes[:max_file_size_bytes]
            prompt_content += file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            prompt_content = f"Could not decode the file content as UTF-8 for '{filename}'. It might be a binary file or use a different text encoding."
        except Exception as e:
            return jsonify({"error": f"Error reading file '{filename}': {str(e)}"}), 500
    else:
        prompt_content = (
            f"Cannot automatically extract text from '{filename}' (type: '{file_extension}'). "
            "This service currently supports text-based files like .txt, .md, .py, .js, .html, .css, .csv, .json, .xml. "
            "Full processing for other file types like PDF or DOCX is not yet implemented."
        )

    try:
        llm_service = get_llm_service()
        analysis_result_content = llm_service.analyze_text(
            text=prompt_content,
            analysis_type="summary" # Defaulting to summary for now
        )

        return jsonify({
            "filename": filename,
            "content_type": file.content_type,
            "file_extension": file_extension,
            "message": "Document processed for analysis.",
            "analysis_preview": analysis_result_content
        })
    except Exception as e:
        print(f"Error during document analysis: {e}") # Server-side log
        return jsonify({"error": f"LLM service error: {str(e)}"}), 500

@app.route('/api/search', methods=['POST'])
def intelligent_search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request"}), 400

    query_text = data['query']

    try:
        llm_service = get_llm_service()
        search_results_content = llm_service.generate_response(prompt=query_text)

        return jsonify({
            "query": query_text,
            "results": search_results_content
        })
    except Exception as e:
        print(f"Error during intelligent search: {e}") # Server-side log
        return jsonify({"error": f"LLM service error: {str(e)}"}), 500

if __name__ == '__main__':
    # Note: For development, ensure the app is run in a way that the relative import works.
    # This might mean running it as a module from the `backend` directory, e.g., python3 -m app.main
    # The debug=True setting is useful for development but should be False in production.
    app.run(debug=True, port=5000)
