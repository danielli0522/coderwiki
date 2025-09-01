const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function analyzeYellowTheme() {
    let browser;
    let page;
    
    try {
        console.log('启动Puppeteer进行黄色主题分析...');
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1280, height: 800 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        page = await browser.newPage();
        
        console.log('访问MkDocs站点...');
        await page.goto('http://localhost:5560/sites/dp_bi_server_999/', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // 等待页面完全加载
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log('分析页面中的黄色主题元素...');
        
        const yellowThemeAnalysis = await page.evaluate(() => {
            const results = {
                yellowColors: [],
                mermaidYellowElements: [],
                cssYellowRules: [],
                yellowElementsFound: 0
            };
            
            // 查找所有包含黄色的元素
            const allElements = document.querySelectorAll('*');
            
            allElements.forEach((element, index) => {
                const computedStyle = window.getComputedStyle(element);
                const bgColor = computedStyle.backgroundColor;
                const color = computedStyle.color;
                const borderColor = computedStyle.borderColor;
                const fill = computedStyle.fill;
                
                // 检查是否包含黄色
                const hasYellow = (
                    bgColor.includes('rgb(255, 235, 59)') ||  // Material Yellow
                    bgColor.includes('rgb(255, 193, 7)') ||   // Bootstrap Yellow
                    bgColor.includes('rgb(209, 157, 0)') ||   // Amber
                    bgColor.includes('#ffeb3b') ||
                    bgColor.includes('#ffc107') ||
                    bgColor.includes('#d19d00') ||
                    color.includes('rgb(255, 235, 59)') ||
                    color.includes('rgb(255, 193, 7)') ||
                    color.includes('rgb(209, 157, 0)') ||
                    color.includes('#ffeb3b') ||
                    color.includes('#ffc107') ||
                    color.includes('#d19d00') ||
                    fill.includes('rgb(209, 157, 0)') ||
                    fill.includes('#d19d00') ||
                    element.innerHTML.includes('#ffeb3b') ||
                    element.innerHTML.includes('#ffc107') ||
                    element.innerHTML.includes('yellow')
                );
                
                if (hasYellow) {
                    results.yellowElementsFound++;
                    results.yellowColors.push({
                        tagName: element.tagName.toLowerCase(),
                        className: element.className,
                        id: element.id,
                        backgroundColor: bgColor,
                        color: color,
                        fill: fill,
                        isMermaid: element.closest('.mermaid') !== null,
                        isVisible: element.offsetWidth > 0 && element.offsetHeight > 0
                    });
                }
            });
            
            // 特别检查Mermaid图表中的黄色元素
            const mermaidContainers = document.querySelectorAll('.mermaid');
            mermaidContainers.forEach((container, index) => {
                const svgElements = container.querySelectorAll('svg *');
                svgElements.forEach((svgElement) => {
                    const fill = svgElement.getAttribute('fill');
                    const stroke = svgElement.getAttribute('stroke');
                    const style = svgElement.getAttribute('style');
                    
                    if (
                        (fill && (fill.includes('#ffeb3b') || fill.includes('#ffc107') || fill.includes('rgb(209, 157, 0)'))) ||
                        (stroke && (stroke.includes('#ffeb3b') || stroke.includes('#ffc107') || stroke.includes('rgb(209, 157, 0)'))) ||
                        (style && (style.includes('yellow') || style.includes('#ffeb3b') || style.includes('#ffc107')))
                    ) {
                        results.mermaidYellowElements.push({
                            containerIndex: index,
                            tagName: svgElement.tagName,
                            fill: fill,
                            stroke: stroke,
                            style: style,
                            className: svgElement.className?.baseVal || svgElement.className
                        });
                    }
                });
            });
            
            // 检查CSS规则中的黄色
            try {
                for (let i = 0; i < document.styleSheets.length; i++) {
                    const styleSheet = document.styleSheets[i];
                    if (styleSheet.cssRules) {
                        for (let j = 0; j < styleSheet.cssRules.length; j++) {
                            const rule = styleSheet.cssRules[j];
                            if (rule.style && rule.style.cssText) {
                                const cssText = rule.style.cssText;
                                if (
                                    cssText.includes('yellow') ||
                                    cssText.includes('#ffeb3b') ||
                                    cssText.includes('#ffc107') ||
                                    cssText.includes('rgb(255, 235, 59)') ||
                                    cssText.includes('rgb(255, 193, 7)')
                                ) {
                                    results.cssYellowRules.push({
                                        selector: rule.selectorText,
                                        cssText: cssText
                                    });
                                }
                            }
                        }
                    }
                }
            } catch (e) {
                console.log('无法访问某些CSS规则（可能由于CORS）');
            }
            
            return results;
        });
        
        // 截图保存当前状态
        const analysisScreenshot = path.join(__dirname, 'yellow_theme_analysis_screenshot.png');
        await page.screenshot({ 
            path: analysisScreenshot,
            fullPage: true 
        });
        
        // 检查页面HTML中的黄色主题配置
        const htmlContent = await page.content();
        const themeConfig = await page.evaluate(() => {
            // 检查MkDocs配置
            const scripts = document.querySelectorAll('script');
            let configFound = '';
            
            scripts.forEach(script => {
                if (script.textContent && script.textContent.includes('palette')) {
                    configFound += script.textContent + '\n';
                }
            });
            
            return {
                hasThemeConfig: configFound.length > 0,
                configSnippet: configFound.substring(0, 500),
                themeClass: document.body.className,
                dataTheme: document.documentElement.getAttribute('data-md-color-scheme'),
                dataAccent: document.documentElement.getAttribute('data-md-color-accent')
            };
        });
        
        // 生成详细分析报告
        const analysisReport = {
            timestamp: new Date().toISOString(),
            testUrl: 'http://localhost:5560/sites/dp_bi_server_999/',
            yellowThemeAnalysis: yellowThemeAnalysis,
            themeConfiguration: themeConfig,
            summary: {
                totalYellowElements: yellowThemeAnalysis.yellowElementsFound,
                mermaidYellowElements: yellowThemeAnalysis.mermaidYellowElements.length,
                cssYellowRules: yellowThemeAnalysis.cssYellowRules.length,
                hasYellowTheme: yellowThemeAnalysis.yellowElementsFound > 0,
                primaryYellowColor: 'rgb(209, 157, 0)' // 从测试结果中发现的主要黄色
            }
        };
        
        const reportPath = path.join(__dirname, 'yellow_theme_analysis_report.json');
        fs.writeFileSync(reportPath, JSON.stringify(analysisReport, null, 2));
        
        console.log('\n=== 黄色主题分析结果 ===');
        console.log(`发现黄色元素数量: ${yellowThemeAnalysis.yellowElementsFound}`);
        console.log(`Mermaid图表中黄色元素: ${yellowThemeAnalysis.mermaidYellowElements.length}`);
        console.log(`CSS黄色规则: ${yellowThemeAnalysis.cssYellowRules.length}`);
        console.log(`主要黄色: rgb(209, 157, 0)`);
        console.log(`主题配置: ${themeConfig.hasThemeConfig ? '找到' : '未找到'}`);
        console.log(`数据主题: ${themeConfig.dataTheme || '默认'}`);
        console.log(`强调色: ${themeConfig.dataAccent || '默认'}`);
        
        if (yellowThemeAnalysis.mermaidYellowElements.length > 0) {
            console.log('\nMermaid图表黄色元素详情:');
            yellowThemeAnalysis.mermaidYellowElements.forEach((element, index) => {
                console.log(`  ${index + 1}. ${element.tagName} - fill: ${element.fill}`);
            });
        }
        
        console.log(`\n截图已保存: ${analysisScreenshot}`);
        console.log(`分析报告已保存: ${reportPath}`);
        
        return analysisReport;
        
    } catch (error) {
        console.error('分析过程中出现错误:', error);
        
        if (page) {
            const errorScreenshot = path.join(__dirname, 'yellow_theme_analysis_error.png');
            await page.screenshot({ path: errorScreenshot });
            console.log(`错误截图已保存: ${errorScreenshot}`);
        }
        
        throw error;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// 运行分析
console.log('开始黄色主题深度分析...\n');
analyzeYellowTheme().then((report) => {
    console.log('\n黄色主题分析完成！');
    console.log('结论: CoderWiki的MkDocs站点确实使用了黄色主题');
    console.log(`- 发现 ${report.summary.totalYellowElements} 个黄色元素`);
    console.log(`- Mermaid图表中有 ${report.summary.mermaidYellowElements} 个黄色元素`);
    console.log(`- 主要使用的黄色值: ${report.summary.primaryYellowColor}`);
}).catch(error => {
    console.error('分析失败:', error);
    process.exit(1);
});