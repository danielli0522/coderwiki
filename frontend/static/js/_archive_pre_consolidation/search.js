/**
 * Search Panel JavaScript
 * 
 * This file contains the logic for the search functionality.
 */

class SearchPanel {
    constructor(options = {}) {
        this.documentId = options.documentId || null;
        this.searchResults = [];
        this.searchHistory = [];
        this.currentSearch = null;
        this.isSearching = false;
        this.searchIndex = null;
        
        this.init();
    }
    
    init() {
        this.loadSearchHistory();
        this.setupEventListeners();
        this.buildSearchIndex();
    }
    
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                this.focusSearch();
            }
        });
        
        // Search input events
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', ViewerUtils.debounce((e) => {
                if (e.target.value.length > 2) {
                    this.performSearch();
                } else if (e.target.value.length === 0) {
                    this.clearSearch();
                }
            }, 500));
        }
    }
    
    /**
     * Build search index from document content
     */
    buildSearchIndex() {
        const content = document.getElementById('documentContent');
        if (!content) return;
        
        this.searchIndex = {
            headings: [],
            paragraphs: [],
            codeBlocks: [],
            tables: [],
            lists: []
        };
        
        // Index headings
        content.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((heading, index) => {
            this.searchIndex.headings.push({
                id: heading.id || `heading-${index}`,
                text: heading.textContent,
                level: parseInt(heading.tagName.charAt(1)),
                position: this.getElementPosition(heading)
            });
        });
        
        // Index paragraphs
        content.querySelectorAll('p').forEach((paragraph, index) => {
            const text = paragraph.textContent.trim();
            if (text.length > 0) {
                this.searchIndex.paragraphs.push({
                    id: `paragraph-${index}`,
                    text: text,
                    position: this.getElementPosition(paragraph)
                });
            }
        });
        
        // Index code blocks
        content.querySelectorAll('pre code').forEach((codeBlock, index) => {
            const text = codeBlock.textContent.trim();
            if (text.length > 0) {
                this.searchIndex.codeBlocks.push({
                    id: `code-${index}`,
                    text: text,
                    language: codeBlock.className.replace('language-', '').replace('hljs', ''),
                    position: this.getElementPosition(codeBlock.closest('pre'))
                });
            }
        });
        
        // Index tables
        content.querySelectorAll('table').forEach((table, index) => {
            const text = table.textContent.trim();
            if (text.length > 0) {
                this.searchIndex.tables.push({
                    id: `table-${index}`,
                    text: text,
                    rows: table.querySelectorAll('tr').length,
                    position: this.getElementPosition(table)
                });
            }
        });
        
        // Index lists
        content.querySelectorAll('ul, ol').forEach((list, index) => {
            const text = list.textContent.trim();
            if (text.length > 0) {
                this.searchIndex.lists.push({
                    id: `list-${index}`,
                    text: text,
                    type: list.tagName.toLowerCase(),
                    items: list.querySelectorAll('li').length,
                    position: this.getElementPosition(list)
                });
            }
        });
    }
    
    /**
     * Get element position for search results
     */
    getElementPosition(element) {
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height
        };
    }
    
    /**
     * Handle search input events
     */
    handleSearchInput(event) {
        if (event.key === 'Enter') {
            this.performSearch();
        } else if (event.key === 'Escape') {
            this.clearSearch();
        }
    }
    
    handleKeyDown(event) {
        if (event.key === 'ArrowDown' && this.searchResults.length > 0) {
            event.preventDefault();
            this.focusNextResult();
        } else if (event.key === 'ArrowUp' && this.searchResults.length > 0) {
            event.preventDefault();
            this.focusPreviousResult();
        }
    }
    
    /**
     * Perform search
     */
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query || query.length < 2) return;
        
        this.isSearching = true;
        this.showLoading(true);
        
        const startTime = performance.now();
        
        try {
            // Try server-side search first
            if (this.documentId) {
                await this.performServerSearch(query);
            } else {
                // Fallback to client-side search
                await this.performClientSearch(query);
            }
            
            const endTime = performance.now();
            this.showSearchStats(this.searchResults.length, endTime - startTime);
            
            // Add to search history
            this.addToSearchHistory(query);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('搜索失败，请重试');
        } finally {
            this.isSearching = false;
            this.showLoading(false);
        }
    }
    
    /**
     * Perform server-side search
     */
    async performServerSearch(query) {
        const scope = document.getElementById('searchScope').value;
        const mode = document.querySelector('input[name="searchMode"]:checked')?.value || 'fuzzy';
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const wholeWord = document.getElementById('wholeWord').checked;
        
        const searchParams = new URLSearchParams({
            query: query,
            scope: scope,
            mode: mode,
            case_sensitive: caseSensitive,
            whole_word: wholeWord
        });
        
        const response = await fetch(`/api/documents/${this.documentId}/search?${searchParams}`);
        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }
        
        const data = await response.json();
        this.searchResults = data.results || [];
        this.renderSearchResults();
    }
    
    /**
     * Perform client-side search
     */
    async performClientSearch(query) {
        const scope = document.getElementById('searchScope').value;
        const mode = document.querySelector('input[name="searchMode"]:checked')?.value || 'fuzzy';
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const wholeWord = document.getElementById('wholeWord').checked;
        
        this.searchResults = [];
        
        // Build search corpus based on scope
        let searchCorpus = [];
        
        if (scope === 'all' || scope === 'titles') {
            searchCorpus = searchCorpus.concat(
                this.searchIndex.headings.map(item => ({...item, type: 'heading'}))
            );
        }
        
        if (scope === 'all' || scope === 'content') {
            searchCorpus = searchCorpus.concat(
                this.searchIndex.paragraphs.map(item => ({...item, type: 'paragraph'}))
            );
        }
        
        if (scope === 'all' || scope === 'code') {
            searchCorpus = searchCorpus.concat(
                this.searchIndex.codeBlocks.map(item => ({...item, type: 'code'}))
            );
        }
        
        if (scope === 'all' || scope === 'tables') {
            searchCorpus = searchCorpus.concat(
                this.searchIndex.tables.map(item => ({...item, type: 'table'}))
            );
        }
        
        // Perform search based on mode
        searchCorpus.forEach(item => {
            if (this.matchesQuery(item.text, query, mode, caseSensitive, wholeWord)) {
                this.searchResults.push({
                    id: item.id,
                    title: this.generateResultTitle(item),
                    snippet: this.generateSnippet(item.text, query),
                    type: item.type,
                    position: item.position,
                    score: this.calculateScore(item.text, query)
                });
            }
        });
        
        // Sort by score
        this.searchResults.sort((a, b) => b.score - a.score);
        
        // Limit results
        this.searchResults = this.searchResults.slice(0, 50);
        
        this.renderSearchResults();
    }
    
    /**
     * Check if text matches query
     */
    matchesQuery(text, query, mode, caseSensitive, wholeWord) {
        let searchText = text;
        let searchQuery = query;
        
        if (!caseSensitive) {
            searchText = searchText.toLowerCase();
            searchQuery = searchQuery.toLowerCase();
        }
        
        switch (mode) {
            case 'exact':
                if (wholeWord) {
                    const wordRegex = new RegExp(`\\b${this.escapeRegex(searchQuery)}\\b`);
                    return wordRegex.test(searchText);
                } else {
                    return searchText.includes(searchQuery);
                }
            
            case 'fuzzy':
                // Simple fuzzy matching - allows for small differences
                const distance = this.levenshteinDistance(searchText, searchQuery);
                return distance <= Math.max(searchQuery.length * 0.3, 2);
            
            case 'regex':
                try {
                    const regex = new RegExp(searchQuery, caseSensitive ? 'g' : 'gi');
                    return regex.test(searchText);
                } catch (e) {
                    console.error('Invalid regex:', e);
                    return false;
                }
            
            default:
                return false;
        }
    }
    
    /**
     * Calculate relevance score
     */
    calculateScore(text, query) {
        const textLower = text.toLowerCase();
        const queryLower = query.toLowerCase();
        
        let score = 0;
        
        // Exact match gets highest score
        if (textLower.includes(queryLower)) {
            score += 100;
        }
        
        // Title matches get bonus
        if (text.length < 100) {
            score += 50;
        }
        
        // Early matches get bonus
        const position = textLower.indexOf(queryLower);
        if (position !== -1) {
            score += Math.max(0, 50 - position / 10);
        }
        
        // Word boundary matches get bonus
        const wordRegex = new RegExp(`\\b${this.escapeRegex(queryLower)}\\b`);
        if (wordRegex.test(textLower)) {
            score += 30;
        }
        
        return score;
    }
    
    /**
     * Generate result title
     */
    generateResultTitle(item) {
        switch (item.type) {
            case 'heading':
                return `${item.level === 1 ? '▶' : '▸'} ${item.text}`;
            case 'code':
                return `💻 ${item.language ? item.language.toUpperCase() : 'Code'}`;
            case 'table':
                return `📊 Table (${item.rows} rows)`;
            case 'list':
                return `📝 List (${item.items} items)`;
            default:
                return item.text.substring(0, 50) + '...';
        }
    }
    
    /**
     * Generate search snippet
     */
    generateSnippet(text, query, maxLength = 150) {
        const queryLower = query.toLowerCase();
        const textLower = text.toLowerCase();
        
        const position = textLower.indexOf(queryLower);
        if (position === -1) return text.substring(0, maxLength) + '...';
        
        const start = Math.max(0, position - 50);
        const end = Math.min(text.length, position + query.length + 100);
        
        let snippet = text.substring(start, end);
        
        // Add ellipsis if truncated
        if (start > 0) snippet = '...' + snippet;
        if (end < text.length) snippet = snippet + '...';
        
        // Highlight query
        snippet = ViewerUtils.highlightText(snippet, query, 'search-highlight');
        
        return snippet;
    }
    
    /**
     * Render search results
     */
    renderSearchResults() {
        const container = document.getElementById('resultsContainer');
        const noResults = document.getElementById('noResults');
        
        if (!container) return;
        
        if (this.searchResults.length === 0) {
            container.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }
        
        noResults.style.display = 'none';
        
        const resultsHtml = this.searchResults.map(result => `
            <div class="search-result-item" tabindex="0" 
                 onclick="searchPanel.navigateToResult('${result.id}', ${result.position.top})"
                 onkeydown="searchPanel.handleResultKeydown(event, '${result.id}', ${result.position.top})">
                <div class="result-header">
                    <div class="result-title">${this.escapeHtml(result.title)}</div>
                    <div class="result-type">${result.type}</div>
                </div>
                <div class="result-location">
                    位置: ${Math.round(result.position.top)}px
                </div>
                <div class="result-snippet">
                    ${result.snippet}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = resultsHtml;
    }
    
    /**
     * Navigate to search result
     */
    navigateToResult(id, position) {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Highlight the element briefly
            element.classList.add('search-result-highlight');
            setTimeout(() => {
                element.classList.remove('search-result-highlight');
            }, 2000);
        } else {
            // Fallback to position
            window.scrollTo({ top: position, behavior: 'smooth' });
        }
        
        // Close mobile search panel
        if (window.innerWidth <= 768) {
            this.togglePanel();
        }
    }
    
    handleResultKeydown(event, id, position) {
        if (event.key === 'Enter') {
            this.navigateToResult(id, position);
        }
    }
    
    focusNextResult() {
        const results = document.querySelectorAll('.search-result-item');
        const focused = document.activeElement;
        
        if (focused && focused.classList.contains('search-result-item')) {
            const index = Array.from(results).indexOf(focused);
            if (index < results.length - 1) {
                results[index + 1].focus();
            }
        } else if (results.length > 0) {
            results[0].focus();
        }
    }
    
    focusPreviousResult() {
        const results = document.querySelectorAll('.search-result-item');
        const focused = document.activeElement;
        
        if (focused && focused.classList.contains('search-result-item')) {
            const index = Array.from(results).indexOf(focused);
            if (index > 0) {
                results[index - 1].focus();
            }
        } else if (results.length > 0) {
            results[results.length - 1].focus();
        }
    }
    
    /**
     * Clear search
     */
    clearSearch() {
        document.getElementById('searchInput').value = '';
        document.getElementById('resultsContainer').innerHTML = '';
        document.getElementById('noResults').style.display = 'none';
        document.getElementById('searchStats').style.display = 'none';
        this.searchResults = [];
        this.currentSearch = null;
        
        // Remove highlights
        document.querySelectorAll('.search-highlight').forEach(element => {
            element.outerHTML = element.innerHTML;
        });
    }
    
    /**
     * Show/hide loading state
     */
    showLoading(show) {
        const loading = document.getElementById('searchLoading');
        if (loading) {
            loading.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * Show search statistics
     */
    showSearchStats(count, time) {
        const stats = document.getElementById('searchStats');
        const countElement = document.getElementById('resultCount');
        const timeElement = document.getElementById('searchTime');
        
        if (stats && countElement && timeElement) {
            countElement.textContent = count;
            timeElement.textContent = Math.round(time);
            stats.style.display = 'block';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('resultsContainer');
        if (container) {
            container.innerHTML = `
                <div class="search-error">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        ${message}
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Search history management
     */
    addToSearchHistory(query) {
        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(item => item.query !== query);
        
        // Add to beginning
        this.searchHistory.unshift({
            query: query,
            timestamp: new Date().toISOString()
        });
        
        // Limit to 20 items
        this.searchHistory = this.searchHistory.slice(0, 20);
        
        this.saveSearchHistory();
        this.renderSearchHistory();
    }
    
    renderSearchHistory() {
        const container = document.getElementById('searchHistory');
        if (!container) return;
        
        if (this.searchHistory.length === 0) {
            container.innerHTML = `
                <div class="no-history">
                    <small class="text-muted">无搜索历史</small>
                </div>
            `;
            return;
        }
        
        const historyHtml = this.searchHistory.map(item => `
            <span class="history-item" onclick="searchPanel.searchFromHistory('${this.escapeHtml(item.query)}')">
                ${this.escapeHtml(item.query)}
            </span>
        `).join('');
        
        container.innerHTML = historyHtml;
    }
    
    searchFromHistory(query) {
        document.getElementById('searchInput').value = query;
        this.performSearch();
    }
    
    clearHistory() {
        if (confirm('确定要清除搜索历史吗？')) {
            this.searchHistory = [];
            this.saveSearchHistory();
            this.renderSearchHistory();
        }
    }
    
    loadSearchHistory() {
        this.searchHistory = ViewerUtils.getLocalStorage('search_history', []);
        this.renderSearchHistory();
    }
    
    saveSearchHistory() {
        ViewerUtils.setLocalStorage('search_history', this.searchHistory);
    }
    
    /**
     * Panel management
     */
    togglePanel() {
        const panel = document.getElementById('searchPanel');
        if (panel) {
            panel.classList.toggle('active');
        }
    }
    
    focusSearch() {
        const input = document.getElementById('searchInput');
        if (input) {
            input.focus();
            input.select();
        }
    }
    
    showAdvancedOptions() {
        const advanced = document.getElementById('advancedSearch');
        if (advanced) {
            advanced.style.display = advanced.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    /**
     * Utility functions
     */
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
    
    /**
     * Public API
     */
    getSearchResults() {
        return this.searchResults;
    }
    
    getSearchHistory() {
        return this.searchHistory;
    }
    
    isSearchActive() {
        return this.isSearching;
    }
}

// Export for global use
window.SearchPanel = SearchPanel;