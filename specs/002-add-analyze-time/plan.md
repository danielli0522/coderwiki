# Implementation Plan: 代码质量分析列表页面添加分析日期

**Branch**: `002-add-analyze-time` | **Date**: 2025-09-28

## 实现概述
在仓库列表表格添加"分析时间"列，显示`Repository.last_analysis`字段。

## 技术方案

### 现状分析
- ✅ `last_analysis`字段已存在于Repository模型
- ✅ API已返回该字段 (`to_dict()`方法第78行)
- ✅ 前端表格框架已完整
- 🎯 **只需前端显示改动**

### 实现要点

#### 1. HTML模板修改 (`frontend/templates/repository/index.html`)
```html
<!-- 在表头添加列 -->
<th>分析时间</th>

<!-- 在数据行添加单元格 -->
<td class="analysis-date-cell"></td>
```

#### 2. JavaScript日期格式化 (`frontend/static/js/repository.js`)
```javascript
function formatAnalysisDate(repo) {
    if (!repo.last_analysis) return '<span class="text-muted">未分析</span>';
    if (repo.status === 'analyzing') return '<span class="text-primary">分析中...</span>';

    const date = new Date(repo.last_analysis);
    const now = new Date();
    const hours = (now - date) / (1000 * 60 * 60);

    if (hours < 24) {
        return `<span class="text-success">${Math.floor(hours)}小时前</span>`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}
```

#### 3. 表格渲染更新
在现有的仓库行渲染逻辑中添加分析时间列的填充。

## 文件清单
- `frontend/templates/repository/index.html` - 添加表格列
- `frontend/static/js/repository.js` - 添加日期格式化和渲染逻辑

## 预期工作量
- **开发时间**: 30分钟
- **测试时间**: 15分钟
- **总计**: 45分钟

---
*极简实现方案 - 无后端改动，纯前端显示增强*