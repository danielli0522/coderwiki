const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

/**
 * Performance testing utilities
 */
class PerformanceTester {
  constructor(page) {
    this.page = page;
    this.results = [];
  }

  /**
   * Collect basic performance metrics
   */
  async collectBasicMetrics(testName) {
    const startTime = Date.now();
    
    // Get browser metrics
    const metrics = await this.page.metrics();
    
    // Get performance timing
    const timing = await this.page.evaluate(() => {
      const perf = performance.timing;
      return {
        loadEventEnd: perf.loadEventEnd,
        loadEventStart: perf.loadEventStart,
        domContentLoadedEventEnd: perf.domContentLoadedEventEnd,
        domContentLoadedEventStart: perf.domContentLoadedEventStart,
        responseEnd: perf.responseEnd,
        responseStart: perf.responseStart,
        requestStart: perf.requestStart,
        navigationStart: perf.navigationStart
      };
    });
    
    // Calculate key timings
    const timings = {
      domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
      loadEvent: timing.loadEventEnd - timing.navigationStart,
      firstByte: timing.responseStart - timing.requestStart,
      responseTime: timing.responseEnd - timing.responseStart
    };
    
    const result = {
      testName,
      timestamp: new Date().toISOString(),
      url: this.page.url(),
      metrics: {
        ...metrics,
        JSHeapUsedSizeMB: Math.round(metrics.JSHeapUsedSize / 1024 / 1024 * 100) / 100,
        JSHeapTotalSizeMB: Math.round(metrics.JSHeapTotalSize / 1024 / 1024 * 100) / 100
      },
      timings,
      loadTime: Date.now() - startTime
    };
    
    this.results.push(result);
    return result;
  }

  /**
   * Run Lighthouse audit
   */
  async runLighthouseAudit(url, options = {}) {
    try {
      const chrome = await chromeLauncher.launch({
        chromeFlags: ['--headless', '--disable-gpu', '--no-sandbox']
      });
      
      const lighthouseOptions = {
        logLevel: 'error',
        output: 'json',
        onlyCategories: ['performance'],
        port: chrome.port,
        ...options
      };
      
      const runnerResult = await lighthouse(url, lighthouseOptions);
      
      await chrome.kill();
      
      const report = runnerResult.report ? JSON.parse(runnerResult.report) : runnerResult.lhr;
      
      return {
        url,
        timestamp: new Date().toISOString(),
        performance: {
          score: report.categories.performance.score * 100,
          metrics: {
            firstContentfulPaint: report.audits['first-contentful-paint']?.numericValue || 0,
            largestContentfulPaint: report.audits['largest-contentful-paint']?.numericValue || 0,
            cumulativeLayoutShift: report.audits['cumulative-layout-shift']?.numericValue || 0,
            totalBlockingTime: report.audits['total-blocking-time']?.numericValue || 0,
            speedIndex: report.audits['speed-index']?.numericValue || 0,
            interactive: report.audits['interactive']?.numericValue || 0
          },
          opportunities: report.audits ? Object.entries(report.audits)
            .filter(([key, audit]) => audit.details && audit.details.type === 'opportunity')
            .map(([key, audit]) => ({
              id: key,
              title: audit.title,
              description: audit.description,
              score: audit.score,
              numericValue: audit.numericValue
            })) : []
        }
      };
    } catch (error) {
      console.error('Lighthouse audit failed:', error);
      return {
        url,
        timestamp: new Date().toISOString(),
        error: error.message,
        performance: {
          score: 0,
          metrics: {},
          opportunities: []
        }
      };
    }
  }

  /**
   * Test page load performance
   */
  async testPageLoad(url, iterations = 3) {
    const results = [];
    
    for (let i = 0; i < iterations; i++) {
      // Clear cache between iterations
      await this.page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      const cookies = await this.page.cookies();
      await this.page.deleteCookie(...cookies);
      
      const startTime = Date.now();
      
      await this.page.goto(url, { waitUntil: 'networkidle2' });
      
      const loadTime = Date.now() - startTime;
      const metrics = await this.page.metrics();
      
      results.push({
        iteration: i + 1,
        loadTime,
        metrics: {
          JSHeapUsedSizeMB: Math.round(metrics.JSHeapUsedSize / 1024 / 1024 * 100) / 100,
          JSHeapTotalSizeMB: Math.round(metrics.JSHeapTotalSize / 1024 / 1024 * 100) / 100,
          LayoutCount: metrics.LayoutCount,
          RecalcStyleCount: metrics.RecalcStyleCount,
          JSEventListeners: metrics.JSEventListeners
        }
      });
    }
    
    // Calculate averages
    const avgLoadTime = results.reduce((sum, r) => sum + r.loadTime, 0) / results.length;
    const avgMemory = results.reduce((sum, r) => sum + r.metrics.JSHeapUsedSizeMB, 0) / results.length;
    
    return {
      url,
      iterations,
      results,
      averages: {
        loadTime: Math.round(avgLoadTime),
        memoryUsage: Math.round(avgMemory * 100) / 100
      }
    };
  }

