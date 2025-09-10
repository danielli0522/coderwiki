const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, waitForModal } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Form Validation Testing Suite', () => {
  let responsiveTester;
  let accessibilityTester;

  beforeEach(async () => {
    responsiveTester = new ResponsiveTester(page);
    accessibilityTester = new AccessibilityTester(page);
  });

  describe('Login Form Validation', () => {
    beforeEach(async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
    });

    test('should validate required fields', async () => {
      // Try submitting empty form
      await page.click(SELECTORS.loginButton);
      await page.waitForTimeout(1000);
      
      // Check for HTML5 validation or custom validation
      const validationResult = await page.evaluate(() => {
        const form = document.querySelector('form');
        const usernameInput = document.querySelector('input[name="username"], input[name="email"]');
        const passwordInput = document.querySelector('input[name="password"]');
        
        return {
          formValid: form.checkValidity(),
          usernameValid: usernameInput.validity.valid,
          passwordValid: passwordInput.validity.valid,
          hasCustomValidation: !!document.querySelector('.error-message, .invalid-feedback, .field-error'),
          usernameValidationMessage: usernameInput.validationMessage,
          passwordValidationMessage: passwordInput.validationMessage
        };
      });
      
      expect(validationResult.formValid).toBe(false);
      expect(validationResult.usernameValid || validationResult.passwordValid).toBe(false);
    });

    test('should validate email format if using email', async () => {
      const usernameInput = await page.$(SELECTORS.usernameInput);
      const inputType = await page.evaluate(input => input.type, usernameInput);
      
      if (inputType === 'email') {
        // Test invalid email format
        await page.fill(SELECTORS.usernameInput, 'invalid-email');
        await page.fill(SELECTORS.passwordInput, 'password123');
        await page.click(SELECTORS.loginButton);
        
        await page.waitForTimeout(1000);
        
        const emailValidation = await page.evaluate(() => {
          const emailInput = document.querySelector('input[type="email"]');
          return {
            isValid: emailInput.validity.valid,
            validationMessage: emailInput.validationMessage
          };
        });
        
        expect(emailValidation.isValid).toBe(false);
      }
    });

    test('should show validation feedback visually', async () => {
      // Submit invalid form
      await page.fill(SELECTORS.usernameInput, 'a'); // Too short
      await page.fill(SELECTORS.passwordInput, '123'); // Too short
      await page.click(SELECTORS.loginButton);
      
      await page.waitForTimeout(1000);
      
      const visualFeedback = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        const feedbackElements = document.querySelectorAll('.error-message, .invalid-feedback, .field-error, .error');
        
        let hasInvalidClass = false;
        let hasFocusOnError = false;
        
        inputs.forEach(input => {
          if (input.classList.contains('is-invalid') || input.classList.contains('error') || input.classList.contains('invalid')) {
            hasInvalidClass = true;
          }
          if (input === document.activeElement && !input.validity.valid) {
            hasFocusOnError = true;
          }
        });
        
        return {
          hasErrorMessages: feedbackElements.length > 0,
          hasInvalidStyling: hasInvalidClass,
          hasFocusOnError: hasFocusOnError
        };
      });
      
      // Should provide visual feedback
      expect(visualFeedback.hasErrorMessages || visualFeedback.hasInvalidStyling).toBe(true);
    });

    test('should clear validation on input change', async () => {
      // Submit invalid form first
      await page.click(SELECTORS.loginButton);
      await page.waitForTimeout(1000);
      
      // Fill in valid data
      await page.fill(SELECTORS.usernameInput, 'demo');
      await page.fill(SELECTORS.passwordInput, 'demo123');
      
      await page.waitForTimeout(500);
      
      const validationCleared = await page.evaluate(() => {
        const form = document.querySelector('form');
        const errorMessages = document.querySelectorAll('.error-message, .invalid-feedback');
        const invalidInputs = document.querySelectorAll('.is-invalid, .error, .invalid');
        
        return {
          formValid: form.checkValidity(),
          noErrorMessages: errorMessages.length === 0,
          noInvalidInputs: invalidInputs.length === 0
        };
      });
      
      expect(validationCleared.formValid).toBe(true);
    });
  });

  describe('Repository Form Validation', () => {
    beforeEach(async () => {
      await login(page, 'demo', 'demo123');
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
    });

    afterEach(async () => {
      await logout(page);
    });

    test('should validate repository form fields', async () => {
      const addButton = await page.$('.add-repository-btn, .add-repo-btn, .btn-primary');
      
      if (addButton) {
        await addButton.click();
        
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          // Try submitting empty form
          const submitButton = await page.$('button[type="submit"], .submit-btn, .save-btn');
          if (submitButton) {
            await submitButton.click();
            await page.waitForTimeout(1000);
            
            // Check for validation
            const formValidation = await page.evaluate(() => {
              const form = document.querySelector('.modal form, form');
              const inputs = form.querySelectorAll('input[required], input');
              
              let hasInvalidInputs = false;
              inputs.forEach(input => {
                if (!input.validity.valid) {
                  hasInvalidInputs = true;
                }
              });
              
              return {
                formValid: form.checkValidity(),
                hasInvalidInputs: hasInvalidInputs,
                hasErrorMessages: !!document.querySelector('.error-message, .invalid-feedback')
              };
            });
            
            expect(formValidation.formValid).toBe(false);
          }
        }
      }
    });

    test('should validate URL format for repository URL', async () => {
      const addButton = await page.$('.add-repository-btn, .add-repo-btn, .btn-primary');
      
      if (addButton) {
        await addButton.click();
        
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          // Find URL input
          const urlInput = await page.$('input[name*="url"], input[type="url"], input[placeholder*="url"]');
          
          if (urlInput) {
            // Test invalid URL
            await urlInput.fill('not-a-valid-url');
            
            const submitButton = await page.$('button[type="submit"], .submit-btn');
            if (submitButton) {
              await submitButton.click();
              await page.waitForTimeout(1000);
              
              const urlValidation = await page.evaluate(() => {
                const urlInput = document.querySelector('input[name*="url"], input[type="url"]');
                return {
                  isValid: urlInput.validity.valid,
                  validationMessage: urlInput.validationMessage,
                  hasVisualFeedback: urlInput.classList.contains('is-invalid') || 
                                   !!document.querySelector('.error-message')
                };
              });
              
              expect(urlValidation.isValid).toBe(false);
            }
          }
        }
      }
    });
  });

  describe('Form Accessibility', () => {
    test('should have proper form labels', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const labelAccessibility = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        const results = [];
        
        inputs.forEach(input => {
          const id = input.id;
          const name = input.name;
          const type = input.type;
          
          const hasLabel = !!document.querySelector(`label[for="${id}"]`);
          const hasAriaLabel = !!input.getAttribute('aria-label');
          const hasAriaLabelledby = !!input.getAttribute('aria-labelledby');
          const hasPlaceholder = !!input.placeholder;
          
          results.push({
            type,
            name,
            hasAccessibleName: hasLabel || hasAriaLabel || hasAriaLabelledby,
            hasPlaceholder
          });
        });
        
        return results;
      });
      
      // All inputs should have accessible names
      labelAccessibility.forEach(input => {
        expect(input.hasAccessibleName || input.hasPlaceholder).toBe(true);
      });
    });

    test('should associate error messages with inputs', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Submit invalid form to trigger errors
      await page.click(SELECTORS.loginButton);
      await page.waitForTimeout(1000);
      
      const errorAssociation = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        const results = [];
        
        inputs.forEach(input => {
          const hasAriaDescribedby = !!input.getAttribute('aria-describedby');
          const hasAriaInvalid = input.getAttribute('aria-invalid') === 'true';
          const nearbyError = !!input.parentNode.querySelector('.error-message, .invalid-feedback');
          
          results.push({
            name: input.name,
            hasAriaDescribedby,
            hasAriaInvalid,
            nearbyError
          });
        });
        
        return results;
      });
      
      // At least some inputs should have proper error association
      const hasProperErrorAssociation = errorAssociation.some(input => 
        input.hasAriaDescribedby || input.hasAriaInvalid || input.nearbyError
      );
      
      expect(hasProperErrorAssociation).toBe(true);
    });

    test('should support keyboard navigation in forms', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const keyboardResult = await accessibilityTester.testKeyboardNavigation();
      
      // Should be able to navigate through form elements
      const formElements = keyboardResult.elements.filter(el => 
        el.tagName === 'INPUT' || el.tagName === 'BUTTON'
      );
      
      expect(formElements.length).toBeGreaterThanOrEqual(2); // At least username/email and password
      
      // No critical keyboard navigation issues
      const criticalIssues = keyboardResult.issues.filter(i => i.severity === 'critical');
      expect(criticalIssues).toHaveLength(0);
    });
  });

  describe('Form Responsive Behavior', () => {
    test('should be usable on mobile devices', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const formResults = await responsiveTester.testFormResponsiveness('form');
      
      // Mobile form should be usable
      const mobileResult = formResults.mobile;
      if (mobileResult && mobileResult.exists) {
        const criticalIssues = mobileResult.issues.filter(i => i.severity === 'high');
        expect(criticalIssues.length).toBeLessThanOrEqual(2); // Allow some mobile form issues
      }
    });

    test('should handle form input focus on mobile', async () => {
      // Set mobile viewport
      await page.setViewport({ width: 375, height: 667 });
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Test input focus behavior
      const usernameInput = await page.$(SELECTORS.usernameInput);
      await usernameInput.focus();
      
      const focusInfo = await page.evaluate(() => {
        const activeElement = document.activeElement;
        const viewport = {
          width: window.innerWidth,
          height: window.innerHeight
        };
        
        return {
          isFocused: activeElement && activeElement.matches('input'),
          viewportHeight: viewport.height,
          inputRect: activeElement ? activeElement.getBoundingClientRect() : null
        };
      });
      
      expect(focusInfo.isFocused).toBe(true);
      
      // Input should be visible when focused (not hidden by virtual keyboard)
      if (focusInfo.inputRect) {
        expect(focusInfo.inputRect.top).toBeGreaterThan(0);
      }
    });
  });

  describe('Form Visual States', () => {
    test('should show different states for form inputs', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      const usernameInput = await page.$(SELECTORS.usernameInput);
      
      // Test focus state
      await usernameInput.focus();
      await page.waitForTimeout(100);
      
      const focusState = await page.evaluate(input => {
        const computedStyle = window.getComputedStyle(input, ':focus');
        return {
          hasFocusOutline: computedStyle.outline !== 'none',
          hasBoxShadow: computedStyle.boxShadow !== 'none',
          hasBorderChange: computedStyle.borderColor !== 'initial'
        };
      }, usernameInput);
      
      // Should have some focus indication
      expect(
        focusState.hasFocusOutline || 
        focusState.hasBoxShadow || 
        focusState.hasBorderChange
      ).toBe(true);
      
      // Test filled state
      await usernameInput.type('demo');
      await usernameInput.blur();
      
      const filledState = await page.evaluate(input => {
        return {
          hasValue: input.value.length > 0,
          hasVisualChange: input.classList.length > 0
        };
      }, usernameInput);
      
      expect(filledState.hasValue).toBe(true);
    });
  });

  describe('Form Error Recovery', () => {
    test('should allow users to correct errors easily', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Submit invalid form
      await page.click(SELECTORS.loginButton);
      await page.waitForTimeout(1000);
      
      // Correct the errors
      await page.fill(SELECTORS.usernameInput, 'demo');
      await page.fill(SELECTORS.passwordInput, 'demo123');
      
      // Submit corrected form
      await page.click(SELECTORS.loginButton);
      
      // Should redirect on successful login
      await page.waitForTimeout(2000);
      const currentUrl = page.url();
      expect(currentUrl).not.toMatch(/login/);
    });

    test('should preserve form data when validation fails', async () => {
      await login(page, 'demo', 'demo123');
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const addButton = await page.$('.add-repository-btn, .add-repo-btn');
      
      if (addButton) {
        await addButton.click();
        
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          // Fill some data
          const nameInput = await page.$('input[name*="name"], input[placeholder*="name"]');
          if (nameInput) {
            await nameInput.fill('Test Repository');
            
            // Submit with incomplete data
            const submitButton = await page.$('button[type="submit"], .submit-btn');
            if (submitButton) {
              await submitButton.click();
              await page.waitForTimeout(1000);
              
              // Check if data is preserved
              const preservedValue = await page.evaluate(input => input.value, nameInput);
              expect(preservedValue).toBe('Test Repository');
            }
          }
        }
      }
      
      await logout(page);
    });
  });

  describe('Form Security', () => {
    test('should not expose sensitive data in error messages', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      // Submit with fake credentials
      await page.fill(SELECTORS.usernameInput, 'fake_user');
      await page.fill(SELECTORS.passwordInput, 'fake_password');
      await page.click(SELECTORS.loginButton);
      
      await page.waitForTimeout(2000);
      
      // Check error messages don't contain sensitive info
      const errorContent = await page.evaluate(() => {
        const errorElements = document.querySelectorAll('.error-message, .alert-danger, .error');
        return Array.from(errorElements).map(el => el.textContent.toLowerCase());
      });
      
      errorContent.forEach(message => {
        expect(message).not.toMatch(/fake_password/);
        expect(message).not.toMatch(/sql/);
        expect(message).not.toMatch(/database/);
      });
    });

    test('should prevent form submission during processing', async () => {
      await page.goto(`${BASE_URL}/auth/login`);
      await waitForElement(page, SELECTORS.loginForm);
      
      await page.fill(SELECTORS.usernameInput, 'demo');
      await page.fill(SELECTORS.passwordInput, 'demo123');
      
      const submitButton = await page.$(SELECTORS.loginButton);
      
      // Click submit multiple times quickly
      await submitButton.click();
      await submitButton.click();
      await submitButton.click();
      
      await page.waitForTimeout(1000);
      
      // Button should be disabled or form should prevent multiple submissions
      const buttonState = await page.evaluate(button => {
        return {
          disabled: button.disabled,
          hasLoadingClass: button.classList.contains('loading') || 
                         button.classList.contains('disabled') ||
                         button.classList.contains('processing')
        };
      }, submitButton);
      
      // Should have some protection against multiple submissions
      expect(buttonState.disabled || buttonState.hasLoadingClass).toBe(true);
    });
  });
});