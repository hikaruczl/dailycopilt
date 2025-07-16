// Daily Copilot 插件主逻辑
class DailyCopilot {
    constructor() {
        this.serverUrl = 'http://localhost:5000';
        this.currentTool = null;
        this.settings = {};
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.setupTabNavigation();
        this.loadAvailableModels();
    }

    // 加载设置
    loadSettings() {
        chrome.storage.sync.get(['serverUrl', 'apiKeys'], (result) => {
            if (result.serverUrl) {
                this.serverUrl = result.serverUrl;
                document.getElementById('server-url').value = result.serverUrl;
            }
            if (result.apiKeys) {
                this.settings = result.apiKeys;
                if (result.apiKeys.openai) {
                    document.getElementById('openai-key').value = result.apiKeys.openai;
                }
                if (result.apiKeys.anthropic) {
                    document.getElementById('anthropic-key').value = result.apiKeys.anthropic;
                }
                if (result.apiKeys.google) {
                    document.getElementById('google-key').value = result.apiKeys.google;
                }
            }
        });
    }

    // 保存设置
    saveSettings() {
        const serverUrl = document.getElementById('server-url').value;
        const apiKeys = {
            openai: document.getElementById('openai-key').value,
            anthropic: document.getElementById('anthropic-key').value,
            google: document.getElementById('google-key').value
        };

        chrome.storage.sync.set({
            serverUrl: serverUrl,
            apiKeys: apiKeys
        }, () => {
            this.serverUrl = serverUrl;
            this.settings = apiKeys;
            this.showMessage('设置已保存', 'success');
        });
    }

