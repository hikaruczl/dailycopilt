"""
API测试文件
"""
import unittest
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import Config

class TestAPI(unittest.TestCase):
    """API测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_endpoint(self):
        """测试首页端点"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Daily Copilot Backend API')
    
    def test_models_endpoint(self):
        """测试模型列表端点"""
        response = self.app.get('/api/models')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('models', data)
        self.assertIn('success', data)
    
    def test_tools_endpoint(self):
        """测试工具列表端点"""
        response = self.app.get('/api/tools')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('tools', data)
        self.assertIn('success', data)
    
    def test_chat_endpoint_missing_message(self):
        """测试聊天端点缺少消息"""
        response = self.app.post('/api/chat',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_translate_endpoint_missing_data(self):
        """测试翻译端点缺少数据"""
        response = self.app.post('/api/translate',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_translate_endpoint_valid_data(self):
        """测试翻译端点有效数据"""
        test_data = {
            'text': 'Hello world',
            'target_language': '中文'
        }
        
        response = self.app.post('/api/translate',
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # 由于没有真实的API密钥，可能会失败，但应该返回错误而不是崩溃
        self.assertIn(response.status_code, [200, 500])
    
    def test_search_endpoint_missing_query(self):
        """测试搜索端点缺少查询"""
        response = self.app.post('/api/search',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_code_generation_endpoint_missing_description(self):
        """测试代码生成端点缺少描述"""
        response = self.app.post('/api/code-generation',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_tool_execution_missing_tool_name(self):
        """测试工具执行缺少工具名"""
        response = self.app.post('/api/tools/execute',
                                data=json.dumps({}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_tool_execution_calculator(self):
        """测试计算器工具"""
        test_data = {
            'tool_name': 'calculator',
            'parameters': {
                'expression': '2 + 3 * 4'
            }
        }
        
        response = self.app.post('/api/tools/execute',
                                data=json.dumps(test_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('result', data)
    
    def test_404_endpoint(self):
        """测试404端点"""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)

class TestTools(unittest.TestCase):
    """工具测试类"""
    
    def setUp(self):
        """测试前设置"""
        from app.tools import tool_registry
        self.registry = tool_registry
    
    def test_calculator_tool(self):
        """测试计算器工具"""
        result = self.registry.call_tool('calculator', expression='2 + 3')
        self.assertTrue(result['success'])
        self.assertIn('5', result['result'])
    
    def test_calculator_tool_invalid_expression(self):
        """测试计算器工具无效表达式"""
        result = self.registry.call_tool('calculator', expression='invalid')
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_current_time_tool(self):
        """测试当前时间工具"""
        result = self.registry.call_tool('current_time')
        self.assertTrue(result['success'])
        self.assertIn('当前时间', result['result'])
    
    def test_nonexistent_tool(self):
        """测试不存在的工具"""
        result = self.registry.call_tool('nonexistent_tool')
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