  /**
   * Test runtime performance during interactions
   */
  async testRuntimePerformance(testName, interactionFn) {
    // Start performance monitoring
    await this.page.tracing.start({
      categories: ['devtools.timeline'],
      screenshots: false
    });
    
    const startMetrics = await this.page.metrics();
    const startTime = Date.now();
    
    // Execute interaction
    await interactionFn(this.page);
    
    const endTime = Date.now();
    const endMetrics = await this.page.metrics();
    
    // Stop tracing
    const trace = await this.page.tracing.stop();
    
    return {
      testName,
      duration: endTime - startTime,
      memoryDelta: {
        JSHeapUsed: endMetrics.JSHeapUsedSize - startMetrics.JSHeapUsedSize,
        JSHeapTotal: endMetrics.JSHeapTotalSize - startMetrics.JSHeapTotalSize
      },
      layoutCount: endMetrics.LayoutCount - startMetrics.LayoutCount,
      recalcStyleCount: endMetrics.RecalcStyleCount - startMetrics.RecalcStyleCount,
      trace: trace ? trace.toString('base64') : null
    };
  }

  /**
   * Test memory usage patterns
   */
  async testMemoryUsage(testName, duration = 30000) {
    const samples = [];
    const sampleInterval = 1000; // Sample every second
    const samples_count = Math.floor(duration / sampleInterval);
    
    for (let i = 0; i < samples_count; i++) {
      const metrics = await this.page.metrics();
      samples.push({
        timestamp: Date.now(),
        JSHeapUsedSize: metrics.JSHeapUsedSize,
        JSHeapTotalSize: metrics.JSHeapTotalSize,
        LayoutCount: metrics.LayoutCount,
        RecalcStyleCount: metrics.RecalcStyleCount
      });
      
      await new Promise(resolve => setTimeout(resolve, sampleInterval));
    }
    
    // Analyze memory patterns
    const heapSizes = samples.map(s => s.JSHeapUsedSize);
    const maxHeap = Math.max(...heapSizes);
    const minHeap = Math.min(...heapSizes);
    const avgHeap = heapSizes.reduce((sum, size) => sum + size, 0) / heapSizes.length;
    
    // Detect memory leaks (increasing trend)
    const firstThird = heapSizes.slice(0, Math.floor(heapSizes.length / 3));
    const lastThird = heapSizes.slice(-Math.floor(heapSizes.length / 3));
    const avgFirstThird = firstThird.reduce((sum, size) => sum + size, 0) / firstThird.length;
    const avgLastThird = lastThird.reduce((sum, size) => sum + size, 0) / lastThird.length;
    const memoryIncrease = avgLastThird - avgFirstThird;
    
    return {
      testName,
      duration,
      samples,
      analysis: {
        maxHeapMB: Math.round(maxHeap / 1024 / 1024 * 100) / 100,
        minHeapMB: Math.round(minHeap / 1024 / 1024 * 100) / 100,
        avgHeapMB: Math.round(avgHeap / 1024 / 1024 * 100) / 100,
        memoryIncreaseMB: Math.round(memoryIncrease / 1024 / 1024 * 100) / 100,
        potentialLeak: memoryIncrease > 5 * 1024 * 1024, // 5MB increase
        stability: (maxHeap - minHeap) / avgHeap // Lower is more stable
      }
    };
  }

