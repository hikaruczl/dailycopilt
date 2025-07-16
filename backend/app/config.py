"""
配置管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # 模型配置
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'gif'}
    
    # 工具配置
    ENABLE_WEB_SEARCH = os.getenv('ENABLE_WEB_SEARCH', 'True').lower() == 'true'
    ENABLE_CODE_EXECUTION = os.getenv('ENABLE_CODE_EXECUTION', 'False').lower() == 'true'
    ENABLE_IMAGE_GENERATION = os.getenv('ENABLE_IMAGE_GENERATION', 'True').lower() == 'true'
    
    # 安全配置
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# 支持的模型列表
SUPPORTED_MODELS = {
    'openai': {
        'gpt-4': {'name': 'GPT-4', 'provider': 'OpenAI', 'supports_vision': True},
        'gpt-4-turbo': {'name': 'GPT-4 Turbo', 'provider': 'OpenAI', 'supports_vision': True},
        'gpt-3.5-turbo': {'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI', 'supports_vision': False},
    },
    'anthropic': {
        'claude-3-opus': {'name': 'Claude 3 Opus', 'provider': 'Anthropic', 'supports_vision': True},
        'claude-3-sonnet': {'name': 'Claude 3 Sonnet', 'provider': 'Anthropic', 'supports_vision': True},
        'claude-3-haiku': {'name': 'Claude 3 Haiku', 'provider': 'Anthropic', 'supports_vision': True},
    },
    'google': {
        'gemini-pro': {'name': 'Gemini Pro', 'provider': 'Google', 'supports_vision': False},
        'gemini-pro-vision': {'name': 'Gemini Pro Vision', 'provider': 'Google', 'supports_vision': True},
    }
}

# 工具配置
AVAILABLE_TOOLS = {
    'web_search': {
        'name': '网页搜索',
        'description': '搜索互联网信息',
        'enabled': True
    },
    'calculator': {
        'name': '计算器',
        'description': '执行数学计算',
        'enabled': True
    },
    'weather': {
        'name': '天气查询',
        'description': '获取天气信息',
        'enabled': True
    },
    'code_generator': {
        'name': '代码生成',
        'description': '生成各种编程语言代码',
        'enabled': True
    },
    'image_analyzer': {
        'name': '图像分析',
        'description': '分析和描述图像内容',
        'enabled': True
    },
    'data_analyzer': {
        'name': '数据分析',
        'description': '分析CSV和Excel数据',
        'enabled': True
    }
}
