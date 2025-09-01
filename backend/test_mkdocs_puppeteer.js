const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function testMkDocsFeature() {
    let browser;
    let page;
    
    try {
        console.log('启动Puppeteer浏览器...');
        browser = await puppeteer.launch({
            headless: false, // 显示浏览器窗口以便调试
            defaultViewport: { width: 1280, height: 800 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        page = await browser.newPage();
        
        // 监听控制台日志
        page.on('console', msg => {
            console.log('页面日志:', msg.text());
        });
        
        // 监听页面错误
        page.on('pageerror', error => {
            console.error('页面错误:', error.message);
        });
        
        console.log('1. 访问 http://localhost:5560...');
        await page.goto('http://localhost:5560', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // 等待页面加载完成
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 检查是否在登录页面
        const loginForm = await page.$('#loginForm');
        if (loginForm) {
            console.log('2. 在登录页面，使用admin/admin123登录...');
            
            // 输入用户名
            await page.waitForSelector('#username', { timeout: 10000 });
            await page.type('#username', 'admin');
            
            // 输入密码
            await page.waitForSelector('#password', { timeout: 10000 });
            await page.type('#password', 'admin123');
            
            // 点击登录按钮
            await page.click('#loginBtn');
            
            // 等待登录完成
            await new Promise(resolve => setTimeout(resolve, 5000));
        } else {
            console.log('2. 已经在主页，跳过登录步骤');
        }
        
        // 检查当前URL，如果还在登录页面说明登录失败
        const currentUrl = page.url();
        const stillOnLogin = await page.$('#loginForm');
        if (currentUrl.includes('/login') || stillOnLogin) {
            console.error('登录失败，仍在登录页面');
            await page.screenshot({ path: 'login_failed.png' });
            return;
        }
        
        console.log('3. 登录成功，访问 /sites/dp_bi_server_999/...');
        
        // 访问MkDocs站点
        await page.goto('http://localhost:5560/sites/dp_bi_server_999/', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // 等待页面加载完成
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log('4. 验证页面是否正确加载...');
        
        // 检查页面标题
        const title = await page.title();
        console.log('页面标题:', title);
        
        // 检查是否有MkDocs特征元素
        const mkdocsElements = await page.evaluate(() => {
            const results = {
                hasMkDocsNav: !!document.querySelector('.md-nav'),
                hasMkDocsContent: !!document.querySelector('.md-content'),
                hasMkDocsSidebar: !!document.querySelector('.md-sidebar'),
                hasTheme: !!document.querySelector('.md-grid'),
                bodyClass: document.body.className
            };
            return results;
        });
        
        console.log('MkDocs元素检查:', mkdocsElements);
        
        // 检查Mermaid图表
        console.log('5. 检查黄色主题的Mermaid图表...');
        
        // 等待Mermaid图表加载
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const mermaidElements = await page.evaluate(() => {
            const mermaidDivs = document.querySelectorAll('.mermaid');
            const svgElements = document.querySelectorAll('svg');
            
            const results = {
                mermaidDivCount: mermaidDivs.length,
                svgCount: svgElements.length,
                mermaidTexts: [],
                svgStyles: []
            };
            
            // 获取Mermaid文本内容
            mermaidDivs.forEach((div, index) => {
                results.mermaidTexts.push({
                    index: index,
                    text: div.textContent.substring(0, 100) + '...',
                    visible: div.offsetWidth > 0 && div.offsetHeight > 0
                });
            });
            
            // 检查SVG样式（寻找黄色主题）
            svgElements.forEach((svg, index) => {
                const style = window.getComputedStyle(svg);
                const rect = svg.getBoundingClientRect();
                results.svgStyles.push({
                    index: index,
                    visible: rect.width > 0 && rect.height > 0,
                    fill: style.fill,
                    stroke: style.stroke,
                    hasYellowTheme: svg.innerHTML.includes('#ffeb3b') || 
                                   svg.innerHTML.includes('#ffc107') ||
                                   svg.innerHTML.includes('yellow')
                });
            });
            
            return results;
        });
        
        console.log('Mermaid图表检查:', JSON.stringify(mermaidElements, null, 2));
        
        // 检查页面内容
        const pageContent = await page.evaluate(() => {
            return {
                hasContent: document.body.textContent.length > 100,
                contentPreview: document.body.textContent.substring(0, 200) + '...',
                hasImages: document.querySelectorAll('img').length,
                hasLinks: document.querySelectorAll('a').length
            };
        });
        
        console.log('页面内容检查:', pageContent);
        
        // 6. 截图保存结果
        console.log('6. 截图保存结果...');
        
        const screenshotPath = path.join(__dirname, 'mkdocs_test_screenshot.png');
        await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
        });
        console.log(`截图已保存到: ${screenshotPath}`);
        
        // 生成测试报告
        const testReport = {
            timestamp: new Date().toISOString(),
            testUrl: 'http://localhost:5560/sites/dp_bi_server_999/',
            status: 'success',
            results: {
                pageTitle: title,
                mkdocsElements: mkdocsElements,
                mermaidElements: mermaidElements,
                pageContent: pageContent
            },
            screenshots: [screenshotPath]
        };
        
        const reportPath = path.join(__dirname, 'mkdocs_test_report.json');
        fs.writeFileSync(reportPath, JSON.stringify(testReport, null, 2));
        console.log(`测试报告已保存到: ${reportPath}`);
        
        // 验证结果
        let success = true;
        let issues = [];
        
        if (!mkdocsElements.hasMkDocsContent) {
            success = false;
            issues.push('MkDocs内容区域未找到');
        }
        
        if (mermaidElements.mermaidDivCount === 0 && mermaidElements.svgCount === 0) {
            issues.push('未找到Mermaid图表');
        }
        
        if (!pageContent.hasContent) {
            success = false;
            issues.push('页面内容为空');
        }
        
        console.log('\n=== 测试结果 ===');
        console.log(`状态: ${success ? '成功' : '失败'}`);
        if (issues.length > 0) {
            console.log('发现问题:');
            issues.forEach(issue => console.log(`- ${issue}`));
        }
        console.log(`MkDocs页面: ${mkdocsElements.hasMkDocsContent ? '✓' : '✗'}`);
        console.log(`Mermaid图表: ${mermaidElements.mermaidDivCount > 0 || mermaidElements.svgCount > 0 ? '✓' : '✗'}`);
        console.log(`页面内容: ${pageContent.hasContent ? '✓' : '✗'}`);
        
        // 检查黄色主题
        const hasYellowTheme = mermaidElements.svgStyles.some(style => style.hasYellowTheme);
        console.log(`黄色主题: ${hasYellowTheme ? '✓' : '?'}`);
        
    } catch (error) {
        console.error('测试过程中出现错误:', error);
        
        if (page) {
            const errorScreenshot = path.join(__dirname, 'mkdocs_test_error.png');
            await page.screenshot({ path: errorScreenshot });
            console.log(`错误截图已保存到: ${errorScreenshot}`);
        }
        
        // 生成错误报告
        const errorReport = {
            timestamp: new Date().toISOString(),
            status: 'error',
            error: {
                message: error.message,
                stack: error.stack
            }
        };
        
        const errorReportPath = path.join(__dirname, 'mkdocs_test_error_report.json');
        fs.writeFileSync(errorReportPath, JSON.stringify(errorReport, null, 2));
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// 运行测试
console.log('开始测试CoderWiki的MkDocs站点功能...\n');
testMkDocsFeature().then(() => {
    console.log('\n测试完成！');
}).catch(error => {
    console.error('测试失败:', error);
    process.exit(1);
});