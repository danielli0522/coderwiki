/**
 * 测试仓库管理按钮点击功能
 * 在浏览器控制台中运行此脚本
 */

console.log('🧪 开始测试仓库管理页面按钮功能...');

// 测试1：检查RepositoryManager是否已加载
function testRepositoryManagerLoaded() {
    console.log('📝 测试1: 检查RepositoryManager是否已加载');
    
    if (typeof repositoryManager !== 'undefined' && repositoryManager) {
        console.log('✅ RepositoryManager已加载:', repositoryManager);
        return true;
    } else {
        console.log('❌ RepositoryManager未加载');
        return false;
    }
}

// 测试2：检查添加仓库按钮是否存在且可点击
function testAddRepositoryButton() {
    console.log('📝 测试2: 检查添加仓库按钮');
    
    // 查找所有添加仓库按钮
    const addButtons = document.querySelectorAll('[data-bs-target="#addRepositoryModal"]');
    console.log(`找到 ${addButtons.length} 个添加仓库按钮`);
    
    addButtons.forEach((button, index) => {
        console.log(`按钮 ${index + 1}:`, {
            text: button.textContent.trim(),
            disabled: button.disabled,
            display: window.getComputedStyle(button).display,
            visibility: window.getComputedStyle(button).visibility,
            pointerEvents: window.getComputedStyle(button).pointerEvents
        });
    });
    
    return addButtons.length > 0;
}

// 测试3：模拟点击添加仓库按钮
function testClickAddRepositoryButton() {
    console.log('📝 测试3: 模拟点击添加仓库按钮');
    
    const addButton = document.querySelector('[data-bs-target="#addRepositoryModal"]');
    if (!addButton) {
        console.log('❌ 找不到添加仓库按钮');
        return false;
    }
    
    console.log('🖱️ 模拟点击添加仓库按钮...');
    addButton.click();
    
    // 等待模态框出现
    setTimeout(() => {
        const modal = document.getElementById('addRepositoryModal');
        if (modal) {
            const isVisible = window.getComputedStyle(modal).display !== 'none';
            console.log('模态框是否显示:', isVisible);
            
            if (isVisible) {
                console.log('✅ 添加仓库模态框成功打开');
                testModalInteractions();
            } else {
                console.log('❌ 添加仓库模态框未能打开');
            }
        }
    }, 500);
    
    return true;
}

// 测试4：测试模态框内的交互
function testModalInteractions() {
    console.log('📝 测试4: 测试模态框内的交互');
    
    const modal = document.getElementById('addRepositoryModal');
    if (!modal) {
        console.log('❌ 模态框不存在');
        return false;
    }
    
    // 测试输入框
    const urlInput = modal.querySelector('#repoUrl');
    const nameInput = modal.querySelector('#repoName');
    const descInput = modal.querySelector('#repoDescription');
    
    if (urlInput) {
        console.log('🔗 测试URL输入框...');
        urlInput.focus();
        urlInput.value = 'https://github.com/microsoft/vscode';
        urlInput.dispatchEvent(new Event('input', { bubbles: true }));
        console.log('✅ URL输入框可用:', urlInput.value);
    }
    
    if (nameInput) {
        console.log('📛 测试名称输入框...');
        nameInput.focus();
        nameInput.value = 'vscode-test';
        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
        console.log('✅ 名称输入框可用:', nameInput.value);
    }
    
    if (descInput) {
        console.log('📝 测试描述输入框...');
        descInput.focus();
        descInput.value = 'VSCode测试仓库';
        descInput.dispatchEvent(new Event('input', { bubbles: true }));
        console.log('✅ 描述输入框可用:', descInput.value);
    }
    
    // 测试验证按钮
    const validateBtn = modal.querySelector('#validateUrlBtn');
    if (validateBtn) {
        console.log('🔍 测试URL验证按钮...');
        validateBtn.click();
        console.log('✅ URL验证按钮可点击');
    }
    
    // 等待一秒后测试提交按钮
    setTimeout(() => {
        const addRepoBtn = modal.querySelector('#addRepoBtn');
        if (addRepoBtn) {
            console.log('➕ 测试添加仓库提交按钮...');
            console.log('提交按钮状态:', {
                disabled: addRepoBtn.disabled,
                text: addRepoBtn.textContent.trim()
            });
            
            if (!addRepoBtn.disabled) {
                console.log('🚀 模拟提交仓库...');
                // 不实际提交，只是验证可点击性
                console.log('✅ 添加仓库按钮可用（未实际提交）');
            }
        }
        
        // 关闭模态框
        const closeBtn = modal.querySelector('.btn-close');
        if (closeBtn) {
            console.log('❌ 关闭模态框...');
            closeBtn.click();
        }
    }, 1000);
    
    return true;
}

// 测试5：检查仓库列表中的操作按钮
function testRepositoryListButtons() {
    console.log('📝 测试5: 检查仓库列表操作按钮');
    
    const tableBody = document.getElementById('repositoriesTable');
    if (!tableBody) {
        console.log('❌ 找不到仓库表格');
        return false;
    }
    
    const rows = tableBody.querySelectorAll('tr');
    console.log(`找到 ${rows.length} 个仓库行`);
    
    if (rows.length > 0) {
        const firstRow = rows[0];
        const actionButtons = firstRow.querySelectorAll('.btn');
        console.log(`第一行找到 ${actionButtons.length} 个操作按钮`);
        
        actionButtons.forEach((button, index) => {
            console.log(`操作按钮 ${index + 1}:`, {
                classes: button.className,
                title: button.title || button.textContent.trim(),
                disabled: button.disabled,
                onclick: button.onclick ? 'has onclick' : 'no onclick'
            });
        });
    }
    
    return true;
}

// 执行所有测试
function runAllTests() {
    console.log('🚀 开始执行完整测试套件...');
    
    const results = {
        repositoryManagerLoaded: testRepositoryManagerLoaded(),
        addButtonExists: testAddRepositoryButton(),
        repositoryListButtons: testRepositoryListButtons()
    };
    
    console.log('📊 测试结果汇总:', results);
    
    // 延迟执行点击测试，让页面完全加载
    setTimeout(() => {
        testClickAddRepositoryButton();
    }, 1000);
    
    return results;
}

// 等待页面完全加载后执行测试
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(runAllTests, 2000);
    });
} else {
    setTimeout(runAllTests, 2000);
}