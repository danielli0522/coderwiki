const { VIEWPORTS, takeScreenshot, waitForElement } = require('./test-helpers');

/**
 * Comprehensive responsive testing utilities
 */
class ResponsiveTester {
  constructor(page) {
    this.page = page;
    this.results = {};
  }

  /**
   * Test layout at different viewport sizes
   */
  async testLayout(testName, selectors = []) {
    const results = {};
    
    for (const [viewportName, viewport] of Object.entries(VIEWPORTS)) {
      await this.page.setViewport(viewport);
      await this.page.waitForTimeout(500); // Allow layout to settle
      
      const viewportResult = {
        viewport: viewportName,
        dimensions: viewport,
        elements: {},
        issues: []
      };
      
      // Test each selector
      for (const selector of selectors) {
        const elementInfo = await this.getElementInfo(selector);
        viewportResult.elements[selector] = elementInfo;
        
        // Check for common responsive issues
        const issues = await this.checkResponsiveIssues(selector, viewport);
        viewportResult.issues.push(...issues);
      }
      
      // Take screenshot
      const screenshotResult = await takeScreenshot(this.page, testName, viewportName);
      viewportResult.screenshot = screenshotResult;
      
      results[viewportName] = viewportResult;
    }
    
    this.results[testName] = results;
    return results;
  }

