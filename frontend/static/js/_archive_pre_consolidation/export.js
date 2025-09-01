/**
 * Export Modal JavaScript
 * 
 * This file contains the logic for the export functionality.
 */

class ExportModal {
    constructor(options = {}) {
        this.documentId = options.documentId || null;
        this.selectedFormat = 'pdf';
        this.exportOptions = {
            include_toc: true,
            include_page_numbers: true,
            include_header_footer: true,
            include_metadata: true,
            include_code_highlighting: true,
            include_line_numbers: false,
            include_images: true,
            include_links: true,
            theme: 'light',
            font_size: 14,
            page_size: 'A4',
            page_orientation: 'portrait',
            page_margins: 20,
            custom_styles: false
        };
        this.currentExport = null;
        this.exportProgress = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadExportSettings();
    }
    
    setupEventListeners() {
        // Format selection
        document.querySelectorAll('.format-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const format = e.currentTarget.getAttribute('onclick').match(/'(\w+)'/)[1];
                this.selectFormat(format);
            });
        });
        
        // Export options
        const optionInputs = document.querySelectorAll('#exportModal input, #exportModal select');
        optionInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateExportOptions();
            });
        });
    }
    
    /**
     * Select export format
     */
    selectFormat(format) {
        this.selectedFormat = format;
        
        // Update UI
        document.querySelectorAll('.format-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        const selectedOption = document.querySelector(`.format-option[onclick*="${format}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
        
        // Update available options based on format
        this.updateFormatSpecificOptions(format);
    }
    
    /**
     * Update format-specific options
     */
    updateFormatSpecificOptions(format) {
        // Show/hide options based on format
        const codeHighlighting = document.getElementById('includeCodeHighlighting');
        const lineNumbers = document.getElementById('includeLineNumbers');
        const customStyles = document.getElementById('customStyles');
        const pageSize = document.getElementById('pageSize');
        const pageOrientation = document.getElementById('pageOrientation');
        const pageMargins = document.getElementById('pageMargins');
        
        switch (format) {
            case 'pdf':
                codeHighlighting.disabled = false;
                lineNumbers.disabled = false;
                customStyles.disabled = false;
                pageSize.disabled = false;
                pageOrientation.disabled = false;
                pageMargins.disabled = false;
                break;
                
            case 'word':
                codeHighlighting.disabled = true;
                codeHighlighting.checked = false;
                lineNumbers.disabled = true;
                lineNumbers.checked = false;
                customStyles.disabled = true;
                customStyles.checked = false;
                pageSize.disabled = true;
                pageOrientation.disabled = true;
                pageMargins.disabled = true;
                break;
                
            case 'markdown':
                codeHighlighting.disabled = true;
                codeHighlighting.checked = false;
                lineNumbers.disabled = true;
                lineNumbers.checked = false;
                customStyles.disabled = true;
                customStyles.checked = false;
                pageSize.disabled = true;
                pageOrientation.disabled = true;
                pageMargins.disabled = true;
                break;
                
            case 'html':
                codeHighlighting.disabled = false;
                lineNumbers.disabled = false;
                customStyles.disabled = false;
                pageSize.disabled = true;
                pageOrientation.disabled = true;
                pageMargins.disabled = true;
                break;
        }
        
        this.updateExportOptions();
    }
    
    /**
     * Update export options from UI
     */
    updateExportOptions() {
        this.exportOptions = {
            include_toc: document.getElementById('includeToc').checked,
            include_page_numbers: document.getElementById('includePageNumbers').checked,
            include_header_footer: document.getElementById('includeHeaderFooter').checked,
            include_metadata: document.getElementById('includeMetadata').checked,
            include_code_highlighting: document.getElementById('includeCodeHighlighting').checked,
            include_line_numbers: document.getElementById('includeLineNumbers').checked,
            include_images: document.getElementById('includeImages').checked,
            include_links: document.getElementById('includeLinks').checked,
            theme: document.getElementById('exportTheme').value,
            font_size: parseInt(document.getElementById('fontSize').value),
            page_size: document.getElementById('pageSize').value,
            page_orientation: document.getElementById('pageOrientation').value,
            page_margins: parseInt(document.getElementById('pageMargins').value),
            custom_styles: document.getElementById('customStyles').checked
        };
        
        this.saveExportSettings();
    }
    
    /**
     * Load export settings from localStorage
     */
    loadExportSettings() {
        const saved = ViewerUtils.getLocalStorage('export_settings', null);
        if (saved) {
            this.exportOptions = {...this.exportOptions, ...saved};
            this.applyExportSettings();
        }
    }
    
    /**
     * Apply saved export settings to UI
     */
    applyExportSettings() {
        document.getElementById('includeToc').checked = this.exportOptions.include_toc;
        document.getElementById('includePageNumbers').checked = this.exportOptions.include_page_numbers;
        document.getElementById('includeHeaderFooter').checked = this.exportOptions.include_header_footer;
        document.getElementById('includeMetadata').checked = this.exportOptions.include_metadata;
        document.getElementById('includeCodeHighlighting').checked = this.exportOptions.include_code_highlighting;
        document.getElementById('includeLineNumbers').checked = this.exportOptions.include_line_numbers;
        document.getElementById('includeImages').checked = this.exportOptions.include_images;
        document.getElementById('includeLinks').checked = this.exportOptions.include_links;
        document.getElementById('exportTheme').value = this.exportOptions.theme;
        document.getElementById('fontSize').value = this.exportOptions.font_size;
        document.getElementById('pageSize').value = this.exportOptions.page_size;
        document.getElementById('pageOrientation').value = this.exportOptions.page_orientation;
        document.getElementById('pageMargins').value = this.exportOptions.page_margins;
        document.getElementById('customStyles').checked = this.exportOptions.custom_styles;
    }
    
    /**
     * Save export settings to localStorage
     */
    saveExportSettings() {
        ViewerUtils.setLocalStorage('export_settings', this.exportOptions);
    }
    
    /**
     * Preview export
     */
    async previewExport() {
        try {
            this.showProgress('正在生成预览...', 50);
            
            // Generate preview HTML
            const previewHtml = await this.generatePreview();
            
            // Show preview
            const previewContainer = document.getElementById('previewContent');
            const previewSection = document.getElementById('exportPreview');
            
            if (previewContainer && previewSection) {
                previewContainer.innerHTML = previewHtml;
                previewSection.style.display = 'block';
                
                // Scroll to preview
                previewSection.scrollIntoView({ behavior: 'smooth' });
            }
            
            this.hideProgress();
            
        } catch (error) {
            console.error('Preview error:', error);
            this.showError('生成预览失败');
            this.hideProgress();
        }
    }
    
    /**
     * Generate preview HTML
     */
    async generatePreview() {
        const content = document.getElementById('documentContent');
        if (!content) {
            throw new Error('Document content not found');
        }
        
        let previewHtml = content.innerHTML;
        
        // Apply theme
        if (this.exportOptions.theme === 'dark') {
            previewHtml = `<div class="dark-theme">${previewHtml}</div>`;
        }
        
        // Apply font size
        previewHtml = `<div style="font-size: ${this.exportOptions.font_size}px;">${previewHtml}</div>`;
        
        // Add page simulation for PDF
        if (this.selectedFormat === 'pdf') {
            previewHtml = `
                <div class="page-simulation" style="
                    width: 210mm; 
                    height: 297mm; 
                    padding: ${this.exportOptions.page_margins}mm;
                    border: 1px solid #ddd;
                    background: white;
                ">
                    ${previewHtml}
                </div>
            `;
        }
        
        return previewHtml;
    }
    
    /**
     * Start export
     */
    async startExport() {
        if (!this.documentId) {
            this.showError('文档ID无效');
            return;
        }
        
        try {
            this.showProgress('正在准备导出...', 0);
            
            // Prepare export data
            const exportData = {
                format: this.selectedFormat,
                options: this.exportOptions,
                document_id: this.documentId
            };
            
            // Start export process
            const response = await fetch('/api/documents/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(exportData)
            });
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.task_id) {
                // Poll for completion
                this.pollExportProgress(result.task_id);
            } else if (result.download_url) {
                // Direct download
                this.downloadFile(result.download_url, result.filename);
                this.hideProgress();
                this.closeModal();
            }
            
        } catch (error) {
            console.error('Export error:', error);
            this.showError('导出失败：' + error.message);
            this.hideProgress();
        }
    }
    
    /**
     * Poll export progress
     */
    async pollExportProgress(taskId) {
        const maxAttempts = 120; // 10 minutes max
        let attempts = 0;
        
        const poll = async () => {
            attempts++;
            
            try {
                const response = await fetch(`/api/tasks/${taskId}/status`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    this.downloadFile(data.download_url, data.filename);
                    this.hideProgress();
                    this.closeModal();
                } else if (data.status === 'failed') {
                    this.showError('导出失败: ' + (data.error || '未知错误'));
                    this.hideProgress();
                } else if (attempts < maxAttempts) {
                    const progress = data.progress || 0;
                    this.showProgress(`正在导出... ${progress}%`, progress);
                    setTimeout(poll, 5000); // Poll every 5 seconds
                } else {
                    this.showError('导出超时，请重试');
                    this.hideProgress();
                }
            } catch (error) {
                console.error('Poll error:', error);
                if (attempts < maxAttempts) {
                    setTimeout(poll, 5000);
                } else {
                    this.showError('导出状态检查失败');
                    this.hideProgress();
                }
            }
        };
        
        poll();
    }
    
    /**
     * Download file
     */
    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        this.showSuccess(`文件 "${filename}" 下载成功`);
        
        // Add to export history
        this.addToExportHistory({
            format: this.selectedFormat,
            filename: filename,
            timestamp: new Date().toISOString(),
            options: {...this.exportOptions}
        });
    }
    
    /**
     * Show progress
     */
    showProgress(text, progress = 0) {
        const progressContainer = document.getElementById('exportProgress');
        const progressBar = document.getElementById('exportProgressBar');
        const progressText = document.getElementById('exportProgressText');
        
        if (progressContainer && progressBar && progressText) {
            progressContainer.style.display = 'block';
            progressBar.style.width = `${progress}%`;
            progressText.textContent = text;
        }
        
        this.exportProgress = progress;
    }
    
    /**
     * Hide progress
     */
    hideProgress() {
        const progressContainer = document.getElementById('exportProgress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        this.exportProgress = 0;
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.showToast(message, 'error');
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    /**
     * Close modal
     */
    closeModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
        if (modal) {
            modal.hide();
        }
        
        // Reset form
        this.hideProgress();
        document.getElementById('exportPreview').style.display = 'none';
    }
    
    /**
     * Export history management
     */
    addToExportHistory(exportData) {
        const history = ViewerUtils.getLocalStorage('export_history', []);
        history.unshift(exportData);
        
        // Keep only last 20 exports
        const trimmedHistory = history.slice(0, 20);
        ViewerUtils.setLocalStorage('export_history', trimmedHistory);
    }
    
    getExportHistory() {
        return ViewerUtils.getLocalStorage('export_history', []);
    }
    
    clearExportHistory() {
        if (confirm('确定要清除导出历史吗？')) {
            ViewerUtils.removeLocalStorage('export_history');
        }
    }
    
    /**
     * Get export options for specific format
     */
    getFormatOptions(format) {
        const formatOptions = {
            pdf: {
                include_toc: true,
                include_page_numbers: true,
                include_header_footer: true,
                include_code_highlighting: true,
                include_line_numbers: false,
                theme: 'light',
                page_size: 'A4',
                page_orientation: 'portrait',
                page_margins: 20
            },
            word: {
                include_toc: true,
                include_page_numbers: true,
                include_header_footer: true,
                include_metadata: true,
                theme: 'light'
            },
            markdown: {
                include_metadata: true
            },
            html: {
                include_toc: true,
                include_code_highlighting: true,
                include_line_numbers: false,
                theme: 'light'
            }
        };
        
        return formatOptions[format] || {};
    }
    
    /**
     * Validate export options
     */
    validateExportOptions() {
        const errors = [];
        
        // Validate page margins
        if (this.exportOptions.page_margins < 10 || this.exportOptions.page_margins > 50) {
            errors.push('页面边距必须在 10-50mm 之间');
        }
        
        // Validate font size
        if (this.exportOptions.font_size < 8 || this.exportOptions.font_size > 24) {
            errors.push('字体大小必须在 8-24px 之间');
        }
        
        // Format-specific validations
        switch (this.selectedFormat) {
            case 'pdf':
                if (this.exportOptions.include_line_numbers && !this.exportOptions.include_code_highlighting) {
                    errors.push('行号显示需要启用代码高亮');
                }
                break;
                
            case 'word':
                if (this.exportOptions.include_code_highlighting) {
                    errors.push('Word 格式不支持代码高亮');
                }
                break;
        }
        
        return errors;
    }
    
    /**
     * Get export capabilities
     */
    getExportCapabilities() {
        return {
            formats: ['pdf', 'word', 'markdown', 'html'],
            options: {
                pdf: ['toc', 'page_numbers', 'header_footer', 'metadata', 'code_highlighting', 'line_numbers', 'images', 'links', 'theme', 'page_size', 'page_orientation', 'margins'],
                word: ['toc', 'page_numbers', 'header_footer', 'metadata', 'images', 'links', 'theme'],
                markdown: ['metadata'],
                html: ['toc', 'code_highlighting', 'line_numbers', 'images', 'links', 'theme']
            }
        };
    }
    
    /**
     * Public API
     */
    getSelectedFormat() {
        return this.selectedFormat;
    }
    
    getExportOptions() {
        return {...this.exportOptions};
    }
    
    getExportProgress() {
        return this.exportProgress;
    }
    
    isExportInProgress() {
        return this.exportProgress > 0 && this.exportProgress < 100;
    }
}

// Export for global use
window.ExportModal = ExportModal;