# CoderWiki UI Test Suite

Comprehensive automated UI testing framework for the CoderWiki application using Puppeteer, Jest, and various testing utilities.

## Features

- **Comprehensive Test Coverage**
  - Authentication flows (login/logout)
  - Dashboard functionality
  - Repository management UI
  - Document generation interface
  - Modal dialogs and interactions
  - Form validation

- **Responsive Testing**
  - Mobile (375px width)
  - Tablet (768px width)
  - Desktop (1200px+ width)
  - Automated layout issue detection

- **Accessibility Testing**
  - WCAG compliance audits
  - Keyboard navigation testing
  - Screen reader compatibility
  - Color contrast validation

- **Performance Testing**
  - Lighthouse audits
  - Load time measurements
  - Memory usage tracking
  - Network performance analysis

- **Visual Regression Testing**
  - Screenshot comparison
  - Automated baseline management
  - Cross-browser visual consistency

- **Comprehensive Reporting**
  - HTML reports with visualizations
  - JSON data export
  - CI/CD integration
  - Performance recommendations

## Quick Start

### Prerequisites

1. **Node.js** (v18+ recommended)
2. **Python** (3.9+) with CoderWiki backend running
3. **Chrome/Chromium** (for Puppeteer)

### Installation

```bash
# Navigate to UI tests directory
cd backend/tests/ui

# Install dependencies
npm install

# Make sure the CoderWiki backend is running
# In a separate terminal:
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
PORT=5001 python run.py
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test categories
npm run test:responsive     # Responsive design tests
npm run test:accessibility  # Accessibility tests
npm run test:performance    # Performance tests
npm run test:visual         # Visual regression tests

# Run with custom settings
BASE_URL=http://localhost:3000 npm test
HEADLESS=false npm test  # Run with visible browser

# Generate reports
npm run report
```

## Test Structure

```
backend/tests/ui/
├── tests/                  # Test files
│   ├── auth.test.js       # Authentication tests
│   ├── dashboard.test.js  # Dashboard functionality
│   ├── repository.test.js # Repository management
│   ├── modals.test.js     # Modal dialogs
│   ├── forms.test.js      # Form validation
│   └── document-generation.test.js
├── utils/                 # Test utilities
│   ├── test-helpers.js    # Common test functions
│   ├── responsive-tester.js
│   ├── accessibility-tester.js
│   └── performance-tester.js
├── screenshots/           # Visual testing assets
│   ├── baseline/         # Reference screenshots
│   ├── actual/           # Current test screenshots
│   └── diff/             # Visual difference images
├── reports/              # Generated test reports
└── package.json          # Dependencies and scripts
```

## Configuration

### Environment Variables

- `BASE_URL`: Application base URL (default: `http://localhost:5001`)
- `HEADLESS`: Run browser in headless mode (default: `true`)
- `SLOWMO`: Add delay between actions in ms for debugging
- `DEVTOOLS`: Open browser DevTools (default: `false`)
- `UPDATE_BASELINES`: Update visual regression baselines

### Jest Configuration

The test suite uses `jest-puppeteer` with custom configuration in `jest-puppeteer.config.js`:

```javascript
module.exports = {
  launch: {
    headless: process.env.HEADLESS !== 'false',
    slowMo: process.env.SLOWMO ? parseInt(process.env.SLOWMO) : 0,
    devtools: process.env.DEVTOOLS === 'true'
  }
};
```

## Writing Tests

### Basic Test Structure

```javascript
const { BASE_URL, SELECTORS, login, logout, takeScreenshot } = require('../utils/test-helpers');
const ResponsiveTester = require('../utils/responsive-tester');
const AccessibilityTester = require('../utils/accessibility-tester');

describe('My Feature Tests', () => {
  let responsiveTester;
  let accessibilityTester;

  beforeEach(async () => {
    responsiveTester = new ResponsiveTester(page);
    accessibilityTester = new AccessibilityTester(page);
  });

  test('should display feature correctly', async () => {
    await page.goto(`${BASE_URL}/my-feature`);
    await waitForElement(page, '.my-feature');
    
    // Your test assertions here
    const element = await page.$('.my-feature');
    expect(element).toBeTruthy();
  });
});
```

### Using Test Utilities

#### Authentication
```javascript
// Login with default demo user
await login(page);

// Login with specific credentials
await login(page, 'username', 'password');

// Logout
await logout(page);
```

#### Responsive Testing
```javascript
const results = await responsiveTester.testLayout('test-name', [
  '.selector1',
  '.selector2'
]);

// Check for issues
Object.values(results).forEach(result => {
  const criticalIssues = result.issues.filter(i => i.severity === 'high');
  expect(criticalIssues).toHaveLength(0);
});
```

