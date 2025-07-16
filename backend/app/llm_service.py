"""
多模型LLM服务模块
支持OpenAI、Anthropic、Google等多种AI模型
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# 第三方库导入
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from .config import Config, SUPPORTED_MODELS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None

class LLMService:
    """多模型LLM服务类"""

    def __init__(self):
        self.config = Config()
        self._initialize_clients()

    def _initialize_clients(self):
        """初始化各个AI服务客户端"""
        self.clients = {}

        # 初始化OpenAI客户端
        if self.config.OPENAI_API_KEY and openai:
            try:
                openai.api_key = self.config.OPENAI_API_KEY
                self.clients['openai'] = openai
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

        # 初始化Anthropic客户端
        if self.config.ANTHROPIC_API_KEY and anthropic:
            try:
                self.clients['anthropic'] = anthropic.Anthropic(
                    api_key=self.config.ANTHROPIC_API_KEY
                )
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

        # 初始化Google客户端
        if self.config.GOOGLE_API_KEY and genai:
            try:
                genai.configure(api_key=self.config.GOOGLE_API_KEY)
                self.clients['google'] = genai
                logger.info("Google client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google client: {e}")

    def get_available_models(self) -> Dict[str, Any]:
        """获取可用的模型列表"""
        available = {}
        for provider, models in SUPPORTED_MODELS.items():
            if provider in self.clients:
                available[provider] = models
        return available

    def _get_provider_from_model(self, model: str) -> Optional[str]:
        """根据模型名称获取提供商"""
        for provider, models in SUPPORTED_MODELS.items():
            if model in models:
                return provider
        return None

    async def call_openai(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> LLMResponse:
        """调用OpenAI模型"""
        try:
            client = self.clients.get('openai')
            if not client:
                return LLMResponse(
                    content="", model=model, provider="openai",
                    error="OpenAI client not available"
                )

            response = client.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', self.config.MAX_TOKENS),
                temperature=kwargs.get('temperature', self.config.TEMPERATURE)
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return LLMResponse(
                content=content,
                model=model,
                provider="openai",
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content="", model=model, provider="openai",
                error=str(e)
            )

    async def call_anthropic(self, prompt: str, model: str = "claude-3-sonnet", **kwargs) -> LLMResponse:
        """调用Anthropic模型"""
        try:
            client = self.clients.get('anthropic')
            if not client:
                return LLMResponse(
                    content="", model=model, provider="anthropic",
                    error="Anthropic client not available"
                )

            response = client.messages.create(
                model=model,
                max_tokens=kwargs.get('max_tokens', self.config.MAX_TOKENS),
                temperature=kwargs.get('temperature', self.config.TEMPERATURE),
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return LLMResponse(
                content=content,
                model=model,
                provider="anthropic",
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return LLMResponse(
                content="", model=model, provider="anthropic",
                error=str(e)
            )

    async def call_google(self, prompt: str, model: str = "gemini-pro", **kwargs) -> LLMResponse:
        """调用Google模型"""
        try:
            client = self.clients.get('google')
            if not client:
                return LLMResponse(
                    content="", model=model, provider="google",
                    error="Google client not available"
                )

            model_instance = client.GenerativeModel(model)
            response = model_instance.generate_content(
                prompt,
                generation_config=client.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', self.config.MAX_TOKENS),
                    temperature=kwargs.get('temperature', self.config.TEMPERATURE)
                )
            )

            content = response.text

            return LLMResponse(
                content=content,
                model=model,
                provider="google"
            )

        except Exception as e:
            logger.error(f"Google API error: {e}")
            return LLMResponse(
                content="", model=model, provider="google",
                error=str(e)
            )

    async def call_llm(self, prompt: str, model: str = None, task: str = "general", **kwargs) -> LLMResponse:
        """统一的LLM调用接口"""
        if not model:
            model = self.config.DEFAULT_MODEL

        provider = self._get_provider_from_model(model)
        if not provider:
            return LLMResponse(
                content="", model=model, provider="unknown",
                error=f"Unsupported model: {model}"
            )

        # 根据任务类型优化提示词
        optimized_prompt = self._optimize_prompt_for_task(prompt, task)

        # 调用对应的提供商
        if provider == "openai":
            return await self.call_openai(optimized_prompt, model, **kwargs)
        elif provider == "anthropic":
            return await self.call_anthropic(optimized_prompt, model, **kwargs)
        elif provider == "google":
            return await self.call_google(optimized_prompt, model, **kwargs)
        else:
            return LLMResponse(
                content="", model=model, provider=provider,
                error=f"Provider {provider} not implemented"
            )

    def _optimize_prompt_for_task(self, prompt: str, task: str) -> str:
        """根据任务类型优化提示词"""
        task_prompts = {
            "translate": f"请将以下文本翻译：\n{prompt}",
            "search": f"请帮我搜索并总结以下查询的相关信息：\n{prompt}",
            "analyze_document": f"请分析以下文档内容并提供摘要：\n{prompt}",
            "code_generation": f"请根据以下需求生成代码：\n{prompt}",
            "image_analysis": f"请分析这张图片并描述其内容：\n{prompt}",
            "data_analysis": f"请分析以下数据并提供洞察：\n{prompt}",
            "general": prompt
        }

        return task_prompts.get(task, prompt)

# 创建全局LLM服务实例
llm_service = LLMService()

# 兼容旧版本的函数
def call_llm(prompt: str, task: str = "general", model: str = None) -> str:
    """兼容旧版本的同步调用函数"""
    import asyncio

    try:
        # 在新的事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            llm_service.call_llm(prompt, model, task)
        )
        loop.close()

        if response.error:
            return f"Error: {response.error}"
        return response.content

    except Exception as e:
        logger.error(f"Error in call_llm: {e}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # 测试示例
    print("Testing LLM Service...")
    print(call_llm("Hello, how are you?", "translate"))
    print(call_llm("What is the capital of France?", "search"))
    print(call_llm("This is a test document.", "analyze_document"))
