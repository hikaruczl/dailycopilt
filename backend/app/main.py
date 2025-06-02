import os
from flask import Flask, request, jsonify
from .llm_service import call_llm # Assuming llm_service is in the same directory

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

    # Construct a prompt for the LLM
    prompt = f"Translate the following text to {target_language}: {text_to_translate}"

    # The llm_service.call_llm function for "translate" expects a prompt
    # that includes the text and target language directly.
    translated_text = call_llm(prompt=prompt, task="translate")

    return jsonify({
        "original_text": text_to_translate,
        "target_language": target_language,
        "translated_text": translated_text
    })

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
            # Read up to max_file_size_bytes + 1 to check if it exceeds the limit
            file_bytes = file.read(max_file_size_bytes + 1)
            if len(file_bytes) > max_file_size_bytes:
                prompt_content = f"File content is too large (over {max_file_size_bytes // (1024*1024)}MB). Processing only the first {max_file_size_bytes // (1024*1024)}MB.\n\n"
                file_bytes = file_bytes[:max_file_size_bytes]

            prompt_content += file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            prompt_content = f"Could not decode the file content as UTF-8. It might be a binary file or use a different text encoding."
        except Exception as e:
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500
    else:
        prompt_content = (
            f"Cannot automatically extract text from '{file_extension}' files. "
            "This service currently supports text-based files like .txt, .md, .py, .js, .html, .css, .csv, .json, .xml. "
            "Full processing for file types like PDF or DOCX is not yet implemented."
        )

    # The llm_service.call_llm function for "analyze_document" will prepend
    # specific instructions to this content.
    analysis_result = call_llm(prompt=prompt_content, task="analyze_document")

    return jsonify({
        "filename": filename,
        "content_type": file.content_type,
        "file_extension": file_extension,
        "message": "Document processed for analysis.",
        "analysis_preview": analysis_result
    })

@app.route('/api/search', methods=['POST'])
def intelligent_search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request"}), 400

    query_text = data['query']

    # The llm_service.call_llm function for "search" will prepend
    # specific instructions to this query.
    search_results = call_llm(prompt=query_text, task="search")

    return jsonify({
        "query": query_text,
        "results": search_results
    })

if __name__ == '__main__':
    # Note: For development, ensure the app is run in a way that the relative import works.
    # This might mean running it as a module from the `backend` directory, e.g., python -m app.main
    app.run(debug=True, port=5000)
