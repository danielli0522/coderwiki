const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, testResponsive } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Dashboard Functionality Tests', () => {
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

  describe('Dashboard Layout', () => {
    test('should display all dashboard components', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Check for main dashboard elements
      const components = {
        navbar: await page.$(SELECTORS.navbar),
        sidebar: await page.$(SELECTORS.sidebar),
        statsCards: await page.$$(SELECTORS.statsCards),
        recentActivity: await page.$(SELECTORS.recentActivity),
        repositoryList: await page.$(SELECTORS.repositoryList)
      };
      
      expect(components.navbar).toBeTruthy();
      expect(components.sidebar).toBeTruthy();
      expect(components.statsCards.length).toBeGreaterThan(0);
      // Recent activity and repository list may be empty for new users
    });

    test('should be responsive across all viewports', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      const results = await responsiveTester.testLayout('dashboard', [
        SELECTORS.dashboard,
        SELECTORS.navbar,
        SELECTORS.sidebar,
        SELECTORS.statsCards
      ]);
      
      // Check for critical responsive issues
      Object.entries(results).forEach(([viewport, result]) => {
        const criticalIssues = result.issues.filter(i => i.severity === 'high');
        expect(criticalIssues).toHaveLength(0);
        
        // Dashboard should exist on all viewports
        expect(result.elements[SELECTORS.dashboard].exists).toBe(true);
      });
    });

    test('should handle mobile navigation correctly', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      const navResults = await responsiveTester.testNavigationResponsiveness();
      
      // Mobile should have hamburger menu
      expect(navResults.mobile.hasMobileToggle || navResults.mobile.mobileToggleVisible).toBe(true);
      
      // Desktop should not show mobile toggle
      expect(navResults.desktop.mobileToggleVisible).toBe(false);
    });

    test('should pass accessibility standards', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      const auditResult = await accessibilityTester.runAudit('dashboard');
      
      // Should have reasonable accessibility score
      expect(auditResult.score).toBeGreaterThan(70);
      
      // No critical accessibility violations
      const criticalViolations = auditResult.violations.filter(v => v.impact === 'critical');
      expect(criticalViolations).toHaveLength(0);
    });
  });

  describe('Statistics Cards', () => {
    test('should display statistics cards with data', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Wait for stats to load
      await page.waitForTimeout(2000);
      
      const statsInfo = await page.evaluate(() => {
        const cards = document.querySelectorAll('.stats-card, .stat-card, .card');
        return Array.from(cards).map(card => {
          const title = card.querySelector('h3, h4, h5, .card-title')?.textContent?.trim();
          const value = card.querySelector('.stat-value, .card-text, .number')?.textContent?.trim();
          return { title, value, hasContent: !!(title && value) };
        });
      });
      
      // Should have at least some stats cards
      expect(statsInfo.length).toBeGreaterThan(0);
      
      // At least one card should have content
      const hasContent = statsInfo.some(stat => stat.hasContent);
      expect(hasContent).toBe(true);
    });

    test('should handle loading states', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      
      // Check for loading indicators
      const hasLoadingStates = await page.evaluate(() => {
        const loadingSelectors = ['.loading', '.spinner', '.skeleton', '.shimmer'];
        return loadingSelectors.some(selector => document.querySelector(selector) !== null);
      });
      
      // Either has loading states or content loads immediately
      const hasStatsContent = await page.$$eval('.stats-card, .stat-card', cards => 
        cards.length > 0
      );
      
      expect(hasLoadingStates || hasStatsContent).toBe(true);
    });
  });

  describe('Repository List', () => {
    test('should display repository list or empty state', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Wait for repository list to load
      await page.waitForTimeout(3000);
      
      const repoInfo = await page.evaluate(() => {
        const repoList = document.querySelector('.repository-list, .repo-list');
        const repoItems = document.querySelectorAll('.repository-card, .repo-item, .repo-card');
        const emptyState = document.querySelector('.empty-state, .no-repositories, .empty');
        
        return {
          hasRepoList: !!repoList,
          repoCount: repoItems.length,
          hasEmptyState: !!emptyState
        };
      });
      
      // Should have either repositories or empty state
      expect(repoInfo.hasRepoList || repoInfo.hasEmptyState).toBe(true);
    });

    test('should handle repository cards correctly', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      await page.waitForTimeout(3000);
      
      const repoCards = await page.$$('.repository-card, .repo-card');
      
      if (repoCards.length > 0) {
        // Test first repository card
        const firstCard = repoCards[0];
        
        // Check card elements
        const cardInfo = await page.evaluate(card => {
          const title = card.querySelector('h3, h4, h5, .card-title')?.textContent?.trim();
          const description = card.querySelector('.description, .card-text')?.textContent?.trim();
          const actions = card.querySelectorAll('button, .btn, a[class*="btn"]');
          
          return {
            hasTitle: !!title,
            hasDescription: !!description,
            actionCount: actions.length
          };
        }, firstCard);
        
        expect(cardInfo.hasTitle).toBe(true);
        expect(cardInfo.actionCount).toBeGreaterThan(0);
      }
    });
  });

  describe('Recent Activity', () => {
    test('should display recent activity or empty state', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      await page.waitForTimeout(2000);
      
      const activityInfo = await page.evaluate(() => {
        const activitySection = document.querySelector('.recent-activity, .activity-list');
        const activityItems = document.querySelectorAll('.activity-item, .activity');
        const emptyState = document.querySelector('.no-activity, .empty-activity');
        
        return {
          hasActivitySection: !!activitySection,
          activityCount: activityItems.length,
          hasEmptyState: !!emptyState
        };
      });
      
      // Should have activity section
      expect(activityInfo.hasActivitySection || activityInfo.activityCount > 0).toBe(true);
    });
  });

  describe('Dashboard Navigation', () => {
    test('should navigate to different sections', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Test navigation links
      const navLinks = await page.$$(SELECTORS.navLinks);
      
      if (navLinks.length > 0) {
        const linkTexts = await Promise.all(
          navLinks.map(link => page.evaluate(el => el.textContent?.trim(), link))
        );
        
        // Should have common navigation items
        const expectedItems = ['Dashboard', 'Repositories', 'Documents', 'Tasks'];
        const hasCommonItems = expectedItems.some(item => 
          linkTexts.some(text => text?.toLowerCase().includes(item.toLowerCase()))
        );
        
        expect(hasCommonItems).toBe(true);
      }
    });

    test('should handle sidebar toggle on mobile', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Set mobile viewport
      await page.setViewport({ width: 375, height: 667 });
      await page.waitForTimeout(500);
      
      // Look for mobile menu toggle
      const mobileToggle = await page.$('.navbar-toggler, .mobile-toggle, .hamburger, .menu-toggle');
      
      if (mobileToggle) {
        // Test toggle functionality
        const initialState = await page.evaluate(() => {
          const sidebar = document.querySelector('.sidebar, .nav-sidebar');
          return sidebar ? window.getComputedStyle(sidebar).display : null;
        });
        
        await mobileToggle.click();
        await page.waitForTimeout(500);
        
        const afterToggleState = await page.evaluate(() => {
          const sidebar = document.querySelector('.sidebar, .nav-sidebar');
          return sidebar ? window.getComputedStyle(sidebar).display : null;
        });
        
        // State should change after toggle
        expect(afterToggleState).not.toBe(initialState);
      }
    });
  });

  describe('Dashboard Performance', () => {
    test('should load dashboard within reasonable time', async () => {
      const startTime = Date.now();
      
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      const loadTime = Date.now() - startTime;
      
      // Dashboard should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should not have memory leaks', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Get initial metrics
      const initialMetrics = await page.metrics();
      
      // Navigate around the dashboard
      const navLinks = await page.$$('.nav-link');
      if (navLinks.length > 0) {
        for (let i = 0; i < Math.min(3, navLinks.length); i++) {
          await navLinks[i].click();
          await page.waitForTimeout(1000);
        }
      }
      
      // Get final metrics
      const finalMetrics = await page.metrics();
      
      // Memory shouldn't increase dramatically
      const memoryIncrease = finalMetrics.JSHeapUsedSize - initialMetrics.JSHeapUsedSize;
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // Less than 10MB increase
    });
  });

  describe('Dashboard Visual Regression', () => {
    test('should match visual baselines', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Wait for content to load
      await page.waitForTimeout(3000);
      
      const viewports = ['mobile', 'tablet', 'desktop'];
      for (const viewport of viewports) {
        await page.setViewport(require('../utils/test-helpers').VIEWPORTS[viewport]);
        await page.waitForTimeout(500);
        
        const screenshotResult = await takeScreenshot(page, 'dashboard', viewport);
        
        if (!screenshotResult.isBaseline) {
          // Allow up to 3% visual difference for dashboard due to dynamic content
          expect(screenshotResult.percentage).toBeLessThan(3.0);
        }
      }
    });
  });

  describe('Dashboard Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForElement(page, SELECTORS.dashboard);
      
      // Intercept and fail API requests to test error handling
      await page.setRequestInterception(true);
      
      page.on('request', (request) => {
        if (request.url().includes('/api/')) {
          request.abort();
        } else {
          request.continue();
        }
      });
      
      // Reload to trigger failed API calls
      await page.reload({ waitUntil: 'networkidle' });
      
      // Check for error states
      const hasErrorStates = await page.evaluate(() => {
        const errorSelectors = ['.error', '.error-message', '.alert-danger', '.error-state'];
        return errorSelectors.some(selector => document.querySelector(selector) !== null);
      });
      
      // Should have error handling (either error messages or fallback content)
      const hasContent = await page.evaluate(() => {
        const dashboard = document.querySelector('.dashboard, main');
        return dashboard && dashboard.textContent.trim().length > 0;
      });
      
      expect(hasErrorStates || hasContent).toBe(true);
      
      // Disable request interception
      await page.setRequestInterception(false);
    });
  });
});