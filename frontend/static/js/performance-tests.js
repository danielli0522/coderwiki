// 性能测试套件

// 性能测试工具
const PerformanceTestUtils = {
    // 测量函数执行时间
    measureTime: function(fn, ...args) {
        const start = performance.now();
        const result = fn(...args);
        const end = performance.now();
        return {
            result,
            time: end - start
        };
    },
    
    // 测量多个函数的平均执行时间
    measureAverageTime: function(fn, iterations = 100, ...args) {
        const times = [];
        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            fn(...args);
            const end = performance.now();
            times.push(end - start);
        }
        
        return {
            average: times.reduce((a, b) => a + b, 0) / times.length,
            min: Math.min(...times),
            max: Math.max(...times),
            times
        };
    },
    
    // 测量内存使用
    measureMemory: function() {
        if (window.performance && window.performance.memory) {
            return {
                used: window.performance.memory.usedJSHeapSize,
                total: window.performance.memory.totalJSHeapSize,
                limit: window.performance.memory.jsHeapSizeLimit
            };
        }
        return null;
    },
    
    // 测量页面加载性能
    measurePageLoad: function() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            return {
                totalLoadTime: timing.loadEventEnd - timing.navigationStart,
                domReadyTime: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaintTime: timing.responseEnd - timing.navigationStart,
                dnsTime: timing.domainLookupEnd - timing.domainLookupStart,
                tcpTime: timing.connectEnd - timing.connectStart,
                requestTime: timing.responseEnd - timing.requestStart,
                domProcessingTime: timing.domComplete - timing.domLoading,
                scriptTime: timing.loadEventEnd - timing.domContentLoadedEventEnd
            };
        }
        return null;
    },
    
    // 测量渲染性能
    measureRenderPerformance: function() {
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                const start = performance.now();
                requestAnimationFrame(() => {
                    const end = performance.now();
                    resolve(end - start);
                });
            });
        });
    },
    
    // 创建测试元素
    createTestElements: function(count = 1000) {
        const container = document.createElement('div');
        container.style.display = 'none';
        
        for (let i = 0; i < count; i++) {
            const element = document.createElement('div');
            element.className = 'test-element';
            element.textContent = `Test element ${i}`;
            container.appendChild(element);
        }
        
        document.body.appendChild(container);
        return container;
    },
    
    // 清理测试元素
    cleanupTestElements: function(container) {
        if (container && container.parentNode) {
            container.parentNode.removeChild(container);
        }
    }
};

// 性能测试套件
const PerformanceTestSuite = {
    tests: [],
    results: [],
    
    // 添加性能测试
    addTest: function(name, testFunction, threshold) {
        this.tests.push({ name, testFunction, threshold });
    },
    
    // 运行性能测试
    run: function() {
        console.group('🚀 性能测试开始');
        
        this.tests.forEach(test => {
            try {
                const result = test.testFunction();
                this.results.push({
                    name: test.name,
                    result,
                    threshold: test.threshold,
                    passed: test.threshold ? result <= test.threshold : true
                });
                
                if (test.threshold) {
                    if (result <= test.threshold) {
                        console.log(`✅ ${test.name}: ${result.toFixed(2)}ms (阈值: ${test.threshold}ms)`);
                    } else {
                        console.warn(`⚠️ ${test.name}: ${result.toFixed(2)}ms (阈值: ${test.threshold}ms)`);
                    }
                } else {
                    console.log(`✅ ${test.name}: ${result.toFixed(2)}ms`);
                }
            } catch (error) {
                console.error(`❌ ${test.name}:`, error.message);
                this.results.push({
                    name: test.name,
                    error: error.message,
                    passed: false
                });
            }
        });
        
        console.groupEnd();
        return this.results;
    },
    
    // 生成性能报告
    generateReport: function() {
        const passed = this.results.filter(r => r.passed).length;
        const failed = this.results.filter(r => !r.passed).length;
        
        console.log('📊 性能测试报告');
        console.log(`通过: ${passed}/${this.results.length}`);
        console.log(`失败: ${failed}/${this.results.length}`);
        
        return {
            passed,
            failed,
            total: this.results.length,
            results: this.results,
            success: failed === 0
        };
    }
};

