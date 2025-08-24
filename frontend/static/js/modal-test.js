/**
 * Modal Test Script
 * 测试模态框检测和功能
 */

class ModalTest {
    constructor() {
        this.init();
    }

    init() {
        console.log('ModalTest: 初始化测试...');

        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.runTests());
        } else {
            this.runTests();
        }
    }

    runTests() {
        console.log('ModalTest: 开始运行测试...');

        // 测试1: 检查模态框是否存在
        this.testModalExistence();

        // 测试2: 检查模态框结构
        this.testModalStructure();

        // 测试3: 检查事件监听器
        this.testEventListeners();

        // 测试4: 检查Bootstrap可用性
        this.testBootstrapAvailability();

        console.log('ModalTest: 测试完成');
    }

    testModalExistence() {
        console.log('ModalTest: 测试模态框存在性...');

        // 方法1: 通过ID查找
        const modalById = document.getElementById('addRepositoryModal');
        console.log('ModalTest: 通过ID查找结果:', modalById ? '成功' : '失败');

        // 方法2: 通过选择器查找
        const modalBySelector = document.querySelector('#addRepositoryModal');
        console.log('ModalTest: 通过选择器查找结果:', modalBySelector ? '成功' : '失败');

        // 方法3: 通过类名查找
        const modalsByClass = document.querySelectorAll('.modal');
        const targetModal = Array.from(modalsByClass).find(m => m.id === 'addRepositoryModal');
        console.log('ModalTest: 通过类名查找结果:', targetModal ? '成功' : '失败');

        // 方法4: 通过表单查找
        const form = document.getElementById('addRepositoryForm');
        const modalByForm = form ? form.closest('.modal') : null;
        console.log('ModalTest: 通过表单查找结果:', modalByForm ? '成功' : '失败');

        // 总结
        const modalExists = modalById || modalBySelector || targetModal || modalByForm;
        console.log('ModalTest: 模态框存在性测试结果:', modalExists ? '通过' : '失败');

        if (!modalExists) {
            console.error('ModalTest: 所有查找方法都失败了！');
            this.logPageStructure();
        }
    }

    testModalStructure() {
        console.log('ModalTest: 测试模态框结构...');

        const modal = document.getElementById('addRepositoryModal');
        if (!modal) {
            console.error('ModalTest: 无法找到模态框进行结构测试');
            return;
        }

        // 检查必要的类名
        const hasModalClass = modal.classList.contains('modal');
        const hasFadeClass = modal.classList.contains('fade');
        console.log('ModalTest: 模态框类名检查:', {
            modal: hasModalClass,
            fade: hasFadeClass
        });

        // 检查必要的子元素
        const modalDialog = modal.querySelector('.modal-dialog');
        const modalContent = modal.querySelector('.modal-content');
        const modalHeader = modal.querySelector('.modal-header');
        const modalBody = modal.querySelector('.modal-body');
        const modalFooter = modal.querySelector('.modal-footer');

        console.log('ModalTest: 模态框子元素检查:', {
            modalDialog: !!modalDialog,
            modalContent: !!modalContent,
            modalHeader: !!modalHeader,
            modalBody: !!modalBody,
            modalFooter: !!modalFooter
        });

        // 检查表单元素
        const form = modal.querySelector('#addRepositoryForm');
        const urlInput = modal.querySelector('#repoUrl');
        const nameInput = modal.querySelector('#repoName');
        const descriptionTextarea = modal.querySelector('#repoDescription');

        console.log('ModalTest: 表单元素检查:', {
            form: !!form,
            urlInput: !!urlInput,
            nameInput: !!nameInput,
            descriptionTextarea: !!descriptionTextarea
        });
    }

    testEventListeners() {
        console.log('ModalTest: 测试事件监听器...');

        // 检查按钮
        const addRepoButtons = document.querySelectorAll('[data-bs-target="#addRepositoryModal"]');
        console.log('ModalTest: 找到的添加仓库按钮数量:', addRepoButtons.length);

        addRepoButtons.forEach((btn, index) => {
            console.log(`ModalTest: 按钮 ${index + 1}:`, {
                text: btn.textContent.trim(),
                classes: btn.className,
                dataTarget: btn.getAttribute('data-bs-target')
            });
        });

        // 检查关闭按钮
        const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
        console.log('ModalTest: 找到的关闭按钮数量:', closeButtons.length);
    }

    testBootstrapAvailability() {
        console.log('ModalTest: 测试Bootstrap可用性...');

        const bootstrapAvailable = typeof bootstrap !== 'undefined';
        const modalClassAvailable = bootstrapAvailable && typeof bootstrap.Modal !== 'undefined';

        console.log('ModalTest: Bootstrap检查:', {
            bootstrap: bootstrapAvailable,
            modalClass: modalClassAvailable
        });

        if (bootstrapAvailable && modalClassAvailable) {
            // 测试创建模态框实例
            const modal = document.getElementById('addRepositoryModal');
            if (modal) {
                try {
                    const bsModal = new bootstrap.Modal(modal);
                    console.log('ModalTest: Bootstrap模态框实例创建成功');
                } catch (error) {
                    console.error('ModalTest: Bootstrap模态框实例创建失败:', error);
                }
            }
        }
    }

    logPageStructure() {
        console.log('ModalTest: 记录页面结构...');

        // 记录所有模态框
        const allModals = document.querySelectorAll('.modal');
        console.log('ModalTest: 页面中的所有模态框:', allModals.length);
        allModals.forEach((modal, index) => {
            console.log(`ModalTest: 模态框 ${index + 1}:`, {
                id: modal.id,
                classes: modal.className,
                children: modal.children.length
            });
        });

        // 记录所有表单
        const allForms = document.querySelectorAll('form');
        console.log('ModalTest: 页面中的所有表单:', allForms.length);
        allForms.forEach((form, index) => {
            console.log(`ModalTest: 表单 ${index + 1}:`, {
                id: form.id,
                action: form.action,
                method: form.method
            });
        });

        // 记录页面标题和URL
        console.log('ModalTest: 页面信息:', {
            title: document.title,
            url: window.location.href,
            readyState: document.readyState
        });
    }
}

// 初始化测试
new ModalTest();

// 导出到全局
window.ModalTest = ModalTest;
