# Daily Copilot - AI生产力助手 2.0

一个功能强大的AI生产力助手，集成多种AI模型和实用工具，提供智能翻译、代码生成、文档分析、数据处理等功能。

## ✨ 功能特性

### 🤖 多模型支持
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku
- **Google**: Gemini Pro, Gemini Pro Vision

### 🛠️ 智能工具
- 🌐 **智能翻译**: 支持多语言高质量翻译
- 💻 **代码生成**: 支持多种编程语言代码生成
- 📄 **文档分析**: PDF、Word、TXT文档智能分析
- 📊 **数据分析**: CSV数据分析和可视化
- 🧮 **计算器**: 复杂数学表达式计算
- 🌤️ **天气查询**: 实时天气信息获取
- 🔍 **智能搜索**: 基于AI的智能搜索和总结

### 🚀 浏览器集成
- Chrome插件形式，使用便捷
- 右键菜单快速操作
- 浮动助手面板
- 页面内容智能分析

## 📁 项目结构

```
dailycopilt/
├── backend/                    # Flask后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # 主应用文件
│   │   ├── llm_service.py     # 多模型LLM服务
│   │   ├── tools.py           # 工具调用系统
│   │   └── config.py          # 配置管理
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py        # API测试
│   ├── requirements.txt       # Python依赖
│   ├── run.py                # 启动脚本
│   └── .env.example          # 环境变量示例
├── plugin/                    # Chrome浏览器插件
│   ├── images/               # 插件图标
│   ├── manifest.json         # 插件配置
│   ├── popup.html            # 插件界面
│   ├── popup.js              # 插件逻辑
│   ├── style.css             # 样式文件
│   ├── background.js         # 后台脚本
│   └── content.js            # 内容脚本
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Chrome浏览器
- 至少一个AI模型的API密钥

### 后端服务设置

1. **克隆项目**：
```bash
git clone https://github.com/hikaruczl/dailycopilt.git
cd dailycopilt/backend
```

2. **配置环境**：
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

3. **启动服务**（推荐使用启动脚本）：
```bash
python run.py
```

或者手动启动：
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main
```

服务将在 `http://localhost:5000` 启动。

### 浏览器插件安装

1. 打开Chrome浏览器
2. 进入扩展程序管理页面 (`chrome://extensions/`)
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择项目中的 `plugin` 文件夹
6. 插件安装完成后，点击插件图标进行配置

### 配置API密钥

在插件的设置页面中配置你的API密钥：
- OpenAI API Key
- Anthropic API Key
- Google API Key

至少需要配置一个API密钥才能正常使用。

## 📖 使用指南

### 插件功能

1. **聊天助手**: 选择AI模型，输入问题获得智能回答
2. **翻译工具**: 快速翻译文本到多种语言
3. **工具集合**:
   - 代码生成：描述需求生成代码
   - 智能搜索：AI增强的搜索功能
   - 文档分析：上传文档获得分析报告
   - 数据分析：分析CSV数据
   - 计算器：复杂数学计算
   - 天气查询：获取天气信息

### 右键菜单功能

- **翻译选中文本**: 选中文本后右键翻译
- **分析当前页面**: 右键分析页面内容
- **生成代码**: 选中需求描述后生成代码

### 浮动助手

页面右下角的浮动按钮提供快速AI助手功能。

## 🔧 API接口文档

### 基础信息
- 基础URL: `http://localhost:5000`
- 内容类型: `application/json`
- 认证: 无需认证（本地服务）

### 核心接口

#### 1. 获取可用模型
```http
GET /api/models
```

#### 2. 通用聊天接口
```http
POST /api/chat
Content-Type: application/json

{
    "message": "你的问题",
    "model": "gpt-3.5-turbo",
    "use_tools": false
}
```

#### 3. 翻译接口
```http
POST /api/translate
Content-Type: application/json

{
    "text": "要翻译的文本",
    "target_language": "目标语言",
    "model": "gpt-3.5-turbo"
}
```

#### 4. 代码生成接口
```http
POST /api/code-generation
Content-Type: application/json

{
    "description": "代码需求描述",
    "language": "python",
    "model": "gpt-4"
}
```

#### 5. 文档分析接口
```http
POST /api/convert-document
Content-Type: multipart/form-data

document: 文档文件
model: AI模型名称
analysis_type: 分析类型
```

#### 6. 智能搜索接口
```http
POST /api/search
Content-Type: application/json

{
    "query": "搜索查询",
    "model": "gpt-3.5-turbo",
    "use_web_search": true
}
```

#### 7. 数据分析接口
```http
POST /api/data-analysis
Content-Type: application/json

{
    "data": "CSV格式数据",
    "analysis_type": "summary",
    "model": "gpt-3.5-turbo"
}
```

#### 8. 工具执行接口
```http
POST /api/tools/execute
Content-Type: application/json

{
    "tool_name": "calculator",
    "parameters": {
        "expression": "2 + 3 * 4"
    }
}
```

## 🧪 测试

运行后端测试：
```bash
cd backend
python -m pytest tests/ -v
```

或者运行单个测试文件：
```bash
python tests/test_api.py
```

## 🛠️ 开发说明

### 技术栈
- **后端**: Flask, Python, OpenAI API, Anthropic API, Google AI
- **前端**: HTML5, CSS3, JavaScript ES6+
- **插件**: Chrome Extension Manifest V3
- **工具**: pandas, numpy, matplotlib, BeautifulSoup

### 开发环境
- Python 3.7+
- Chrome浏览器
- 代码编辑器（推荐VS Code）

### 项目特点
- 🔄 **异步处理**: 支持异步AI模型调用
- 🛡️ **错误处理**: 完善的错误处理和用户反馈
- 🎨 **现代UI**: 响应式设计，支持深色模式
- 🔧 **可扩展**: 模块化设计，易于添加新功能
- 📱 **跨平台**: 支持多种操作系统和浏览器

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 贡献类型
- 🐛 Bug修复
- ✨ 新功能开发
- 📚 文档改进
- 🎨 UI/UX优化
- 🧪 测试覆盖
- 🌐 国际化支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📝 更新日志

### v2.0.0 (2024-01-XX)
- 🚀 **重大更新**: 完全重构的架构
- 🤖 **多模型支持**: 集成OpenAI、Anthropic、Google AI
- 🛠️ **工具系统**: 新增6种实用工具
- 🎨 **全新UI**: 现代化的用户界面
- 📱 **浏览器集成**: 右键菜单和浮动助手
- 🔧 **配置管理**: 完善的设置和配置系统
- 🧪 **测试覆盖**: 添加单元测试和API测试

### v0.1.0 (2024-01-XX)
- 🎉 初始版本发布
- 🌐 基础翻译功能
- 📄 文档分析功能
- 🔍 智能搜索功能

## 🙏 致谢

感谢以下开源项目和服务：
- [OpenAI](https://openai.com/) - GPT模型
- [Anthropic](https://www.anthropic.com/) - Claude模型
- [Google AI](https://ai.google/) - Gemini模型
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Chrome Extensions](https://developer.chrome.com/docs/extensions/) - 浏览器扩展平台

## 📞 支持

如果你遇到问题或有建议，请：
1. 查看 [Issues](https://github.com/hikaruczl/dailycopilt/issues)
2. 创建新的 Issue
3. 参与 [Discussions](https://github.com/hikaruczl/dailycopilt/discussions)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！