const fs = require('fs-extra');
const path = require('path');

/**
 * Comprehensive UI test report generator
 */
class UITestReportGenerator {
  constructor() {
    this.reportData = {
      summary: {},
      testResults: [],
      screenshots: [],
      performanceResults: [],
      accessibilityResults: [],
      responsiveResults: [],
      coverage: {},
      recommendations: []
    };
  }

  /**
   * Add test results to report
   */
  addTestResults(testSuite, results) {
    this.reportData.testResults.push({
      testSuite,
      timestamp: new Date().toISOString(),
      results
    });
  }

  /**
   * Add screenshot comparison results
   */
  addScreenshotResults(screenshots) {
    this.reportData.screenshots.push(...screenshots);
  }

  /**
   * Add performance test results
   */
  addPerformanceResults(performanceData) {
    this.reportData.performanceResults.push(performanceData);
  }

  /**
   * Add accessibility audit results
   */
  addAccessibilityResults(accessibilityData) {
    this.reportData.accessibilityResults.push(accessibilityData);
  }

  /**
   * Add responsive testing results
   */
  addResponsiveResults(responsiveData) {
    this.reportData.responsiveResults.push(responsiveData);
  }

  /**
   * Generate comprehensive HTML report
   */
  async generateHTMLReport() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportDir = path.join(__dirname, '..', 'reports');
    const reportPath = path.join(reportDir, `ui-test-report-${timestamp}.html`);
    
    await fs.ensureDir(reportDir);
    
    // Calculate summary statistics
    this.calculateSummary();
    
    const htmlContent = this.generateHTMLContent();
    
    await fs.writeFile(reportPath, htmlContent);
    
    // Also generate JSON report
    const jsonPath = path.join(reportDir, `ui-test-report-${timestamp}.json`);
    await fs.writeFile(jsonPath, JSON.stringify(this.reportData, null, 2));
    
    console.log(`\nUI Test Reports generated:`);
    console.log(`HTML: ${reportPath}`);
    console.log(`JSON: ${jsonPath}`);
    
