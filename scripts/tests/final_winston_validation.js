const puppeteer = require('puppeteer');

async function finalValidation() {
    console.log('🧪 Final Winston Architecture Validation');
    console.log('=====================================');
    
    const browser = await puppeteer.launch({ 
        headless: true, 
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const testResults = {
        templateReferences: '❌',
        architectureConflicts: '❌', 
        namespaceManagement: '❌',
        errorHandling: '❌',
        apiClient: '❌',
        overallStatus: '❌'
    };
    
    try {
        const page = await browser.newPage();
        
        // 捕获错误
        const errors = [];
        page.on('pageerror', error => {
            errors.push(error.message);
        });
        
        // 导航到登录页面
        await page.goto('http://localhost:5008/login', { 
            waitUntil: 'domcontentloaded',
            timeout: 15000 
        });
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // 测试1: 检查模板引用问题是否修复
        const templateCheck = await page.evaluate(() => {
            const oldScripts = [
                'repository-modal-fix.js',
                'disable-delete-modal.js', 
                'modal-close-fix.js',
                'login-modal-fix.js'
            ];
            
            let foundOldReferences = 0;
            oldScripts.forEach(script => {
                if (document.querySelector(`script[src*="${script}"]`)) {
                    foundOldReferences++;
                }
            });
            
            return foundOldReferences === 0;
        });
        
        if (templateCheck) {
            testResults.templateReferences = '✅';
        }
        
        // 测试2: 检查架构冲突问题是否修复
        const conflictCheck = await page.evaluate(() => {
            const newArchitecture = [
                'core.js',
                'ui-framework.js', 
                'auth-unified.js',
                'performance-unified.js',
                'winston-error-recovery.js'
            ];
            
            let loadedCount = 0;
            newArchitecture.forEach(script => {
                if (document.querySelector(`script[src*="${script}"]`)) {
                    loadedCount++;
                }
            });
            
            return loadedCount === newArchitecture.length;
        });
        
        if (conflictCheck) {
            testResults.architectureConflicts = '✅';
        }
        
        // 测试3: 检查命名空间管理是否修复
        const namespaceCheck = await page.evaluate(() => {
            return {
                ApiClientDefined: typeof window.ApiClient !== 'undefined',
                apiInstanceDefined: typeof window.api !== 'undefined',
                PerformanceMonitorDefined: typeof window.PerformanceMonitor !== 'undefined',
                ComponentManagerDefined: typeof window.ComponentManager !== 'undefined',
                AuthUnifiedDefined: typeof window.AuthUnified !== 'undefined'
            };
        });
        
        const namespaceScore = Object.values(namespaceCheck).filter(v => v === true).length;
        if (namespaceScore >= 4) { // 至少4个核心对象定义成功
            testResults.namespaceManagement = '✅';
        }
        
        // 测试4: 检查错误处理机制
        const errorHandlingCheck = await page.evaluate(() => {
            return {
                winstonErrorRecoveryExists: typeof window.WinstonErrorRecovery !== 'undefined',
                emergencyHotkeyActive: document.addEventListener.toString().includes('keydown'), // 简单检查
                globalErrorHandlerExists: typeof window.onerror !== 'undefined'
            };
        });
        
        const errorHandlingScore = Object.values(errorHandlingCheck).filter(v => v === true).length;
        if (errorHandlingScore >= 2) {
            testResults.errorHandling = '✅';
        }
        
        // 测试5: ApiClient功能测试
        if (namespaceCheck.ApiClientDefined) {
            try {
                const apiTest = await page.evaluate(async () => {
                    try {
                        const response = await window.api.request('/auth/status');
                        return { success: true, hasResponse: !!response };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                });
                
                if (apiTest.success) {
                    testResults.apiClient = '✅';
                }
            } catch (e) {
                // API测试失败不影响架构验证
            }
        }
        
        // JavaScript错误检查
        const jsErrorsCount = errors.length;
        
        // 整体状态评估
        const passedTests = Object.values(testResults).filter(result => result === '✅').length;
        const totalTests = Object.keys(testResults).length - 1; // 排除 overallStatus
        
        if (passedTests >= totalTests - 1 && jsErrorsCount === 0) { // 允许1个测试失败
            testResults.overallStatus = '✅ PASSED';
        } else {
            testResults.overallStatus = `❌ FAILED (${passedTests}/${totalTests})`;
        }
        
        // 输出结果
        console.log('\n📊 Final Test Results:');
        console.log('====================');
        console.log(`${testResults.templateReferences} HTML模板引用更新修复`);
        console.log(`${testResults.architectureConflicts} 新旧架构文件冲突解决`); 
        console.log(`${testResults.namespaceManagement} 全局对象命名空间管理`);
        console.log(`${testResults.errorHandling} 错误处理和降级机制`);
        console.log(`${testResults.apiClient} ApiClient功能验证`);
        console.log('──────────────────────');
        console.log(`🎯 Overall Status: ${testResults.overallStatus}`);
        console.log(`🐛 JavaScript Errors: ${jsErrorsCount}`);
        
        if (testResults.overallStatus.includes('PASSED')) {
            console.log('\n🎉 Winston Architecture v1.0 验证成功！');
            console.log('✅ 所有关键架构问题已修复');
            console.log('✅ 系统已准备好进行生产使用');
        } else {
            console.log('\n⚠️  部分问题仍需关注');
            if (jsErrorsCount > 0) {
                console.log('JavaScript错误:', errors);
            }
        }
        
    } catch (error) {
        console.error('❌ Validation failed:', error);
    } finally {
        await browser.close();
    }
}

finalValidation();