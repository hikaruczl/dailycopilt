// Daily Copilot 后台脚本
chrome.runtime.onInstalled.addListener(() => {
    console.log('Daily Copilot installed');
    
    // 创建右键菜单
    chrome.contextMenus.create({
        id: 'translate-selection',
        title: '翻译选中文本',
        contexts: ['selection']
    });
    
    chrome.contextMenus.create({
        id: 'analyze-page',
        title: '分析当前页面',
        contexts: ['page']
    });
    
    chrome.contextMenus.create({
        id: 'generate-code',
        title: '生成代码',
        contexts: ['selection']
    });
});

// 处理右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
        case 'translate-selection':
            handleTranslateSelection(info, tab);
            break;
        case 'analyze-page':
            handleAnalyzePage(info, tab);
            break;
        case 'generate-code':
            handleGenerateCode(info, tab);
            break;
    }
});

// 翻译选中文本
async function handleTranslateSelection(info, tab) {
    const selectedText = info.selectionText;
    if (!selectedText) return;
    
    try {
        // 获取设置
        const settings = await chrome.storage.sync.get(['serverUrl', 'apiKeys']);
        const serverUrl = settings.serverUrl || 'http://localhost:5000';
        
        // 调用翻译API
        const response = await fetch(`${serverUrl}/api/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: selectedText,
                target_language: '中文'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 在页面上显示翻译结果
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: showTranslationResult,
                args: [selectedText, data.translated_text]
            });
        }
    } catch (error) {
        console.error('Translation error:', error);
    }
}

// 分析当前页面
async function handleAnalyzePage(info, tab) {
    try {
        // 获取页面内容
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: getPageContent
        });
        
        const pageContent = results[0].result;
        
        // 获取设置
        const settings = await chrome.storage.sync.get(['serverUrl']);
        const serverUrl = settings.serverUrl || 'http://localhost:5000';
        
        // 调用分析API
        const response = await fetch(`${serverUrl}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `请分析以下网页内容并提供摘要：\n${pageContent.substring(0, 2000)}`
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 显示分析结果
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: showAnalysisResult,
                args: [data.response]
            });
        }
    } catch (error) {
        console.error('Analysis error:', error);
    }
}

// 生成代码
async function handleGenerateCode(info, tab) {
    const selectedText = info.selectionText;
    if (!selectedText) return;
    
    try {
        const settings = await chrome.storage.sync.get(['serverUrl']);
        const serverUrl = settings.serverUrl || 'http://localhost:5000';
        
        const response = await fetch(`${serverUrl}/api/code-generation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: selectedText,
                language: 'python'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: showCodeResult,
                args: [data.code]
            });
        }
    } catch (error) {
        console.error('Code generation error:', error);
    }
}

// 注入到页面的函数
function showTranslationResult(original, translation) {
    const popup = createResultPopup();
    popup.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">翻译结果</div>
        <div style="margin-bottom: 8px; color: #666;">原文: ${original}</div>
        <div>译文: ${translation}</div>
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 5000);
}

function showAnalysisResult(analysis) {
    const popup = createResultPopup();
    popup.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">页面分析</div>
        <div>${analysis}</div>
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 8000);
}

function showCodeResult(code) {
    const popup = createResultPopup();
    popup.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">生成的代码</div>
        <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; overflow-x: auto;">${code}</pre>
    `;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 10000);
}

function createResultPopup() {
    const popup = document.createElement('div');
    popup.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
    `;
    return popup;
}

function getPageContent() {
    return document.body.innerText || document.body.textContent || '';
}
