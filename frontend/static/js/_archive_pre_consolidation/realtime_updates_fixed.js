/**
 * 修复版本的实时更新模块
 * 仅使用Socket.IO，避免WebSocket冲突
 */
class RealtimeUpdatesFixed {
    constructor() {
        this.socket = null;
        this.socketio = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventListeners = new Map();

        this.init();
    }

    async init() {
        console.log('初始化实时更新模块 (修复版本)');
        await this.loadSocketIO();
        this.connectSocketIO();
    }

    async loadSocketIO() {
        return new Promise((resolve, reject) => {
            if (window.io) {
                this.socketio = window.io;
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
            script.onload = () => {
                this.socketio = window.io;
                resolve();
            };
            script.onerror = () => {
                console.warn('Socket.IO 加载失败，将禁用实时更新功能');
                reject(new Error('Socket.IO 加载失败'));
            };
            document.head.appendChild(script);
        });
    }

    connectSocketIO() {
        if (!this.socketio) {
            console.warn('Socket.IO 不可用，跳过连接');
            return;
        }

        try {
            this.socket = this.socketio({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: false,
                timeout: 20000,
                forceNew: false,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay
            });

            this.socket.on('connect', () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
                this.flushMessageQueue();
                this.subscribeToChannels();
                console.log('Socket.IO连接已建立');
            });

            this.socket.on('disconnect', (reason) => {
                this.isConnected = false;
                this.showConnectionStatus('disconnected');
                console.log('Socket.IO连接已断开:', reason);
            });

            this.socket.on('connect_error', (error) => {
                console.error('Socket.IO连接错误:', error);
                this.showConnectionStatus('error');
            });

            this.socket.on('reconnect', (attemptNumber) => {
                console.log(`Socket.IO重连成功，尝试次数: ${attemptNumber}`);
                this.showConnectionStatus('connected');
            });

            this.socket.on('reconnect_attempt', (attemptNumber) => {
                console.log(`Socket.IO重连尝试: ${attemptNumber}`);
            });

            this.socket.on('reconnect_error', (error) => {
                console.error('Socket.IO重连失败:', error);
            });

            this.socket.on('reconnect_failed', () => {
                console.error('Socket.IO重连失败，已达到最大尝试次数');
                this.showConnectionStatus('failed');
            });

            // 监听消息
            this.socket.on('message', (data) => {
                this.handleMessage(data);
            });

            this.socket.on('task_update', (data) => {
                this.handleTaskUpdate(data);
            });

            this.socket.on('document_update', (data) => {
                this.handleDocumentUpdate(data);
            });

            this.socket.on('system_status', (data) => {
                this.handleSystemStatus(data);
            });

        } catch (error) {
            console.error('创建Socket.IO连接失败:', error);
            this.showConnectionStatus('error');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
    }

    send(event, data) {
        if (this.isConnected && this.socket) {
            this.socket.emit(event, data);
        } else {
            this.messageQueue.push({ event, data });
        }
    }

    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const { event, data } = this.messageQueue.shift();
            this.socket.emit(event, data);
        }
    }

    subscribeToChannels() {
        // 订阅默认频道
        this.send('subscribe', { channels: ['tasks', 'documents', 'system'] });
    }

    handleMessage(data) {
        console.log('收到消息:', data);
        this.triggerEvent('message', data);
    }

    handleTaskUpdate(data) {
        console.log('任务更新:', data);
        this.triggerEvent('task_update', data);

        // 更新UI
        this.updateTaskUI(data);
    }

    handleDocumentUpdate(data) {
        console.log('文档更新:', data);
        this.triggerEvent('document_update', data);

        // 更新UI
        this.updateDocumentUI(data);
    }

    handleSystemStatus(data) {
        console.log('系统状态:', data);
        this.triggerEvent('system_status', data);

        // 更新UI
        this.updateSystemStatusUI(data);
    }

    updateTaskUI(data) {
        // 更新任务进度条
        const progressBar = document.querySelector(`[data-task-id="${data.task_id}"] .progress-bar`);
        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.textContent = `${data.progress}%`;
        }

        // 更新任务状态
        const statusElement = document.querySelector(`[data-task-id="${data.task_id}"] .task-status`);
        if (statusElement) {
            statusElement.textContent = data.status;
            statusElement.className = `task-status status-${data.status}`;
        }
    }

    updateDocumentUI(data) {
        // 更新文档列表
        const documentCard = document.querySelector(`[data-document-id="${data.document_id}"]`);
        if (documentCard) {
            const statusElement = documentCard.querySelector('.document-status');
            if (statusElement) {
                statusElement.textContent = data.status;
                statusElement.className = `document-status status-${data.status}`;
            }
        }
    }

    updateSystemStatusUI(data) {
        // 更新系统状态指示器
        const statusIndicator = document.querySelector('.system-status');
        if (statusIndicator) {
            statusIndicator.className = `system-status status-${data.status}`;
            statusIndicator.title = data.message || '';
        }
    }

    showConnectionStatus(status) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.className = `connection-status status-${status}`;

            let message = '';
            switch (status) {
                case 'connected':
                    message = '已连接';
                    break;
                case 'disconnected':
                    message = '已断开';
                    break;
                case 'error':
                    message = '连接错误';
                    break;
                case 'failed':
                    message = '连接失败';
                    break;
                default:
                    message = '未知状态';
            }

            statusElement.textContent = message;
        }

        // 显示通知 - 只在首次连接成功或连接失败时显示
        if (status === 'connected' && !this.hasShownConnectedNotification) {
            this.hasShownConnectedNotification = true;
            // 只在首次连接时显示提示，避免频繁提示
            // this.showNotification('实时更新已连接', 'success');
        } else if (status === 'disconnected') {
            this.hasShownConnectedNotification = false; // 重置标志
        } else if (status === 'error' || status === 'failed') {
            this.showNotification('实时更新连接失败', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // 简单的通知显示
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // 事件系统
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    triggerEvent(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`事件处理器错误 (${event}):`, error);
                }
            });
        }
    }
}

// 全局实例
let realtimeUpdates = null;

// 初始化函数
function initRealtimeUpdates() {
    if (!realtimeUpdates) {
        realtimeUpdates = new RealtimeUpdatesFixed();
    }
    return realtimeUpdates;
}

// 页面加载完成后自动初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRealtimeUpdates);
} else {
    initRealtimeUpdates();
}

// 导出全局访问
window.RealtimeUpdates = RealtimeUpdatesFixed;
window.realtimeUpdates = realtimeUpdates;
