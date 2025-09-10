const { BASE_URL, SELECTORS, login, logout, takeScreenshot, waitForElement, waitForModal, closeModal } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('Repository Management UI Tests', () => {
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

  describe('Repository List Page', () => {
    test('should display repository list correctly', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      
      // Wait for page to load
      await page.waitForSelector('main, .main-content, .repositories', { timeout: 10000 });
      
      // Check for key elements
      const pageElements = await page.evaluate(() => {
        return {
          hasTitle: !!document.querySelector('h1, h2, .page-title'),
          hasAddButton: !!document.querySelector('.add-repository-btn, .add-repo-btn, .btn-primary'),
          hasRepositoryList: !!document.querySelector('.repository-list, .repo-list, .repositories'),
          hasRepositoryCards: document.querySelectorAll('.repository-card, .repo-card, .card').length > 0,
          hasEmptyState: !!document.querySelector('.empty-state, .no-repositories')
        };
      });
      
      expect(pageElements.hasTitle).toBe(true);
      expect(pageElements.hasAddButton || pageElements.hasRepositoryCards || pageElements.hasEmptyState).toBe(true);
    });

    test('should be responsive across viewports', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main, .main-content', { timeout: 10000 });
      
      const results = await responsiveTester.testLayout('repository-list', [
        '.repositories, .repository-list, main',
        '.add-repository-btn, .add-repo-btn',
        '.repository-card, .repo-card'
      ]);
      
      Object.entries(results).forEach(([viewport, result]) => {
        const criticalIssues = result.issues.filter(i => i.severity === 'high');
        expect(criticalIssues.length).toBeLessThanOrEqual(1); // Allow one critical issue
      });
    });

    test('should handle empty repository state', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main, .main-content', { timeout: 10000 });
      
      const hasRepositories = await page.$$eval('.repository-card, .repo-card', cards => cards.length > 0);
      
      if (!hasRepositories) {
        // Should show empty state
        const emptyStateExists = await page.evaluate(() => {
          const emptySelectors = ['.empty-state', '.no-repositories', '.empty', '.placeholder'];
          return emptySelectors.some(selector => document.querySelector(selector) !== null);
        });
        
        expect(emptyStateExists).toBe(true);
        
        // Should have add repository button or call-to-action
        const hasCallToAction = await page.evaluate(() => {
          const ctaSelectors = ['.add-repository', '.add-repo', '.get-started', '.cta-button'];
          return ctaSelectors.some(selector => document.querySelector(selector) !== null);
        });
        
        expect(hasCallToAction).toBe(true);
      }
    });
  });

  describe('Add Repository Modal/Form', () => {
    test('should open add repository modal', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Look for add repository button
      const addButton = await page.$('.add-repository-btn, .add-repo-btn, .btn-primary');
      
      if (addButton) {
        await addButton.click();
        
        // Wait for modal or form to appear
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog, .overlay');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          // Check modal content
          const modalContent = await page.evaluate(() => {
            const modal = document.querySelector('.modal, .dialog');
            return {
              hasTitle: !!modal.querySelector('.modal-title, .dialog-title, h1, h2, h3'),
              hasForm: !!modal.querySelector('form'),
              hasNameField: !!modal.querySelector('input[name*="name"], input[placeholder*="name"]'),
              hasUrlField: !!modal.querySelector('input[name*="url"], input[placeholder*="url"], input[type="url"]'),
              hasSubmitButton: !!modal.querySelector('button[type="submit"], .submit-btn, .save-btn')
            };
          });
          
          expect(modalContent.hasTitle).toBe(true);
          expect(modalContent.hasForm).toBe(true);
          expect(modalContent.hasNameField || modalContent.hasUrlField).toBe(true);
          expect(modalContent.hasSubmitButton).toBe(true);
        }
      }
    });

    test('should validate repository form fields', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const addButton = await page.$('.add-repository-btn, .add-repo-btn, .btn-primary');
      
      if (addButton) {
        await addButton.click();
        
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog, .overlay');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          // Try submitting empty form
          const submitButton = await page.$('button[type="submit"], .submit-btn, .save-btn');
          if (submitButton) {
            await submitButton.click();
            
            // Check for validation messages
            await page.waitForTimeout(1000);
            const hasValidation = await page.evaluate(() => {
              const validationSelectors = [
                '.error-message', '.invalid-feedback', '.error', '.field-error',
                'input:invalid', '.is-invalid'
              ];
              return validationSelectors.some(selector => document.querySelector(selector) !== null);
            });
            
            expect(hasValidation).toBe(true);
          }
        }
      }
    });

    test('should test repository form responsiveness', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const addButton = await page.$('.add-repository-btn, .add-repo-btn, .btn-primary');
      
      if (addButton) {
        await addButton.click();
        
        const modalAppeared = await page.waitForFunction(() => {
          const modal = document.querySelector('.modal, .dialog');
          return modal && window.getComputedStyle(modal).display !== 'none';
        }, { timeout: 5000 }).catch(() => false);
        
        if (modalAppeared) {
          await waitForModal(page);
          
          const formResults = await responsiveTester.testFormResponsiveness('.modal form, form');
          
          Object.entries(formResults).forEach(([viewport, result]) => {
            if (result.exists) {
              const criticalIssues = result.issues.filter(i => i.severity === 'high');
              expect(criticalIssues.length).toBeLessThanOrEqual(2); // Allow some form issues
            }
          });
        }
      }
    });
  });

  describe('Repository Cards', () => {
    test('should display repository information correctly', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const repositoryCards = await page.$$('.repository-card, .repo-card, .card');
      
      if (repositoryCards.length > 0) {
        // Test first repository card
        const firstCard = repositoryCards[0];
        
        const cardInfo = await page.evaluate(card => {
          return {
            hasTitle: !!card.querySelector('h3, h4, h5, .card-title, .repo-name'),
            hasDescription: !!card.querySelector('.description, .card-text, .repo-description'),
            hasActions: card.querySelectorAll('button, .btn, a[class*="btn"]').length > 0,
            hasStatus: !!card.querySelector('.status, .badge, .label'),
            hasMetadata: !!card.querySelector('.metadata, .repo-info, .created-date')
          };
        }, firstCard);
        
        expect(cardInfo.hasTitle).toBe(true);
        expect(cardInfo.hasActions).toBe(true);
      }
    });

    test('should handle repository card actions', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const repositoryCards = await page.$$('.repository-card, .repo-card, .card');
      
      if (repositoryCards.length > 0) {
        const firstCard = repositoryCards[0];
        
        // Look for action buttons
        const actionButtons = await firstCard.$$('button, .btn, a[class*="btn"]');
        
        if (actionButtons.length > 0) {
          const buttonTexts = await Promise.all(
            actionButtons.map(btn => page.evaluate(el => el.textContent?.trim().toLowerCase(), btn))
          );
          
          // Should have common actions
          const commonActions = ['view', 'edit', 'delete', 'sync', 'generate', 'analyze'];
          const hasCommonAction = buttonTexts.some(text => 
            commonActions.some(action => text?.includes(action))
          );
          
          expect(hasCommonAction).toBe(true);
        }
      }
    });

    test('should test repository card click behavior', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const repositoryCards = await page.$$('.repository-card, .repo-card, .card');
      
      if (repositoryCards.length > 0) {
        const firstCard = repositoryCards[0];
        const initialUrl = page.url();
        
        // Click on the card (not on buttons)
        await firstCard.click();
        await page.waitForTimeout(1000);
        
        const newUrl = page.url();
        
        // Should either navigate or show modal/details
        const hasNavigated = newUrl !== initialUrl;
        const hasModal = await page.evaluate(() => {
          const modal = document.querySelector('.modal, .dialog');
          return modal && window.getComputedStyle(modal).display !== 'none';
        });
        
        expect(hasNavigated || hasModal).toBe(true);
      }
    });
  });

  describe('Repository Search and Filtering', () => {
    test('should have search functionality', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const searchElements = await page.evaluate(() => {
        return {
          hasSearchInput: !!document.querySelector('input[type="search"], input[placeholder*="search"], .search-input'),
          hasSearchButton: !!document.querySelector('.search-btn, .search-button, button[type="search"]'),
          hasFilterOptions: !!document.querySelector('.filter, .dropdown, select')
        };
      });
      
      // At least one search mechanism should exist if there are repositories
      const hasRepositories = await page.$$eval('.repository-card, .repo-card', cards => cards.length > 0);
      
      if (hasRepositories) {
        expect(searchElements.hasSearchInput || searchElements.hasFilterOptions).toBe(true);
      }
    });

    test('should test search functionality', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const searchInput = await page.$('input[type="search"], input[placeholder*="search"], .search-input');
      
      if (searchInput) {
        const initialRepoCount = await page.$$eval('.repository-card, .repo-card', cards => cards.length);
        
        // Type a search term
        await searchInput.type('test');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1000);
        
        const afterSearchCount = await page.$$eval('.repository-card, .repo-card', cards => cards.length);
        
        // Search should either filter results or show no change if no matches
        expect(afterSearchCount <= initialRepoCount).toBe(true);
      }
    });
  });

  describe('Repository Management Actions', () => {
    test('should test delete repository functionality', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const repositoryCards = await page.$$('.repository-card, .repo-card, .card');
      
      if (repositoryCards.length > 0) {
        const firstCard = repositoryCards[0];
        
        // Look for delete button
        const deleteButton = await firstCard.$('button[class*="delete"], .delete-btn, .btn-danger');
        
        if (deleteButton) {
          await deleteButton.click();
          
          // Should show confirmation dialog
          const confirmationAppeared = await page.waitForFunction(() => {
            const confirmDialog = document.querySelector('.modal, .dialog, .confirm-dialog');
            return confirmDialog && window.getComputedStyle(confirmDialog).display !== 'none';
          }, { timeout: 3000 }).catch(() => false);
          
          if (confirmationAppeared) {
            // Check for confirmation dialog elements
            const dialogContent = await page.evaluate(() => {
              const dialog = document.querySelector('.modal, .dialog');
              return {
                hasWarning: !!dialog.querySelector('.warning, .danger, .alert-danger'),
                hasConfirmButton: !!dialog.querySelector('.confirm, .delete, .btn-danger'),
                hasCancelButton: !!dialog.querySelector('.cancel, .btn-secondary, .close')
              };
            });
            
            expect(dialogContent.hasConfirmButton).toBe(true);
            expect(dialogContent.hasCancelButton).toBe(true);
            
            // Cancel the deletion
            const cancelButton = await page.$('.cancel, .btn-secondary, .close');
            if (cancelButton) {
              await cancelButton.click();
            }
          }
        }
      }
    });

    test('should test repository sync functionality', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const repositoryCards = await page.$$('.repository-card, .repo-card, .card');
      
      if (repositoryCards.length > 0) {
        const firstCard = repositoryCards[0];
        
        // Look for sync button
        const syncButton = await firstCard.$('button[class*="sync"], .sync-btn, .refresh-btn');
        
        if (syncButton) {
          await syncButton.click();
          
          // Should show loading state or feedback
          await page.waitForTimeout(1000);
          
          const hasFeedback = await page.evaluate(() => {
            const feedbackSelectors = ['.loading', '.spinner', '.syncing', '.progress', '.success', '.error'];
            return feedbackSelectors.some(selector => document.querySelector(selector) !== null);
          });
          
          expect(hasFeedback).toBe(true);
        }
      }
    });
  });

  describe('Repository Visual Tests', () => {
    test('should match visual baselines', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      // Wait for content to load
      await page.waitForTimeout(2000);
      
      const viewports = ['mobile', 'tablet', 'desktop'];
      for (const viewport of viewports) {
        await page.setViewport(require('../utils/test-helpers').VIEWPORTS[viewport]);
        await page.waitForTimeout(500);
        
        const screenshotResult = await takeScreenshot(page, 'repository-list', viewport);
        
        if (!screenshotResult.isBaseline) {
          // Allow up to 4% visual difference for repository list due to dynamic content
          expect(screenshotResult.percentage).toBeLessThan(4.0);
        }
      }
    });
  });

  describe('Repository Accessibility', () => {
    test('should pass accessibility audit', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const auditResult = await accessibilityTester.runAudit('repository-page');
      
      // Should have reasonable accessibility score
      expect(auditResult.score).toBeGreaterThan(60);
      
      // No critical accessibility violations
      const criticalViolations = auditResult.violations.filter(v => v.impact === 'critical');
      expect(criticalViolations).toHaveLength(0);
    });

    test('should support keyboard navigation', async () => {
      await page.goto(`${BASE_URL}/repositories`);
      await page.waitForSelector('main', { timeout: 10000 });
      
      const keyboardResult = await accessibilityTester.testKeyboardNavigation();
      
      // Should be able to navigate to interactive elements
      const interactiveElements = keyboardResult.elements.filter(el => 
        el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'INPUT'
      );
      
      expect(interactiveElements.length).toBeGreaterThan(0);
      
      // No critical keyboard navigation issues
      const criticalIssues = keyboardResult.issues.filter(i => i.severity === 'critical');
      expect(criticalIssues).toHaveLength(0);
    });
  });
});