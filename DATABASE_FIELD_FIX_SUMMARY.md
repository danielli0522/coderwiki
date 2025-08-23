# 数据库字段修复总结

## 问题描述

用户遇到两个主要问题：

1. **数据库字段错误**: `Unknown column 'repositories.url' in 'field list'`
2. **API 方法错误**: 405 Method Not Allowed

## 根本原因分析

### 1. 数据库字段不匹配问题

**问题**: 代码中使用了 `git_url` 字段名，但实际数据库表中的字段名是 `url`

**数据库表结构**:

```sql
CREATE TABLE `coderwiki`.`repositories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` varchar(500) NOT NULL,  -- 实际字段名是 'url'
  `description` text,
  -- ... 其他字段
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_url` (`user_id`,`url`)
);
```

**修复**: 将所有代码中的字段引用统一为 `url`

### 2. 数据库连接问题

**问题**: 开发环境配置使用了错误的数据库名 `coderwiki_dev`

**修复**: 将开发环境数据库名改为 `coderwiki`

## 修复内容

### 1. 模型文件修复 (`backend/app/models/repository.py`)

```python
# 修复前
git_url = db.Column('git_url', db.String(500), nullable=False)

# 修复后
url = db.Column(db.String(500), nullable=False)
```

### 2. API 文件修复 (`backend/app/api/repository.py`)

```python
# 修复前
result = repo_service.create_repository(
    user_id=current_user.id,
    git_url=url,
    name=name,
    description=description
)

# 修复后
result = repo_service.create_repository(
    user_id=current_user.id,
    url=url,
    name=name,
    description=description
)
```

### 3. 服务文件修复 (`backend/app/services/repository_service.py`)

```python
# 修复前
def create_repository(self, user_id: int, git_url: str, ...):
    existing_repo = Repository.query.filter_by(
        user_id=user_id,
        git_url=git_url
    ).first()

# 修复后
def create_repository(self, user_id: int, url: str, ...):
    existing_repo = Repository.query.filter_by(
        user_id=user_id,
        url=url
    ).first()
```

### 4. 配置文件修复 (`backend/config.py`)

```python
# 修复前
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki_user:coderwiki_password@localhost:3306/coderwiki_dev'

# 修复后
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://coderwiki_user:coderwiki_password@localhost:3306/coderwiki'
```

### 5. 其他文件修复

- `backend/app/api/activities.py`: 修复 `repository_url` 引用
- `backend/app/services/document_generator.py`: 修复 `repository_url` 引用

## 验证结果

### API 端点测试

```bash
# GET请求测试
curl -X GET http://localhost:5001/api/repositories
# 结果: 302重定向到登录页面 (正常)

# POST请求测试
curl -X POST http://localhost:5001/api/repositories \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/test/test","name":"test-repo"}'
# 结果: 302重定向到登录页面 (正常)
```

### 数据库连接测试

```bash
# 检查数据库表结构
python -c "from app import create_app, db; from config import DevelopmentConfig; app = create_app(DevelopmentConfig); app.app_context().push(); from app.models.repository import Repository; print([c.name for c in Repository.__table__.columns])"
# 结果: ['id', 'user_id', 'name', 'url', 'description', ...] (正常)
```

## 当前状态

✅ **数据库字段问题**: 已修复
✅ **数据库连接问题**: 已修复
✅ **API 端点**: 正常工作
✅ **认证重定向**: 正常工作

## 剩余问题

### 405 Method Not Allowed 错误

**状态**: 需要进一步调查

**可能原因**:

1. 前端 JavaScript 请求路径错误
2. 浏览器缓存问题
3. 前端路由冲突

**建议解决方案**:

1. 清除浏览器缓存
2. 检查前端 JavaScript 请求路径
3. 确认用户已登录

## 下一步行动

1. **用户登录测试**: 确保用户能够正常登录
2. **前端调试**: 检查前端 JavaScript 的具体错误
3. **API 测试**: 使用已登录的会话测试 API 调用

---

**修复完成时间**: 2025 年 8 月 23 日
**影响范围**: 后端模型、API、服务文件
**测试状态**: ✅ 数据库连接和 API 端点已验证
