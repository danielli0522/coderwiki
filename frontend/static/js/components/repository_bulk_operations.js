/**
 * Repository Bulk Operations Component (QA Fix for UI-001)
 * Provides bulk operations functionality for repository management
 */
class RepositoryBulkOperations {
    constructor() {
        this.selectedRepositories = new Set();
        this.isSelectionMode = false;
        this.init();
    }

    init() {
        this.createBulkToolbar();
        this.bindEvents();
        console.log('✅ Repository bulk operations initialized');
    }

    createBulkToolbar() {
        // Check if bulk toolbar already exists
        if (document.getElementById('bulk-operations-toolbar')) {
            return;
        }

        // Find the repositories table container
        const tableContainer = document.getElementById('repositoriesTable');
        if (!tableContainer) {
            console.warn('⚠️ Repository table not found, bulk operations not available');
            return;
        }

        // Create bulk operations toolbar
        const toolbar = document.createElement('div');
        toolbar.id = 'bulk-operations-toolbar';
        toolbar.className = 'bulk-operations-toolbar alert alert-info d-none';
        toolbar.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-square me-2"></i>
                    <span id="selected-count">0</span> 个仓库已选中
                </div>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-danger" id="bulk-delete-btn">
                        <i class="fas fa-trash me-1"></i> 批量删除
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" id="bulk-analyze-btn">
                        <i class="fas fa-sync me-1"></i> 批量分析
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" id="clear-selection-btn">
                        <i class="fas fa-times me-1"></i> 取消选择
                    </button>
                </div>
            </div>
        `;

        // Insert toolbar before the table
        tableContainer.parentNode.insertBefore(toolbar, tableContainer);
    }

    bindEvents() {
        // Master checkbox for select all/none
        this.addMasterCheckbox();

        // Bulk operation buttons
        document.addEventListener('click', (event) => {
            if (event.target.id === 'bulk-delete-btn' || event.target.closest('#bulk-delete-btn')) {
                this.handleBulkDelete();
            } else if (event.target.id === 'bulk-analyze-btn' || event.target.closest('#bulk-analyze-btn')) {
                this.handleBulkAnalyze();
            } else if (event.target.id === 'clear-selection-btn' || event.target.closest('#clear-selection-btn')) {
                this.clearSelection();
            } else if (event.target.id === 'master-checkbox') {
                this.handleMasterCheckbox(event.target.checked);
            } else if (event.target.classList.contains('repo-checkbox')) {
                this.handleRepositoryCheckbox(event.target);
            }
        });

        // Listen for table updates to refresh checkboxes
        document.addEventListener('repositoriesLoaded', () => {
            this.refreshCheckboxes();
        });
    }

    addMasterCheckbox() {
        // Add master checkbox to table header
        const tableHeader = document.querySelector('#repositoriesTable thead tr');
        if (!tableHeader) return;

        // Check if already added
        if (tableHeader.querySelector('.bulk-select-header')) return;

        const masterCheckboxHeader = document.createElement('th');
        masterCheckboxHeader.className = 'bulk-select-header';
        masterCheckboxHeader.style.width = '50px';
        masterCheckboxHeader.innerHTML = `
            <div class="form-check">
                <input type="checkbox" class="form-check-input" id="master-checkbox" title="全选/取消全选">
                <label class="form-check-label" for="master-checkbox"></label>
            </div>
        `;

        // Insert as first column
        tableHeader.insertBefore(masterCheckboxHeader, tableHeader.firstChild);
    }

    refreshCheckboxes() {
        // Add individual checkboxes to repository rows
        const rows = document.querySelectorAll('#repositoriesTable tbody tr[data-repo-id]');
        
        rows.forEach(row => {
            // Skip if checkbox already exists
            if (row.querySelector('.repo-checkbox')) return;

            const repoId = row.dataset.repoId;
            const checkboxCell = document.createElement('td');
            checkboxCell.className = 'bulk-select-cell';
            checkboxCell.innerHTML = `
                <div class="form-check">
                    <input type="checkbox" class="form-check-input repo-checkbox" 
                           data-repo-id="${repoId}" 
                           id="checkbox-${repoId}">
                    <label class="form-check-label" for="checkbox-${repoId}"></label>
                </div>
            `;

            // Insert as first cell
            row.insertBefore(checkboxCell, row.firstChild);

            // Restore selection state if previously selected
            if (this.selectedRepositories.has(parseInt(repoId))) {
                const checkbox = checkboxCell.querySelector('.repo-checkbox');
                checkbox.checked = true;
            }
        });

        // Update selection count
        this.updateSelectionDisplay();
    }

    handleMasterCheckbox(checked) {
        const repoCheckboxes = document.querySelectorAll('.repo-checkbox');
        
        repoCheckboxes.forEach(checkbox => {
            checkbox.checked = checked;
            const repoId = parseInt(checkbox.dataset.repoId);
            
            if (checked) {
                this.selectedRepositories.add(repoId);
            } else {
                this.selectedRepositories.delete(repoId);
            }
        });

        this.updateSelectionDisplay();
    }

    handleRepositoryCheckbox(checkbox) {
        const repoId = parseInt(checkbox.dataset.repoId);
        
        if (checkbox.checked) {
            this.selectedRepositories.add(repoId);
        } else {
            this.selectedRepositories.delete(repoId);
        }

        this.updateSelectionDisplay();
        this.updateMasterCheckbox();
    }

    updateMasterCheckbox() {
        const masterCheckbox = document.getElementById('master-checkbox');
        if (!masterCheckbox) return;

        const repoCheckboxes = document.querySelectorAll('.repo-checkbox');
        const checkedBoxes = document.querySelectorAll('.repo-checkbox:checked');

        if (checkedBoxes.length === 0) {
            masterCheckbox.indeterminate = false;
            masterCheckbox.checked = false;
        } else if (checkedBoxes.length === repoCheckboxes.length) {
            masterCheckbox.indeterminate = false;
            masterCheckbox.checked = true;
        } else {
            masterCheckbox.indeterminate = true;
            masterCheckbox.checked = false;
        }
    }

    updateSelectionDisplay() {
        const toolbar = document.getElementById('bulk-operations-toolbar');
        const countElement = document.getElementById('selected-count');
        
        if (!toolbar || !countElement) return;

        const selectedCount = this.selectedRepositories.size;
        
        if (selectedCount > 0) {
            toolbar.classList.remove('d-none');
            countElement.textContent = selectedCount;
        } else {
            toolbar.classList.add('d-none');
        }

        // Enable/disable bulk operation buttons
        const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
        const bulkAnalyzeBtn = document.getElementById('bulk-analyze-btn');
        
        if (bulkDeleteBtn) bulkDeleteBtn.disabled = selectedCount === 0;
        if (bulkAnalyzeBtn) bulkAnalyzeBtn.disabled = selectedCount === 0;
    }

    clearSelection() {
        this.selectedRepositories.clear();
        
        // Uncheck all checkboxes
        document.querySelectorAll('.repo-checkbox:checked').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        this.updateSelectionDisplay();
        this.updateMasterCheckbox();
    }

    async handleBulkDelete() {
        const selectedIds = Array.from(this.selectedRepositories);
        
        if (selectedIds.length === 0) {
            this.showMessage('请先选择要删除的仓库', 'warning');
            return;
        }

        // Get repository names for confirmation
        const repoNames = selectedIds.map(id => {
            const row = document.querySelector(`tr[data-repo-id="${id}"]`);
            return row ? row.querySelector('.repo-name')?.textContent || `ID:${id}` : `ID:${id}`;
        });

        const confirmMessage = `确定要删除以下 ${selectedIds.length} 个仓库吗？\n\n${repoNames.join('\n')}\n\n此操作无法撤销！`;
        
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            // Show loading state
            const deleteBtn = document.getElementById('bulk-delete-btn');
            const originalText = deleteBtn.innerHTML;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> 删除中...';
            deleteBtn.disabled = true;

            // Call bulk delete API
            const response = await fetch('/api/repositories/bulk-delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repository_ids: selectedIds
                }),
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                
                if (result.success) {
                    this.showMessage(`成功删除 ${result.deleted_count} 个仓库`, 'success');
                    
                    // Clear selection and refresh table
                    this.clearSelection();
                    
                    // Trigger repository list refresh
                    if (window.repositoryManager) {
                        window.repositoryManager.loadRepositories();
                        window.repositoryManager.loadStatistics();
                    }
                } else {
                    this.showMessage(result.error || '删除失败', 'danger');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Bulk delete failed:', error);
            this.showMessage('删除操作失败: ' + error.message, 'danger');
        } finally {
            // Restore button state
            const deleteBtn = document.getElementById('bulk-delete-btn');
            deleteBtn.innerHTML = originalText;
            deleteBtn.disabled = false;
        }
    }

    async handleBulkAnalyze() {
        const selectedIds = Array.from(this.selectedRepositories);
        
        if (selectedIds.length === 0) {
            this.showMessage('请先选择要分析的仓库', 'warning');
            return;
        }

        try {
            // Show loading state
            const analyzeBtn = document.getElementById('bulk-analyze-btn');
            const originalText = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> 分析中...';
            analyzeBtn.disabled = true;

            // Call bulk analyze API
            const response = await fetch('/api/repositories/bulk-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repository_ids: selectedIds
                }),
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                
                if (result.success) {
                    this.showMessage(`已启动 ${result.started_count} 个仓库的分析任务`, 'success');
                    
                    // Clear selection (optional)
                    this.clearSelection();
                } else {
                    this.showMessage(result.error || '分析启动失败', 'danger');
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Bulk analyze failed:', error);
            this.showMessage('批量分析失败: ' + error.message, 'danger');
        } finally {
            // Restore button state
            const analyzeBtn = document.getElementById('bulk-analyze-btn');
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    }

    showMessage(message, type) {
        // Create toast notification if framework supports it
        if (window.showToast) {
            window.showToast(message, type);
            return;
        }

        // Fallback to alert
        const icon = {
            'success': '✅',
            'warning': '⚠️',
            'danger': '❌',
            'info': 'ℹ️'
        }[type] || 'ℹ️';

        alert(`${icon} ${message}`);
    }

    // Public methods
    getSelectedRepositories() {
        return Array.from(this.selectedRepositories);
    }

    selectRepository(repoId) {
        this.selectedRepositories.add(parseInt(repoId));
        const checkbox = document.querySelector(`[data-repo-id="${repoId}"]`);
        if (checkbox) checkbox.checked = true;
        this.updateSelectionDisplay();
        this.updateMasterCheckbox();
    }

    deselectRepository(repoId) {
        this.selectedRepositories.delete(parseInt(repoId));
        const checkbox = document.querySelector(`[data-repo-id="${repoId}"]`);
        if (checkbox) checkbox.checked = false;
        this.updateSelectionDisplay();
        this.updateMasterCheckbox();
    }

    isRepositorySelected(repoId) {
        return this.selectedRepositories.has(parseInt(repoId));
    }
}

// Initialize if we're on a repository management page
if (typeof window !== 'undefined') {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (document.getElementById('repositoriesTable')) {
                window.repositoryBulkOperations = new RepositoryBulkOperations();
            }
        });
    } else {
        // DOM is already ready
        if (document.getElementById('repositoriesTable')) {
            window.repositoryBulkOperations = new RepositoryBulkOperations();
        }
    }
}