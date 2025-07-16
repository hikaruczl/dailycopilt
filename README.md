# Daily Copilot - AI Productivity Assistant

一个集成了AI功能的浏览器插件和后端服务，提供翻译、文档分析和智能搜索功能。

## 功能特性

- 🌐 **智能翻译**: 支持多语言文本翻译
- 📄 **文档分析**: 上传文档进行AI分析
- 🔍 **智能搜索**: 基于AI的智能搜索功能
- 🚀 **浏览器集成**: Chrome插件形式，使用便捷

## 项目结构

```
dailycopilt/
├── backend/                 # Flask后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # 主应用文件
│   │   └── llm_service.py  # LLM服务接口
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python依赖
├── plugin/                 # Chrome浏览器插件
│   ├── images/            # 插件图标
│   ├── manifest.json      # 插件配置
│   ├── popup.html         # 插件界面
│   ├── popup.js           # 插件逻辑
│   └── style.css          # 样式文件
└── README.md
```

## 快速开始

### 后端服务设置

1. 进入后端目录：
```bash
cd backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动服务：
```bash
python -m app.main
```

服务将在 `http://localhost:5000` 启动。

### 浏览器插件安装

1. 打开Chrome浏览器
2. 进入扩展程序管理页面 (`chrome://extensions/`)
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择项目中的 `plugin` 文件夹

## API接口

### 翻译接口
```
POST /api/translate
Content-Type: application/json

{
    "text": "要翻译的文本",
    "target_language": "目标语言"
}
```

### 文档分析接口
```
POST /api/convert-document
Content-Type: multipart/form-data

document: 文档文件
```

### 智能搜索接口
```
POST /api/search
Content-Type: application/json

{
    "query": "搜索查询"
}
```

## 开发说明

### 技术栈
- **后端**: Flask, Python
- **前端**: HTML, CSS, JavaScript
- **插件**: Chrome Extension Manifest V3

### 开发环境
- Python 3.7+
- Chrome浏览器

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v0.1.0
- 初始版本发布
- 基础翻译功能
- 文档分析功能
- 智能搜索功能