  /**
   * Test network performance
   */
  async testNetworkPerformance(url) {
    const requests = [];
    
    // Monitor network requests
    this.page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
        startTime: Date.now()
      });
    });
    
    this.page.on('response', response => {
      const request = requests.find(req => 
        req.url === response.url() && !req.endTime
      );
      
      if (request) {
        request.endTime = Date.now();
        request.status = response.status();
        request.size = response.headers()['content-length'] || 0;
        request.responseTime = request.endTime - request.startTime;
      }
    });
    
    await this.page.goto(url, { waitUntil: 'networkidle2' });
    
    // Wait a bit for all responses to complete
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Remove event listeners
    this.page.removeAllListeners('request');
    this.page.removeAllListeners('response');
    
    // Analyze requests
    const completedRequests = requests.filter(req => req.endTime);
    const totalSize = completedRequests.reduce((sum, req) => sum + parseInt(req.size || 0), 0);
    const avgResponseTime = completedRequests.reduce((sum, req) => sum + req.responseTime, 0) / completedRequests.length;
    
    const byResourceType = {};
    completedRequests.forEach(req => {
      if (!byResourceType[req.resourceType]) {
        byResourceType[req.resourceType] = { count: 0, totalSize: 0, totalTime: 0 };
      }
      byResourceType[req.resourceType].count++;
      byResourceType[req.resourceType].totalSize += parseInt(req.size || 0);
      byResourceType[req.resourceType].totalTime += req.responseTime;
    });
    
    return {
      url,
      timestamp: new Date().toISOString(),
      requests: completedRequests,
      summary: {
        totalRequests: completedRequests.length,
        totalSizeKB: Math.round(totalSize / 1024 * 100) / 100,
        avgResponseTime: Math.round(avgResponseTime),
        byResourceType,
        slowRequests: completedRequests.filter(req => req.responseTime > 2000),
        failedRequests: completedRequests.filter(req => req.status >= 400)
      }
    };
  }

  /**
   * Generate performance report
   */
  generateReport() {
    const performanceScores = [];
    const loadTimes = [];
    const memoryUsages = [];
    
    this.results.forEach(result => {
      if (result.timings) {
        loadTimes.push(result.timings.loadEvent);
      }
      if (result.metrics) {
        memoryUsages.push(result.metrics.JSHeapUsedSizeMB);
      }
      if (result.performance && result.performance.score) {
        performanceScores.push(result.performance.score);
      }
    });
    
    const avgLoadTime = loadTimes.length > 0 ? 
      loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length : 0;
    
    const avgMemoryUsage = memoryUsages.length > 0 ?
      memoryUsages.reduce((sum, mem) => sum + mem, 0) / memoryUsages.length : 0;
      
    const avgPerformanceScore = performanceScores.length > 0 ?
      performanceScores.reduce((sum, score) => sum + score, 0) / performanceScores.length : 0;
    
    return {
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: this.results.length,
        averageLoadTime: Math.round(avgLoadTime),
        averageMemoryUsage: Math.round(avgMemoryUsage * 100) / 100,
        averagePerformanceScore: Math.round(avgPerformanceScore * 100) / 100,
        recommendations: this.generateRecommendations()
      },
      results: this.results
    };
  }

  /**
   * Generate performance recommendations
   */
  generateRecommendations() {
    const recommendations = [];
    
    // Analyze load times
    const loadTimes = this.results
      .filter(r => r.timings && r.timings.loadEvent)
      .map(r => r.timings.loadEvent);
    
    if (loadTimes.length > 0) {
      const avgLoadTime = loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length;
      
      if (avgLoadTime > 3000) {
        recommendations.push({
          category: 'performance',
          priority: 'high',
          title: 'Improve Page Load Time',
          description: `Average load time is ${Math.round(avgLoadTime)}ms. Consider optimizing images, minifying CSS/JS, and using CDN.`,
          impact: 'High - affects user experience significantly'
        });
      }
    }
    
    // Analyze memory usage
    const memoryUsages = this.results
      .filter(r => r.metrics && r.metrics.JSHeapUsedSizeMB)
      .map(r => r.metrics.JSHeapUsedSizeMB);
    
    if (memoryUsages.length > 0) {
      const avgMemory = memoryUsages.reduce((sum, mem) => sum + mem, 0) / memoryUsages.length;
      
      if (avgMemory > 50) {
        recommendations.push({
          category: 'memory',
          priority: 'medium',
          title: 'Reduce Memory Usage',
          description: `Average memory usage is ${avgMemory}MB. Consider removing unused JavaScript and optimizing DOM size.`,
          impact: 'Medium - may cause performance issues on low-end devices'
        });
      }
    }
    
    return recommendations;
  }
}

module.exports = PerformanceTester;