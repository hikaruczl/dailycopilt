// Daily Copilot 内容脚本
(function() {
    'use strict';
    
    // 创建浮动按钮
    function createFloatingButton() {
        const button = document.createElement('div');
        button.id = 'daily-copilot-float-btn';
        button.innerHTML = '🤖';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            cursor: pointer;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
            transition: all 0.3s ease;
        `;
        
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
        
        button.addEventListener('click', () => {
            showQuickPanel();
        });
        
        return button;
    }
    
    // 创建快速面板
    function createQuickPanel() {
        const panel = document.createElement('div');
        panel.id = 'daily-copilot-quick-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 300px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            z-index: 10000;
            display: none;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        panel.innerHTML = `
            <div style="padding: 16px; border-bottom: 1px solid #e5e7eb;">
                <div style="font-weight: 600; margin-bottom: 8px;">Daily Copilot</div>
                <div style="font-size: 12px; color: #6b7280;">快速AI助手</div>
            </div>
            <div style="padding: 16px;">
                <div style="margin-bottom: 12px;">
                    <textarea id="quick-input" placeholder="输入你的问题..." style="
                        width: 100%;
                        height: 60px;
                        border: 1px solid #d1d5db;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 14px;
                        resize: none;
                        box-sizing: border-box;
                    "></textarea>
                </div>
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <button class="quick-action" data-action="translate">翻译</button>
                    <button class="quick-action" data-action="summarize">总结</button>
                    <button class="quick-action" data-action="explain">解释</button>
                </div>
                <button id="quick-send" style="
                    width: 100%;
                    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    cursor: pointer;
                ">发送</button>
                <div id="quick-result" style="
                    margin-top: 12px;
                    padding: 8px;
                    background: #f9fafb;
                    border-radius: 6px;
                    font-size: 13px;
                    line-height: 1.4;
                    display: none;
                "></div>
            </div>
        `;
        
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .quick-action {
                flex: 1;
                background: #f3f4f6;
                border: none;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                cursor: pointer;
                transition: background 0.2s;
            }
            .quick-action:hover {
                background: #e5e7eb;
            }
        `;
        document.head.appendChild(style);
        
        return panel;
    }
    
    // 显示快速面板
    function showQuickPanel() {
        const panel = document.getElementById('daily-copilot-quick-panel');
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            
            // 点击外部关闭
            setTimeout(() => {
                document.addEventListener('click', closeOnClickOutside);
            }, 100);
        } else {
            panel.style.display = 'none';
            document.removeEventListener('click', closeOnClickOutside);
        }
    }
    
    // 点击外部关闭面板
    function closeOnClickOutside(event) {
        const panel = document.getElementById('daily-copilot-quick-panel');
        const button = document.getElementById('daily-copilot-float-btn');
        
        if (!panel.contains(event.target) && !button.contains(event.target)) {
            panel.style.display = 'none';
            document.removeEventListener('click', closeOnClickOutside);
        }
    }
    
    // 处理快速操作
    function handleQuickAction(action) {
        const input = document.getElementById('quick-input');
        const selectedText = window.getSelection().toString();
        
        let prompt = '';
        switch (action) {
            case 'translate':
                prompt = selectedText ? `翻译: ${selectedText}` : '请输入要翻译的文本';
                break;
            case 'summarize':
                prompt = selectedText ? `总结: ${selectedText}` : `总结当前页面: ${document.title}`;
                break;
            case 'explain':
                prompt = selectedText ? `解释: ${selectedText}` : '请输入要解释的内容';
                break;
        }
        
        input.value = prompt;
    }
    
    // 发送请求
    async function sendQuickRequest() {
        const input = document.getElementById('quick-input');
        const result = document.getElementById('quick-result');
        const sendBtn = document.getElementById('quick-send');
        
        const message = input.value.trim();
        if (!message) return;
        
        sendBtn.textContent = '处理中...';
        sendBtn.disabled = true;
        result.style.display = 'block';
        result.textContent = '正在处理...';
        
        try {
            // 获取设置
            const settings = await chrome.storage.sync.get(['serverUrl']);
            const serverUrl = settings.serverUrl || 'http://localhost:5000';
            
            const response = await fetch(`${serverUrl}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                result.textContent = data.response;
            } else {
                result.textContent = `错误: ${data.error}`;
            }
        } catch (error) {
            result.textContent = `连接错误: ${error.message}`;
        } finally {
            sendBtn.textContent = '发送';
            sendBtn.disabled = false;
        }
    }
    
    // 初始化
    function init() {
        // 检查是否已经初始化
        if (document.getElementById('daily-copilot-float-btn')) {
            return;
        }
        
        // 创建浮动按钮
        const floatBtn = createFloatingButton();
        document.body.appendChild(floatBtn);
        
        // 创建快速面板
        const quickPanel = createQuickPanel();
        document.body.appendChild(quickPanel);
        
        // 绑定事件
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-action')) {
                handleQuickAction(e.target.dataset.action);
            } else if (e.target.id === 'quick-send') {
                sendQuickRequest();
            }
        });
        
        // 支持回车发送
        document.addEventListener('keypress', (e) => {
            if (e.target.id === 'quick-input' && e.key === 'Enter' && e.ctrlKey) {
                sendQuickRequest();
            }
        });
    }
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