    return { htmlPath: reportPath, jsonPath };
  }

  /**
   * Calculate summary statistics
   */
  calculateSummary() {
    const summary = {
      timestamp: new Date().toISOString(),
      testExecution: {
        totalSuites: this.reportData.testResults.length,
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        passRate: 0
      },
      performance: {
        averageScore: 0,
        averageLoadTime: 0,
        criticalIssues: 0
      },
      accessibility: {
        averageScore: 0,
        totalViolations: 0,
        criticalViolations: 0
      },
      responsive: {
        totalIssues: 0,
        highSeverityIssues: 0,
        testedViewports: ['mobile', 'tablet', 'desktop']
      },
      screenshots: {
        total: this.reportData.screenshots.length,
        visualRegressions: 0,
        newBaselines: 0
      }
    };
    
    // Calculate test execution summary
    this.reportData.testResults.forEach(suite => {
      if (suite.results && Array.isArray(suite.results)) {
        summary.testExecution.totalTests += suite.results.length;
        summary.testExecution.passed += suite.results.filter(r => r.status === 'passed').length;
        summary.testExecution.failed += suite.results.filter(r => r.status === 'failed').length;
        summary.testExecution.skipped += suite.results.filter(r => r.status === 'skipped').length;
      }
    });
    
    summary.testExecution.passRate = summary.testExecution.totalTests > 0 ?
      Math.round((summary.testExecution.passed / summary.testExecution.totalTests) * 100) : 0;
    
    // Calculate performance summary
    if (this.reportData.performanceResults.length > 0) {
      const scores = this.reportData.performanceResults
        .filter(p => p.performance && p.performance.score)
        .map(p => p.performance.score);
      
      summary.performance.averageScore = scores.length > 0 ?
        Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0;
      
      const loadTimes = this.reportData.performanceResults
        .filter(p => p.timings && p.timings.loadEvent)
        .map(p => p.timings.loadEvent);
      
      summary.performance.averageLoadTime = loadTimes.length > 0 ?
        Math.round(loadTimes.reduce((sum, time) => sum + time, 0) / loadTimes.length) : 0;
    }
    
    // Calculate accessibility summary
    if (this.reportData.accessibilityResults.length > 0) {
      const scores = this.reportData.accessibilityResults
        .filter(a => a.score)
        .map(a => a.score);
      
      summary.accessibility.averageScore = scores.length > 0 ?
        Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 0;
      
      this.reportData.accessibilityResults.forEach(result => {
        if (result.violations) {
          summary.accessibility.totalViolations += result.violations.length;
          summary.accessibility.criticalViolations += result.violations
            .filter(v => v.impact === 'critical').length;
        }
      });
    }
    
    // Calculate responsive summary
    this.reportData.responsiveResults.forEach(result => {
      if (result.allIssues) {
        summary.responsive.totalIssues += result.allIssues.length;
        summary.responsive.highSeverityIssues += result.allIssues
          .filter(issue => issue.severity === 'high').length;
      }
    });
    
    // Calculate screenshot summary
    this.reportData.screenshots.forEach(screenshot => {
      if (screenshot.isBaseline) {
        summary.screenshots.newBaselines++;
      } else if (screenshot.percentage > 1.0) { // More than 1% difference
        summary.screenshots.visualRegressions++;
      }
    });
    
    this.reportData.summary = summary;
    this.generateRecommendations();
  }

  /**
   * Generate recommendations based on results
   */
  generateRecommendations() {
    const recommendations = [];
    const summary = this.reportData.summary;
    
    // Test execution recommendations
    if (summary.testExecution.passRate < 90) {
      recommendations.push({
        category: 'Test Quality',
        priority: 'high',
        title: 'Improve Test Pass Rate',
        description: `Current pass rate is ${summary.testExecution.passRate}%. Investigate and fix failing tests.`,
        impact: 'High - indicates potential application issues or test stability problems'
      });
    }
    
    // Performance recommendations
    if (summary.performance.averageScore < 70) {
      recommendations.push({
        category: 'Performance',
        priority: 'high',
        title: 'Improve Page Performance',
        description: `Average performance score is ${summary.performance.averageScore}. Focus on optimizing load times and resource usage.`,
        impact: 'High - directly affects user experience and SEO'
      });
    }
    
    if (summary.performance.averageLoadTime > 3000) {
      recommendations.push({
        category: 'Performance',
        priority: 'medium',
        title: 'Optimize Load Times',
        description: `Average load time is ${summary.performance.averageLoadTime}ms. Consider code splitting, lazy loading, and CDN usage.`,
        impact: 'Medium - users may experience slow loading'
      });
    }
    
    // Accessibility recommendations
    if (summary.accessibility.averageScore < 80) {
      recommendations.push({
        category: 'Accessibility',
        priority: 'high',
        title: 'Improve Accessibility',
        description: `Average accessibility score is ${summary.accessibility.averageScore}. Address accessibility violations to improve usability.`,
        impact: 'High - affects users with disabilities and legal compliance'
      });
    }
    
    if (summary.accessibility.criticalViolations > 0) {
      recommendations.push({
        category: 'Accessibility',
        priority: 'critical',
        title: 'Fix Critical Accessibility Issues',
        description: `${summary.accessibility.criticalViolations} critical accessibility violations found. These must be addressed immediately.`,
        impact: 'Critical - prevents users from accessing content'
      });
    }
    
    // Responsive design recommendations
    if (summary.responsive.highSeverityIssues > 0) {
      recommendations.push({
        category: 'Responsive Design',
        priority: 'high',
        title: 'Fix Mobile Layout Issues',
        description: `${summary.responsive.highSeverityIssues} high-severity responsive issues found. These affect mobile usability.`,
        impact: 'High - poor mobile experience affects user engagement'
      });
    }
    
    // Visual regression recommendations
    if (summary.screenshots.visualRegressions > 0) {
      recommendations.push({
        category: 'Visual Quality',
        priority: 'medium',
        title: 'Review Visual Changes',
        description: `${summary.screenshots.visualRegressions} visual regressions detected. Review changes to ensure they are intentional.`,
        impact: 'Medium - unexpected visual changes may confuse users'
      });
    }
    
    this.reportData.recommendations = recommendations;
  }

  /**
   * Generate HTML content for the report
   */
  generateHTMLContent() {
    const summary = this.reportData.summary;
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoderWiki UI Test Report - ${summary.timestamp}</title>
    <style>
        ${this.getReportCSS()}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>CoderWiki UI Test Report</h1>
            <p class="timestamp">Generated: ${new Date(summary.timestamp).toLocaleString()}</p>
        </header>
        
        <section class="summary-section">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card ${this.getStatusClass(summary.testExecution.passRate, 90, 70)}">
                    <h3>Test Execution</h3>
                    <div class="metric">${summary.testExecution.passRate}%</div>
                    <p>Pass Rate (${summary.testExecution.passed}/${summary.testExecution.totalTests})</p>
                </div>
                
                <div class="summary-card ${this.getStatusClass(summary.performance.averageScore, 80, 60)}">
                    <h3>Performance</h3>
                    <div class="metric">${summary.performance.averageScore}</div>
                    <p>Average Score</p>
                </div>
                
                <div class="summary-card ${this.getStatusClass(summary.accessibility.averageScore, 80, 60)}">
                    <h3>Accessibility</h3>
                    <div class="metric">${summary.accessibility.averageScore}</div>
                    <p>Average Score</p>
                </div>
                
                <div class="summary-card ${summary.responsive.highSeverityIssues === 0 ? 'good' : (summary.responsive.highSeverityIssues < 5 ? 'warning' : 'error')}">
                    <h3>Responsive</h3>
                    <div class="metric">${summary.responsive.totalIssues}</div>
                    <p>Total Issues</p>
                </div>
            </div>
        </section>
        
        ${this.generateRecommendationsSection()}
        ${this.generateTestResultsSection()}
        ${this.generatePerformanceSection()}
        ${this.generateAccessibilitySection()}
        ${this.generateResponsiveSection()}
        ${this.generateScreenshotSection()}
        
        <footer class="report-footer">
            <p>Report generated by CoderWiki UI Test Suite</p>
        </footer>
    </div>
    
    <script>
        ${this.getReportJavaScript()}
    </script>
</body>
</html>`;
  }

  /**
   * Generate recommendations section
   */
  generateRecommendationsSection() {
    if (this.reportData.recommendations.length === 0) {
      return '<section class="recommendations-section"><h2>Recommendations</h2><p>No specific recommendations - all metrics look good!</p></section>';
    }
    
    const recommendations = this.reportData.recommendations
      .sort((a, b) => {
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      })
      .map(rec => `
        <div class="recommendation ${rec.priority}">
            <h4>${rec.title}</h4>
            <div class="rec-meta">
                <span class="category">${rec.category}</span>
                <span class="priority">${rec.priority.toUpperCase()}</span>
            </div>
            <p>${rec.description}</p>
            <div class="impact">Impact: ${rec.impact}</div>
        </div>
      `).join('');
    
    return `
      <section class="recommendations-section">
          <h2>Recommendations</h2>
          <div class="recommendations">
              ${recommendations}
          </div>
      </section>
    `;
  }

  /**
   * Generate test results section
   */
  generateTestResultsSection() {
    const testSuites = this.reportData.testResults.map(suite => {
      const results = suite.results || [];
      const passed = results.filter(r => r.status === 'passed').length;
      const failed = results.filter(r => r.status === 'failed').length;
      const skipped = results.filter(r => r.status === 'skipped').length;
      
      return `
        <div class="test-suite">
            <h4>${suite.testSuite}</h4>
            <div class="test-stats">
                <span class="passed">${passed} passed</span>
                <span class="failed">${failed} failed</span>
                <span class="skipped">${skipped} skipped</span>
            </div>
            <div class="test-details" style="display: none;">
                ${results.map(test => `
                  <div class="test-item ${test.status}">
                      <span class="test-name">${test.title || test.name}</span>
                      <span class="test-status">${test.status}</span>
                      ${test.error ? `<div class="test-error">${test.error}</div>` : ''}
                  </div>
                `).join('')}
            </div>
            <button class="toggle-details" onclick="toggleTestDetails(this)">Show Details</button>
        </div>
      `;
    }).join('');
    
    return `
      <section class="test-results-section">
          <h2>Test Results</h2>
          <div class="test-suites">
              ${testSuites}
          </div>
      </section>
    `;
  }

  /**
   * Generate performance section
   */
  generatePerformanceSection() {
    if (this.reportData.performanceResults.length === 0) {
      return '<section class="performance-section"><h2>Performance</h2><p>No performance data available.</p></section>';
    }
    
    const performanceData = this.reportData.performanceResults
      .map(result => `
        <div class="performance-result">
            <h4>${result.url || result.testName}</h4>
            <div class="performance-metrics">
                ${result.performance && result.performance.score ? 
                  `<div class="metric">Score: ${Math.round(result.performance.score)}/100</div>` : ''}
                ${result.timings && result.timings.loadEvent ? 
                  `<div class="metric">Load Time: ${result.timings.loadEvent}ms</div>` : ''}
                ${result.metrics && result.metrics.JSHeapUsedSizeMB ? 
                  `<div class="metric">Memory: ${result.metrics.JSHeapUsedSizeMB}MB</div>` : ''}
            </div>
        </div>
      `).join('');
    
    return `
      <section class="performance-section">
          <h2>Performance Results</h2>
          <div class="performance-results">
              ${performanceData}
          </div>
      </section>
    `;
  }

  /**
   * Generate accessibility section
   */
  generateAccessibilitySection() {
    if (this.reportData.accessibilityResults.length === 0) {
      return '<section class="accessibility-section"><h2>Accessibility</h2><p>No accessibility data available.</p></section>';
    }
    
    const accessibilityData = this.reportData.accessibilityResults
      .map(result => `
        <div class="accessibility-result">
            <h4>${result.testName || result.url}</h4>
            <div class="accessibility-score">Score: ${Math.round(result.score || 0)}/100</div>
            ${result.violations && result.violations.length > 0 ? `
              <div class="violations">
                  <h5>Violations (${result.violations.length})</h5>
                  ${result.violations.slice(0, 5).map(violation => `
                    <div class="violation ${violation.impact}">
                        <strong>${violation.id}</strong>: ${violation.description}
                        <div class="violation-help">${violation.help}</div>
                    </div>
                  `).join('')}
                  ${result.violations.length > 5 ? `<p>... and ${result.violations.length - 5} more</p>` : ''}
              </div>
            ` : ''}
        </div>
      `).join('');
    
    return `
      <section class="accessibility-section">
          <h2>Accessibility Results</h2>
          <div class="accessibility-results">
              ${accessibilityData}
          </div>
      </section>
    `;
  }

  /**
   * Generate responsive section
   */
  generateResponsiveSection() {
    if (this.reportData.responsiveResults.length === 0) {
      return '<section class="responsive-section"><h2>Responsive Design</h2><p>No responsive testing data available.</p></section>';
    }
    
    const responsiveData = this.reportData.responsiveResults
      .map(result => `
        <div class="responsive-result">
            <h4>Responsive Issues Summary</h4>
            <div class="responsive-summary">
                <div class="metric">Total Issues: ${result.summary.totalIssues}</div>
                <div class="metric high-severity">High Severity: ${result.summary.issuesBySeverity.high || 0}</div>
                <div class="metric medium-severity">Medium Severity: ${result.summary.issuesBySeverity.medium || 0}</div>
            </div>
            ${result.allIssues && result.allIssues.length > 0 ? `
              <div class="issues">
                  <h5>Issues</h5>
                  ${result.allIssues.slice(0, 10).map(issue => `
                    <div class="issue ${issue.severity}">
                        <strong>${issue.type}</strong> (${issue.viewport}): ${issue.message}
                    </div>
                  `).join('')}
              </div>
            ` : ''}
        </div>
      `).join('');
    
    return `
      <section class="responsive-section">
          <h2>Responsive Design Results</h2>
          <div class="responsive-results">
              ${responsiveData}
          </div>
      </section>
    `;
  }

  /**
   * Generate screenshot section
   */
  generateScreenshotSection() {
    if (this.reportData.screenshots.length === 0) {
      return '<section class="screenshots-section"><h2>Visual Testing</h2><p>No screenshot data available.</p></section>';
    }
    
    const screenshots = this.reportData.screenshots
      .filter(screenshot => !screenshot.isBaseline && screenshot.percentage > 0.1)
      .map(screenshot => `
        <div class="screenshot-result">
            <h4>${screenshot.name}</h4>
            <div class="screenshot-info">
                <div class="metric">Difference: ${screenshot.percentage.toFixed(2)}%</div>
                <div class="status ${screenshot.percentage > 2 ? 'error' : 'warning'}">
                    ${screenshot.percentage > 2 ? 'Significant Change' : 'Minor Change'}
                </div>
            </div>
        </div>
      `).join('');
    
    return `
      <section class="screenshots-section">
          <h2>Visual Testing Results</h2>
          <div class="screenshot-summary">
              <div class="metric">Total Screenshots: ${this.reportData.screenshots.length}</div>
              <div class="metric">Visual Regressions: ${this.reportData.summary.screenshots.visualRegressions}</div>
              <div class="metric">New Baselines: ${this.reportData.summary.screenshots.newBaselines}</div>
          </div>
          ${screenshots.length > 0 ? `
            <div class="screenshot-results">
                <h3>Visual Changes Detected</h3>
                ${screenshots}
            </div>
          ` : '<p>No significant visual changes detected.</p>'}
      </section>
    `;
  }

  /**
   * Get status class based on score thresholds
   */
  getStatusClass(value, goodThreshold, warningThreshold) {
    if (value >= goodThreshold) return 'good';
    if (value >= warningThreshold) return 'warning';
    return 'error';
  }

  /**
   * Get CSS styles for the report
   */
  getReportCSS() {
    return `
      * { box-sizing: border-box; }
      body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
      .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
      .report-header { text-align: center; margin-bottom: 40px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .timestamp { color: #666; margin: 0; }
      .summary-section { margin-bottom: 40px; }
      .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
      .summary-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
      .summary-card.good { border-left: 4px solid #28a745; }
      .summary-card.warning { border-left: 4px solid #ffc107; }
      .summary-card.error { border-left: 4px solid #dc3545; }
      .metric { font-size: 2em; font-weight: bold; margin: 10px 0; }
      .recommendations-section, .test-results-section, .performance-section, .accessibility-section, .responsive-section, .screenshots-section {
        background: white; margin-bottom: 30px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      .recommendation { padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #ddd; }
      .recommendation.critical { border-left-color: #dc3545; background: #f8d7da; }
      .recommendation.high { border-left-color: #fd7e14; background: #fff3cd; }
      .recommendation.medium { border-left-color: #ffc107; background: #fff3cd; }
      .recommendation.low { border-left-color: #17a2b8; background: #d1ecf1; }
      .rec-meta { margin: 5px 0; }
      .category, .priority { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 10px; }
      .category { background: #e9ecef; }
      .priority { background: #6c757d; color: white; }
      .impact { font-size: 0.9em; color: #666; margin-top: 10px; }
      .test-suite { margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 6px; }
      .test-stats span { display: inline-block; margin-right: 15px; padding: 2px 8px; border-radius: 4px; }
      .passed { background: #d4edda; color: #155724; }
      .failed { background: #f8d7da; color: #721c24; }
      .skipped { background: #fff3cd; color: #856404; }
      .test-details { margin-top: 15px; }
      .test-item { padding: 8px; margin: 5px 0; border-radius: 4px; display: flex; justify-content: space-between; }
      .test-item.passed { background: #d4edda; }
      .test-item.failed { background: #f8d7da; }
      .test-item.skipped { background: #fff3cd; }
      .test-error { font-size: 0.9em; color: #721c24; margin-top: 5px; }
      .toggle-details { margin-top: 10px; padding: 5px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
      .performance-result, .accessibility-result, .responsive-result { margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 6px; }
      .performance-metrics, .accessibility-score { margin: 10px 0; }
      .violation, .issue { margin: 8px 0; padding: 8px; border-radius: 4px; }
      .violation.critical, .issue.high { background: #f8d7da; }
      .violation.serious, .issue.medium { background: #fff3cd; }
      .violation.moderate, .issue.low { background: #d1ecf1; }
      .violation-help { font-size: 0.9em; color: #666; margin-top: 5px; }
      .screenshot-result { margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 6px; }
      .screenshot-info { display: flex; justify-content: space-between; align-items: center; }
      .status.error { color: #dc3545; font-weight: bold; }
      .status.warning { color: #ffc107; font-weight: bold; }
      .report-footer { text-align: center; margin-top: 40px; color: #666; }
      @media (max-width: 768px) {
        .container { padding: 10px; }
        .summary-grid { grid-template-columns: 1fr; }
        .screenshot-info { flex-direction: column; align-items: flex-start; }
      }
    `;
  }

  /**
   * Get JavaScript for the report
   */
  getReportJavaScript() {
    return `
      function toggleTestDetails(button) {
        const details = button.parentElement.querySelector('.test-details');
        if (details.style.display === 'none') {
          details.style.display = 'block';
          button.textContent = 'Hide Details';
        } else {
          details.style.display = 'none';
          button.textContent = 'Show Details';
        }
      }
    `;
  }
}

// If run directly, generate a sample report
if (require.main === module) {
  const generator = new UITestReportGenerator();
  
  // Add sample data
  generator.addTestResults('Authentication Tests', [
    { title: 'Login with valid credentials', status: 'passed' },
    { title: 'Login with invalid credentials', status: 'passed' },
    { title: 'Logout functionality', status: 'failed', error: 'Logout button not found' }
  ]);
  
  generator.addPerformanceResults({
    testName: 'Dashboard Load',
    performance: { score: 75 },
    timings: { loadEvent: 2500 },
    metrics: { JSHeapUsedSizeMB: 25.5 }
  });
  
  generator.generateHTMLReport()
    .then(paths => {
      console.log('Sample report generated successfully');
    })
    .catch(error => {
      console.error('Error generating report:', error);
    });
}

module.exports = UITestReportGenerator;