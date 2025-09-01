#!/usr/bin/env node

/**
 * Debug script to identify which JavaScript files are returning 404 errors
 */

const puppeteer = require('puppeteer');

async function debug404s() {
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    
    // Track network requests
    const failedRequests = [];
    const successfulRequests = [];
    
    page.on('response', response => {
        if (response.url().includes('.js')) {
            if (response.status() === 404) {
                failedRequests.push({
                    url: response.url(),
                    status: response.status()
                });
            } else if (response.status() === 200) {
                successfulRequests.push({
                    url: response.url(),
                    status: response.status()
                });
            }
        }
    });
    
    try {
        console.log('🌐 Navigating and logging in to check JavaScript file loading...');
        
        // Login
        await page.goto('http://localhost:5001', { waitUntil: 'networkidle2', timeout: 30000 });
        
        const usernameField = await page.$('input[name="username"]');
        const passwordField = await page.$('input[name="password"]');
        const loginButton = await page.$('button[type="submit"], input[type="submit"]');
        
        if (usernameField && passwordField && loginButton) {
            await usernameField.type('admin');
            await passwordField.type('admin123');
            await loginButton.click();
            await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
        }
        
        // Wait for all scripts to attempt loading
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log('\n📊 JAVASCRIPT FILE LOADING ANALYSIS:');
        console.log('====================================');
        
        console.log(`\n✅ Successfully loaded (${successfulRequests.length}):`);
        successfulRequests.forEach((req, index) => {
            const filename = req.url.split('/').pop();
            console.log(`  ${index + 1}. ${filename}`);
        });
        
        console.log(`\n❌ Failed to load (${failedRequests.length}):`);
        failedRequests.forEach((req, index) => {
            const filename = req.url.split('/').pop();
            console.log(`  ${index + 1}. ${filename} (${req.status})`);
            console.log(`     Full URL: ${req.url}`);
        });
        
        // Check which files exist on disk
        console.log('\n🔍 CHECKING FILE EXISTENCE ON DISK:');
        const { execSync } = require('child_process');
        
        failedRequests.forEach(req => {
            const filename = req.url.split('/').pop().split('?')[0]; // Remove query params
            const possiblePaths = [
                `/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/frontend/static/js/${filename}`,
                `/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/frontend/static/js/components/${filename}`,
                `/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/frontend/static/js/_archive_pre_consolidation/${filename}`
            ];
            
            let found = false;
            possiblePaths.forEach(path => {
                try {
                    execSync(`ls "${path}"`, { stdio: 'ignore' });
                    console.log(`  ✅ Found: ${path}`);
                    found = true;
                } catch (e) {
                    // File doesn't exist at this path
                }
            });
            
            if (!found) {
                console.log(`  ❌ Not found: ${filename}`);
            }
        });
        
    } catch (error) {
        console.error('❌ Error during debugging:', error.message);
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    debug404s().catch(console.error);
}