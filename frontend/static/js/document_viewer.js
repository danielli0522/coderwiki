/**
 * Document Viewer - Main JavaScript
 * 
 * This file contains the main logic for the document viewer interface.
 */

class DocumentViewer {
    constructor(options = {}) {
        this.documentId = options.documentId || null;
        this.initialVersion = options.initialVersion || '1.0';
        this.autoLoad = options.autoLoad || false;
        this.currentVersion = this.initialVersion;
        this.currentContent = '';
        this.currentToc = [];
        this.isLoading = false;
        this.theme = localStorage.getItem('viewer-theme') || 'light';
        this.fontSize = parseInt(localStorage.getItem('viewer-font-size')) || 16;
        this.lineNumbers = localStorage.getItem('viewer-line-numbers') === 'true';
        this.fullscreen = false;
        this.searchHistory = JSON.parse(localStorage.getItem('viewer-search-history') || '[]');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.applyTheme();
        this.applyFontSize();
        
        if (this.autoLoad && this.documentId) {
            this.loadDocument();
        }
    }
    
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'f':
                        e.preventDefault();
                        this.focusSearch();
                        break;
                    case 'p':
                        e.preventDefault();
                        this.printDocument();
                        break;
                    case 's':
                        e.preventDefault();
                        this.exportDocument('pdf');
                        break;
                    case '+':
                    case '=':
                        e.preventDefault();
                        this.increaseFontSize();
                        break;
                    case '-':
                        e.preventDefault();
                        this.decreaseFontSize();
                        break;
                }
            }
            
            // Escape key to exit fullscreen
            if (e.key === 'Escape' && this.fullscreen) {
                this.toggleFullscreen();
            }
        });
        
        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Scroll handler for table of contents
        document.addEventListener('scroll', () => {
            this.updateActiveSection();
        });
    }
    
    async loadDocument(version = null) {
        if (!this.documentId) {
            console.error('No document ID provided');
            return;
        }
        
        this.setLoading(true);
        const targetVersion = version || this.currentVersion;
        
        try {
            // Load document content
            const contentResponse = await fetch(`/api/documents/${this.documentId}/content?version=${targetVersion}`);
            if (!contentResponse.ok) {
                throw new Error(`Failed to load document: ${contentResponse.status}`);
            }
            
            const contentData = await contentResponse.json();
            this.currentContent = contentData.content;
            
            // Load table of contents
            const tocResponse = await fetch(`/api/documents/${this.documentId}/toc?version=${targetVersion}`);
            if (tocResponse.ok) {
                const tocData = await tocResponse.json();
                this.currentToc = tocData.toc || [];
                this.renderToc();
            }
            
            // Render content
            this.renderContent(contentData.content);
            
            // Update document info
            this.updateDocumentInfo(contentData.metadata);
            
            // Update current version
            this.currentVersion = targetVersion;
            
            // Load available versions
            this.loadAvailableVersions();
            
            // Hide loading spinner
            this.setLoading(false);
            
        } catch (error) {
            console.error('Error loading document:', error);
            this.showError('Failed to load document. Please try again.');
            this.setLoading(false);
        }
    }
    
    renderContent(content) {
        const contentElement = document.getElementById('documentContent');
        
        // Convert markdown to HTML
        const html = marked.parse(content);
        
        // Apply custom processing
        const processedHtml = this.processContent(html);
        
        contentElement.innerHTML = processedHtml;
        
        // Apply syntax highlighting
        this.applySyntaxHighlighting();
        
        // Add line numbers if enabled
        if (this.lineNumbers) {
            this.addLineNumbers();
        }
        
        // Setup internal links
        this.setupInternalLinks();
        
        // Update document statistics
        this.updateDocumentStats();
    }
    
    processContent(html) {
        // Custom content processing
        let processed = html;
        
        // Add anchor links to headings
        processed = processed.replace(/<h([1-6])[^>]*>([^<]+)<\/h[1-6]>/g, (match, level, text) => {
            const anchor = this.generateAnchor(text);
            return `<h${level} id="${anchor}" class="heading-link">
                        ${text}
                        <a href="#${anchor}" class="anchor-link" title="Link to this section">
                            <i class="fas fa-link"></i>
                        </a>
                    </h${level}>`;
        });
        
        // Enhance tables
        processed = processed.replace(/<table>/g, '<table class="table table-striped table-hover">');
        
        // Enhance code blocks
        processed = processed.replace(/<pre><code class="language-([^"]+)">/g, '<pre><code class="language-$1 hljs">');
        
        // Add responsive images
        processed = processed.replace(/<img([^>]+)>/g, '<img$1 class="img-fluid" loading="lazy">');
        
        return processed;
    }
    
    applySyntaxHighlighting() {
        // Highlight.js will automatically highlight code blocks
        // due to the marked configuration
        hljs.highlightAll();
    }
    
    addLineNumbers() {
        const codeBlocks = document.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            const lines = block.textContent.split('\n');
            const numberedLines = lines.map((line, index) => {
                return `<span class="line-number" data-line="${index + 1}">${line}</span>`;
            }).join('\n');
            
            block.innerHTML = numberedLines;
            block.classList.add('has-line-numbers');
        });
    }
    
    setupInternalLinks() {
        // Handle internal anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    history.pushState(null, null, link.getAttribute('href'));
                }
            });
        });
    }
    
    updateDocumentStats() {
        const content = document.getElementById('documentContent');
        const text = content.textContent || '';
        
        // Word count
        const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
        document.getElementById('wordCount').textContent = wordCount.toLocaleString();
        
        // Reading time (average 200 words per minute)
        const readingTimeMinutes = Math.ceil(wordCount / 200);
        const readingTimeText = readingTimeMinutes < 60 
            ? `${readingTimeMinutes} 分钟` 
            : `${Math.floor(readingTimeMinutes / 60)} 小时 ${readingTimeMinutes % 60} 分钟`;
        document.getElementById('readingTime').textContent = readingTimeText;
    }
    
    updateDocumentInfo(metadata) {
        if (metadata) {
            if (metadata.title) {
                document.getElementById('documentTitle').textContent = metadata.title;
            }
            if (metadata.version) {
                document.getElementById('documentVersion').textContent = `v${metadata.version}`;
            }
            if (metadata.author) {
                document.getElementById('documentAuthor').textContent = metadata.author;
            }
            if (metadata.created_at) {
                document.getElementById('documentTime').textContent = new Date(metadata.created_at).toLocaleString();
                document.getElementById('generatedAt').textContent = new Date(metadata.created_at).toLocaleString();
            }
            if (metadata.updated_at) {
                document.getElementById('lastUpdated').textContent = new Date(metadata.updated_at).toLocaleString();
            }
        }
    }
    
    async loadAvailableVersions() {
        try {
            const response = await fetch(`/api/documents/${this.documentId}/versions`);
            if (response.ok) {
                const data = await response.json();
                this.renderVersionSelector(data.versions);
            }
        } catch (error) {
            console.error('Error loading versions:', error);
        }
    }
    
    renderVersionSelector(versions) {
        const selector = document.getElementById('versionSelect');
        selector.innerHTML = '';
        
        versions.forEach(version => {
            const option = document.createElement('option');
            option.value = version.version;
            option.textContent = `v${version.version} - ${new Date(version.created_at).toLocaleDateString()}`;
            if (version.version === this.currentVersion) {
                option.selected = true;
            }
            selector.appendChild(option);
        });
    }
    
    async changeVersion(version) {
        if (version !== this.currentVersion) {
            await this.loadDocument(version);
        }
    }
    
    async exportDocument(format, options = {}) {
        try {
            this.showProgress('正在导出文档...', 0);
            
            const exportOptions = {
                format: format,
                include_toc: options.includeToc !== false,
                include_line_numbers: this.lineNumbers,
                theme: this.theme,
                ...options
            };
            
            const response = await fetch(`/api/documents/${this.documentId}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(exportOptions)
            });
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.task_id) {
                // Poll for completion
                this.pollExportStatus(result.task_id);
            } else if (result.download_url) {
                // Direct download
                this.downloadFile(result.download_url, `${this.documentId}.${format}`);
                this.hideProgress();
            }
            
        } catch (error) {
            console.error('Export error:', error);
            this.showError('导出失败，请重试');
            this.hideProgress();
        }
    }
    
    async pollExportStatus(taskId) {
        const maxAttempts = 60; // 5 minutes max
        let attempts = 0;
        
        const poll = async () => {
            attempts++;
            
            try {
                const response = await fetch(`/api/tasks/${taskId}/status`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    this.downloadFile(data.download_url, data.filename);
                    this.hideProgress();
                } else if (data.status === 'failed') {
                    this.showError('导出失败: ' + (data.error || '未知错误'));
                    this.hideProgress();
                } else if (attempts < maxAttempts) {
                    this.showProgress(`正在导出... ${data.progress || 0}%`, data.progress || 0);
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
    
    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    showShareModal() {
        const modal = new bootstrap.Modal(document.getElementById('shareModal'));
        modal.show();
    }
    
    async generateShareLink() {
        const expiry = document.getElementById('shareExpiry').value;
        const password = document.getElementById('sharePassword').value;
        
        try {
            const response = await fetch(`/api/documents/${this.documentId}/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    expiry_hours: parseInt(expiry),
                    password: password || null
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('shareLink').value = data.share_url;
            } else {
                this.showError('生成分享链接失败');
            }
        } catch (error) {
            console.error('Share error:', error);
            this.showError('生成分享链接失败');
        }
    }
    
    copyShareLink() {
        const shareLink = document.getElementById('shareLink');
        shareLink.select();
        document.execCommand('copy');
        
        // Show success message
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> 已复制';
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    }
    
    showVersionHistory() {
        const modal = new bootstrap.Modal(document.getElementById('versionHistoryModal'));
        modal.show();
        this.loadVersionHistory();
    }
    
    async loadVersionHistory() {
        try {
            const response = await fetch(`/api/documents/${this.documentId}/versions`);
            if (response.ok) {
                const data = await response.json();
                this.renderVersionHistory(data.versions);
            }
        } catch (error) {
            console.error('Error loading version history:', error);
        }
    }
    
    renderVersionHistory(versions) {
        const container = document.getElementById('versionHistory');
        container.innerHTML = '';
        
        versions.forEach(version => {
            const versionElement = document.createElement('div');
            versionElement.className = 'version-item';
            versionElement.innerHTML = `
                <div class="version-header">
                    <h5>v${version.version}</h5>
                    <small class="text-muted">${new Date(version.created_at).toLocaleString()}</small>
                </div>
                <div class="version-changes">
                    <p>${version.changes || '无变更说明'}</p>
                </div>
                <div class="version-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="documentViewer.changeVersion('${version.version}')">
                        查看此版本
                    </button>
                </div>
            `;
            container.appendChild(versionElement);
        });
    }
    
    printDocument() {
        window.print();
    }
    
    toggleFullscreen() {
        this.fullscreen = !this.fullscreen;
        const container = document.querySelector('.document-viewer-container');
        
        if (this.fullscreen) {
            container.classList.add('fullscreen');
            document.documentElement.requestFullscreen();
        } else {
            container.classList.remove('fullscreen');
            document.exitFullscreen();
        }
    }
    
    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('viewer-theme', this.theme);
    }
    
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
    }
    
    increaseFontSize() {
        this.fontSize = Math.min(this.fontSize + 2, 24);
        this.applyFontSize();
        localStorage.setItem('viewer-font-size', this.fontSize);
    }
    
    decreaseFontSize() {
        this.fontSize = Math.max(this.fontSize - 2, 12);
        this.applyFontSize();
        localStorage.setItem('viewer-font-size', this.fontSize);
    }
    
    applyFontSize() {
        document.getElementById('documentContent').style.fontSize = `${this.fontSize}px`;
    }
    
    toggleLineNumbers() {
        this.lineNumbers = !this.lineNumbers;
        localStorage.setItem('viewer-line-numbers', this.lineNumbers);
        this.renderContent(this.currentContent);
    }
    
    focusSearch() {
        const searchInput = document.querySelector('#searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    toggleMobileSidebar() {
        const sidebar = document.querySelector('.navigation-sidebar');
        sidebar.classList.toggle('active');
    }
    
    toggleMobileSearch() {
        const searchPanel = document.querySelector('.search-panel');
        searchPanel.classList.toggle('active');
    }
    
    reloadDocument() {
        this.loadDocument();
    }
    
    async downloadOriginal() {
        try {
            const response = await fetch(`/api/documents/${this.documentId}/download`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                this.downloadFile(url, `${this.documentId}_original.md`);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showError('下载失败');
        }
    }
    
    showProgress(text, progress = 0) {
        const container = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        container.style.display = 'block';
        progressBar.style.width = `${progress}%`;
        progressText.textContent = text;
    }
    
    hideProgress() {
        const container = document.getElementById('progressContainer');
        container.style.display = 'none';
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = loading ? 'flex' : 'none';
        }
    }
    
    showError(message) {
        // Show error message (you can use a toast or alert)
        alert(message);
    }
    
    handleResize() {
        // Handle responsive layout changes
        if (window.innerWidth > 768) {
            const sidebar = document.querySelector('.navigation-sidebar');
            sidebar.classList.remove('active');
        }
    }
    
    updateActiveSection() {
        // Update active section in table of contents based on scroll position
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const scrollPosition = window.scrollY + 100;
        
        let activeHeading = null;
        headings.forEach(heading => {
            const rect = heading.getBoundingClientRect();
            if (rect.top <= scrollPosition) {
                activeHeading = heading;
            }
        });
        
        if (activeHeading) {
            this.highlightTocItem(activeHeading.id);
        }
    }
    
    highlightTocItem(anchor) {
        // Highlight the corresponding TOC item
        const tocItems = document.querySelectorAll('.toc-item');
        tocItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${anchor}`) {
                item.classList.add('active');
            }
        });
    }
    
    renderToc() {
        // This will be implemented in the navigation component
        if (window.navigationSidebar) {
            window.navigationSidebar.renderToc(this.currentToc);
        }
    }
    
    generateAnchor(text) {
        return text.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim('-');
    }
    
    showExportModal() {
        const modal = new bootstrap.Modal(document.getElementById('exportModal'));
        modal.show();
    }
}

// Export the class for global use
window.DocumentViewer = DocumentViewer;