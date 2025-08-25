const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, testResponsive } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Authentication Flow Tests', () => {
  let responsiveTester;
  let accessibilityTester;

  beforeEach(async () => {
    responsiveTester = new ResponsiveTester(page);
    accessibilityTester = new AccessibilityTester(page);
  });

  describe('Login Page', () => {
    test('should display login form correctly', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Check form elements
      const usernameInput = await page.$(SELECTORS.usernameInput);
      const passwordInput = await page.$(SELECTORS.passwordInput);
      const loginButton = await page.$(SELECTORS.loginButton);
      
      expect(usernameInput).toBeTruthy();
      expect(passwordInput).toBeTruthy();
      expect(loginButton).toBeTruthy();
      
      // Check labels and accessibility
      const hasUsernameLabel = await page.$('label[for*="username"], label[for*="email"]');
      const hasPasswordLabel = await page.$('label[for*="password"]');
      
      expect(hasUsernameLabel).toBeTruthy();
      expect(hasPasswordLabel).toBeTruthy();
    });

    test('should be responsive across all viewports', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const results = await responsiveTester.testLayout('login-form', [
        SELECTORS.loginForm,
        SELECTORS.usernameInput,
        SELECTORS.passwordInput,
        SELECTORS.loginButton
      ]);
      
      // Check for responsive issues
      Object.values(results).forEach(result => {
        expect(result.issues.filter(i => i.severity === 'high')).toHaveLength(0);
      });
      
      // Ensure form exists on all viewports
      Object.values(results).forEach(result => {
        expect(result.elements[SELECTORS.loginForm].exists).toBe(true);
        expect(result.elements[SELECTORS.loginForm].visible).toBe(true);
      });
    });

    test('should pass accessibility standards', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const auditResult = await accessibilityTester.runAudit('login-page');
      
      // Should have high accessibility score
      expect(auditResult.score).toBeGreaterThan(80);
      
      // Critical violations should be zero
      const criticalViolations = auditResult.violations.filter(v => v.impact === 'critical');
      expect(criticalViolations).toHaveLength(0);
    });

    test('should handle form validation correctly', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Test empty form submission
      await page.click(SELECTORS.loginButton);
      
      // Check for validation messages
      await page.waitForTimeout(1000);
      const hasValidationMessage = await page.evaluate(() => {
        const form = document.querySelector('form');
        return form.checkValidity() === false || 
               document.querySelector('.error-message, .alert-danger, .invalid-feedback') !== null;
      });
      
      expect(hasValidationMessage).toBe(true);
      
      // Test invalid credentials
      await page.fill(SELECTORS.usernameInput, 'invalid_user');
      await page.fill(SELECTORS.passwordInput, 'wrong_password');
      await page.click(SELECTORS.loginButton);
      
      // Wait for error message
      await page.waitForTimeout(2000);
      const errorMessage = await page.$('.error-message, .alert-danger, .text-danger');
      expect(errorMessage).toBeTruthy();
    });

    test('should support keyboard navigation', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const keyboardResult = await accessibilityTester.testKeyboardNavigation();
      
      // Should be able to navigate to all form elements
      const focusableElements = keyboardResult.elements;
      const formElements = focusableElements.filter(el => 
        el.tagName === 'INPUT' || el.tagName === 'BUTTON'
      );
      
      expect(formElements.length).toBeGreaterThanOrEqual(3); // username, password, submit
      
      // No critical keyboard issues
      const criticalIssues = keyboardResult.issues.filter(i => i.severity === 'critical');
      expect(criticalIssues).toHaveLength(0);
    });

    test('should take visual regression screenshots', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Test across different viewports
      const viewports = ['mobile', 'tablet', 'desktop'];
      for (const viewport of viewports) {
        await page.setViewport(require('../utils/test-helpers').VIEWPORTS[viewport]);
        await page.waitForTimeout(500);
        
        const screenshotResult = await takeScreenshot(page, 'login-page', viewport);
        
        if (!screenshotResult.isBaseline) {
          // Allow up to 2% visual difference
          expect(screenshotResult.percentage).toBeLessThan(2.0);
        }
      }
    });
  });

  describe('Login Functionality', () => {
    test('should login with valid credentials', async () => {
      const loginSuccess = await login(page, 'demo', 'demo123');
      expect(loginSuccess).toBe(true);
      
      // Check redirect to dashboard
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/dashboard|home/);
      
      // Check for logout button or user menu
      const logoutElement = await page.$(SELECTORS.logoutButton);
      expect(logoutElement).toBeTruthy();
    });

    test('should show error for invalid credentials', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      await page.fill(SELECTORS.usernameInput, 'invalid_user');
      await page.fill(SELECTORS.passwordInput, 'wrong_password');
      
      await Promise.all([
        page.waitForTimeout(2000), // Wait for potential redirect or error
        page.click(SELECTORS.loginButton)
      ]);
      
      // Should still be on login page
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/login/);
      
      // Should show error message
      const errorExists = await page.evaluate(() => {
        const errorSelectors = ['.error-message', '.alert-danger', '.text-danger', '.invalid-feedback'];
        return errorSelectors.some(selector => document.querySelector(selector) !== null);
      });
      expect(errorExists).toBe(true);
    });

    test('should handle login with different user accounts', async () => {
      const testAccounts = [
        { username: 'admin', password: 'admin123' },
        { username: 'demo', password: 'demo123' },
        { username: 'testuser', password: 'test123' }
      ];
      
      for (const account of testAccounts) {
        // Logout first if needed
        if (page.url().includes('dashboard')) {
          await logout(page);
        }
        
        const loginSuccess = await login(page, account.username, account.password);
        expect(loginSuccess).toBe(true);
        
        // Verify successful login
        const hasLogoutButton = await page.$(SELECTORS.logoutButton);
        expect(hasLogoutButton).toBeTruthy();
        
        await logout(page);
      }
    });
  });

  describe('Logout Functionality', () => {
    test('should logout successfully', async () => {
      // Login first
      await login(page, 'demo', 'demo123');
      
      // Logout
      await logout(page);
      
      // Should redirect to login page
      await page.waitForTimeout(1000);
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/login|auth/);
      
      // Should not have access to protected pages
      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForTimeout(1000);
      const redirectedUrl = page.url();
      expect(redirectedUrl).toMatch(/login|auth/);
    });

    test('should clear session data on logout', async () => {
      // Login first
      await login(page, 'demo', 'demo123');
      
      // Check session data exists
      const beforeLogout = await page.evaluate(() => {
        return {
          localStorage: Object.keys(localStorage).length > 0,
          sessionStorage: Object.keys(sessionStorage).length > 0,
          cookies: document.cookie.length > 0
        };
      });
      
      // Logout
      await logout(page);
      
      // Check session data cleared
      const afterLogout = await page.evaluate(() => {
        return {
          localStorage: Object.keys(localStorage).length > 0,
          sessionStorage: Object.keys(sessionStorage).length > 0,
          cookies: document.cookie.length > 0
        };
      });
      
      // At least one storage method should be cleared
      expect(
        !afterLogout.localStorage || 
        !afterLogout.sessionStorage || 
        !afterLogout.cookies
      ).toBe(true);
    });
  });

  describe('Session Management', () => {
    test('should handle session timeout gracefully', async () => {
      // Login
      await login(page, 'demo', 'demo123');
      
      // Simulate session expiry by clearing cookies
      const cookies = await page.cookies();
      await page.deleteCookie(...cookies);
      
      // Try to access protected page
      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForTimeout(2000);
      
      // Should redirect to login
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/login|auth/);
    });

    test('should maintain session across page reloads', async () => {
      // Login
      await login(page, 'demo', 'demo123');
      const initialUrl = page.url();
      
      // Reload page
      await page.reload({ waitUntil: 'networkidle' });
      
      // Should still be logged in
      const afterReloadUrl = page.url();
      expect(afterReloadUrl).toBe(initialUrl);
      
      const logoutButton = await page.$(SELECTORS.logoutButton);
      expect(logoutButton).toBeTruthy();
    });
  });

  afterEach(async () => {
    // Clean up - logout if logged in
    try {
      const logoutButton = await page.$(SELECTORS.logoutButton);
      if (logoutButton) {
        await logout(page);
      }
    } catch (error) {
      // Ignore errors during cleanup
    }
  });
});