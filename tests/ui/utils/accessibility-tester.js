const { AxePuppeteer } = require('@axe-core/puppeteer');

/**
 * Accessibility testing utilities using axe-core
 */
class AccessibilityTester {
  constructor(page) {
    this.page = page;
    this.results = [];
  }

  /**
   * Run comprehensive accessibility audit
   */
  async runAudit(testName, options = {}) {
    try {
      const axe = new AxePuppeteer(this.page);
      
      // Configure axe options
      if (options.include) {
        axe.include(options.include);
      }
      if (options.exclude) {
        axe.exclude(options.exclude);
      }
      if (options.tags) {
        axe.withTags(options.tags);
      }
      
      const results = await axe.analyze();
      
      const auditResult = {
        testName,
        timestamp: new Date().toISOString(),
        url: this.page.url(),
        summary: {
          violations: results.violations.length,
          passes: results.passes.length,
          incomplete: results.incomplete.length,
          inapplicable: results.inapplicable.length
        },
        violations: results.violations.map(this.formatViolation),
        incomplete: results.incomplete.map(this.formatIncomplete),
        passes: results.passes.length, // Just count for performance
        score: this.calculateAccessibilityScore(results)
      };
      
      this.results.push(auditResult);
      return auditResult;
    } catch (error) {
      console.error('Accessibility audit failed:', error);
      throw error;
    }
  }

  /**
   * Format violation for reporting
   */
  formatViolation(violation) {
    return {
      id: violation.id,
      description: violation.description,
      impact: violation.impact,
      help: violation.help,
      helpUrl: violation.helpUrl,
      tags: violation.tags,
      nodes: violation.nodes.map(node => ({
        html: node.html,
        target: node.target,
        failureSummary: node.failureSummary,
        xpath: node.xpath
      }))
    };
  }

  /**
   * Format incomplete test for reporting
   */
  formatIncomplete(incomplete) {
    return {
      id: incomplete.id,
      description: incomplete.description,
      help: incomplete.help,
      helpUrl: incomplete.helpUrl,
      tags: incomplete.tags,
      nodes: incomplete.nodes.map(node => ({
        html: node.html,
        target: node.target,
        xpath: node.xpath
      }))
    };
  }

  /**
   * Calculate accessibility score (0-100)
   */
  calculateAccessibilityScore(results) {
    const totalTests = results.violations.length + results.passes.length + results.incomplete.length;
    if (totalTests === 0) return 100;
    
    // Weight violations by impact
    const impactWeights = { critical: 10, serious: 7, moderate: 3, minor: 1 };
    let violationScore = 0;
    
    results.violations.forEach(violation => {
      const weight = impactWeights[violation.impact] || 1;
      violationScore += weight * violation.nodes.length;
    });
    
    // Deduct points for incomplete tests too
    const incompleteScore = results.incomplete.length * 0.5;
    
    const maxPossibleScore = totalTests * 10;
    const score = Math.max(0, ((maxPossibleScore - violationScore - incompleteScore) / maxPossibleScore) * 100);
    
    return Math.round(score * 100) / 100;
  }

