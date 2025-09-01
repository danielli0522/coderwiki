#!/usr/bin/env node

/**
 * Debug DragDropManager specific issues
 */

const puppeteer = require('puppeteer');

async function debugDragDrop() {
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    
    // Track specific DragDropManager errors with location
    const dragDropErrors = [];
    
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('DragDropManager') && text.includes('not defined')) {
            dragDropErrors.push({
                text: text,
                location: msg.location(),
                type: msg.type()
            });
        }
    });
    
    page.on('pageerror', err => {
        if (err.message.includes('DragDropManager') && err.message.includes('not defined')) {
            dragDropErrors.push({
                text: err.message,
                stack: err.stack,
                type: 'pageerror'
            });
        }
    });
    
    try {
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
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Check what's actually available on window
        const windowCheck = await page.evaluate(() => {
            const result = {};
            result.DragDropManagerExists = typeof window.DragDropManager !== 'undefined';
            result.DragDropManagerType = typeof window.DragDropManager;
            result.windowKeys = Object.keys(window).filter(key => key.includes('Drag') || key.includes('Drop'));
            result.componentManagerExists = typeof window.ComponentManager !== 'undefined';
            result.appInitializerExists = typeof window.AppInitializer !== 'undefined';
            
            // Try to access DragDropManager directly
            try {
                result.canAccessInit = window.DragDropManager && typeof window.DragDropManager.init === 'function';
            } catch (e) {
                result.accessError = e.message;
            }
            
            return result;
        });
        
        console.log('🔍 DRAGDROPMANAGER DEBUG ANALYSIS');
        console.log('==================================');
        console.log('Window object analysis:');
        console.log(`  DragDropManager exists: ${windowCheck.DragDropManagerExists}`);
        console.log(`  DragDropManager type: ${windowCheck.DragDropManagerType}`);
        console.log(`  Can access init method: ${windowCheck.canAccessInit}`);
        console.log(`  ComponentManager exists: ${windowCheck.componentManagerExists}`);
        console.log(`  AppInitializer exists: ${windowCheck.appInitializerExists}`);
        console.log(`  Window keys with Drag/Drop: ${windowCheck.windowKeys}`);
        
        if (windowCheck.accessError) {
            console.log(`  Access error: ${windowCheck.accessError}`);
        }
        
        console.log(`\n🚨 DragDropManager Errors Found: ${dragDropErrors.length}`);
        dragDropErrors.forEach((error, index) => {
            console.log(`\nError ${index + 1}:`);
            console.log(`  Text: ${error.text}`);
            console.log(`  Type: ${error.type}`);
            if (error.location) {
                console.log(`  Location: ${error.location.url}:${error.location.lineNumber}`);
            }
            if (error.stack) {
                console.log(`  Stack: ${error.stack.split('\n')[0]}`);
            }
        });
        
        // Try to manually initialize DragDropManager
        const manualTest = await page.evaluate(() => {
            try {
                if (window.DragDropManager && window.DragDropManager.init) {
                    window.DragDropManager.init();
                    return { success: true, message: 'Manual init successful' };
                } else {
                    return { success: false, message: 'DragDropManager or init method not available' };
                }
            } catch (e) {
                return { success: false, message: e.message };
            }
        });
        
        console.log(`\n🧪 Manual Test Result:`);
        console.log(`  Success: ${manualTest.success}`);
        console.log(`  Message: ${manualTest.message}`);
        
    } catch (error) {
        console.error('❌ Debug failed:', error.message);
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    debugDragDrop().catch(console.error);
}