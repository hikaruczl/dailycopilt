from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import asyncio
from werkzeug.utils import secure_filename

from .config import Config, SUPPORTED_MODELS, AVAILABLE_TOOLS
from .llm_service import llm_service, call_llm
from .tools import tool_registry, tool_executor

app = Flask(__name__)
app.config.from_object(Config)

# 启用CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return jsonify({
        "message": "Daily Copilot Backend API",
        "version": "2.0.0",
        "status": "running",
        "available_endpoints": [
            "/api/models",
            "/api/tools",
            "/api/chat",
            "/api/translate",
            "/api/convert-document",
            "/api/search",
            "/api/code-generation",
            "/api/image-analysis",
            "/api/data-analysis"
        ]
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用的AI模型列表"""
    try:
        available_models = llm_service.get_available_models()
        return jsonify({
            "success": True,
            "models": available_models,
            "default_model": app.config['DEFAULT_MODEL']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """获取可用的工具列表"""
    try:
        tools = tool_registry.get_tool_definitions()
        return jsonify({
            "success": True,
            "tools": tools,
            "available_tools": AVAILABLE_TOOLS
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """通用聊天接口，支持模型选择和工具调用"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400

        message = data['message']
        model = data.get('model', app.config['DEFAULT_MODEL'])
        use_tools = data.get('use_tools', False)
        tools = data.get('tools', [])

        # 异步调用LLM
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(message, model, "general")
        )

        loop.close()

        if response.error:
            return jsonify({"error": response.error}), 500

        result = {
            "success": True,
            "response": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_used": response.tokens_used
        }

        # 如果启用工具调用，处理工具调用
        if use_tools and tools:
            tool_results = tool_executor.execute_tool_calls(tools)
            result["tool_results"] = tool_results

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """翻译文本"""
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify({"error": "Missing 'text' or 'target_language' in request"}), 400

        text_to_translate = data['text']
        target_language = data['target_language']
        model = data.get('model', app.config['DEFAULT_MODEL'])

        # 构建翻译提示词
        prompt = f"请将以下文本翻译成{target_language}，只返回翻译结果：\n{text_to_translate}"

        # 异步调用LLM
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, "translate")
        )

        loop.close()

        if response.error:
            return jsonify({"error": response.error}), 500

        return jsonify({
            "success": True,
            "original_text": text_to_translate,
            "target_language": target_language,
            "translated_text": response.content,
            "model": response.model,
            "provider": response.provider
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/code-generation', methods=['POST'])
def generate_code():
    """代码生成接口"""
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({"error": "Missing 'description' in request"}), 400

        description = data['description']
        language = data.get('language', 'python')
        model = data.get('model', app.config['DEFAULT_MODEL'])

        prompt = f"请根据以下需求生成{language}代码，只返回代码，不要解释：\n{description}"

        # 异步调用LLM
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, "code_generation")
        )

        loop.close()

        if response.error:
            return jsonify({"error": response.error}), 500

        return jsonify({
            "success": True,
            "description": description,
            "language": language,
            "code": response.content,
            "model": response.model,
            "provider": response.provider
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/convert-document', methods=['POST'])
def convert_document_format():
    """文档分析和转换"""
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No document file provided"}), 400

        file = request.files['document']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # 检查文件类型
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({"error": f"File type {file_ext} not supported"}), 400

        # 保存文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 提取文件内容
        content = extract_file_content(file_path, file_ext)

        if not content:
            return jsonify({"error": "Could not extract content from file"}), 400

        model = request.form.get('model', app.config['DEFAULT_MODEL'])
        analysis_type = request.form.get('analysis_type', 'summary')

        # 构建分析提示词
        prompt = f"请分析以下文档内容并提供{analysis_type}：\n{content[:4000]}"  # 限制长度

        # 异步调用LLM
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, "analyze_document")
        )

        loop.close()

        # 清理临时文件
        os.remove(file_path)

        if response.error:
            return jsonify({"error": response.error}), 500

        return jsonify({
            "success": True,
            "filename": filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "analysis_type": analysis_type,
            "analysis_result": response.content,
            "model": response.model,
            "provider": response.provider
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_file_content(file_path: str, file_ext: str) -> str:
    """提取文件内容"""
    try:
        if file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext == 'pdf':
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        elif file_ext in ['docx', 'doc']:
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return ""
    except Exception as e:
        print(f"Error extracting content: {e}")
        return ""

@app.route('/api/search', methods=['POST'])
def intelligent_search():
    """智能搜索接口"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' in request"}), 400

        query_text = data['query']
        model = data.get('model', app.config['DEFAULT_MODEL'])
        use_web_search = data.get('use_web_search', True)

        # 如果启用网页搜索工具
        if use_web_search:
            search_result = tool_registry.call_tool('web_search', query=query_text)
            if search_result.get('success'):
                web_info = search_result['result']
                prompt = f"基于以下搜索结果回答问题：{query_text}\n\n搜索结果：\n{web_info}"
            else:
                prompt = f"请回答以下问题：{query_text}"
        else:
            prompt = f"请回答以下问题：{query_text}"

        # 异步调用LLM
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, "search")
        )

        loop.close()

        if response.error:
            return jsonify({"error": response.error}), 500

        return jsonify({
            "success": True,
            "query": query_text,
            "results": response.content,
            "model": response.model,
            "provider": response.provider,
            "used_web_search": use_web_search
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data-analysis', methods=['POST'])
def analyze_data():
    """数据分析接口"""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({"error": "Missing 'data' in request"}), 400

        csv_data = data['data']
        analysis_type = data.get('analysis_type', 'summary')
        model = data.get('model', app.config['DEFAULT_MODEL'])

        # 使用数据分析工具
        analysis_result = tool_registry.call_tool(
            'analyze_data',
            data=csv_data,
            analysis_type=analysis_type
        )

        if not analysis_result.get('success'):
            return jsonify({"error": analysis_result.get('error')}), 400

        # 让LLM解释分析结果
        prompt = f"请解释以下数据分析结果：\n{analysis_result['result']}"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, "data_analysis")
        )

        loop.close()

        return jsonify({
            "success": True,
            "analysis_type": analysis_type,
            "raw_analysis": analysis_result['result'],
            "interpretation": response.content if not response.error else "无法生成解释",
            "model": response.model if not response.error else None,
            "provider": response.provider if not response.error else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """执行工具调用"""
    try:
        data = request.get_json()
        if not data or 'tool_name' not in data:
            return jsonify({"error": "Missing 'tool_name' in request"}), 400

        tool_name = data['tool_name']
        parameters = data.get('parameters', {})

        result = tool_registry.call_tool(tool_name, **parameters)

        return jsonify({
            "success": result.get('success', False),
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result.get('result'),
            "error": result.get('error')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({"error": "File too large"}), 413

if __name__ == '__main__':
    print("Starting Daily Copilot Backend Server...")
    print(f"Available models: {list(llm_service.get_available_models().keys())}")
    print(f"Available tools: {len(tool_registry.tools)}")
    app.run(debug=app.config['DEBUG'], port=5000, host='0.0.0.0')