  /**
   * Test keyboard navigation
   */
  async testKeyboardNavigation(interactiveSelectors = []) {
    const results = {
      testName: 'keyboard-navigation',
      timestamp: new Date().toISOString(),
      url: this.page.url(),
      elements: [],
      issues: []
    };
    
    // Get all potentially interactive elements
    const allInteractiveElements = await this.page.evaluate(() => {
      const selectors = [
        'a[href]',
        'button',
        'input',
        'select',
        'textarea',
        '[tabindex]',
        '[role="button"]',
        '[role="link"]',
        '[role="menuitem"]',
        '[onclick]'
      ];
      
      const elements = [];
      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
          const rect = el.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) { // Only visible elements
            elements.push({
              selector: el.tagName.toLowerCase() + 
                       (el.id ? `#${el.id}` : '') + 
                       (el.className ? `.${el.className.split(' ').join('.')}` : ''),
              tagName: el.tagName,
              tabIndex: el.tabIndex,
              role: el.role || null,
              ariaLabel: el.getAttribute('aria-label') || null,
              hasOnClick: !!el.onclick
            });
          }
        });
      });
      return elements;
    });
    
    // Test Tab navigation
    let tabCount = 0;
    const maxTabs = 50; // Prevent infinite loops
    const focusedElements = [];
    
    await this.page.keyboard.press('Tab');
    
    while (tabCount < maxTabs) {
      const focusedElement = await this.page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return null;
        
        const rect = el.getBoundingClientRect();
        return {
          tagName: el.tagName,
          id: el.id || null,
          className: el.className || null,
          tabIndex: el.tabIndex,
          isVisible: rect.width > 0 && rect.height > 0,
          hasKeyboardIndicator: window.getComputedStyle(el, ':focus').outline !== 'none'
        };
      });
      
      if (!focusedElement) break;
      
      focusedElements.push(focusedElement);
      
      // Check for focus indicator
      if (!focusedElement.hasKeyboardIndicator) {
        results.issues.push({
          type: 'missing-focus-indicator',
          severity: 'high',
          message: `Element lacks visible focus indicator`,
          element: focusedElement
        });
      }
      
      await this.page.keyboard.press('Tab');
      tabCount++;
      
      // Check if we've cycled back to the first element
      if (focusedElements.length > 1) {
        const current = focusedElements[focusedElements.length - 1];
        const first = focusedElements[0];
        if (current.tagName === first.tagName && 
            current.id === first.id && 
            current.className === first.className) {
          break;
        }
      }
    }
    
    results.elements = focusedElements;
    results.summary = {
      totalInteractiveElements: allInteractiveElements.length,
      keyboardAccessibleElements: focusedElements.length,
      issuesFound: results.issues.length
    };
    
    // Check for keyboard traps
    if (tabCount >= maxTabs) {
      results.issues.push({
        type: 'keyboard-trap',
        severity: 'critical',
        message: 'Potential keyboard trap detected - unable to complete tab cycle'
      });
    }
    
    return results;
  }

  /**
   * Test color contrast
   */
  async testColorContrast() {
    return await this.page.evaluate(() => {
      const results = {
        testName: 'color-contrast',
        timestamp: new Date().toISOString(),
        elements: [],
        issues: []
      };
      
      // Get all text elements
      const textElements = document.querySelectorAll('*');
      
      textElements.forEach(element => {
        const text = element.textContent?.trim();
        if (!text || text.length === 0) return;
        
        const rect = element.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return; // Skip hidden elements
        
        const computedStyle = window.getComputedStyle(element);
        const color = computedStyle.color;
        const backgroundColor = computedStyle.backgroundColor;
        const fontSize = parseFloat(computedStyle.fontSize);
        const fontWeight = computedStyle.fontWeight;
        
        // Simple contrast ratio calculation (not exact but indicative)
        const colorValues = color.match(/\d+/g);
        const bgColorValues = backgroundColor.match(/\d+/g);
        
        if (colorValues && bgColorValues && colorValues.length >= 3 && bgColorValues.length >= 3) {
          const textLuminance = this.calculateLuminance(
            parseInt(colorValues[0]), 
            parseInt(colorValues[1]), 
            parseInt(colorValues[2])
          );
          const bgLuminance = this.calculateLuminance(
            parseInt(bgColorValues[0]), 
            parseInt(bgColorValues[1]), 
            parseInt(bgColorValues[2])
          );
          
          const contrastRatio = (Math.max(textLuminance, bgLuminance) + 0.05) / 
                               (Math.min(textLuminance, bgLuminance) + 0.05);
          
          const isLargeText = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || fontWeight >= 700));
          const minRatio = isLargeText ? 3 : 4.5;
          
          const elementInfo = {
            selector: element.tagName.toLowerCase() + 
                     (element.id ? `#${element.id}` : '') + 
                     (element.className ? `.${element.className.split(' ').join('.')}` : ''),
            text: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
            color,
            backgroundColor,
            fontSize,
            fontWeight,
            contrastRatio: Math.round(contrastRatio * 100) / 100,
            isLargeText,
            meetsStandard: contrastRatio >= minRatio
          };
          
          results.elements.push(elementInfo);
          
          if (!elementInfo.meetsStandard) {
            results.issues.push({
              type: 'low-contrast',
              severity: contrastRatio < (minRatio * 0.7) ? 'high' : 'medium',
              message: `Text contrast ratio ${elementInfo.contrastRatio} is below ${minRatio} standard`,
              element: elementInfo
            });
          }
        }
      });
      
      return results;
    });
  }

  /**
   * Calculate relative luminance (simplified)
   */
  calculateLuminance(r, g, b) {
    const rsRGB = r / 255;
    const gsRGB = g / 255;
    const bsRGB = b / 255;
    
    const rLinear = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
    const gLinear = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
    const bLinear = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);
    
    return 0.2126 * rLinear + 0.7152 * gLinear + 0.0722 * bLinear;
  }

  /**
   * Generate comprehensive accessibility report
   */
  generateReport() {
    const allViolations = [];
    const allIssues = [];
    let totalScore = 0;
    let auditCount = 0;
    
    this.results.forEach(result => {
      if (result.violations) {
        allViolations.push(...result.violations);
        totalScore += result.score;
        auditCount++;
      }
      if (result.issues) {
        allIssues.push(...result.issues);
      }
    });
    
    const averageScore = auditCount > 0 ? totalScore / auditCount : 0;
    
    return {
      timestamp: new Date().toISOString(),
      summary: {
        totalAudits: this.results.length,
        averageScore: Math.round(averageScore * 100) / 100,
        totalViolations: allViolations.length,
        totalIssues: allIssues.length,
        violationsByImpact: this.groupBy(allViolations, 'impact'),
        violationsByType: this.groupBy(allViolations, 'id')
      },
      results: this.results,
      recommendations: this.generateRecommendations(allViolations, allIssues)
    };
  }

  /**
   * Group array by property
   */
  groupBy(array, property) {
    return array.reduce((groups, item) => {
      const key = item[property] || 'unknown';
      groups[key] = (groups[key] || 0) + 1;
      return groups;
    }, {});
  }

  /**
   * Generate accessibility recommendations
   */
  generateRecommendations(violations, issues) {
    const recommendations = [];
    
    // Analyze violations and provide recommendations
    const violationTypes = this.groupBy(violations, 'id');
    
    Object.entries(violationTypes).forEach(([violationType, count]) => {
      switch (violationType) {
        case 'color-contrast':
          recommendations.push({
            priority: 'high',
            category: 'visual',
            title: 'Improve Color Contrast',
            description: `${count} color contrast issues found. Ensure text has sufficient contrast against background colors.`,
            actions: [
              'Use online contrast checkers to verify color combinations',
              'Aim for 4.5:1 ratio for normal text, 3:1 for large text',
              'Consider using darker text or lighter backgrounds'
            ]
          });
          break;
        
        case 'keyboard-navigation':
          recommendations.push({
            priority: 'high',
            category: 'keyboard',
            title: 'Fix Keyboard Navigation',
            description: `${count} keyboard navigation issues found.`,
            actions: [
              'Ensure all interactive elements are keyboard accessible',
              'Provide visible focus indicators',
              'Implement logical tab order'
            ]
          });
          break;
        
        case 'missing-alt-text':
          recommendations.push({
            priority: 'medium',
            category: 'content',
            title: 'Add Alternative Text',
            description: `${count} images missing alternative text.`,
            actions: [
              'Add descriptive alt attributes to images',
              'Use empty alt="" for decorative images',
              'Consider using aria-label for complex images'
            ]
          });
          break;
      }
    });
    
    return recommendations;
  }
}

module.exports = AccessibilityTester;