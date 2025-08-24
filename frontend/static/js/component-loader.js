/**
 * Component Loader Utility
 * Prevents duplicate component loading and provides better error handling
 */

const ComponentLoader = {
    // Track loaded components to prevent duplicates
    loadedComponents: new Set(),

    // Track loading promises to prevent race conditions
    loadingPromises: new Map(),

    /**
     * Load a component script safely
     * @param {string} scriptSrc - The script source URL
     * @param {string} componentName - The component name for tracking
     * @returns {Promise} - Promise that resolves when script is loaded
     */
    loadComponent: function(scriptSrc, componentName) {
        // Check if already loaded
        if (this.loadedComponents.has(componentName)) {
            console.log(`Component ${componentName} already loaded, skipping...`);
            return Promise.resolve();
        }

        // Check if currently loading
        if (this.loadingPromises.has(componentName)) {
            console.log(`Component ${componentName} is currently loading, waiting...`);
            return this.loadingPromises.get(componentName);
        }

        // Create loading promise
        const loadPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = scriptSrc;
            script.onload = () => {
                this.loadedComponents.add(componentName);
                this.loadingPromises.delete(componentName);
                console.log(`Component ${componentName} loaded successfully`);
                resolve();
            };
            script.onerror = (error) => {
                this.loadingPromises.delete(componentName);
                console.error(`Failed to load component ${componentName}:`, error);
                reject(error);
            };
            document.head.appendChild(script);
        });

        this.loadingPromises.set(componentName, loadPromise);
        return loadPromise;
    },

    /**
     * Load multiple components safely
     * @param {Array} components - Array of {src, name} objects
     * @returns {Promise} - Promise that resolves when all components are loaded
     */
    loadComponents: function(components) {
        const loadPromises = components.map(comp =>
            this.loadComponent(comp.src, comp.name)
        );
        return Promise.all(loadPromises);
    },

    /**
     * Check if a component is loaded
     * @param {string} componentName - The component name to check
     * @returns {boolean} - True if component is loaded
     */
    isLoaded: function(componentName) {
        return this.loadedComponents.has(componentName);
    },

    /**
     * Get list of loaded components
     * @returns {Array} - Array of loaded component names
     */
    getLoadedComponents: function() {
        return Array.from(this.loadedComponents);
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentLoader;
}
