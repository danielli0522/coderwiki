// CoderWiki 主JavaScript文件

// 全局变量
const CoderWiki = {
    // 应用配置
    config: {
        apiBaseUrl: '/api',
        debug: false,
        timeout: 30000
    },
    
    // 工具函数
    utils: {
        // 显示加载动画
        showLoading: function(element) {
            const loadingHtml = '<div class="loading"></div> 加载中...';
            if (element) {
                element.innerHTML = loadingHtml;
                element.disabled = true;
            }
        },
        
        // 隐藏加载动画
        hideLoading: function(element, originalContent) {
            if (element) {
                element.innerHTML = originalContent || element.getAttribute('data-original-content');
                element.disabled = false;
            }
        },
        
        // 显示消息提示
        showMessage: function(message, type = 'info') {
            const alertClass = type === 'error' ? 'alert-danger' : 
                             type === 'success' ? 'alert-success' : 
                             type === 'warning' ? 'alert-warning' : 'alert-info';
            
            const alertHtml = `
                <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            // 在页面顶部插入消息
            const container = document.querySelector('main .container') || document.querySelector('main');
            container.insertAdjacentHTML('afterbegin', alertHtml);
            
            // 5秒后自动关闭
            setTimeout(() => {
                const alert = container.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        },
        
        // 确认对话框
        confirmDialog: function(message, callback) {
            if (confirm(message)) {
                callback();
            }
        },
        
        // 格式化日期
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // 格式化文件大小
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        // 防抖函数
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // 节流函数
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    },
    
    // API请求
    api: {
        // GET请求
        get: function(url, params = {}) {
            return this.request('GET', url, params);
        },
        
        // POST请求
        post: function(url, data = {}) {
            return this.request('POST', url, data);
        },
        
        // PUT请求
        put: function(url, data = {}) {
            return this.request('PUT', url, data);
        },
        
        // DELETE请求
        delete: function(url) {
            return this.request('DELETE', url);
        },
        
        // 通用请求方法
        request: function(method, url, data = {}) {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };
            
            // 添加CSRF令牌
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            if (csrfToken) {
                options.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
            }
            
            if (method !== 'GET') {
                options.body = JSON.stringify(data);
            }
            
            // 构建完整URL
            const fullUrl = CoderWiki.config.apiBaseUrl + url;
            
            return fetch(fullUrl, options)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('API请求失败:', error);
                    throw error;
                });
        }
    },
    
    // 表单处理
    forms: {
        // 初始化表单验证
        initValidation: function(formId, rules) {
            const form = document.getElementById(formId);
            if (!form) return;
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // 验证表单
                if (this.validateForm(form, rules)) {
                    // 提交表单
                    this.submitForm(form);
                }
            }.bind(this));
        },
        
        // 验证表单
        validateForm: function(form, rules) {
            let isValid = true;
            
            for (const [fieldName, rule] of Object.entries(rules)) {
                const field = form.querySelector(`[name="${fieldName}"]`);
                if (!field) continue;
                
                const value = field.value.trim();
                let errorMessage = '';
                
                // 必填验证
                if (rule.required && !value) {
                    errorMessage = '此字段为必填项';
                }
                
                // 长度验证
                if (value && rule.minLength && value.length < rule.minLength) {
                    errorMessage = `最少需要${rule.minLength}个字符`;
                }
                
                if (value && rule.maxLength && value.length > rule.maxLength) {
                    errorMessage = `最多允许${rule.maxLength}个字符`;
                }
                
                // 格式验证
                if (value && rule.pattern && !rule.pattern.test(value)) {
                    errorMessage = rule.message || '格式不正确';
                }
                
                // 显示错误信息
                this.showFieldError(field, errorMessage);
                
                if (errorMessage) {
                    isValid = false;
                }
            }
            
            return isValid;
        },
        
        // 显示字段错误
        showFieldError: function(field, message) {
            // 移除旧的错误信息
            const oldError = field.parentNode.querySelector('.invalid-feedback');
            if (oldError) {
                oldError.remove();
            }
            
            field.classList.remove('is-invalid');
            
            if (message) {
                field.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = message;
                field.parentNode.appendChild(errorDiv);
            }
        },
        
        // 提交表单
        submitForm: function(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            const submitUrl = form.getAttribute('action');
            const submitMethod = form.getAttribute('method') || 'POST';
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalContent = submitBtn.innerHTML;
            
            this.utils.showLoading(submitBtn);
            
            this.api.request(submitMethod, submitUrl, data)
                .then(response => {
                    this.utils.showMessage(response.message || '操作成功', 'success');
                    
                    // 处理成功回调
                    if (form.dataset.successCallback) {
                        window[form.dataset.successCallback](response);
                    } else if (response.redirect) {
                        window.location.href = response.redirect;
                    } else {
                        form.reset();
                    }
                })
                .catch(error => {
                    this.utils.showMessage(error.message || '操作失败', 'error');
                })
                .finally(() => {
                    this.utils.hideLoading(submitBtn, originalContent);
                });
        }
    },
    
    // 文件上传
    fileUpload: {
        // 初始化文件上传
        init: function(inputId, options = {}) {
            const input = document.getElementById(inputId);
            if (!input) return;
            
            const defaults = {
                maxFileSize: 10 * 1024 * 1024, // 10MB
                allowedTypes: [],
                onSuccess: null,
                onError: null
            };
            
            const config = { ...defaults, ...options };
            
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                // 验证文件大小
                if (file.size > config.maxFileSize) {
                    CoderWiki.utils.showMessage('文件大小超过限制', 'error');
                    return;
                }
                
                // 验证文件类型
                if (config.allowedTypes.length > 0 && !config.allowedTypes.includes(file.type)) {
                    CoderWiki.utils.showMessage('文件类型不支持', 'error');
                    return;
                }
                
                // 处理文件上传
                this.uploadFile(file, config);
            }.bind(this));
        },
        
        // 上传文件
        uploadFile: function(file, config) {
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    this.updateProgress(percent);
                }
            }.bind(this);
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    if (config.onSuccess) {
                        config.onSuccess(response);
                    }
                } else {
                    const error = JSON.parse(xhr.responseText);
                    if (config.onError) {
                        config.onError(error);
                    }
                }
            };
            
            xhr.onerror = function() {
                CoderWiki.utils.showMessage('文件上传失败', 'error');
                if (config.onError) {
                    config.onError({ message: '网络错误' });
                }
            };
            
            xhr.open('POST', CoderWiki.config.apiBaseUrl + '/upload', true);
            xhr.send(formData);
        },
        
        // 更新进度
        updateProgress: function(percent) {
            const progressBar = document.querySelector('.upload-progress');
            if (progressBar) {
                progressBar.style.width = percent + '%';
                progressBar.setAttribute('aria-valuenow', percent);
            }
        }
    },
    
    // 初始化应用
    init: function() {
        // 初始化工具提示
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // 初始化弹出框
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // 初始化自动关闭的警告框
        const alertList = document.querySelectorAll('.alert');
        alertList.forEach(function(alert) {
            setTimeout(function() {
                alert.remove();
            }, 5000);
        });
        
        // 初始化AJAX链接
        this.initAjaxLinks();
        
        // 初始化确认对话框
        this.initConfirmDialogs();
        
        console.log('CoderWiki initialized');
    },
    
    // 初始化AJAX链接
    initAjaxLinks: function() {
        document.querySelectorAll('a[data-ajax]').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const url = this.getAttribute('href');
                const method = this.getAttribute('data-method') || 'GET';
                const confirmMessage = this.getAttribute('data-confirm');
                
                if (confirmMessage) {
                    this.utils.confirmDialog(confirmMessage, function() {
                        this.makeAjaxRequest(url, method);
                    }.bind(this));
                } else {
                    this.makeAjaxRequest(url, method);
                }
            }.bind(this));
        }.bind(this));
    },
    
    // 初始化确认对话框
    initConfirmDialogs: function() {
        document.querySelectorAll('button[data-confirm]').forEach(function(button) {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    },
    
    // 发送AJAX请求
    makeAjaxRequest: function(url, method) {
        this.api.request(method, url)
            .then(response => {
                this.utils.showMessage(response.message || '操作成功', 'success');
                if (response.redirect) {
                    window.location.href = response.redirect;
                }
            })
            .catch(error => {
                this.utils.showMessage(error.message || '操作失败', 'error');
            });
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    CoderWiki.init();
});

// 导出到全局
window.CoderWiki = CoderWiki;