const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, waitForModal, closeModal } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Modal Dialog and Interaction Tests', () => {
  let responsiveTester;
  let accessibilityTester;

  beforeEach(async () => {
    responsiveTester = new ResponsiveTester(page);
    accessibilityTester = new AccessibilityTester(page);
    
    // Login before each test
    await login(page, 'demo', 'demo123');
  });

  afterEach(async () => {
    // Close any open modals and logout
    try {
      await closeModal(page);
    } catch (error) {
      // Ignore if no modal to close
    }
    
    try {
      await logout(page);
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('Modal Structure and Behavior', () => {
    test('should open modal correctly', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Look for modal trigger buttons
      const modalTriggers = await page.$$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn, .add-repo-btn');
      
      if (modalTriggers.length > 0) {
        const trigger = modalTriggers[0];
        await trigger.click();
        
        // Wait for modal to appear
        const modalOpened = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog, .overlay');
          if (!modal) return false;
          
          const computedStyle = window.getComputedStyle(modal);
          return computedStyle.display !== 'none' && computedStyle.visibility !== 'hidden';
        }, { timeout: 5000 }).catch(() => false);
        
        expect(modalOpened).toBe(true);
        
        if (modalOpened) {
          // Check modal structure
          const modalStructure = await page.evaluate(() => {
            const modal = document.querySelector('.modal, .dialog');
            return {
              hasBackdrop: !!document.querySelector('.modal-backdrop, .overlay, .backdrop'),
              hasHeader: !!modal.querySelector('.modal-header, .dialog-header, .header'),
              hasBody: !!modal.querySelector('.modal-body, .dialog-body, .body, .content'),
              hasFooter: !!modal.querySelector('.modal-footer, .dialog-footer, .footer, .actions'),
              hasCloseButton: !!modal.querySelector('.close, .modal-close, .dialog-close, [aria-label="close"]'),
              hasTitle: !!modal.querySelector('.modal-title, .dialog-title, h1, h2, h3, h4, h5, h6')
            };
          });
          
          expect(modalStructure.hasBody).toBe(true);
          expect(modalStructure.hasCloseButton || modalStructure.hasFooter).toBe(true);
        }
      }
    });

    test('should close modal with close button', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn, .add-repo-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Find and click close button
        const closeButton = await page.$('.close, .modal-close, .dialog-close, [aria-label="close"]');
        
        if (closeButton) {
          await closeButton.click();
          
          // Wait for modal to close
          const modalClosed = await page.waitForFunction(() => {
            const modal = document.querySelector('.modal, .dialog');
            if (!modal) return true;
            
            const computedStyle = window.getComputedStyle(modal);
            return computedStyle.display === 'none' || computedStyle.visibility === 'hidden';
          }, { timeout: 5000 }).catch(() => false);
          
          expect(modalClosed).toBe(true);
        }
      }
    });

    test('should close modal with Escape key', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Press Escape key
        await page.keyboard.press('Escape');
        
        // Wait for modal to close
        const modalClosed = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          if (!modal) return true;
          
          const computedStyle = window.getComputedStyle(modal);
          return computedStyle.display === 'none' || computedStyle.visibility === 'hidden';
        }, { timeout: 5000 }).catch(() => false);
        
        expect(modalClosed).toBe(true);
      }
    });

    test('should close modal by clicking backdrop', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Click on backdrop/overlay
        const backdrop = await page.$('.modal-backdrop, .overlay, .backdrop');
        const modal = await page.$('.modal, .dialog');
        
        if (backdrop) {
          await backdrop.click();
        } else if (modal) {
          // Click outside modal content
          const modalBox = await modal.boundingBox();
          if (modalBox) {
            await page.click(modalBox.x - 10, modalBox.y - 10);
          }
        }
        
        // Wait for modal to close
        await page.waitForTimeout(1000);
        const modalClosed = await page.evaluate(() => {
          const modal = document.querySelector('.modal, .dialog');
          if (!modal) return true;
          
          const computedStyle = window.getComputedStyle(modal);
          return computedStyle.display === 'none' || computedStyle.visibility === 'hidden';
        });
        
        expect(modalClosed).toBe(true);
      }
    });
  });

  describe('Modal Responsiveness', () => {
    test('should be responsive across different viewports', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        const viewports = ['mobile', 'tablet', 'desktop'];
        
        for (const viewportName of viewports) {
          const viewport = require('../utils/test-helpers').VIEWPORTS[viewportName];
          await page.setViewport(viewport);
          await page.waitForTimeout(500);
          
          // Open modal
          await modalTrigger.click();
          await waitForModal(page);
          
          // Test modal responsiveness
          const modalInfo = await page.evaluate(() => {
            const modal = document.querySelector('.modal, .dialog');
            if (!modal) return null;
            
            const rect = modal.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            
            return {
              width: rect.width,
              height: rect.height,
              fitsInViewport: rect.width <= viewportWidth && rect.height <= viewportHeight,
              overflowsHorizontally: rect.width > viewportWidth,
              overflowsVertically: rect.height > viewportHeight,
              isCentered: Math.abs(rect.left + rect.width/2 - viewportWidth/2) < 50
            };
          });
          
          if (modalInfo) {
            // Modal should fit in viewport or be scrollable
            expect(modalInfo.fitsInViewport || !modalInfo.overflowsHorizontally).toBe(true);
            
            // On mobile, modal should use most of the width
            if (viewportName === 'mobile') {
              expect(modalInfo.width / viewport.width).toBeGreaterThan(0.8);
            }
          }
          
          // Close modal for next iteration
          await closeModal(page);
        }
      }
    });

    test('should handle modal content overflow', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Test scroll behavior with long content
        const scrollInfo = await page.evaluate(() => {
          const modal = document.querySelector('.modal, .dialog');
          const modalBody = modal?.querySelector('.modal-body, .dialog-body, .body, .content');
          
          if (!modalBody) return null;
          
          return {
            hasScroll: modalBody.scrollHeight > modalBody.clientHeight,
            scrollable: getComputedStyle(modalBody).overflowY !== 'hidden',
            maxHeight: getComputedStyle(modalBody).maxHeight
          };
        });
        
        if (scrollInfo) {
          // If content overflows, it should be scrollable
          if (scrollInfo.hasScroll) {
            expect(scrollInfo.scrollable).toBe(true);
          }
        }
      }
    });
  });

  describe('Modal Forms and Interactions', () => {
    test('should handle form submission in modal', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Check if modal has a form
        const hasForm = await page.$('.modal form, .dialog form');
        
        if (hasForm) {
          // Try form validation
          const submitButton = await page.$('.modal button[type="submit"], .modal .submit-btn, .modal .save-btn');
          
          if (submitButton) {
            // Submit empty form to test validation
            await submitButton.click();
            await page.waitForTimeout(1000);
            
            // Check for validation feedback
            const hasValidation = await page.evaluate(() => {
              const validationSelectors = [
                '.error-message', '.invalid-feedback', '.error', '.field-error',
                'input:invalid', '.is-invalid', '.has-error'
              ];
              return validationSelectors.some(selector => document.querySelector(selector) !== null);
            });
            
            // Should have validation or form should have submitted (modal closed)
            const modalStillOpen = await page.evaluate(() => {
              const modal = document.querySelector('.modal, .dialog');
              if (!modal) return false;
              return getComputedStyle(modal).display !== 'none';
            });
            
            expect(hasValidation || !modalStillOpen).toBe(true);
          }
        }
      }
    });

    test('should handle form input interactions', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Find form inputs
        const inputs = await page.$$('.modal input, .dialog input');
        
        if (inputs.length > 0) {
          const firstInput = inputs[0];
          
          // Test input focus
          await firstInput.focus();
          
          const isFocused = await page.evaluate(input => {
            return document.activeElement === input;
          }, firstInput);
          
          expect(isFocused).toBe(true);
          
          // Test input typing
          await firstInput.type('test input');
          
          const inputValue = await page.evaluate(input => input.value, firstInput);
          expect(inputValue).toBe('test input');
          
          // Test input validation styling
          await firstInput.blur();
          await page.waitForTimeout(500);
          
          const hasValidationStyling = await page.evaluate(input => {
            const classList = input.classList;
            return classList.contains('is-valid') || 
                   classList.contains('is-invalid') || 
                   classList.contains('error') || 
                   classList.contains('success');
          }, firstInput);
          
          // Validation styling is optional but good to have
          // expect(hasValidationStyling).toBe(true);
        }
      }
    });
  });

  describe('Modal Accessibility', () => {
    test('should have proper ARIA attributes', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        const ariaAttributes = await page.evaluate(() => {
          const modal = document.querySelector('.modal, .dialog');
          if (!modal) return null;
          
          return {
            hasRole: modal.hasAttribute('role'),
            roleValue: modal.getAttribute('role'),
            hasAriaLabel: modal.hasAttribute('aria-label') || modal.hasAttribute('aria-labelledby'),
            hasAriaModal: modal.hasAttribute('aria-modal'),
            hasAriaHidden: modal.hasAttribute('aria-hidden'),
            tabIndex: modal.getAttribute('tabindex')
          };
        });
        
        if (ariaAttributes) {
          // Modal should have proper role
          expect(ariaAttributes.hasRole).toBe(true);
          expect(['dialog', 'alertdialog', 'modal'].includes(ariaAttributes.roleValue)).toBe(true);
          
          // Should have accessible name
          expect(ariaAttributes.hasAriaLabel).toBe(true);
        }
      }
    });

    test('should trap focus within modal', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        // Find focusable elements in modal
        const focusableElements = await page.$$eval('.modal, .dialog', modals => {
          const modal = modals[0];
          const focusableSelectors = [
            'button', 'input', 'select', 'textarea', 'a[href]',
            '[tabindex]:not([tabindex="-1"])', '[contenteditable]'
          ];
          
          const focusable = [];
          focusableSelectors.forEach(selector => {
            modal.querySelectorAll(selector).forEach(el => {
              if (!el.disabled && !el.hidden) {
                focusable.push({
                  tagName: el.tagName,
                  type: el.type || null,
                  tabIndex: el.tabIndex
                });
              }
            });
          });
          
          return focusable;
        });
        
        if (focusableElements.length > 0) {
          // Test Tab navigation within modal
          await page.keyboard.press('Tab');
          
          const focusedElement = await page.evaluate(() => {
            const focused = document.activeElement;
            return {
              tagName: focused.tagName,
              isInModal: !!focused.closest('.modal, .dialog')
            };
          });
          
          // Focus should be trapped within modal
          expect(focusedElement.isInModal).toBe(true);
        }
      }
    });

    test('should pass accessibility audit', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        await modalTrigger.click();
        await waitForModal(page);
        
        const auditResult = await accessibilityTester.runAudit('modal-dialog', {
          include: '.modal, .dialog'
        });
        
        // Should have reasonable accessibility score
        expect(auditResult.score).toBeGreaterThan(70);
        
        // No critical violations in modal
        const criticalViolations = auditResult.violations.filter(v => v.impact === 'critical');
        expect(criticalViolations).toHaveLength(0);
      }
    });
  });

  describe('Modal Animation and Performance', () => {
    test('should have smooth animations', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        // Measure modal opening time
        const startTime = Date.now();
        await modalTrigger.click();
        await waitForModal(page);
        const openTime = Date.now() - startTime;
        
        // Modal should open reasonably quickly
        expect(openTime).toBeLessThan(2000);
        
        // Test modal closing time
        const closeStartTime = Date.now();
        await closeModal(page);
        
        const modalClosed = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          if (!modal) return true;
          return getComputedStyle(modal).display === 'none';
        }, { timeout: 3000 }).catch(() => false);
        
        const closeTime = Date.now() - closeStartTime;
        
        expect(modalClosed).toBe(true);
        expect(closeTime).toBeLessThan(1500);
      }
    });

    test('should not block main thread during animations', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        // Get initial metrics
        const initialMetrics = await page.metrics();
        
        // Open and close modal multiple times
        for (let i = 0; i < 3; i++) {
          await modalTrigger.click();
          await waitForModal(page);
          await closeModal(page);
          await page.waitForTimeout(100);
        }
        
        // Get final metrics
        const finalMetrics = await page.metrics();
        
        // Script duration shouldn't increase dramatically
        const scriptDurationIncrease = finalMetrics.ScriptDuration - initialMetrics.ScriptDuration;
        expect(scriptDurationIncrease).toBeLessThan(1000); // Less than 1 second
      }
    });
  });

  describe('Modal Visual Regression', () => {
    test('should match visual baselines', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const modalTrigger = await page.$('button[data-toggle="modal"], .modal-trigger, .add-repository-btn');
      
      if (modalTrigger) {
        const viewports = ['mobile', 'tablet', 'desktop'];
        
        for (const viewport of viewports) {
          await page.setViewport(require('../utils/test-helpers').VIEWPORTS[viewport]);
          await page.waitForTimeout(500);
          
          await modalTrigger.click();
          await waitForModal(page);
          
          const screenshotResult = await takeScreenshot(page, 'modal-dialog', viewport);
          
          if (!screenshotResult.isBaseline) {
            // Allow up to 2% visual difference for modals
            expect(screenshotResult.percentage).toBeLessThan(2.0);
          }
          
          await closeModal(page);
        }
      }
    });
  });
});