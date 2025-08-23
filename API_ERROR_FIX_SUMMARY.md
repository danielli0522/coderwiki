# API 错误修复总结

## 问题描述

用户遇到"SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON"错误，这表明 API 返回了 HTML 页面而不是 JSON 数据。

## 问题分析

经过代码检查，发现以下问题：

1. **API 路径重复**：前端使用了`/api/repositories`，但后端 API 蓝图已经注册了`/api/repositories`前缀
2. **错误处理不足**：没有检查 API 响应的内容类型
3. **缺少诊断信息**：无法快速定位 API 问题

## 修复方案

### 1. 修复 API 路径问题

**文件**: `frontend/static/js/repository.js`

- 确保使用正确的 API 路径
- 添加更好的错误处理
- 支持多种数据格式

### 2. 创建 API 错误处理脚本

**文件**: `frontend/static/js/api-error-handler.js`

- 检查 API 响应的内容类型
- 提供详细的错误诊断
- 显示用户友好的错误消息

### 3. 创建 Repository API 修复脚本

**文件**: `frontend/static/js/repository-fix.js`

- 修复所有 repository.js 中的 API 路径
- 提供全局 fetch 拦截器
- 确保 API 路径正确

## 修复内容

### API 路径修复

```javascript
// 修复前
const response = await fetch("/repositories", {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
  },
});

// 修复后
const data = await window.apiErrorHandler.fetchWithErrorHandling(
  "/api/repositories",
  {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  }
);
```

### 错误处理增强

```javascript
// 检查响应内容类型
const contentType = response.headers.get("content-type");
if (!contentType || !contentType.includes("application/json")) {
  const text = await response.text();
  console.warn(`API返回非JSON响应: ${endpoint}`, text.substring(0, 200));
  throw new Error(`API返回非JSON响应: ${endpoint}`);
}

// 检查HTML响应
if (
  errorText.trim().startsWith("<!DOCTYPE") ||
  errorText.trim().startsWith("<html")
) {
  throw new Error(`API端点返回HTML而不是JSON: ${endpoint}`);
}
```

### API 健康检查

```javascript
async checkApiHealth() {
    try {
        const response = await fetch('/api/system/health', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log('API健康检查:', data);
            return true;
        } else {
            console.warn('API健康检查失败:', response.status);
            return false;
        }
    } catch (error) {
        console.error('API健康检查错误:', error);
        return false;
    }
}
```

## 诊断功能

### 错误计数

- 跟踪 API 错误次数
- 达到阈值时显示诊断信息
- 提供详细的错误日志

### 用户友好的错误消息

- 显示具体的错误原因
- 提供解决建议
- 自动关闭错误通知

### 诊断面板

- 显示当前页面 URL
- 显示错误次数和时间戳
- 提供网络连接检查

## 测试方法

1. **重启 Flask 应用**
2. **清除浏览器缓存**
3. **打开浏览器开发者工具**
4. **访问仓库管理页面**
5. **检查控制台错误信息**

## 预期效果

- ✅ API 请求正常
- ✅ 返回正确的 JSON 数据
- ✅ 显示详细的错误信息
- ✅ 提供诊断和解决建议

## 如果问题仍然存在

如果修复后问题仍然存在，请：

1. 打开浏览器开发者工具
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页的 API 请求
4. 检查 API 响应的内容类型
5. 查看诊断面板的信息

## 文件清单

- ✅ `frontend/static/js/repository.js` - 修复 API 调用
- ✅ `frontend/static/js/api-error-handler.js` - API 错误处理
- ✅ `frontend/static/js/repository-fix.js` - Repository API 修复
- ✅ `frontend/templates/base.html` - 添加修复脚本引用

## 使用说明

1. 重启 Flask 应用
2. 清除浏览器缓存
3. 刷新页面
4. 测试仓库加载功能
5. 检查控制台日志

## 技术细节

- 使用 fetch 拦截器修复 API 路径
- 检查响应内容类型
- 提供详细的错误诊断
- 支持多种数据格式
- 自动健康检查
- 用户友好的错误提示

## 常见问题解决

### 1. API 返回 HTML 而不是 JSON

**原因**: API 端点不存在或服务器错误
**解决**: 检查后端 API 路由配置

### 2. 网络连接问题

**原因**: 服务器未启动或网络问题
**解决**: 检查服务器状态和网络连接

### 3. 认证问题

**原因**: 用户未登录或 token 过期
**解决**: 重新登录或刷新 token

### 4. CORS 问题

**原因**: 跨域请求被阻止
**解决**: 检查后端 CORS 配置