    // 设置事件监听器
    setupEventListeners() {
        // 聊天功能
        document.getElementById('chat-send').addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.sendChatMessage();
            }
        });

        // 翻译功能
        document.getElementById('translate-button').addEventListener('click', () => this.translateText());

        // 工具选择
        document.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('click', () => this.selectTool(card.dataset.tool));
        });

        // 工具执行
        document.getElementById('tool-execute').addEventListener('click', () => this.executeTool());

        // 设置
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
        document.getElementById('test-connection').addEventListener('click', () => this.testConnection());
    }

    // 设置标签页导航
    setupTabNavigation() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    // 切换标签页
    switchTab(tabName) {
        // 更新导航标签
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 更新内容区域
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    // 加载可用模型
    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.serverUrl}/api/models`);
            if (response.ok) {
                const data = await response.json();
                this.updateModelOptions(data.models);
            }
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }

    // 更新模型选项
    updateModelOptions(models) {
        const chatModelSelect = document.getElementById('chat-model');
        chatModelSelect.innerHTML = '';

        for (const [provider, providerModels] of Object.entries(models)) {
            for (const [modelId, modelInfo] of Object.entries(providerModels)) {
                const option = document.createElement('option');
                option.value = modelId;
                option.textContent = `${modelInfo.name} (${modelInfo.provider})`;
                chatModelSelect.appendChild(option);
            }
        }
    }

    // 发送聊天消息
    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const modelSelect = document.getElementById('chat-model');
        const resultDiv = document.getElementById('chat-result');

        const message = input.value.trim();
        if (!message) {
            this.showMessage('请输入消息', 'error', resultDiv);
            return;
        }

        const model = modelSelect.value;

        this.showMessage('正在处理...', 'loading', resultDiv);

        try {
            const response = await fetch(`${this.serverUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: model
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.response, 'success', resultDiv);
                input.value = '';
            } else {
                this.showMessage(`错误: ${data.error}`, 'error', resultDiv);
            }
        } catch (error) {
            this.showMessage(`连接错误: ${error.message}`, 'error', resultDiv);
        }
    }

    // 翻译文本
    async translateText() {
        const textInput = document.getElementById('text-to-translate');
        const languageSelect = document.getElementById('target-language');
        const resultDiv = document.getElementById('translation-result');

        const text = textInput.value.trim();
        if (!text) {
            this.showMessage('请输入要翻译的文本', 'error', resultDiv);
            return;
        }

        const targetLanguage = languageSelect.value;

        this.showMessage('正在翻译...', 'loading', resultDiv);

        try {
            const response = await fetch(`${this.serverUrl}/api/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    target_language: targetLanguage
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.translated_text, 'success', resultDiv);
            } else {
                this.showMessage(`翻译失败: ${data.error}`, 'error', resultDiv);
            }
        } catch (error) {
            this.showMessage(`连接错误: ${error.message}`, 'error', resultDiv);
        }
    }

    // 选择工具
    selectTool(toolName) {
        // 更新工具卡片状态
        document.querySelectorAll('.tool-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-tool="${toolName}"]`).classList.add('active');

        this.currentTool = toolName;
        this.setupToolInput(toolName);
    }

    // 设置工具输入界面
    setupToolInput(toolName) {
        const inputArea = document.getElementById('tool-input-area');
        const inputLabel = document.getElementById('tool-input-label');
        const toolInput = document.getElementById('tool-input');
        const extraInputs = document.getElementById('tool-extra-inputs');

        inputArea.style.display = 'block';
        extraInputs.innerHTML = '';

        const toolConfigs = {
            code: {
                label: '代码需求描述',
                placeholder: '请描述你需要的代码功能...',
                extraInputs: [
                    { type: 'select', id: 'code-language', label: '编程语言', options: ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust'] }
                ]
            },
            search: {
                label: '搜索查询',
                placeholder: '输入你想搜索的内容...'
            },
            document: {
                label: '文档文件',
                placeholder: '选择要分析的文档...',
                type: 'file'
            },
            data: {
                label: 'CSV数据',
                placeholder: '粘贴CSV格式的数据...',
                extraInputs: [
                    { type: 'select', id: 'analysis-type', label: '分析类型', options: ['summary', 'info'] }
                ]
            },
            calculator: {
                label: '数学表达式',
                placeholder: '输入数学表达式，如: 2 + 3 * 4'
            },
            weather: {
                label: '城市名称',
                placeholder: '输入城市名称，如: 北京'
            }
        };

        const config = toolConfigs[toolName];
        if (config) {
            inputLabel.textContent = config.label;
            toolInput.placeholder = config.placeholder;

            if (config.type === 'file') {
                toolInput.type = 'file';
                toolInput.accept = '.txt,.pdf,.docx,.doc';
            } else {
                toolInput.type = 'text';
            }

            // 添加额外输入
            if (config.extraInputs) {
                config.extraInputs.forEach(extra => {
                    const div = document.createElement('div');
                    div.className = 'form-group';

                    const label = document.createElement('label');
                    label.className = 'form-label';
                    label.textContent = extra.label;

                    if (extra.type === 'select') {
                        const select = document.createElement('select');
                        select.id = extra.id;
                        select.className = 'form-select';

                        extra.options.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option.toLowerCase();
                            optionElement.textContent = option;
                            select.appendChild(optionElement);
                        });

                        div.appendChild(label);
                        div.appendChild(select);
                    }

                    extraInputs.appendChild(div);
                });
            }
        }
    }

    // 执行工具
    async executeTool() {
        if (!this.currentTool) {
            this.showMessage('请先选择一个工具', 'error');
            return;
        }

        const toolInput = document.getElementById('tool-input');
        const resultDiv = document.getElementById('tool-result');

        let inputValue = toolInput.value.trim();
        if (!inputValue && toolInput.type !== 'file') {
            this.showMessage('请输入内容', 'error', resultDiv);
            return;
        }

        this.showMessage('正在执行...', 'loading', resultDiv);

        try {
            let result;

            switch (this.currentTool) {
                case 'code':
                    result = await this.executeCodeGeneration(inputValue);
                    break;
                case 'search':
                    result = await this.executeSearch(inputValue);
                    break;
                case 'document':
                    result = await this.executeDocumentAnalysis();
                    break;
                case 'data':
                    result = await this.executeDataAnalysis(inputValue);
                    break;
                case 'calculator':
                    result = await this.executeCalculator(inputValue);
                    break;
                case 'weather':
                    result = await this.executeWeather(inputValue);
                    break;
                default:
                    throw new Error('未知的工具类型');
            }

            if (result.success) {
                this.showMessage(result.data, 'success', resultDiv);
            } else {
                this.showMessage(`执行失败: ${result.error}`, 'error', resultDiv);
            }
        } catch (error) {
            this.showMessage(`执行错误: ${error.message}`, 'error', resultDiv);
        }
    }

    // 代码生成
    async executeCodeGeneration(description) {
        const languageSelect = document.getElementById('code-language');
        const language = languageSelect ? languageSelect.value : 'python';

        const response = await fetch(`${this.serverUrl}/api/code-generation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: description,
                language: language
            })
        });

        const data = await response.json();
        return { success: data.success, data: data.code, error: data.error };
    }

    // 智能搜索
    async executeSearch(query) {
        const response = await fetch(`${this.serverUrl}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        return { success: data.success, data: data.results, error: data.error };
    }

    // 文档分析
    async executeDocumentAnalysis() {
        const fileInput = document.getElementById('tool-input');
        const file = fileInput.files[0];

        if (!file) {
            throw new Error('请选择文件');
        }

        const formData = new FormData();
        formData.append('document', file);

        const response = await fetch(`${this.serverUrl}/api/convert-document`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        return {
            success: data.success,
            data: data.analysis_result,
            error: data.error
        };
    }

    // 数据分析
    async executeDataAnalysis(csvData) {
        const analysisTypeSelect = document.getElementById('analysis-type');
        const analysisType = analysisTypeSelect ? analysisTypeSelect.value : 'summary';

        const response = await fetch(`${this.serverUrl}/api/data-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: csvData,
                analysis_type: analysisType
            })
        });

        const data = await response.json();
        return {
            success: data.success,
            data: data.interpretation || data.raw_analysis,
            error: data.error
        };
    }

    // 计算器
    async executeCalculator(expression) {
        const response = await fetch(`${this.serverUrl}/api/tools/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool_name: 'calculator',
                parameters: { expression: expression }
            })
        });

        const data = await response.json();
        return { success: data.success, data: data.result, error: data.error };
    }

    // 天气查询
    async executeWeather(location) {
        const response = await fetch(`${this.serverUrl}/api/tools/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool_name: 'weather',
                parameters: { location: location }
            })
        });

        const data = await response.json();
        return { success: data.success, data: data.result, error: data.error };
    }

    // 测试连接
    async testConnection() {
        const serverUrl = document.getElementById('server-url').value;

        try {
            const response = await fetch(`${serverUrl}/`);
            const data = await response.json();

            if (data.message) {
                this.showMessage('连接成功！', 'success');
            } else {
                this.showMessage('连接失败：服务器响应异常', 'error');
            }
        } catch (error) {
            this.showMessage(`连接失败：${error.message}`, 'error');
        }
    }

    // 显示消息
    showMessage(message, type, targetElement = null) {
        const element = targetElement || document.createElement('div');

        if (!targetElement) {
            // 如果没有指定目标元素，创建临时通知
            element.className = `result-area ${type}`;
            element.textContent = message;
            element.style.position = 'fixed';
            element.style.top = '10px';
            element.style.right = '10px';
            element.style.zIndex = '1000';
            element.style.maxWidth = '300px';

            document.body.appendChild(element);

            setTimeout(() => {
                document.body.removeChild(element);
            }, 3000);
        } else {
            element.className = `result-area ${type}`;
            element.textContent = message;
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', function () {
    new DailyCopilot();
});
