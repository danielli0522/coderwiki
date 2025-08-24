/**
 * 组件加载器
 * 统一管理组件的加载和重复声明检查
 */

// 组件注册表
window.ComponentRegistry = window.ComponentRegistry || {
    components: new Map(),

    // 注册组件
    register: function(name, componentClass) {
        if (this.components.has(name)) {
            console.warn(`${name} already registered, skipping...`);
            return false;
        }

        this.components.set(name, componentClass);
        window[name] = componentClass;
        console.log(`${name} registered successfully`);
        return true;
    },

    // 检查组件是否已注册
    isRegistered: function(name) {
        return this.components.has(name);
    },

    // 获取组件
    get: function(name) {
        return this.components.get(name);
    },

    // 列出所有已注册的组件
    list: function() {
        return Array.from(this.components.keys());
    }
};

// 组件加载器
window.ComponentLoader = {
    // 加载组件脚本
    loadComponent: function(scriptPath, componentName) {
        return new Promise((resolve, reject) => {
            // 检查组件是否已加载
            if (window.ComponentRegistry.isRegistered(componentName)) {
                console.log(`${componentName} already loaded, skipping...`);
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = scriptPath;
            script.onload = () => {
                console.log(`${componentName} loaded successfully`);
                resolve();
            };
            script.onerror = () => {
                console.error(`Failed to load ${componentName} from ${scriptPath}`);
                reject(new Error(`Failed to load ${componentName}`));
            };
            document.head.appendChild(script);
        });
    },

    // 批量加载组件
    loadComponents: async function(componentList) {
        const results = [];

        for (const [scriptPath, componentName] of componentList) {
            try {
                await this.loadComponent(scriptPath, componentName);
                results.push({ component: componentName, status: 'success' });
            } catch (error) {
                results.push({ component: componentName, status: 'error', error: error.message });
            }
        }

        return results;
    }
};

// 导出到全局
window.ComponentRegistry = window.ComponentRegistry;
window.ComponentLoader = window.ComponentLoader;
