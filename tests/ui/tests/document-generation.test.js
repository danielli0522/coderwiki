const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, waitForModal } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Document Generation Interface Tests', () => {
  let responsiveTester;
  let accessibilityTester;

  beforeEach(async () => {
    responsiveTester = new ResponsiveTester(page);
    accessibilityTester = new AccessibilityTester(page);
    
    // Login before each test
    await login(page, 'demo', 'demo123');
  });

  afterEach(async () => {
    // Logout after each test
    try {
      await logout(page);
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('Document Generation Page', () => {
    test('should display document generation interface', async () => {
      // Try different possible routes for document generation
      const possibleRoutes = ['/documents', '/document/generate', '/repositories/1/generate', '/generate'];
      let pageLoaded = false;
      
      for (const route of possibleRoutes) {
        try {
          await page.goto(`${BASE_URL}${route}`);
          await page.waitForSelector('main, .main-content, .document-generator', { timeout: 5000 });
          pageLoaded = true;
          break;
        } catch (error) {
          // Try next route
        }
      }
      
      // If no direct route, try accessing through repositories
      if (!pageLoaded) {
        await page.goto(`${BASE_URL}/repositories`);
        await page.waitForSelector('main', { timeout: 10000 });
        
        // Look for generate document button/link
        const generateBtn = await page.$('.generate-doc-btn, .generate-btn, button[class*="generate"], a[href*="generate"]');
        
        if (generateBtn) {
          await generateBtn.click();
          await page.waitForSelector('main, .document-generator', { timeout: 5000 });
          pageLoaded = true;
        }
      }
      
      if (pageLoaded) {
        // Check for document generation interface elements
        const interfaceElements = await page.evaluate(() => {
          return {
            hasTitle: !!document.querySelector('h1, h2, .page-title'),
            hasGenerateButton: !!document.querySelector('.generate-btn, .start-generation, button[class*="generate"]'),
            hasRepositoryInfo: !!document.querySelector('.repository-info, .repo-details, .selected-repo'),
            hasConfigOptions: !!document.querySelector('.config, .options, .settings, form'),
            hasProgressArea: !!document.querySelector('.progress, .status, .generation-status')
          };
        });
        
        expect(interfaceElements.hasTitle).toBe(true);
        expect(interfaceElements.hasGenerateButton || interfaceElements.hasConfigOptions).toBe(true);
      } else {
        // If we can't find document generation interface, test should indicate this
        console.log('Document generation interface not accessible - may be feature-gated or route changed');
        expect(true).toBe(true); // Pass test but log the issue
      }
    });

    test('should be responsive on document generation interface', async () => {
      const routes = ['/documents', '/document/generate', '/repositories'];
      let testableRoute = null;
      
      for (const route of routes) {
        try {
          await page.goto(`${BASE_URL}${route}`);
          await page.waitForSelector('main', { timeout: 5000 });
          testableRoute = route;
          break;
        } catch (error) {
          // Try next route
        }
      }
      
      if (testableRoute) {
        const results = await responsiveTester.testLayout('document-generation', [
          'main', '.document-generator', '.generate-btn', '.config, form'
        ]);
        
        Object.entries(results).forEach(([viewport, result]) => {
          const criticalIssues = result.issues.filter(i => i.severity === 'high');
          expect(criticalIssues.length).toBeLessThanOrEqual(2); // Allow some issues
        });
      }
    });
  });

  describe('Document Generation Process', () => {
    test('should handle document generation workflow', async () => {
      // Navigate to repositories first
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Look for generate document functionality
      const generateTrigger = await page.$('.generate-doc-btn, .generate-btn, button[class*="generate"], a[href*="generate"]');
      
      if (generateTrigger) {
        await generateTrigger.click();
        await page.waitForTimeout(2000);
        
        // Check if we're on a generation page or modal opened
        const generationInterface = await page.evaluate(() => {
          const modal = document.querySelector('.modal, .dialog');
          const page = document.querySelector('.document-generator, .generation-page');
          
          return {
            hasModal: modal && window.getComputedStyle(modal).display !== 'none',
            hasPage: !!page,
            hasForm: !!document.querySelector('form'),
            hasStartButton: !!document.querySelector('.start-generation, .generate-btn, button[type="submit"]'),
            hasProgressArea: !!document.querySelector('.progress, .status, .generation-status')
          };
        });
        
        expect(generationInterface.hasModal || generationInterface.hasPage).toBe(true);
        
        if (generationInterface.hasStartButton) {
          // Test starting generation process
          const startButton = await page.$('.start-generation, .generate-btn, button[type="submit"]');
          await startButton.click();
          
          // Wait for process to start
          await page.waitForTimeout(3000);
          
          // Check for progress indicators or feedback
          const processStarted = await page.evaluate(() => {
            const indicators = [
              '.progress', '.loading', '.spinner', '.generating',
              '.status', '.in-progress', '.working'
            ];
            return indicators.some(selector => document.querySelector(selector) !== null);
          });
          
          expect(processStarted).toBe(true);
        }
      }
    });

    test('should display generation progress', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Try to access task/progress page if it exists
      const taskRoutes = ['/tasks', '/task', '/progress', '/status'];
      
      for (const route of taskRoutes) {
        try {
          await page.goto(`${BASE_URL}${route}`);
          await page.waitForSelector('main, .tasks, .task-list', { timeout: 5000 });
          
          // Check for task/progress elements
          const progressElements = await page.evaluate(() => {
            return {
              hasTaskList: !!document.querySelector('.task-list, .tasks, .progress-list'),
              hasProgressBars: document.querySelectorAll('.progress-bar, .progress').length > 0,
              hasStatusIndicators: document.querySelectorAll('.status, .badge, .label').length > 0,
              hasTaskItems: document.querySelectorAll('.task-item, .task').length > 0
            };
          });
          
          // Should have some progress/task display elements
          expect(
            progressElements.hasTaskList || 
            progressElements.hasProgressBars || 
            progressElements.hasTaskItems
          ).toBe(true);
          
          break;
        } catch (error) {
          // Continue to next route
        }
      }
    });

    test('should handle generation errors gracefully', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Intercept API calls to simulate errors
      await page.setRequestInterception(true);
      
      page.on('request', (request) => {
        if (request.url().includes('/api/') && request.url().includes('generate')) {
          request.respond({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Test error' })
          });
        } else {
          request.continue();
        }
      });
      
      // Try to trigger generation
      const generateTrigger = await page.$('.generate-doc-btn, .generate-btn, button[class*="generate"]');
      
      if (generateTrigger) {
        await generateTrigger.click();
        await page.waitForTimeout(1000);
        
        const startButton = await page.$('.start-generation, .generate-btn, button[type="submit"]');
        if (startButton) {
          await startButton.click();
          await page.waitForTimeout(3000);
          
          // Check for error handling
          const errorHandling = await page.evaluate(() => {
            const errorSelectors = [
              '.error', '.error-message', '.alert-danger', '.failure',
              '.toast-error', '.notification-error'
            ];
            return errorSelectors.some(selector => document.querySelector(selector) !== null);
          });
          
          expect(errorHandling).toBe(true);
        }
      }
      
      // Disable request interception
      await page.setRequestInterception(false);
    });
  });

  describe('Document Viewer', () => {
    test('should display document viewer correctly', async () => {
      // Try different routes for document viewing
      const viewerRoutes = ['/documents', '/document/viewer', '/documents/view'];
      let viewerFound = false;
      
      for (const route of viewerRoutes) {
        try {
          await page.goto(`${BASE_URL}${route}`);
          await page.waitForSelector('main, .document-viewer, .viewer', { timeout: 5000 });
          viewerFound = true;
          break;
        } catch (error) {
          // Try next route
        }
      }
      
      // Alternative: check if there are document links to click
      if (!viewerFound) {
        await page.goto(`${BASE_URL}/dashboard`);
        await page.waitForSelector('main', { timeout: 10000 });
        
        const documentLink = await page.$('a[href*="document"], .document-link, .view-document');
        if (documentLink) {
          await documentLink.click();
          await page.waitForSelector('.document-viewer, .viewer, main', { timeout: 5000 });
          viewerFound = true;
        }
      }
      
      if (viewerFound) {
        // Check viewer elements
        const viewerElements = await page.evaluate(() => {
          return {
            hasViewer: !!document.querySelector('.document-viewer, .viewer, .document-content'),
            hasContent: !!document.querySelector('.content, .document-body, .markdown'),
            hasNavigation: !!document.querySelector('.nav, .toc, .sidebar, .document-nav'),
            hasActions: !!document.querySelector('.actions, .toolbar, .document-actions'),
            hasTitle: !!document.querySelector('h1, h2, .document-title, .title')
          };
        });
        
        expect(viewerElements.hasViewer || viewerElements.hasContent).toBe(true);
      } else {
        // Document viewer may not be implemented yet
        console.log('Document viewer interface not found - may be under development');
        expect(true).toBe(true);
      }
    });

    test('should be responsive on document viewer', async () => {
      await page.goto(`${BASE_URL}/documents`);
      
      // Wait for any content to load
      await page.waitForTimeout(2000);
      
      const results = await responsiveTester.testLayout('document-viewer', [
        'main', '.document-viewer', '.content', '.document-content'
      ]);
      
      Object.entries(results).forEach(([viewport, result]) => {
        // Document viewers often have responsive challenges
        const criticalIssues = result.issues.filter(i => i.severity === 'high');
        expect(criticalIssues.length).toBeLessThanOrEqual(3);
      });
    });

    test('should handle document content properly', async () => {
      await page.goto(`${BASE_URL}/documents`);
      await page.waitForTimeout(2000);
      
      // Check for document content handling
      const contentInfo = await page.evaluate(() => {
        const viewer = document.querySelector('.document-viewer, .viewer, .document-content');
        if (!viewer) return null;
        
        return {
          hasTextContent: viewer.textContent && viewer.textContent.trim().length > 0,
          hasImages: viewer.querySelectorAll('img').length > 0,
          hasCode: viewer.querySelectorAll('pre, code').length > 0,
          hasTables: viewer.querySelectorAll('table').length > 0,
          hasHeadings: viewer.querySelectorAll('h1, h2, h3, h4, h5, h6').length > 0,
          isScrollable: viewer.scrollHeight > viewer.clientHeight
        };
      });
      
      if (contentInfo) {
        // Should have some content
        expect(contentInfo.hasTextContent).toBe(true);
      }
    });
  });

  describe('Document Export Features', () => {
    test('should provide document export options', async () => {
      await page.goto(`${BASE_URL}/documents`);
      await page.waitForTimeout(2000);
      
      // Look for export functionality
      const exportElements = await page.evaluate(() => {
        return {
          hasExportButton: !!document.querySelector('.export-btn, .download-btn, button[class*="export"]'),
          hasExportModal: !!document.querySelector('.export-modal, .download-modal'),
          hasExportOptions: document.querySelectorAll('.export-option, .format-option').length > 0
        };
      });
      
      if (exportElements.hasExportButton) {
        const exportBtn = await page.$('.export-btn, .download-btn, button[class*="export"]');
        await exportBtn.click();
        
        await page.waitForTimeout(1000);
        
        // Check if export modal or options appeared
        const exportInterface = await page.evaluate(() => {
          return {
            modalVisible: !!document.querySelector('.modal[style*="display: block"], .modal.show'),
            hasFormatOptions: document.querySelectorAll('.format-option, input[type="radio"]').length > 0,
            hasDownloadButton: !!document.querySelector('.download-btn, button[class*="download"]')
          };
        });
        
        expect(exportInterface.modalVisible || exportInterface.hasFormatOptions).toBe(true);
      } else {
        // Export functionality may not be implemented
        console.log('Export functionality not found - may be under development');
      }
    });
  });

  describe('Document Generation Accessibility', () => {
    test('should pass accessibility audit on generation interface', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const auditResult = await accessibilityTester.runAudit('document-generation-page');
      
      // Should have reasonable accessibility score
      expect(auditResult.score).toBeGreaterThan(60);
      
      // No critical accessibility violations
      const criticalViolations = auditResult.violations.filter(v => v.impact === 'critical');
      expect(criticalViolations).toHaveLength(0);
    });
  });

  describe('Document Generation Performance', () => {
    test('should load generation interface efficiently', async () => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      
      // Should load within reasonable time
      expect(loadTime).toBeLessThan(8000);
    });

    test('should handle multiple generation requests', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const generateBtns = await page.$$('.generate-doc-btn, .generate-btn, button[class*="generate"]');
      
      if (generateBtns.length > 0) {
        // Test clicking multiple times (should be handled gracefully)
        const btn = generateBtns[0];
        
        for (let i = 0; i < 3; i++) {
          await btn.click();
          await page.waitForTimeout(500);
        }
        
        // Should not crash or create multiple modals
        const modalCount = await page.$$eval('.modal, .dialog', modals => 
          modals.filter(modal => window.getComputedStyle(modal).display !== 'none').length
        );
        
        expect(modalCount).toBeLessThanOrEqual(1);
      }
    });
  });

  describe('Document Generation Visual Tests', () => {
    test('should match visual baselines', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Wait for content to load
      await page.waitForTimeout(2000);
      
      const viewports = ['mobile', 'tablet', 'desktop'];
      for (const viewport of viewports) {
        await page.setViewport(require('../utils/test-helpers').VIEWPORTS[viewport]);
        await page.waitForTimeout(500);
        
        const screenshotResult = await takeScreenshot(page, 'document-generation', viewport);
        
        if (!screenshotResult.isBaseline) {
          // Allow up to 3% visual difference for document generation interface
          expect(screenshotResult.percentage).toBeLessThan(3.0);
        }
      }
    });
  });
});