  /**
   * Get detailed element information
   */
  async getElementInfo(selector) {
    return await this.page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (!element) {
        return { exists: false };
      }
      
      const rect = element.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(element);
      
      return {
        exists: true,
        visible: rect.width > 0 && rect.height > 0,
        position: {
          top: rect.top,
          left: rect.left,
          right: rect.right,
          bottom: rect.bottom,
          width: rect.width,
          height: rect.height
        },
        style: {
          display: computedStyle.display,
          visibility: computedStyle.visibility,
          position: computedStyle.position,
          zIndex: computedStyle.zIndex,
          overflow: computedStyle.overflow,
          fontSize: computedStyle.fontSize,
          margin: {
            top: computedStyle.marginTop,
            right: computedStyle.marginRight,
            bottom: computedStyle.marginBottom,
            left: computedStyle.marginLeft
          },
          padding: {
            top: computedStyle.paddingTop,
            right: computedStyle.paddingRight,
            bottom: computedStyle.paddingBottom,
            left: computedStyle.paddingLeft
          }
        },
        inViewport: (
          rect.top >= 0 &&
          rect.left >= 0 &&
          rect.bottom <= window.innerHeight &&
          rect.right <= window.innerWidth
        )
      };
    }, selector);
  }

  /**
   * Check for common responsive issues
   */
  async checkResponsiveIssues(selector, viewport) {
    const issues = [];
    
    const elementInfo = await this.page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (!element) return null;
      
      const rect = element.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(element);
      
      return {
        rect,
        hasHorizontalScroll: document.documentElement.scrollWidth > window.innerWidth,
        hasVerticalScroll: document.documentElement.scrollHeight > window.innerHeight,
        fontSize: parseFloat(computedStyle.fontSize),
        touchTargetSize: Math.min(rect.width, rect.height),
        isClickable: element.tagName === 'BUTTON' || 
                    element.tagName === 'A' || 
                    element.onclick || 
                    computedStyle.cursor === 'pointer'
      };
    }, selector);
    
    if (!elementInfo) return issues;
    
    // Check for horizontal overflow
    if (elementInfo.rect.right > viewport.width) {
      issues.push({
        type: 'overflow',
        severity: 'high',
        message: `Element extends beyond viewport width (${elementInfo.rect.right}px > ${viewport.width}px)`,
        selector
      });
    }
    
    // Check for horizontal scrolling
    if (elementInfo.hasHorizontalScroll && viewport.width <= 768) {
      issues.push({
        type: 'horizontal-scroll',
        severity: 'medium',
        message: 'Page has horizontal scrolling on mobile viewport',
        selector: 'body'
      });
    }
    
    // Check touch target size for mobile
    if (viewport.width <= 768 && elementInfo.isClickable && elementInfo.touchTargetSize < 44) {
      issues.push({
        type: 'touch-target',
        severity: 'high',
        message: `Touch target too small (${elementInfo.touchTargetSize}px < 44px minimum)`,
        selector
      });
    }
    
    // Check font size for mobile readability
    if (viewport.width <= 768 && elementInfo.fontSize < 16) {
      issues.push({
        type: 'font-size',
        severity: 'medium',
        message: `Font size too small for mobile (${elementInfo.fontSize}px < 16px recommended)`,
        selector
      });
    }
    
    return issues;
  }

  /**
   * Test navigation menu responsiveness
   */
  async testNavigationResponsiveness() {
    const results = {};
    
    for (const [viewportName, viewport] of Object.entries(VIEWPORTS)) {
      await this.page.setViewport(viewport);
      await this.page.waitForTimeout(500);
      
      const navInfo = await this.page.evaluate(() => {
        const navbar = document.querySelector('.navbar, .nav, nav');
        const mobileToggle = document.querySelector('.navbar-toggler, .mobile-toggle, .hamburger');
        const navItems = document.querySelectorAll('.nav-link, .navbar-nav li');
        
        return {
          hasNavbar: !!navbar,
          hasMobileToggle: !!mobileToggle,
          mobileToggleVisible: mobileToggle ? window.getComputedStyle(mobileToggle).display !== 'none' : false,
          navItemsCount: navItems.length,
          navItemsVisible: Array.from(navItems).filter(item => 
            window.getComputedStyle(item).display !== 'none'
          ).length
        };
      });
      
      results[viewportName] = {
        viewport: viewportName,
        ...navInfo,
        issues: []
      };
      
      // Check for navigation issues
      if (viewport.width <= 768 && !navInfo.hasMobileToggle) {
        results[viewportName].issues.push({
          type: 'missing-mobile-nav',
          severity: 'high',
          message: 'Mobile navigation toggle not found'
        });
      }
      
      if (viewport.width > 768 && navInfo.mobileToggleVisible) {
        results[viewportName].issues.push({
          type: 'desktop-mobile-toggle',
          severity: 'low',
          message: 'Mobile toggle visible on desktop viewport'
        });
      }
    }
    
    return results;
  }

  /**
   * Test form responsiveness
   */
  async testFormResponsiveness(formSelector = 'form') {
    const results = {};
    
    for (const [viewportName, viewport] of Object.entries(VIEWPORTS)) {
      await this.page.setViewport(viewport);
      await this.page.waitForTimeout(500);
      
      const formInfo = await this.page.evaluate((selector) => {
        const form = document.querySelector(selector);
        if (!form) return { exists: false };
        
        const inputs = form.querySelectorAll('input, select, textarea');
        const buttons = form.querySelectorAll('button, input[type="submit"]');
        
        const inputSizes = Array.from(inputs).map(input => {
          const rect = input.getBoundingClientRect();
          const style = window.getComputedStyle(input);
          return {
            width: rect.width,
            height: rect.height,
            fontSize: parseFloat(style.fontSize)
          };
        });
        
        const buttonSizes = Array.from(buttons).map(button => {
          const rect = button.getBoundingClientRect();
          return {
            width: rect.width,
            height: rect.height
          };
        });
        
        return {
          exists: true,
          inputCount: inputs.length,
          buttonCount: buttons.length,
          inputSizes,
          buttonSizes
        };
      }, formSelector);
      
      results[viewportName] = {
        viewport: viewportName,
        ...formInfo,
        issues: []
      };
      
      if (formInfo.exists) {
        // Check input sizes for mobile
        if (viewport.width <= 768) {
          formInfo.inputSizes.forEach((size, index) => {
            if (size.height < 44) {
              results[viewportName].issues.push({
                type: 'input-touch-target',
                severity: 'high',
                message: `Input ${index + 1} too small for touch (${size.height}px < 44px)`,
                selector: `${formSelector} input:nth-child(${index + 1})`
              });
            }
            if (size.fontSize < 16) {
              results[viewportName].issues.push({
                type: 'input-font-size',
                severity: 'medium',
                message: `Input ${index + 1} font size too small (${size.fontSize}px < 16px)`,
                selector: `${formSelector} input:nth-child(${index + 1})`
              });
            }
          });
          
          formInfo.buttonSizes.forEach((size, index) => {
            if (Math.min(size.width, size.height) < 44) {
              results[viewportName].issues.push({
                type: 'button-touch-target',
                severity: 'high',
                message: `Button ${index + 1} too small for touch`,
                selector: `${formSelector} button:nth-child(${index + 1})`
              });
            }
          });
        }
      }
    }
    
    return results;
  }

  /**
   * Generate responsive test report
   */
  generateReport() {
    const allIssues = [];
    const summary = {
      totalTests: Object.keys(this.results).length,
      totalIssues: 0,
      issuesByType: {},
      issuesBySeverity: { high: 0, medium: 0, low: 0 }
    };
    
    for (const [testName, viewports] of Object.entries(this.results)) {
      for (const [viewportName, result] of Object.entries(viewports)) {
        if (result.issues) {
          result.issues.forEach(issue => {
            allIssues.push({
              test: testName,
              viewport: viewportName,
              ...issue
            });
            
            summary.totalIssues++;
            summary.issuesByType[issue.type] = (summary.issuesByType[issue.type] || 0) + 1;
            summary.issuesBySeverity[issue.severity]++;
          });
        }
      }
    }
    
    return {
      timestamp: new Date().toISOString(),
      summary,
      results: this.results,
      allIssues,
      viewports: VIEWPORTS
    };
  }
}

module.exports = ResponsiveTester;