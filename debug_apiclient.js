const puppeteer = require('puppeteer');

async function debugApiClient() {
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        args: ['--no-sandbox'] 
    });
    
    try {
        const page = await browser.newPage();
        
        // 导航到登录页面
        await page.goto('http://localhost:5008/login', { 
            waitUntil: 'networkidle0',
            timeout: 10000 
        });
        
        // 等待页面加载完成
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // 详细检查ApiClient
        const debugInfo = await page.evaluate(() => {
            return {
                // 检查条件语句
                windowApiClientUndefined: typeof window.ApiClient === 'undefined',
                windowApiClientType: typeof window.ApiClient,
                windowApiClient: window.ApiClient ? 'defined' : 'undefined',
                
                // 检查全局实例
                windowApiType: typeof window.api,
                windowApi: window.api ? 'defined' : 'undefined',
                
                // 检查核心系统
                windowCoreSystemType: typeof window.coreSystem,
                windowCoreSystem: window.coreSystem ? 'defined' : 'undefined',
                
                // 检查类定义
                ApiClientConstructor: typeof ApiClient !== 'undefined' ? 'defined in global scope' : 'not in global scope',
                
                // 检查script标签加载
                coreJsLoaded: !!document.querySelector('script[src*="core.js"]'),
                
                // 获取所有脚本
                allScripts: Array.from(document.querySelectorAll('script[src]')).map(s => s.src)
            };
        });
        
        console.log('🔍 Debug Info:', JSON.stringify(debugInfo, null, 2));
        
        // 尝试手动执行ApiClient定义检查
        const manualCheck = await page.evaluate(() => {
            console.log('Manual check - typeof window.ApiClient:', typeof window.ApiClient);
            
            // 检查是否存在未捕获的JavaScript错误
            const errors = [];
            window.onerror = function(msg, url, lineNo, columnNo, error) {
                errors.push({ msg, url, lineNo, columnNo, error: error ? error.toString() : 'unknown' });
            };
            
            return {
                errors: errors,
                manualApiClientCheck: typeof window.ApiClient === 'undefined'
            };
        });
        
        console.log('🔧 Manual Check:', manualCheck);
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
    } catch (error) {
        console.error('❌ Debug failed:', error);
    } finally {
        await browser.close();
    }
}

debugApiClient();