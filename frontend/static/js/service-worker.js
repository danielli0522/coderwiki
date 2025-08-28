/**
 * CoderWiki Service Worker
 * Provides offline capability and performance optimizations
 */

const CACHE_NAME = 'coderwiki-v1';
const URLS_TO_CACHE = [
    '/',
    '/static/css/style.css',
    '/static/js/core.js',
    '/static/js/components.js',
    '/static/js/performance-unified.js',
    '/static/images/logo.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
    console.log('Service Worker: Installing');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: Caching files');
                return cache.addAll(URLS_TO_CACHE);
            })
            .catch(error => {
                console.log('Service Worker: Cache failed', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip API requests (let them fail naturally when offline)
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request)
                    .catch(() => {
                        // If both cache and network fail, return a basic offline page
                        if (event.request.destination === 'document') {
                            return new Response(`
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <title>CoderWiki - Offline</title>
                                    <meta charset="utf-8">
                                    <meta name="viewport" content="width=device-width, initial-scale=1">
                                </head>
                                <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 50px;">
                                    <h1>CoderWiki</h1>
                                    <p>You're currently offline. Please check your connection and try again.</p>
                                </body>
                                </html>
                            `, {
                                headers: { 'Content-Type': 'text/html' }
                            });
                        }
                    });
            })
    );
});

// Background sync for failed API requests (future enhancement)
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('Service Worker: Background sync triggered');
        // Handle background sync logic here
    }
});

console.log('Service Worker: Script loaded');