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

    # Call the LLM service
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

    # For now, we'll just read a small part of the file content as a placeholder
    # In a real scenario, you'd save the file, then process it.
    # For LLM processing, you might extract text first.
    try:
        # Read up to 1MB of the file for safety as a placeholder
        file_content_sample = file.read(1024 * 1024).decode('utf-8', errors='ignore')
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500

    # Simulate document analysis using the LLM service
    # In a real conversion, the prompt would be more specific to the conversion task
    analysis_result = call_llm(prompt=file_content_sample, task="analyze_document")

    return jsonify({
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Document received, placeholder analysis performed.",
        "analysis_preview": analysis_result
    })

@app.route('/api/search', methods=['POST'])
def intelligent_search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request"}), 400

    query_text = data['query']

    # Call the LLM service for search
    search_results = call_llm(prompt=query_text, task="search")

    return jsonify({
        "query": query_text,
        "results": search_results
    })

if __name__ == '__main__':
    # Note: For development, ensure the app is run in a way that the relative import works.
    # This might mean running it as a module from the `backend` directory, e.g., python -m app.main
    app.run(debug=True, port=5000)
