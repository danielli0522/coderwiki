// Service Worker for CoderWiki
const CACHE_NAME = 'coderwiki-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/components.css',
    '/static/js/components.js',
    '/static/js/performance.js',
    '/static/js/main.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// 安装Service Worker
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// 激活Service Worker
self.addEventListener('activate', function(event) {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// 拦截网络请求
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // 如果在缓存中找到响应，则返回缓存的响应
                if (response) {
                    return response;
                }
                
                // 否则，发起网络请求
                return fetch(event.request).then(
                    function(response) {
                        // 检查是否收到有效的响应
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // 克隆响应，因为响应是流，只能使用一次
                        var responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    }
                );
            })
    );
});

// 处理后台同步
self.addEventListener('sync', function(event) {
    if (event.tag === 'sync-forms') {
        event.waitUntil(
            // 同步表单数据
            syncForms()
        );
    }
});

// 处理推送通知
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: '/static/images/icon-192x192.png',
            badge: '/static/images/badge-72x72.png',
            vibrate: [100, 50, 100],
            data: {
                url: data.url || '/'
            }
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// 处理通知点击
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.notification.data.url) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});

// 同步表单数据
function syncForms() {
    return new Promise((resolve, reject) => {
        // 从IndexedDB获取待同步的表单数据
        const request = indexedDB.open('CoderWikiDB', 1);
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction(['forms'], 'readwrite');
            const store = transaction.objectStore('forms');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = function() {
                const forms = getAllRequest.result;
                
                // 同步每个表单
                const syncPromises = forms.map(form => {
                    return fetch('/api/forms', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(form.data)
                    }).then(response => {
                        if (response.ok) {
                            // 同步成功，删除本地存储
                            store.delete(form.id);
                        }
                    });
                });
                
                Promise.all(syncPromises)
                    .then(() => resolve())
                    .catch(() => reject());
            };
        };
    });
}