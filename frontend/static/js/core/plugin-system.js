/**
 * Winston Architecture 2.0 - 插件系统
 * 提供插件注册、加载、生命周期管理
 */

export class PluginSystem {
    constructor(application) {
        this.app = application;
        this.plugins = new Map();
        this.loadedPlugins = new Set();
        this.pluginDependencies = new Map();
    }

    /**
     * 注册插件
     */
    register(plugin, options = {}) {
        const pluginInfo = this.validatePlugin(plugin);
        
        this.plugins.set(pluginInfo.name, {
            plugin,
            options,
            state: 'registered',
            dependencies: pluginInfo.dependencies || [],
            version: pluginInfo.version || '1.0.0'
        });

        console.log(`📝 Plugin registered: ${pluginInfo.name}`);
        return this;
    }

    /**
     * 动态加载插件
     */
    async load(pluginConfig) {
        try {
            let plugin;
            
            if (typeof pluginConfig === 'string') {
                // 从路径加载插件
                const module = await import(pluginConfig);
                plugin = module.default || module;
            } else if (pluginConfig.path) {
                // 从配置加载插件
                const module = await import(pluginConfig.path);
                plugin = module.default || module;
            } else {
                // 直接使用插件对象
                plugin = pluginConfig;
            }

            return this.register(plugin, pluginConfig.options || {});
        } catch (error) {
            console.error('Failed to load plugin:', error);
            throw error;
        }
    }

    /**
     * 安装插件
     */
    async install(pluginName) {
        const pluginInfo = this.plugins.get(pluginName);
        if (!pluginInfo) {
            throw new Error(`Plugin not found: ${pluginName}`);
        }

        if (this.loadedPlugins.has(pluginName)) {
            console.warn(`Plugin already installed: ${pluginName}`);
            return;
        }

        // 检查并安装依赖
        await this.installDependencies(pluginInfo.dependencies);

        try {
            pluginInfo.state = 'installing';

            // 执行插件安装
            if (typeof pluginInfo.plugin.install === 'function') {
                await pluginInfo.plugin.install(this.app, pluginInfo.options);
            }

            pluginInfo.state = 'installed';
            this.loadedPlugins.add(pluginName);

            console.log(`✅ Plugin installed: ${pluginName}`);

            // 发布插件安装事件
            this.app.eventBus.emit('plugin:installed', {
                name: pluginName,
                plugin: pluginInfo.plugin
            });

        } catch (error) {
            pluginInfo.state = 'error';
            console.error(`❌ Plugin installation failed: ${pluginName}`, error);
            throw error;
        }
    }

    /**
     * 安装插件依赖
     */
    async installDependencies(dependencies) {
        for (const dep of dependencies) {
            if (!this.loadedPlugins.has(dep)) {
                await this.install(dep);
            }
        }
    }

    /**
     * 卸载插件
     */
    async uninstall(pluginName) {
        const pluginInfo = this.plugins.get(pluginName);
        if (!pluginInfo) {
            throw new Error(`Plugin not found: ${pluginName}`);
        }

        if (!this.loadedPlugins.has(pluginName)) {
            console.warn(`Plugin not installed: ${pluginName}`);
            return;
        }

        try {
            pluginInfo.state = 'uninstalling';

            // 执行插件卸载
            if (typeof pluginInfo.plugin.uninstall === 'function') {
                await pluginInfo.plugin.uninstall(this.app);
            }

            pluginInfo.state = 'uninstalled';
            this.loadedPlugins.delete(pluginName);

            console.log(`🗑️ Plugin uninstalled: ${pluginName}`);

            // 发布插件卸载事件
            this.app.eventBus.emit('plugin:uninstalled', {
                name: pluginName,
                plugin: pluginInfo.plugin
            });

        } catch (error) {
            pluginInfo.state = 'error';
            console.error(`❌ Plugin uninstallation failed: ${pluginName}`, error);
            throw error;
        }
    }

