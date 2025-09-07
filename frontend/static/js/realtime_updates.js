/**
 * Enhanced Real-time Updates Component (QA Fix for PERF-001)
 * Provides WebSocket-based real-time updates for repository status and system events
 * Includes fallback to polling for compatibility
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
        this.pollingInterval = null;
        this.pollingEnabled = false;

        // Socket.IO availability
        this.socketio = null;
        this.loadSocketIO();

        this.init();
    }

    async loadSocketIO() {
        try {
            if (typeof io !== 'undefined') {
                this.socketio = io;
                console.log('✅ Socket.IO detected and ready');
            } else {
                console.log('⚠️ Socket.IO not found, will use fallback polling');
                this.enablePollingFallback();
            }
        } catch (error) {
            console.warn('Socket.IO load failed, using polling fallback:', error);
            this.enablePollingFallback();
        }
    }

    init() {
        this.setupEventListeners();
        
        // Try WebSocket first, fallback to polling if needed
        if (this.socketio) {
            this.connect();
        } else {
            console.log('🔄 Starting with polling fallback while Socket.IO loads');
            this.enablePollingFallback();
        }
    }

    setupEventListeners() {
        // Page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected && !this.pollingEnabled) {
                this.connect();
            }
        });

        // Page unload cleanup
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });

        // Listen for repository status update requests
        document.addEventListener('requestRepositoryStatusUpdate', (event) => {
            if (this.isConnected) {
                this.send({
                    type: 'get_repository_status',
                    repository_id: event.detail.repositoryId
                });
            }
        });
    }

    connect() {
        if (this.isConnected) return;

        if (this.socketio) {
            this.connectSocketIO();
        } else {
            console.log('🔄 Socket.IO not available, using polling fallback');
            this.enablePollingFallback();
        }
    }

    connectSocketIO() {
        try {
            console.log('🔌 Attempting Socket.IO connection...');

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
                this.disablePollingFallback(); // Stop polling when WebSocket works
                this.showConnectionStatus('connected');
                this.flushMessageQueue();
                this.subscribeToChannels();
                console.log('✅ Socket.IO connection established');
            });

            this.socket.on('disconnect', (reason) => {
                this.isConnected = false;
                this.showConnectionStatus('disconnected');
                console.log('❌ Socket.IO disconnected:', reason);
                
                // Enable polling fallback if WebSocket fails
                if (reason === 'transport error' || reason === 'transport close') {
                    console.log('🔄 Enabling polling fallback due to transport issues');
                    this.enablePollingFallback();
                }
            });

            this.socket.on('connect_error', (error) => {
                console.error('❌ Socket.IO connection error:', error);
                this.showConnectionStatus('error');
                // Enable polling fallback on connection error
                this.enablePollingFallback();
            });

            this.socket.on('message', (data) => {
                this.handleMessage(data);
            });

            // Repository-specific events
            this.socket.on('repository_status_update', (data) => {
                this.handleRepositoryStatusUpdate(data);
            });

            this.socket.on('task_update', (data) => {
                this.handleTaskUpdate(data);
            });

        } catch (error) {
            console.error('❌ Socket.IO connection failed, using polling fallback:', error);
            this.enablePollingFallback();
        }
    }

    enablePollingFallback() {
        if (this.pollingEnabled) return;
        
        this.pollingEnabled = true;
        console.log('🔄 Starting polling fallback for real-time updates');
        
        this.showConnectionStatus('polling');
        
        // Poll every 10 seconds for repository status updates
        this.pollingInterval = setInterval(() => {
            this.pollRepositoryStatus();
            this.pollTaskStatus();
        }, 10000);
        
        // Initial poll
        setTimeout(() => {
            this.pollRepositoryStatus();
            this.pollTaskStatus();
        }, 1000);
    }

    disablePollingFallback() {
        if (!this.pollingEnabled) return;
        
        this.pollingEnabled = false;
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        console.log('✅ Polling fallback disabled - WebSocket active');
    }

    async pollRepositoryStatus() {
        try {
            const response = await fetch('/api/repositories?status_only=true', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                if (data.repositories) {
                    // Check for status changes and emit events
                    data.repositories.forEach(repo => {
                        // Emit repository status update event
                        this.handleRepositoryStatusUpdate({
                            repository_id: repo.id,
                            status: repo.status,
                            name: repo.name,
                            progress: repo.progress || 0,
                            last_updated: repo.updated_at
                        });
                    });
                }
            }
        } catch (error) {
            console.warn('⚠️ Polling repository status failed:', error);
        }
    }

    async pollTaskStatus() {
        try {
            const response = await fetch('/api/tasks?status_only=true&active=true', {
                method: 'GET', 
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                if (data.tasks) {
                    data.tasks.forEach(task => {
                        if (task.status === 'running' || task.status === 'pending') {
                            this.handleTaskUpdate({
                                task_id: task.id,
                                status: task.status,
                                progress: task.progress || 0,
                                repository_id: task.repository_id
                            });
                        }
                    });
                }
            }
        } catch (error) {
            console.warn('⚠️ Polling task status failed:', error);
        }
    }

    disconnect() {
        if (this.socket) {
            if (this.socketio && this.socket.connected) {
                this.socket.disconnect();
            }
            this.socket = null;
            this.isConnected = false;
            this.showConnectionStatus('disconnected');
        }
        
        this.disablePollingFallback();
    }

    subscribeToChannels() {
        if (!this.isConnected) return;

        // Subscribe to user-specific updates
        const userId = this.getCurrentUserId();
        if (userId) {
            this.subscribe(`user:${userId}`);
        }

        // Subscribe to system-wide updates
        this.subscribe('system:status');
        this.subscribe('repositories:updates');
        this.subscribe('tasks:updates');
    }

    send(data) {
        if (this.isConnected && this.socket) {
            if (this.socketio && this.socket.connected) {
                this.socket.emit('message', data);
            }
        } else {
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
            const messageType = data.type || data.message_type;
            switch (messageType) {
                case 'repository_status_update':
                    this.handleRepositoryStatusUpdate(data);
                    break;
                case 'task_update':
                    this.handleTaskUpdate(data);
                    break;
                case 'system_status':
                    this.handleSystemStatus(data);
                    break;
                case 'user_notification':
                    this.handleUserNotification(data);
                    break;
                default:
                    console.log('📨 Received message:', data);
            }
        } catch (error) {
            console.error('❌ Message handling failed:', error);
        }
    }

    handleRepositoryStatusUpdate(data) {
        console.log('📁 Repository status update:', data);
        
        const event = new CustomEvent('repositoryStatusUpdate', {
            detail: {
                repositoryId: data.repository_id,
                status: data.status,
                name: data.name,
                progress: data.progress || 0,
                error: data.error,
                lastUpdated: data.last_updated,
                data: data
            }
        });
        document.dispatchEvent(event);
        
        // Update UI elements directly if they exist
        this.updateRepositoryUI(data);
    }

    handleTaskUpdate(data) {
        console.log('⚙️ Task update:', data);
        
        const event = new CustomEvent('taskUpdate', {
            detail: {
                taskId: data.task_id,
                status: data.status,
                progress: data.progress || 0,
                repositoryId: data.repository_id,
                data: data
            }
        });
        document.dispatchEvent(event);
    }

    handleSystemStatus(data) {
        const event = new CustomEvent('systemStatus', {
            detail: { status: data.status, metrics: data.metrics, data: data }
        });
        document.dispatchEvent(event);
    }

    handleUserNotification(data) {
        const event = new CustomEvent('userNotification', {
            detail: {
                message: data.message,
                type: data.notification_type || 'info',
                data: data
            }
        });
        document.dispatchEvent(event);
        
        // Show notification if UI framework is available
        if (window.showToast) {
            window.showToast(data.message, data.notification_type || 'info');
        }
    }

    updateRepositoryUI(data) {
        // Update repository status in tables/cards
        const repoElements = document.querySelectorAll(`[data-repo-id="${data.repository_id}"]`);
        
        repoElements.forEach(element => {
            // Update status badge
            const statusBadge = element.querySelector('.repo-status, .status-badge');
            if (statusBadge) {
                statusBadge.className = `repo-status status-${data.status}`;
                statusBadge.textContent = this.formatStatus(data.status);
            }

            // Update progress bar
            const progressBar = element.querySelector('.progress-bar');
            if (progressBar && data.progress !== undefined) {
                progressBar.style.width = `${data.progress}%`;
                progressBar.setAttribute('aria-valuenow', data.progress);
            }

            // Update progress text
            const progressText = element.querySelector('.progress-text');
            if (progressText && data.progress !== undefined) {
                progressText.textContent = `${data.progress}%`;
            }

            // Update timestamp
            const timestamp = element.querySelector('.last-updated');
            if (timestamp && data.last_updated) {
                timestamp.textContent = this.formatTimestamp(data.last_updated);
            }
        });
    }

    formatStatus(status) {
        const statusMap = {
            'pending': '等待中',
            'analyzing': '分析中',
            'completed': '已完成',
            'failed': '失败',
            'running': '运行中'
        };
        return statusMap[status] || status;
    }

    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-CN');
        } catch (error) {
            return timestamp;
        }
    }

    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = this.getStatusText(status);
        }

        // Update favicon or page title to indicate connection status
        if (status === 'connected') {
            document.title = document.title.replace(' (离线)', '');
        } else if (status === 'disconnected' || status === 'error') {
            if (!document.title.includes('(离线)')) {
                document.title += ' (离线)';
            }
        }

        const event = new CustomEvent('connectionStatus', {
            detail: { status }
        });
        document.dispatchEvent(event);
    }

    getStatusText(status) {
        const statusTexts = {
            'connected': '✅ 已连接',
            'disconnected': '❌ 未连接', 
            'polling': '🔄 轮询模式',
            'error': '⚠️ 连接错误',
            'failed': '💥 连接失败'
        };
        return statusTexts[status] || '❓ 未知状态';
    }

    getCurrentUserId() {
        const userData = document.querySelector('meta[name="user-id"]');
        if (userData) {
            return userData.getAttribute('content');
        }
        return localStorage.getItem('user_id');
    }

    // Public methods
    subscribe(channel) {
        if (this.subscribedChannels.has(channel)) return;
        
        this.subscribedChannels.add(channel);
        this.send({
            type: 'subscribe',
            channel: channel
        });
    }

    unsubscribe(channel) {
        if (!this.subscribedChannels.has(channel)) return;
        
        this.subscribedChannels.delete(channel);
        this.send({
            type: 'unsubscribe',
            channel: channel
        });
    }

    // Request immediate repository status update
    requestRepositoryUpdate(repositoryId) {
        if (this.isConnected) {
            this.send({
                type: 'get_repository_status',
                repository_id: repositoryId
            });
        } else {
            // Force a poll if not connected via WebSocket
            this.pollRepositoryStatus();
        }
    }

    // Check if real-time updates are working
    isRealTimeActive() {
        return this.isConnected || this.pollingEnabled;
    }

    // Get connection info for debugging
    getConnectionInfo() {
        return {
            connected: this.isConnected,
            polling: this.pollingEnabled,
            socketType: this.socketio ? 'Socket.IO' : 'WebSocket',
            subscribedChannels: Array.from(this.subscribedChannels)
        };
    }
}

// Initialize global instance
if (typeof window !== 'undefined') {
    window.realtimeUpdates = new RealtimeUpdates();
    
    // Expose for debugging
    window.debugRealtime = () => {
        console.log('🔍 Realtime Updates Debug Info:', window.realtimeUpdates.getConnectionInfo());
    };
}