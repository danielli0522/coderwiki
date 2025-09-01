/**
 * Navigation Sidebar JavaScript
 *
 * This file contains the logic for the navigation sidebar component.
 */

class NavigationSidebar {
    constructor(options = {}) {
        this.documentId = options.documentId || null;
        this.tocData = [];
        this.bookmarks = [];
        this.currentSection = null;
        this.expandedItems = new Set();
        this.searchTerm = '';
        this.scrollProgress = 0;

        this.init();
    }

    init() {
        this.loadBookmarks();
        this.setupEventListeners();
        this.setupScrollListener();
    }

    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.goToPreviousSection();
            } else if (e.key === 'ArrowRight' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.goToNextSection();
            }
        });

        // TOC search
        const searchInput = document.getElementById('tocSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', ViewerUtils.debounce((e) => {
                this.searchToc(e.target.value);
            }, 300));
        }
    }

    setupScrollListener() {
        // Throttled scroll listener for performance
        window.addEventListener('scroll', ViewerUtils.throttle(() => {
            this.updateScrollProgress();
            this.updateActiveSection();
        }, 100));
    }

    /**
     * Render table of contents
     */
    renderToc(tocData) {
        this.tocData = tocData || [];
        const container = document.getElementById('tableOfContents');

        if (!container) return;

        if (this.tocData.length === 0) {
            container.innerHTML = `
                <div class="no-toc">
                    <small class="text-muted">无目录结构</small>
                </div>
            `;
            return;
        }

        const tocHtml = this.buildTocHtml(this.tocData);
        container.innerHTML = tocHtml;

        // Update document statistics
        this.updateDocumentStats();

        // Setup TOC item click handlers
        this.setupTocItemHandlers();
    }

    /**
     * Build TOC HTML recursively
     */
    buildTocHtml(items, level = 1) {
        let html = '';

        items.forEach(item => {
            const hasChildren = item.children && item.children.length > 0;
            const isExpanded = this.expandedItems.has(item.anchor);
            const anchor = this.generateAnchor(item.title);

            html += `
                <a href="#${anchor}"
                   class="toc-item level-${level}"
                   data-level="${level}"
                   data-anchor="${anchor}"
                   data-title="${item.title}"
                   onclick="navigationSidebar.navigateToSection('${anchor}')">
                    ${hasChildren ? `<i class="fas fa-chevron-right toc-toggle ${isExpanded ? 'expanded' : ''}"
                                   onclick="event.stopPropagation(); navigationSidebar.toggleTocItem('${anchor}')"></i>` : ''}
                    <span class="toc-text">${this.escapeHtml(item.title)}</span>
                </a>
            `;

            if (hasChildren && isExpanded) {
                html += `<div class="toc-children" data-parent="${anchor}">`;
                html += this.buildTocHtml(item.children, level + 1);
                html += `</div>`;
            }
        });

        return html;
    }

    /**
     * Setup TOC item click handlers
     */
    setupTocItemHandlers() {
        const tocItems = document.querySelectorAll('.toc-item');
        tocItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const anchor = item.getAttribute('data-anchor');
                this.navigateToSection(anchor);
            });
        });
    }

    /**
     * Navigate to specific section
     */
    navigateToSection(anchor) {
        const target = document.getElementById(anchor);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });

            // Update URL without page reload
            history.pushState(null, null, `#${anchor}`);

            // Update active section
            this.setActiveSection(anchor);

            // Close mobile sidebar
            if (window.innerWidth <= 768) {
                this.closeMobile();
            }
        }
    }

    /**
     * Set active section
     */
    setActiveSection(anchor) {
        // Remove active class from all items
        document.querySelectorAll('.toc-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to current item
        const activeItem = document.querySelector(`.toc-item[data-anchor="${anchor}"]`);
        if (activeItem) {
            activeItem.classList.add('active');

            // Ensure active item is visible
            this.scrollIntoView(activeItem);
        }

        this.currentSection = anchor;
    }

    /**
     * Update active section based on scroll position
     */
    updateActiveSection() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const scrollPosition = window.scrollY + 100;

        let activeHeading = null;
        let activeAnchor = null;

        headings.forEach(heading => {
            const rect = heading.getBoundingClientRect();
            const top = rect.top + window.scrollY;

            if (top <= scrollPosition) {
                activeHeading = heading;
                activeAnchor = heading.id;
            }
        });

        if (activeAnchor && activeAnchor !== this.currentSection) {
            this.setActiveSection(activeAnchor);
        }
    }

    /**
     * Scroll element into view in TOC
     */
    scrollIntoView(element) {
        const container = document.getElementById('tableOfContents');
        if (!container) return;

        const containerRect = container.getBoundingClientRect();
        const elementRect = element.getBoundingClientRect();

        if (elementRect.top < containerRect.top || elementRect.bottom > containerRect.bottom) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Toggle TOC item expansion
     */
    toggleTocItem(anchor) {
        if (this.expandedItems.has(anchor)) {
            this.expandedItems.delete(anchor);
        } else {
            this.expandedItems.add(anchor);
        }

        // Re-render TOC
        this.renderToc(this.tocData);
    }

    /**
     * Toggle expand/collapse all items
     */
    toggleExpandAll() {
        const allAnchors = this.getAllAnchors(this.tocData);

        if (this.expandedItems.size === 0) {
            // Expand all
            allAnchors.forEach(anchor => this.expandedItems.add(anchor));
        } else {
            // Collapse all
            this.expandedItems.clear();
        }

        this.renderToc(this.tocData);
    }

    /**
     * Get all anchors from TOC data
     */
    getAllAnchors(items, anchors = []) {
        items.forEach(item => {
            anchors.push(item.anchor);
            if (item.children) {
                this.getAllAnchors(item.children, anchors);
            }
        });
        return anchors;
    }

    /**
     * Search in TOC
     */
    searchToc(term) {
        this.searchTerm = term.toLowerCase();

        if (!this.searchTerm) {
            this.clearTocSearch();
            return;
        }

        const container = document.getElementById('tableOfContents');
        const tocItems = container.querySelectorAll('.toc-item');

        tocItems.forEach(item => {
            const title = item.getAttribute('data-title').toLowerCase();
            const text = item.querySelector('.toc-text').textContent.toLowerCase();

            if (title.includes(this.searchTerm) || text.includes(this.searchTerm)) {
                item.style.display = 'block';
                item.classList.add('highlight');

                // Expand parent items
                this.expandParentItems(item);
            } else {
                item.style.display = 'none';
                item.classList.remove('highlight');
            }
        });

        // Highlight search term
        this.highlightSearchTerm();
    }

    /**
     * Clear TOC search
     */
    clearTocSearch() {
        this.searchTerm = '';
        const searchInput = document.getElementById('tocSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }

        // Re-render TOC to reset
        this.renderToc(this.tocData);
    }

    /**
     * Expand parent items for search results
     */
    expandParentItems(item) {
        let parent = item.parentElement;
        while (parent) {
            if (parent.classList.contains('toc-children')) {
                const parentAnchor = parent.getAttribute('data-parent');
                if (parentAnchor) {
                    this.expandedItems.add(parentAnchor);
                }
            }
            parent = parent.parentElement;
        }
    }

    /**
     * Highlight search term in TOC
     */
    highlightSearchTerm() {
        if (!this.searchTerm) return;

        const tocTexts = document.querySelectorAll('.toc-text');
        tocTexts.forEach(textElement => {
            const text = textElement.textContent;
            const highlightedText = ViewerUtils.highlightText(text, this.searchTerm, 'search-highlight');
            textElement.innerHTML = highlightedText;
        });
    }

    /**
     * Refresh TOC
     */
    async refreshToc() {
        if (!this.documentId) return;

        try {
            const response = await fetch(`/api/documents/${this.documentId}/toc`);
            if (response.ok) {
                const data = await response.json();
                this.renderToc(data.toc || []);
            }
        } catch (error) {
            console.error('Error refreshing TOC:', error);
        }
    }

    /**
     * Navigation functions
     */
    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    scrollToBottom() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }

    goToNextSection() {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        const currentIndex = headings.findIndex(h => h.id === this.currentSection);

        if (currentIndex < headings.length - 1) {
            const nextHeading = headings[currentIndex + 1];
            this.navigateToSection(nextHeading.id);
        }
    }

    goToPreviousSection() {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        const currentIndex = headings.findIndex(h => h.id === this.currentSection);

        if (currentIndex > 0) {
            const prevHeading = headings[currentIndex - 1];
            this.navigateToSection(prevHeading.id);
        }
    }

    /**
     * Update scroll progress
     */
    updateScrollProgress() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;

        this.scrollProgress = Math.min(Math.max(progress, 0), 100);

        const progressBar = document.getElementById('readingProgressBar');
        const progressText = document.getElementById('progressPercentage');

        if (progressBar) {
            progressBar.style.width = `${this.scrollProgress}%`;
        }

        if (progressText) {
            progressText.textContent = `${Math.round(this.scrollProgress)}%`;
        }
    }

    /**
     * Update document statistics
     */
    updateDocumentStats() {
        const content = document.getElementById('documentContent');
        if (!content) return;

        // Count headings
        const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
        document.getElementById('chapterCount').textContent = headings.length;

        // Count code blocks
        const codeBlocks = content.querySelectorAll('pre code');
        document.getElementById('codeBlockCount').textContent = codeBlocks.length;

        // Count tables
        const tables = content.querySelectorAll('table');
        document.getElementById('tableCount').textContent = tables.length;

        // Count images
        const images = content.querySelectorAll('img');
        document.getElementById('imageCount').textContent = images.length;
    }

    /**
     * Bookmark functions
     */
    addBookmark() {
        const title = prompt('请输入书签标题:');
        if (!title) return;

        const bookmark = {
            id: Date.now(),
            title: title,
            anchor: this.currentSection || 'top',
            timestamp: new Date().toISOString(),
            scrollPosition: window.scrollY
        };

        this.bookmarks.push(bookmark);
        this.saveBookmarks();
        this.renderBookmarks();

        // Show success message
        ViewerUtils.announceToScreenReader(`书签"${title}"已添加`);
    }

    removeBookmark(id) {
        this.bookmarks = this.bookmarks.filter(b => b.id !== id);
        this.saveBookmarks();
        this.renderBookmarks();
    }

    goToBookmark(id) {
        const bookmark = this.bookmarks.find(b => b.id === id);
        if (bookmark) {
            if (bookmark.anchor === 'top') {
                this.scrollToTop();
            } else {
                this.navigateToSection(bookmark.anchor);
            }
        }
    }

    renderBookmarks() {
        const container = document.getElementById('bookmarksList');
        if (!container) return;

        if (this.bookmarks.length === 0) {
            container.innerHTML = `
                <div class="no-bookmarks">
                    <small class="text-muted">暂无书签</small>
                </div>
            `;
            return;
        }

        const bookmarksHtml = this.bookmarks.map(bookmark => `
            <div class="bookmark-item">
                <div class="bookmark-title" title="${bookmark.title}">
                    ${this.escapeHtml(bookmark.title)}
                </div>
                <div class="bookmark-actions">
                    <button class="btn btn-sm btn-outline-primary"
                            onclick="navigationSidebar.goToBookmark(${bookmark.id})"
                            title="跳转">
                        <i class="fas fa-arrow-right"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger"
                            onclick="navigationSidebar.removeBookmark(${bookmark.id})"
                            title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = bookmarksHtml;
    }

    loadBookmarks() {
        const saved = ViewerUtils.getLocalStorage(`bookmarks_${this.documentId}`, []);
        this.bookmarks = saved;
        this.renderBookmarks();
    }

    saveBookmarks() {
        ViewerUtils.setLocalStorage(`bookmarks_${this.documentId}`, this.bookmarks);
    }

    /**
     * Mobile functions
     */
    closeMobile() {
        const sidebar = document.getElementById('navigationSidebar');
        if (sidebar) {
            sidebar.classList.remove('active');
        }
    }

    /**
     * Utility functions
     */
    generateAnchor(text) {
        return text.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim('-');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Public API
     */
    getTocData() {
        return this.tocData;
    }

    getCurrentSection() {
        return this.currentSection;
    }

    getScrollProgress() {
        return this.scrollProgress;
    }

    getBookmarks() {
        return this.bookmarks;
    }
}

// Export for global use
window.NavigationSidebar = NavigationSidebar;

// Create global instance when needed
window.navigationSidebar = null;

// Function to initialize navigation sidebar with document ID
window.initNavigationSidebar = function(documentId) {
    if (window.navigationSidebar) {
        // Update existing instance
        window.navigationSidebar.documentId = documentId;
        window.navigationSidebar.loadBookmarks();
    } else {
        // Create new instance
        window.navigationSidebar = new NavigationSidebar({ documentId: documentId });
    }
};