#### Accessibility Testing
```javascript
// Run full accessibility audit
const auditResult = await accessibilityTester.runAudit('page-name');
expect(auditResult.score).toBeGreaterThan(80);

// Test keyboard navigation
const keyboardResult = await accessibilityTester.testKeyboardNavigation();
expect(keyboardResult.issues.filter(i => i.severity === 'critical')).toHaveLength(0);
```

#### Visual Regression Testing
```javascript
// Take screenshot for comparison
const screenshotResult = await takeScreenshot(page, 'feature-name', 'desktop');

if (!screenshotResult.isBaseline) {
  expect(screenshotResult.percentage).toBeLessThan(2.0); // Allow 2% difference
}
```

### Performance Testing
```javascript
const PerformanceTester = require('../utils/performance-tester');
const performanceTester = new PerformanceTester(page);

// Collect basic metrics
const metrics = await performanceTester.collectBasicMetrics('test-name');
expect(metrics.timings.loadEvent).toBeLessThan(3000);

// Run Lighthouse audit
const lighthouseResult = await performanceTester.runLighthouseAudit(url);
expect(lighthouseResult.performance.score).toBeGreaterThan(70);
```

## Selectors Reference

Common selectors are defined in `utils/test-helpers.js`:

```javascript
const SELECTORS = {
  // Authentication
  loginForm: '#login-form',
  usernameInput: 'input[name="username"]',
  passwordInput: 'input[name="password"]',
  loginButton: 'button[type="submit"]',
  logoutButton: '.logout-btn, a[href*="logout"]',
  
  // Navigation
  navbar: '.navbar',
  sidebar: '.sidebar',
  navLinks: '.nav-link',
  
  // Dashboard
  dashboard: '.dashboard',
  statsCards: '.stats-card',
  recentActivity: '.recent-activity',
  
  // Modals
  modal: '.modal',
  modalCloseBtn: '.modal .close, .modal-close'
};
```

## CI/CD Integration

The test suite includes GitHub Actions workflow (`.github/workflows/ui-tests.yml`) that:

1. Sets up the test environment
2. Starts the CoderWiki application
3. Runs all UI test categories
4. Generates comprehensive reports
5. Comments on pull requests with results
6. Updates visual regression baselines on main branch

### Lighthouse CI

The suite includes Lighthouse CI configuration (`lighthouserc.json`) for automated performance auditing:

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:5001",
        "http://localhost:5001/auth/login",
        "http://localhost:5001/dashboard"
      ]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["warn", {"minScore": 0.7}],
        "categories:accessibility": ["error", {"minScore": 0.8}]
      }
    }
  }
}
```

## Reports

The test suite generates comprehensive HTML and JSON reports with:

- **Executive Summary**: Pass rates, scores, and key metrics
- **Recommendations**: Prioritized action items
- **Test Results**: Detailed test execution results
- **Performance Metrics**: Load times, Lighthouse scores
- **Accessibility Audits**: WCAG violations and keyboard navigation
- **Responsive Issues**: Layout problems across viewports
- **Visual Regressions**: Screenshot comparisons

Reports are saved to the `reports/` directory with timestamps.

## Troubleshooting

### Common Issues

1. **Application not responding**
   ```bash
   # Make sure the backend is running
   cd backend
   PORT=5001 python run.py
   ```

2. **Puppeteer launch errors**
   ```bash
   # Install Chrome/Chromium dependencies on Linux
   sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2
   ```

3. **Permission errors**
   ```bash
   # Make test runner executable
   chmod +x run-ui-tests.js
   ```

4. **Visual regression false positives**
   - Run tests multiple times to ensure consistency
   - Update baselines if intentional changes were made:
     ```bash
     UPDATE_BASELINES=true npm run test:visual
     ```

### Debugging Tests

```bash
# Run with visible browser
HEADLESS=false npm test

# Add delays for debugging
SLOWMO=500 npm test

# Open DevTools
DEVTOOLS=true HEADLESS=false npm test

# Run specific test file
npx jest tests/auth.test.js --verbose
```

### Performance Optimization

- Use `page.waitForSelector()` instead of `page.waitForTimeout()` when possible
- Implement proper cleanup in `afterEach` hooks
- Avoid unnecessary page navigations
- Use request interception carefully to avoid blocking legitimate requests

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Use the provided test utilities and helpers
3. Add appropriate assertions for responsive, accessibility, and performance concerns
4. Update this README if adding new utilities or test categories
5. Ensure tests are deterministic and don't depend on external factors
6. Add visual regression tests for new UI components

## Best Practices

1. **Test Independence**: Each test should be able to run independently
2. **Cleanup**: Always clean up after tests (logout, close modals, etc.)
3. **Selectors**: Use stable selectors (data attributes preferred over classes)
4. **Assertions**: Include multiple types of validation (functional, visual, accessibility)
5. **Error Handling**: Provide meaningful error messages and debugging information
6. **Performance**: Keep tests fast and avoid unnecessary waits
7. **Maintenance**: Regular review and update of baselines and expected values

For more information, see the individual test files and utility modules for detailed examples and documentation.