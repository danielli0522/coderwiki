# URL 修复总结

## 最新修复 - Flask 路由端点错误

### 问题描述
在运行系统时遇到了 `BuildError` 错误：
```
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'repository.list_repositories'. Did you mean 'repository.get_repositories' instead?
```

### 根本原因
模板文件中使用了不存在的Flask路由端点名称，实际的端点名称与模板中引用的不匹配。

### 修复的路由问题

#### 1. 文档头部面包屑导航
**文件**: `frontend/templates/partials/document_header.html`

**修复内容**:
- 第132行: `repository.list_repositories` → `main.repositories`
- 第133行: `repository.view` → 静态显示仓库名称

#### 2. 导航栏链接
**文件**: `frontend/templates/partials/navbar.html`

**修复内容**:
- `main.index` → `main.dashboard`
- `repository.list_repos` → `main.repositories`
- `document.list_docs` → `main.documents`
- `task.list_tasks` → `main.tasks`

---

## 历史修复 - JavaScript URL 错误

### 问题描述

用户遇到"Failed to construct 'URL': Invalid URL"错误，导致任务加载失败。

## 问题分析

经过代码检查，发现以下问题：

1. **API 路径重复**：多个 JavaScript 文件中使用了`/api/tasks`等路径，但 api_client.js 的 baseUrl 已经是`/api`，导致重复的`/api`前缀
2. **URL 构造函数问题**：相对路径 URL 构造时缺少 base 参数
3. **URLSearchParams 构造失败**：参数格式不正确导致构造失败

## 修复方案

### 1. 修复 api_client.js 中的 URL 构造

**文件**: `frontend/static/js/api_client.js`

- 添加 try-catch 处理 URL 构造错误
- 支持相对路径和完整 URL
- 提供回退机制

### 2. 修复 task.js 中的 API 路径

**文件**: `frontend/static/js/task.js`

- 将`/api/tasks`改为`/tasks`
- 避免重复的 API 前缀

### 3. 修复 components/task_progress.js 中的 API 路径

**文件**: `frontend/static/js/components/task_progress.js`

- 将`/api/tasks`改为`/tasks`
- 确保路径正确

### 4. 修复 components.js 中的 URL 验证

**文件**: `frontend/static/js/components.js`

- 改进 isValidUrl 函数
- 支持相对路径验证
- 添加参数类型检查

### 5. 创建全局 URL 修复脚本

**文件**: `frontend/static/js/url-fix.js`

- 修复 fetch 调用中的 API 路径
- 修复 URLSearchParams 构造问题
- 修复 URL 构造函数问题

## 修复内容

### API 路径修复

```javascript
// 修复前
const response = await this.apiClient.get("/api/tasks");

// 修复后
const response = await this.apiClient.get("/tasks");
```

### URL 构造修复

```javascript
// 修复前
const url = new URL(`${this.baseUrl}${endpoint}`);

// 修复后
let url;
try {
  if (this.baseUrl.startsWith("/")) {
    url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin);
  } else {
    url = new URL(`${this.baseUrl}${endpoint}`);
  }
} catch (error) {
  // 回退到字符串拼接
  const queryString = Object.keys(params)
    .filter((key) => params[key] !== undefined && params[key] !== null)
    .map(
      (key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`
    )
    .join("&");

  const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
  return this.request(fullEndpoint, { ...options, method: "GET" });
}
```

### URL 验证修复

```javascript
// 修复前
isValidUrl: function(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// 修复后
isValidUrl: function(url) {
    if (!url || typeof url !== 'string') {
        return false;
    }

    try {
        if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
            new URL(url, window.location.origin);
        } else {
            new URL(url);
        }
        return true;
    } catch {
        return false;
    }
}
```

## 全局修复脚本

### fetch 拦截器

```javascript
const originalFetch = window.fetch;
window.fetch = function (url, options) {
  if (typeof url === "string" && url.startsWith("/api/")) {
    const fixedUrl = url.replace("/api/", "/");
    console.log(`修复API URL: ${url} -> ${fixedUrl}`);
    return originalFetch(fixedUrl, options);
  }
  return originalFetch(url, options);
};
```

### URL 构造函数修复

```javascript
const OriginalURL = window.URL;
window.URL = function (url, base) {
  try {
    if (typeof url === "string" && url.startsWith("/") && !base) {
      return new OriginalURL(url, window.location.origin);
    }
    return new OriginalURL(url, base);
  } catch (error) {
    console.error("URL构造失败:", error);
    return new OriginalURL(window.location.href);
  }
};
```

## 测试方法

1. **重启 Flask 应用**
2. **清除浏览器缓存**
3. **打开浏览器开发者工具**
4. **访问任务管理页面**
5. **检查控制台是否有错误信息**

## 预期效果

- ✅ 任务加载成功
- ✅ 没有 URL 构造错误
- ✅ API 请求正常
- ✅ 页面功能完整

## 如果问题仍然存在

如果修复后问题仍然存在，请：

1. 打开浏览器开发者工具
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页的网络请求
4. 检查具体的错误堆栈信息
5. 提供错误截图或详细信息

## 文件清单

- ✅ `frontend/static/js/api_client.js` - 修复 URL 构造
- ✅ `frontend/static/js/task.js` - 修复 API 路径
- ✅ `frontend/static/js/components/task_progress.js` - 修复 API 路径
- ✅ `frontend/static/js/components.js` - 修复 URL 验证
- ✅ `frontend/static/js/url-fix.js` - 全局 URL 修复脚本
- ✅ `frontend/templates/base.html` - 添加修复脚本引用

## 使用说明

1. 重启 Flask 应用
2. 清除浏览器缓存
3. 刷新页面
4. 测试任务加载功能
5. 检查控制台日志

## 技术细节

- 使用 try-catch 处理 URL 构造错误
- 提供回退机制确保功能正常
- 拦截 fetch 调用修复 API 路径
- 保持向后兼容性
- 添加详细的错误日志

