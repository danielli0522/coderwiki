const fs = require('fs-extra');
const path = require('path');

// Global setup for UI tests
beforeAll(async () => {
  // Ensure screenshot directories exist
  await fs.ensureDir(path.join(__dirname, 'screenshots'));
  await fs.ensureDir(path.join(__dirname, 'screenshots', 'baseline'));
  await fs.ensureDir(path.join(__dirname, 'screenshots', 'actual'));
  await fs.ensureDir(path.join(__dirname, 'screenshots', 'diff'));
  
  // Ensure reports directory exists
  await fs.ensureDir(path.join(__dirname, 'reports'));
  
  console.log('UI Test Setup Complete');
});

beforeEach(async () => {
  // Set default viewport for all tests
  await page.setViewport({ width: 1200, height: 800 });
  
  // Set user agent
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CoderWikiUITest/1.0');
  
  // Enable JavaScript
  await page.setJavaScriptEnabled(true);
  
  // Set default timeout
  page.setDefaultTimeout(10000);
});

afterEach(async () => {
  // Clear cookies and storage after each test
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  
  const cookies = await page.cookies();
  await page.deleteCookie(...cookies);
});

// Global error handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});