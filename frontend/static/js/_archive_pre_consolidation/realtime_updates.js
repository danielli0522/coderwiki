/**
 * 实时更新组件
 * 负责WebSocket连接和实时数据处理
 */
class RealtimeUpdates {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageQueue = [];
        this.subscribedChannels = new Set();

        // 尝试加载Socket.IO
        this.socketio = null;
        this.loadSocketIO();

        this.init();
    }

    async loadSocketIO() {
        try {
            // 动态加载Socket.IO客户端
            if (typeof io !== 'undefined') {
                this.socketio = io;
                console.log('Socket.IO已加载');
            } else {
                // 如果页面没有加载Socket.IO，尝试动态加载
                await this.loadSocketIOScript();
            }
        } catch (error) {
            console.warn('Socket.IO加载失败，将使用原生WebSocket:', error);
        }
    }

    async loadSocketIOScript() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
            script.onload = () => {
                this.socketio = io;
                resolve();
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    init() {
        this.setupEventListeners();
        this.connect();
    }

    setupEventListeners() {
        // 页面可见性变化时重新连接
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected) {
                this.connect();
            }
        });

        // 页面卸载时断开连接
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });
    }

    connect() {
        if (this.isConnected) {
            return;
        }

        // 优先使用Socket.IO
        if (this.socketio) {
            this.connectSocketIO();
        } else {
            this.connectWebSocket();
        }
    }

    connectSocketIO() {
        try {
            console.log('尝试Socket.IO连接...');

            this.socket = this.socketio({
                transports: ['websocket', 'polling'],
                timeout: 5000,
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

            this.socket.on('message', (data) => {
                this.handleMessage(data);
            });

            this.socket.on('subscribed', (data) => {
                console.log('已订阅频道:', data.channel);
            });

            this.socket.on('unsubscribed', (data) => {
                console.log('已取消订阅频道:', data.channel);
            });

        } catch (error) {
            console.error('Socket.IO连接失败，回退到WebSocket:', error);
            this.connectWebSocket();
        }
    }

    connectWebSocket() {
        // WebSocket回退方法
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            // 使用Socket.IO WebSocket endpoint 
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/socket.io/?EIO=4&transport=websocket`;

            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
                this.flushMessageQueue();
                this.subscribeToChannels();
                console.log('WebSocket连接已建立');
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('解析WebSocket消息失败:', error);
                }
            };

            this.socket.onclose = (event) => {
                this.isConnected = false;
                this.showConnectionStatus('disconnected');
                if (event.code !== 1000) {
                    console.log('WebSocket连接已关闭，尝试重连...');
                    this.scheduleReconnect();
                }
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.showConnectionStatus('error');
            };

        } catch (error) {
            console.error('创建WebSocket连接失败:', error);
            this.showConnectionStatus('error');
            this.scheduleReconnect();
        }
    }

    disconnect() {
        if (this.socket) {
            if (this.socketio && this.socket.connected) {
                this.socket.disconnect();
            } else if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.close(1000, '用户主动断开连接');
            }
            this.socket = null;
            this.isConnected = false;
            this.showConnectionStatus('disconnected');
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('达到最大重连次数，停止重连');
            this.showConnectionStatus('failed');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`第${this.reconnectAttempts}次重连，${delay}ms后执行`);

        setTimeout(() => {
            this.connect();
        }, delay);
    }

    subscribeToChannels() {
        if (!this.isConnected) return;

        // 订阅用户相关频道
        const userId = this.getCurrentUserId();
        if (userId) {
            this.send({
                type: 'subscribe',
                channel: `user:${userId}`
            });
        }

        // 订阅系统状态频道
        this.send({
            type: 'subscribe',
            channel: 'system:status'
        });

        // 订阅任务更新频道
        this.send({
            type: 'subscribe',
            channel: 'tasks:updates'
        });
    }

    send(data) {
        if (this.isConnected && this.socket) {
            if (this.socketio && this.socket.connected) {
                this.socket.emit('message', data);
            } else if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify(data));
            }
        } else {
            // 如果未连接，将消息加入队列
            this.messageQueue.push(data);
        }
    }

    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    handleMessage(data) {
        try {
            console.log('收到实时消息:', data);

            // 处理服务器返回的消息格式
            if (data.data && typeof data.data === 'string') {
                // 尝试解析服务器返回的数据
                try {
                    const parsedData = JSON.parse(data.data.replace("Server received: ", ""));
                    if (parsedData && typeof parsedData === 'object') {
                        data = parsedData;
                    }
                } catch (e) {
                    // 如果解析失败，保持原样
                }
            }

            // 根据消息类型处理
            const messageType = data.type || data.message_type;
            switch (messageType) {
                case 'task_update':
                    this.handleTaskUpdate(data);
                    break;
                case 'repository_status_update':
                    this.handleRepositoryStatusUpdate(data);
                    break;
                case 'system_status':
                    this.handleSystemStatus(data);
                    break;
                case 'user_notification':
                    this.handleUserNotification(data);
                    break;
                case 'subscribed':
                    console.log('成功订阅频道:', data.channel);
                    break;
                case 'unsubscribed':
                    console.log('成功取消订阅频道:', data.channel);
                    break;
                case 'connected':
                    console.log('WebSocket连接已建立');
                    break;
                default:
                    if (messageType) {
                        console.log('未知消息类型:', messageType);
                    } else {
                        console.log('收到消息:', data);
                    }
            }
        } catch (error) {
            console.error('处理消息失败:', error);
        }
    }

    handleTaskUpdate(data) {
        // 更新任务状态
        const taskId = data.task_id;
        const status = data.status;
        const progress = data.progress;

        // 触发自定义事件
        const event = new CustomEvent('taskUpdate', {
            detail: { taskId, status, progress, data }
        });
        document.dispatchEvent(event);
    }

    handleRepositoryStatusUpdate(data) {
        // 更新仓库状态
        const repositoryId = data.repository_id;
        const status = data.status;
        const name = data.name;
        const error = data.error;

        // 触发自定义事件
        const event = new CustomEvent('repositoryStatusUpdate', {
            detail: { repositoryId, status, name, error, data }
        });
        document.dispatchEvent(event);
    }

    handleSystemStatus(data) {
        // 更新系统状态
        const status = data.status;
        const metrics = data.metrics;

        // 触发自定义事件
        const event = new CustomEvent('systemStatus', {
            detail: { status, metrics, data }
        });
        document.dispatchEvent(event);
    }

    handleUserNotification(data) {
        // 显示用户通知
        const message = data.message;
        const type = data.notification_type || 'info';

        // 触发自定义事件
        const event = new CustomEvent('userNotification', {
            detail: { message, type, data }
        });
        document.dispatchEvent(event);
    }

    showConnectionStatus(status) {
        // 更新连接状态显示
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = this.getStatusText(status);
        }

        // 触发自定义事件
        const event = new CustomEvent('connectionStatus', {
            detail: { status }
        });
        document.dispatchEvent(event);
    }

    getStatusText(status) {
        const statusTexts = {
            'connected': '已连接',
            'disconnected': '未连接',
            'error': '连接错误',
            'failed': '连接失败'
        };
        return statusTexts[status] || '未知状态';
    }

    getCurrentUserId() {
        // 从页面数据或localStorage获取用户ID
        const userData = document.querySelector('meta[name="user-id"]');
        if (userData) {
            return userData.getAttribute('content');
        }

        // 从localStorage获取
        return localStorage.getItem('user_id');
    }

    // 公共方法：订阅特定频道
    subscribe(channel) {
        if (this.subscribedChannels.has(channel)) {
            return;
        }

        this.subscribedChannels.add(channel);
        this.send({
            type: 'subscribe',
            channel: channel
        });
    }

    // 公共方法：取消订阅特定频道
    unsubscribe(channel) {
        if (!this.subscribedChannels.has(channel)) {
            return;
        }

        this.subscribedChannels.delete(channel);
        this.send({
            type: 'unsubscribe',
            channel: channel
        });
    }
}

// 创建全局实例
window.realtimeUpdates = new RealtimeUpdates();
