/**
 * 强制禁用自动弹出模态框脚本
 * 防止删除进度模态框、分析结果模态框和添加仓库模态框自动弹出
 */

(function() {
    'use strict';

        console.log('🔒 强制禁用自动弹出模态框脚本已加载');

    // 强制禁用自动弹出模态框
    function forceDisableAutoModals() {
        console.log('🔒 强制禁用自动弹出模态框');

        // 移除删除进度模态框
        const progressModal = document.getElementById('deleteProgressModal');
        if (progressModal) {
            console.log('🗑️ 移除删除进度模态框元素');
            progressModal.remove();
        }

        // 移除删除确认模态框
        const deleteModal = document.getElementById('deleteRepositoryModal');
        if (deleteModal) {
            console.log('🗑️ 移除删除确认模态框元素');
            deleteModal.remove();
        }

                // 移除删除相关的toast
        const successToast = document.getElementById('deleteSuccessToast');
        if (successToast) {
            successToast.remove();
        }

        const errorToast = document.getElementById('deleteErrorToast');
        if (errorToast) {
            errorToast.remove();
        }

        // 移除分析结果模态框
        const analysisModal = document.getElementById('analysisResultModal');
        if (analysisModal) {
            console.log('🗑️ 移除分析结果模态框元素');
            analysisModal.remove();
        }

        // 移除添加仓库模态框
        const addRepoModal = document.getElementById('addRepositoryModal');
        if (addRepoModal) {
            console.log('🗑️ 移除添加仓库模态框元素');
            addRepoModal.remove();
        }

        // 覆盖Bootstrap的Modal构造函数
        if (window.bootstrap && window.bootstrap.Modal) {
            const originalModal = window.bootstrap.Modal;
            window.bootstrap.Modal = function(element, options) {
                if (element && element.id && (element.id.includes('delete') || element.id.includes('analysis') || element.id.includes('addRepository'))) {
                    console.log('🚫 阻止模态框创建:', element.id);
                    return {
                        show: function() {
                            console.log('🚫 阻止模态框显示:', element.id);
                        },
                        hide: function() {
                            console.log('🚫 阻止模态框隐藏:', element.id);
                        },
                        dispose: function() {
                            console.log('🚫 阻止模态框销毁:', element.id);
                        }
                    };
                }
                return new originalModal(element, options);
            };

            // 复制静态方法
            Object.setPrototypeOf(window.bootstrap.Modal, originalModal);
            Object.assign(window.bootstrap.Modal, originalModal);
        }

        // 覆盖任何可能的删除函数
        if (window.repositoryManager) {
            if (window.repositoryManager.deleteRepository) {
                window.repositoryManager.deleteRepository = function() {
                    console.log('🚫 阻止删除仓库函数调用');
                    return Promise.resolve();
                };
            }
        }

        // 覆盖组件中的删除函数
        if (window.RepositoryListComponent) {
            if (window.RepositoryListComponent.prototype.deleteRepository) {
                window.RepositoryListComponent.prototype.deleteRepository = function() {
                    console.log('🚫 阻止RepositoryListComponent删除函数调用');
                    return Promise.resolve();
                };
            }
        }

        console.log('✅ 自动弹出模态框已强制禁用');
    }

        // 页面加载时立即执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceDisableAutoModals);
    } else {
        forceDisableAutoModals();
    }

    // 定期检查并禁用
    setInterval(forceDisableAutoModals, 2000);

    // 监听DOM变化，防止模态框被重新添加
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.id && (node.id.includes('delete') || node.id.includes('analysis') || node.id.includes('addRepository'))) {
                        console.log('🚫 检测到模态框被添加，立即移除:', node.id);
                        node.remove();
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 导出函数供其他脚本使用
    window.forceDisableAutoModals = forceDisableAutoModals;

})();
