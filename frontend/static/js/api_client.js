/**
 * API客户端
 * 统一的API请求封装，包含错误处理、缓存和重试机制
 */
class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5分钟缓存
        this.retryCount = 3;
        this.retryDelay = 1000;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include', // 确保发送cookies用于session认证
            ...options
        };

        // 检查缓存
        if (options.method === 'GET' && !options.skipCache) {
            const cached = this.getFromCache(url);
            if (cached) {
                return cached;
            }
        }

        try {
            const response = await this.fetchWithRetry(url, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // 缓存GET请求
            if (options.method === 'GET' || !options.method) {
                this.setToCache(url, data);
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);

            // 处理认证错误
            if (error.message.includes('401')) {
                this.handleAuthError();
            }

            throw error;
        }
    }

    async fetchWithRetry(url, config, retryCount = this.retryCount) {
        try {
            const response = await fetch(url, config);

            // 如果响应状态码是401或403，直接抛出错误不重试
            if (response.status === 401 || response.status === 403) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // 如果响应状态码是5xx，进行重试
            if (response.status >= 500 && retryCount > 0) {
                await this.delay(this.retryDelay);
                return this.fetchWithRetry(url, config, retryCount - 1);
            }

            return response;
        } catch (error) {
            if (retryCount > 0 && !error.message.includes('401') && !error.message.includes('403')) {
                await this.delay(this.retryDelay);
                return this.fetchWithRetry(url, config, retryCount - 1);
            }
            throw error;
        }
    }

    async get(endpoint, params = {}, options = {}) {
        // 修复URL构造问题 - 使用相对路径或完整URL
        let url;
        try {
            // 如果baseUrl是相对路径，使用当前域名构造完整URL
            if (this.baseUrl.startsWith('/')) {
                url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin);
            } else {
                url = new URL(`${this.baseUrl}${endpoint}`);
            }
        } catch (error) {
            console.error('URL构造失败:', error);
            // 回退到简单的字符串拼接
            const queryString = Object.keys(params)
                .filter(key => params[key] !== undefined && params[key] !== null)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
                .join('&');

            const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
            return this.request(fullEndpoint, { ...options, method: 'GET' });
        }

        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        return this.request(url.pathname + url.search, { ...options, method: 'GET' });
    }

    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async patch(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    // 用户相关API
    async getUserProfile() {
        return this.get('/auth/profile');
    }

    async getUserStats() {
        return this.get('/users/stats');
    }

    async updateUserProfile(data) {
        return this.put('/auth/profile', data);
    }

    // 仓库相关API
    async getRepositories(params = {}) {
        return this.get('/repositories', params);
    }

    async getRepository(id) {
        return this.get(`/repositories/${id}`);
    }

    async createRepository(data) {
        return this.post('/repositories', data);
    }

    async updateRepository(id, data) {
        return this.put(`/repositories/${id}`, data);
    }

    async deleteRepository(id) {
        return this.delete(`/repositories/${id}`);
    }

    async generateDocument(repoId, options = {}) {
        return this.post(`/repositories/${repoId}/generate`, options);
    }

    // 任务相关API
    async getTasks(params = {}) {
        return this.get('/tasks', params);
    }

    async getTask(id) {
        return this.get(`/tasks/${id}`);
    }

    async cancelTask(id) {
        return this.post(`/tasks/${id}/cancel`);
    }

    async retryTask(id) {
        return this.post(`/tasks/${id}/retry`);
    }

    // 文档相关API
    async getDocuments(params = {}) {
        return this.get('/documents', params);
    }

    async getDocument(id) {
        return this.get(`/documents/${id}`);
    }

    async getRecentDocuments() {
        return this.get('/documents/recent');
    }

    // 系统相关API
    async getSystemHealth() {
        return this.get('/system/health');
    }

    async getSystemStats() {
        return this.get('/system/stats');
    }

    // 活动相关API
    async getActivities(params = {}) {
        return this.get('/activities', params);
    }

    // 缓存相关方法
    getFromCache(url) {
        const cached = this.cache.get(url);
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }
        return null;
    }

    setToCache(url, data) {
        this.cache.set(url, {
            data: data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        this.cache.clear();
    }

    // 认证相关方法
    setToken(token) {
        // 移除Bearer token认证，使用session认证
        // this.token = token;
        // localStorage.setItem('auth_token', token);
    }

    getToken() {
        // 移除Bearer token认证，使用session认证
        // return this.token;
        return null;
    }

    removeToken() {
        // 移除Bearer token认证，使用session认证
        // this.token = null;
        // localStorage.removeItem('auth_token');
    }

    handleAuthError() {
        // 移除Bearer token认证，使用session认证
        // this.removeToken();
        this.clearCache();
        // 临时禁用自动重定向到登录页面
        // window.location.href = '/login';
        console.log('认证错误，但已禁用自动重定向');
    }

    // 工具方法
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 上传文件方法
    async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);

        // 添加其他字段
        Object.keys(options).forEach(key => {
            formData.append(key, options[key]);
        });

        const config = {
            method: 'POST',
            body: formData,
            // 移除Bearer token认证，使用session认证
            // headers: {
            //     ...this.token ? { 'Authorization': `Bearer ${this.token}` } : {}
            // }
        };

        const response = await fetch(`${this.baseUrl}${endpoint}`, config);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 批量请求方法
    async batch(requests) {
        const promises = requests.map(request => {
            const { method, endpoint, data } = request;
            switch (method.toLowerCase()) {
                case 'get':
                    return this.get(endpoint, data);
                case 'post':
                    return this.post(endpoint, data);
                case 'put':
                    return this.put(endpoint, data);
                case 'delete':
                    return this.delete(endpoint);
                default:
                    throw new Error(`Unsupported method: ${method}`);
            }
        });

        return Promise.all(promises);
    }
}

// 创建全局API客户端实例
const api = new ApiClient();

// 导出API客户端
window.ApiClient = ApiClient;
window.api = api;
