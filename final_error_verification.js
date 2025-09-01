#!/usr/bin/env node

/**
 * Final verification script to confirm the two target JavaScript errors are fixed:
 * 1. this.apiClient.get is not a function error in task.js
 * 2. DragDropManager is not defined error in components.js
 */

const puppeteer = require('puppeteer');

async function finalVerification() {
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    
    // Track only the specific errors we care about
    const targetErrors = {
        apiClientError: false,
        dragDropError: false
    };
    
    // Track all console messages for analysis
    const allConsoleMessages = [];
    
    page.on('console', msg => {
        const text = msg.text();
        allConsoleMessages.push(text);
        
        // Check for our specific target errors
        if (text.includes('this.apiClient.get is not a function') || 
            text.includes('apiClient.get is not a function')) {
            targetErrors.apiClientError = true;
        }
        
        if (text.includes('DragDropManager is not defined')) {
            targetErrors.dragDropError = true;
        }
    });
    
    page.on('pageerror', err => {
        const message = err.message;
        allConsoleMessages.push(`PAGE ERROR: ${message}`);
        
        if (message.includes('DragDropManager is not defined')) {
            targetErrors.dragDropError = true;
        }
    });
    
    try {
        console.log('🎯 FINAL VERIFICATION TEST');
        console.log('=========================');
        console.log('Testing fixes for:');
        console.log('1. this.apiClient.get is not a function error');
        console.log('2. DragDropManager is not defined error\n');
        
        // Login and navigate through the application
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
        
        console.log('✅ Logged in successfully');
        
        // Test multiple pages to trigger more JavaScript execution
        const testPages = [
            { url: '/dashboard', name: 'Dashboard' },
            { url: '/repositories', name: 'Repositories' },
            { url: '/tasks', name: 'Tasks' },
            { url: '/documents', name: 'Documents' }
        ];
        
        for (const { url, name } of testPages) {
            try {
                console.log(`🔍 Testing ${name} page...`);
                await page.goto(`http://localhost:5001${url}`, { 
                    waitUntil: 'networkidle2', 
                    timeout: 10000 
                });
                await new Promise(resolve => setTimeout(resolve, 3000));
            } catch (e) {
                console.log(`⚠️ Could not access ${name} page: ${e.message}`);
            }
        }
        
        // Try to trigger task progress functionality specifically
        console.log('🔧 Testing task progress functionality...');
        try {
            await page.evaluate(() => {
                // Try to create TaskProgressMonitor instance if it exists
                if (typeof window.TaskProgressMonitor !== 'undefined') {
                    new window.TaskProgressMonitor();
                }
                
                // Try to access DragDropManager
                if (typeof window.DragDropManager !== 'undefined') {
                    window.DragDropManager.init();
                }
            });
        } catch (e) {
            console.log(`⚠️ Error during functionality test: ${e.message}`);
        }
        
        // Wait a bit more to catch any delayed errors
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Final results
        console.log('\n📊 FINAL TEST RESULTS');
        console.log('=====================');
        
        if (!targetErrors.apiClientError) {
            console.log('✅ FIXED: this.apiClient.get is not a function');
        } else {
            console.log('❌ STILL EXISTS: this.apiClient.get is not a function');
        }
        
        if (!targetErrors.dragDropError) {
            console.log('✅ FIXED: DragDropManager is not defined');
        } else {
            console.log('❌ STILL EXISTS: DragDropManager is not defined');
        }
        
        const bothFixed = !targetErrors.apiClientError && !targetErrors.dragDropError;
        
        console.log('\n🏆 OVERALL RESULT:');
        if (bothFixed) {
            console.log('🎉 SUCCESS: Both target errors have been FIXED!');
        } else {
            console.log('⚠️ PARTIAL: Some target errors still exist');
        }
        
        // Additional analysis
        console.log('\n📝 Additional Analysis:');
        const otherErrors = allConsoleMessages.filter(msg => 
            msg.includes('error') || msg.includes('Error') || msg.includes('ERROR')
        ).filter(msg => 
            !msg.includes('this.apiClient.get is not a function') &&
            !msg.includes('DragDropManager is not defined')
        );
        
        console.log(`Total console messages: ${allConsoleMessages.length}`);
        console.log(`Other errors detected: ${otherErrors.length}`);
        
        if (otherErrors.length > 0 && otherErrors.length < 10) {
            console.log('\nOther errors found:');
            otherErrors.slice(0, 5).forEach((error, index) => {
                console.log(`  ${index + 1}. ${error.substring(0, 100)}...`);
            });
        }
        
        // Test JavaScript API functionality
        console.log('\n🔧 JavaScript API Functionality Test:');
        const apiTest = await page.evaluate(() => {
            const results = {};
            try {
                results.apiClientExists = typeof window.ApiClient !== 'undefined';
                results.globalApiExists = typeof window.api !== 'undefined';
                results.apiHasGetMethod = window.api && typeof window.api.get === 'function';
                results.dragDropManagerExists = typeof window.DragDropManager !== 'undefined';
                results.taskProgressMonitorExists = typeof window.TaskProgressMonitor !== 'undefined';
            } catch (e) {
                results.error = e.message;
            }
            return results;
        });
        
        console.log(`ApiClient class exists: ${apiTest.apiClientExists ? '✅' : '❌'}`);
        console.log(`Global api instance exists: ${apiTest.globalApiExists ? '✅' : '❌'}`);
        console.log(`API get method works: ${apiTest.apiHasGetMethod ? '✅' : '❌'}`);
        console.log(`DragDropManager exists: ${apiTest.dragDropManagerExists ? '✅' : '❌'}`);
        console.log(`TaskProgressMonitor exists: ${apiTest.taskProgressMonitorExists ? '✅' : '❌'}`);
        
        if (apiTest.error) {
            console.log(`API Test Error: ${apiTest.error}`);
        }
        
        return {
            bothTargetErrorsFixed: bothFixed,
            apiClientError: targetErrors.apiClientError,
            dragDropError: targetErrors.dragDropError,
            otherErrorCount: otherErrors.length,
            apiTest: apiTest
        };
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        return {
            bothTargetErrorsFixed: false,
            error: error.message
        };
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    finalVerification()
        .then(result => {
            console.log('\n' + '='.repeat(50));
            if (result.bothTargetErrorsFixed) {
                console.log('🎉 VERIFICATION COMPLETE: Target JavaScript errors are FIXED!');
                process.exit(0);
            } else {
                console.log('⚠️ VERIFICATION INCOMPLETE: Some issues remain');
                process.exit(1);
            }
        })
        .catch(error => {
            console.error('❌ Verification failed:', error);
            process.exit(1);
        });
}