    /**
     * 安装所有已注册的插件
     */
    async installAll() {
        const pluginNames = Array.from(this.plugins.keys());
        const installOrder = this.resolveInstallOrder(pluginNames);

        for (const pluginName of installOrder) {
            await this.install(pluginName);
        }
    }

    /**
     * 卸载所有插件
     */
    async uninstallAll() {
        const pluginNames = Array.from(this.loadedPlugins);
        
        // 反向卸载
        for (let i = pluginNames.length - 1; i >= 0; i--) {
            await this.uninstall(pluginNames[i]);
        }
    }

    /**
     * 销毁所有插件
     */
    async destroyAll() {
        await this.uninstallAll();
        this.plugins.clear();
        this.loadedPlugins.clear();
        this.pluginDependencies.clear();
    }

    /**
     * 解析插件安装顺序（考虑依赖关系）
     */
    resolveInstallOrder(pluginNames) {
        const visited = new Set();
        const visiting = new Set();
        const result = [];

        const visit = (pluginName) => {
            if (visited.has(pluginName)) return;
            if (visiting.has(pluginName)) {
                throw new Error(`Circular dependency detected: ${pluginName}`);
            }

            visiting.add(pluginName);

            const pluginInfo = this.plugins.get(pluginName);
            if (pluginInfo) {
                for (const dep of pluginInfo.dependencies) {
                    visit(dep);
                }
            }

            visiting.delete(pluginName);
            visited.add(pluginName);
            result.push(pluginName);
        };

        for (const pluginName of pluginNames) {
            visit(pluginName);
        }

        return result;
    }

    /**
     * 验证插件格式
     */
    validatePlugin(plugin) {
        if (!plugin || typeof plugin !== 'object') {
            throw new Error('Plugin must be an object');
        }

        if (!plugin.name || typeof plugin.name !== 'string') {
            throw new Error('Plugin must have a name property');
        }

        if (typeof plugin.install !== 'function') {
            throw new Error('Plugin must have an install method');
        }

        return {
            name: plugin.name,
            version: plugin.version,
            dependencies: plugin.dependencies || [],
            description: plugin.description
        };
    }

    /**
     * 获取插件信息
     */
    getPlugin(name) {
        return this.plugins.get(name);
    }

    /**
     * 检查插件是否已安装
     */
    isInstalled(name) {
        return this.loadedPlugins.has(name);
    }

    /**
     * 列出所有插件
     */
    list() {
        return Array.from(this.plugins.entries()).map(([name, info]) => ({
            name,
            state: info.state,
            version: info.version,
            dependencies: info.dependencies,
            installed: this.loadedPlugins.has(name)
        }));
    }

    /**
     * 获取插件统计信息
     */
    getStats() {
        const plugins = this.list();
        return {
            total: plugins.length,
            installed: plugins.filter(p => p.installed).length,
            failed: plugins.filter(p => p.state === 'error').length,
            plugins
        };
    }
}

/**
 * 插件接口定义
 */
export class PluginBase {
    constructor(name, version = '1.0.0') {
        this.name = name;
        this.version = version;
        this.dependencies = [];
        this.description = '';
    }

    /**
     * 插件安装方法 - 必须实现
     */
    async install(app, options = {}) {
        throw new Error('Plugin install method must be implemented');
    }

    /**
     * 插件卸载方法 - 可选
     */
    async uninstall(app) {
        // 默认为空实现
    }

    /**
     * 设置依赖
     */
    dependsOn(...dependencies) {
        this.dependencies = dependencies;
        return this;
    }

    /**
     * 设置描述
     */
    setDescription(description) {
        this.description = description;
        return this;
    }
}

// 插件工具函数
export const PluginUtils = {
    /**
     * 创建简单插件
     */
    create(name, installFn, uninstallFn = null) {
        return {
            name,
            install: installFn,
            uninstall: uninstallFn
        };
    },

    /**
     * 创建异步插件
     */
    async createAsync(name, modulePath) {
        const module = await import(modulePath);
        return module.default || module;
    }
};