// 具体性能测试
const PerformanceTests = {
    // 测试DOM操作性能
    testDOMOperations: function() {
        const container = PerformanceTestUtils.createTestElements(1000);
        const elements = container.querySelectorAll('.test-element');
        
        // 测试元素查询性能
        const queryTime = PerformanceTestUtils.measureAverageTime(() => {
            container.querySelectorAll('.test-element');
        }, 100);
        
        // 测试元素修改性能
        const modifyTime = PerformanceTestUtils.measureAverageTime(() => {
            elements.forEach(element => {
                element.style.color = 'red';
            });
        }, 10);
        
        // 测试元素添加性能
        const addTime = PerformanceTestUtils.measureAverageTime(() => {
            const newElement = document.createElement('div');
            newElement.textContent = 'New element';
            container.appendChild(newElement);
        }, 100);
        
        PerformanceTestUtils.cleanupTestElements(container);
        
        return {
            queryTime: queryTime.average,
            modifyTime: modifyTime.average,
            addTime: addTime.average,
            totalTime: queryTime.average + modifyTime.average + addTime.average
        };
    },
    
    // 测试CSS动画性能
    testCSSAnimations: function() {
        const container = PerformanceTestUtils.createTestElements(100);
        const elements = container.querySelectorAll('.test-element');
        
        // 设置动画样式
        elements.forEach(element => {
            element.style.transition = 'all 0.3s ease';
            element.style.transform = 'translateX(0)';
        });
        
        // 测试动画性能
        const animationTime = PerformanceTestUtils.measureAverageTime(() => {
            elements.forEach(element => {
                element.style.transform = 'translateX(100px)';
            });
        }, 10);
        
        PerformanceTestUtils.cleanupTestElements(container);
        
        return animationTime.average;
    },
    
    // 测试事件处理性能
    testEventHandling: function() {
        const container = PerformanceTestUtils.createTestElements(100);
        const elements = container.querySelectorAll('.test-element');
        let clickCount = 0;
        
        // 添加事件监听器
        elements.forEach(element => {
            element.addEventListener('click', () => {
                clickCount++;
            });
        });
        
        // 测试事件触发性能
        const eventTime = PerformanceTestUtils.measureAverageTime(() => {
            elements.forEach(element => {
                element.click();
            });
        }, 10);
        
        PerformanceTestUtils.cleanupTestElements(container);
        
        return eventTime.average;
    },
    
    // 测试组件初始化性能
    testComponentInitialization: function() {
        // 创建测试组件
        const components = [];
        for (let i = 0; i < 10; i++) {
            const component = document.createElement('div');
            component.className = 'card-enhanced';
            component.innerHTML = '<div class="card-header">Test Card</div><div class="card-body">Test Content</div>';
            document.body.appendChild(component);
            components.push(component);
        }
        
        // 测试组件初始化性能
        const initTime = PerformanceTestUtils.measureTime(() => {
            ComponentManager.initEnhancedCards();
        });
        
        // 清理
        components.forEach(component => component.remove());
        
        return initTime.time;
    },
    
    // 测试内存使用
    testMemoryUsage: function() {
        const beforeMemory = PerformanceTestUtils.measureMemory();
        
        // 创建大量元素
        const container = PerformanceTestUtils.createTestElements(5000);
        
        const afterMemory = PerformanceTestUtils.measureMemory();
        
        PerformanceTestUtils.cleanupTestElements(container);
        
        if (beforeMemory && afterMemory) {
            return {
                before: beforeMemory.used,
                after: afterMemory.used,
                difference: afterMemory.used - beforeMemory.used
            };
        }
        
        return null;
    },
    
    // 测试渲染性能
    testRenderingPerformance: function() {
        return PerformanceTestUtils.measureRenderPerformance();
    },
    
    // 测试页面加载性能
    testPageLoadPerformance: function() {
        return PerformanceTestUtils.measurePageLoad();
    },
    
    // 测试本地存储性能
    testLocalStoragePerformance: function() {
        const testData = { key: 'value', timestamp: Date.now() };
        
        // 测试写入性能
        const writeTime = PerformanceTestUtils.measureAverageTime(() => {
            localStorage.setItem('test', JSON.stringify(testData));
        }, 100);
        
        // 测试读取性能
        const readTime = PerformanceTestUtils.measureAverageTime(() => {
            JSON.parse(localStorage.getItem('test'));
        }, 100);
        
        // 清理
        localStorage.removeItem('test');
        
        return {
            writeTime: writeTime.average,
            readTime: readTime.average,
            totalTime: writeTime.average + readTime.average
        };
    },
    
    // 测试网络请求性能（模拟）
    testNetworkRequestPerformance: function() {
        // 模拟网络请求
        const mockFetch = () => {
            return new Promise(resolve => {
                setTimeout(() => {
                    resolve({ data: 'test data' });
                }, 100); // 模拟100ms延迟
            });
        };
        
        const requestTime = PerformanceTestUtils.measureAverageTime(async () => {
            await mockFetch();
        }, 10);
        
        return requestTime.average;
    },
    
    // 测试响应式布局性能
    testResponsiveLayoutPerformance: function() {
        const container = document.createElement('div');
        container.className = 'container-fluid';
        container.innerHTML = '<div class="row"><div class="col-md-6">Column 1</div><div class="col-md-6">Column 2</div></div>';
        document.body.appendChild(container);
        
        // 测试窗口大小改变时的性能
        const resizeTime = PerformanceTestUtils.measureAverageTime(() => {
            window.dispatchEvent(new Event('resize'));
        }, 10);
        
        PerformanceTestUtils.cleanupTestElements(container);
        
        return resizeTime.average;
    }
};

// 运行性能测试
async function runPerformanceTests() {
    // 添加性能测试
    PerformanceTestSuite.addTest('DOM操作性能', PerformanceTests.testDOMOperations, 50);
    PerformanceTestSuite.addTest('CSS动画性能', PerformanceTests.testCSSAnimations, 100);
    PerformanceTestSuite.addTest('事件处理性能', PerformanceTests.testEventHandling, 200);
    PerformanceTestSuite.addTest('组件初始化性能', PerformanceTests.testComponentInitialization, 100);
    PerformanceTestSuite.addTest('内存使用测试', PerformanceTests.testMemoryUsage);
    PerformanceTestSuite.addTest('渲染性能测试', PerformanceTests.testRenderingPerformance, 16);
    PerformanceTestSuite.addTest('页面加载性能', PerformanceTests.testPageLoadPerformance);
    PerformanceTestSuite.addTest('本地存储性能', PerformanceTests.testLocalStoragePerformance, 10);
    PerformanceTestSuite.addTest('网络请求性能', PerformanceTests.testNetworkRequestPerformance, 200);
    PerformanceTestSuite.addTest('响应式布局性能', PerformanceTests.testResponsiveLayoutPerformance, 50);
    
    // 运行测试
    const results = PerformanceTestSuite.run();
    const report = PerformanceTestSuite.generateReport();
    
    return {
        results,
        report
    };
}

// 导出性能测试模块
window.PerformanceTestUtils = PerformanceTestUtils;
window.PerformanceTestSuite = PerformanceTestSuite;
window.PerformanceTests = PerformanceTests;
window.runPerformanceTests = runPerformanceTests;