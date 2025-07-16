"""
工具调用系统
提供各种实用工具的集成
"""
import json
import math
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def register_tool(self, name: str, func: callable, description: str, parameters: Dict[str, Any]):
        """注册工具"""
        self.tools[name] = {
            'function': func,
            'description': description,
            'parameters': parameters
        }
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 计算器工具
        self.register_tool(
            'calculator',
            self.calculator,
            '执行数学计算',
            {
                'expression': {'type': 'string', 'description': '数学表达式'}
            }
        )
        
        # 网页搜索工具
        self.register_tool(
            'web_search',
            self.web_search,
            '搜索网页信息',
            {
                'query': {'type': 'string', 'description': '搜索查询'},
                'num_results': {'type': 'integer', 'description': '结果数量', 'default': 5}
            }
        )
        
        # 天气查询工具
        self.register_tool(
            'weather',
            self.get_weather,
            '获取天气信息',
            {
                'location': {'type': 'string', 'description': '城市名称'}
            }
        )
        
        # 时间工具
        self.register_tool(
            'current_time',
            self.get_current_time,
            '获取当前时间',
            {}
        )
        
        # 数据分析工具
        self.register_tool(
            'analyze_data',
            self.analyze_data,
            '分析CSV数据',
            {
                'data': {'type': 'string', 'description': 'CSV格式的数据'},
                'analysis_type': {'type': 'string', 'description': '分析类型', 'default': 'summary'}
            }
        )
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（用于LLM函数调用）"""
        definitions = []
        for name, tool in self.tools.items():
            definitions.append({
                'name': name,
                'description': tool['description'],
                'parameters': {
                    'type': 'object',
                    'properties': tool['parameters'],
                    'required': [k for k, v in tool['parameters'].items() if 'default' not in v]
                }
            })
        return definitions
    
    def call_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """调用工具"""
        if name not in self.tools:
            return {'error': f'Tool {name} not found'}
        
        try:
            result = self.tools[name]['function'](**kwargs)
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {'error': str(e)}
    
    # 工具实现
    def calculator(self, expression: str) -> str:
        """计算器工具"""
        try:
            # 安全的数学表达式计算
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def web_search(self, query: str, num_results: int = 5) -> str:
        """网页搜索工具（模拟实现）"""
        # 这里应该集成真实的搜索API，如Google Search API或Bing Search API
        # 目前返回模拟结果
        return f"搜索 '{query}' 的结果:\n1. 相关信息1\n2. 相关信息2\n3. 相关信息3"
    
    def get_weather(self, location: str) -> str:
        """天气查询工具（模拟实现）"""
        # 这里应该集成真实的天气API，如OpenWeatherMap
        # 目前返回模拟结果
        return f"{location}的天气: 晴天，温度25°C，湿度60%"
    
    def get_current_time(self) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def analyze_data(self, data: str, analysis_type: str = 'summary') -> str:
        """数据分析工具"""
        try:
            # 解析CSV数据
            from io import StringIO
            df = pd.read_csv(StringIO(data))
            
            if analysis_type == 'summary':
                return f"数据摘要:\n{df.describe().to_string()}"
            elif analysis_type == 'info':
                info = f"数据形状: {df.shape}\n"
                info += f"列名: {list(df.columns)}\n"
                info += f"数据类型:\n{df.dtypes.to_string()}"
                return info
            else:
                return "支持的分析类型: summary, info"
                
        except Exception as e:
            return f"数据分析错误: {str(e)}"

# 创建全局工具注册表
tool_registry = ToolRegistry()

class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行多个工具调用"""
        results = []
        for call in tool_calls:
            result = self.execute_tool_call(call)
            results.append(result)
        return results
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个工具调用"""
        tool_name = tool_call.get('name')
        parameters = tool_call.get('parameters', {})
        
        if not tool_name:
            return {'error': 'Tool name is required'}
        
        result = self.registry.call_tool(tool_name, **parameters)
        return {
            'tool_name': tool_name,
            'parameters': parameters,
            **result
        }

# 创建全局工具执行器
tool_executor = ToolExecutor(tool_registry)
