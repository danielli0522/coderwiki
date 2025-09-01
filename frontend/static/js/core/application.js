/**
 * Winston Architecture 2.0 - 应用主入口
 * 统一的应用生命周期管理和依赖注入
 */

import { PluginSystem } from './plugin-system.js';
import { EventBus } from './event-bus.js';
import { ServiceContainer } from './service-container.js';
import { AppConfig } from '../config/app.config.js';

class Application {
    constructor(config = {}) {
        this.config = { ...AppConfig, ...config };
        this.state = 'initializing';
        
        // 核心系统
        this.eventBus = new EventBus();
        this.services = new ServiceContainer(this.eventBus);
        this.plugins = new PluginSystem(this);
        
        // 生命周期钩子
        this.hooks = {
            beforeInit: [],
            afterInit: [],
            beforeDestroy: [],
            afterDestroy: []
        };

        this.bindMethods();
    }

    bindMethods() {
        this.init = this.init.bind(this);
        this.destroy = this.destroy.bind(this);
        this.use = this.use.bind(this);
        this.service = this.service.bind(this);
    }

    /**
     * 初始化应用
     */
    async init() {
        try {
            console.log('🚀 Winston Application 2.0 initializing...');
            
            await this.runHooks('beforeInit');
            
            this.state = 'initializing';
            
            // 1. 注册核心服务
            await this.registerCoreServices();
            
            // 2. 加载插件
            await this.loadPlugins();
            
            // 3. 初始化UI框架
            await this.initUIFramework();
            
            // 4. 启动性能监控
            await this.startPerformanceMonitoring();
            
            this.state = 'ready';
            
            await this.runHooks('afterInit');
            
            console.log('✅ Winston Application initialized successfully');
            
            // 发布应用就绪事件
            this.eventBus.emit('app:ready', { app: this });
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.state = 'error';
            this.eventBus.emit('app:error', { error });
            throw error;
        }
    }

    /**
     * 注册核心服务
     */
    async registerCoreServices() {
        const { ApiClient } = await import('../services/api/client.js');
        const { ApiErrorHandler } = await import('../services/api/error-handler.js');
        const { Authentication } = await import('../services/auth/authentication.js');
        const { PerformanceMonitor } = await import('../services/performance/monitor.js');
        const { FocusManager } = await import('../ui/accessibility/focus-manager.js');

        // 注册服务实例
        this.services.register('api', new ApiClient(this.config.api));
        this.services.register('errorHandler', new ApiErrorHandler());
        this.services.register('auth', new Authentication());
        this.services.register('performance', new PerformanceMonitor());
        this.services.register('focusManager', new FocusManager());
        
        console.log('📦 Core services registered');
    }

    /**
     * 加载插件
     */
    async loadPlugins() {
        const pluginsToLoad = this.config.plugins || [];
        
        for (const pluginConfig of pluginsToLoad) {
            await this.plugins.load(pluginConfig);
        }
        
        console.log(`🔌 Loaded ${pluginsToLoad.length} plugins`);
    }

    /**
     * 初始化UI框架
     */
    async initUIFramework() {
        const { UIFramework } = await import('../ui/framework/component-base.js');
        
        this.ui = new UIFramework({
            eventBus: this.eventBus,
            services: this.services
        });
        
        await this.ui.init();
        
        console.log('🎨 UI Framework initialized');
    }

    /**
     * 启动性能监控
     */
    async startPerformanceMonitoring() {
        const performanceService = this.services.get('performance');
        
        if (performanceService && this.config.performance.enabled) {
            await performanceService.start();
            console.log('⚡ Performance monitoring started');
        }
    }

    /**
     * 使用插件
     */
    use(plugin, options = {}) {
        this.plugins.register(plugin, options);
        return this;
    }

    /**
     * 获取服务
     */
    service(name) {
        return this.services.get(name);
    }

    /**
     * 添加生命周期钩子
     */
    hook(name, callback) {
        if (this.hooks[name]) {
            this.hooks[name].push(callback);
        }
        return this;
    }

    /**
     * 运行生命周期钩子
     */
    async runHooks(hookName) {
        const hooks = this.hooks[hookName] || [];
        
        for (const hook of hooks) {
            try {
                await hook(this);
            } catch (error) {
                console.error(`Hook ${hookName} failed:`, error);
            }
        }
    }

    /**
     * 销毁应用
     */
    async destroy() {
        try {
            await this.runHooks('beforeDestroy');
            
            this.state = 'destroying';
            
            // 销毁插件
            await this.plugins.destroyAll();
            
            // 停止服务
            await this.services.destroyAll();
            
            // 清理UI
            if (this.ui) {
                await this.ui.destroy();
            }
            
            // 清理事件总线
            this.eventBus.removeAllListeners();
            
            this.state = 'destroyed';
            
            await this.runHooks('afterDestroy');
            
            console.log('🗑️ Winston Application destroyed');
            
        } catch (error) {
            console.error('❌ Application destroy failed:', error);
            throw error;
        }
    }

    /**
     * 获取应用状态
     */
    getState() {
        return {
            state: this.state,
            services: this.services.list(),
            plugins: this.plugins.list(),
            config: this.config
        };
    }

    /**
     * 开发者工具
     */
    inspect() {
        return {
            application: this.getState(),
            eventBus: this.eventBus.getListeners(),
            performance: this.service('performance')?.getMetrics() || null
        };
    }
}

// 单例模式 - 确保全局只有一个应用实例
let appInstance = null;

export function createApplication(config) {
    if (appInstance) {
        console.warn('Application instance already exists');
        return appInstance;
    }
    
    appInstance = new Application(config);
    return appInstance;
}

export function getApplication() {
    return appInstance;
}

// 导出应用类
export { Application };