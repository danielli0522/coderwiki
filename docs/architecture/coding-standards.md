# 编码标准

## Python编码标准

### 基本规范
- 遵循PEP 8规范
- 使用4个空格缩进
- 最大行长度120字符
- 使用UTF-8编码

### 导入规范
```python
# 标准库导入
import os
import sys
from datetime import datetime

# 第三方库导入
from flask import Flask, render_template
from sqlalchemy import Column, Integer, String

# 本地模块导入
from app.models.user import User
from app.services.auth_service import AuthService
```

### 类定义规范
```python
class UserService:
    """用户服务类，处理用户相关的业务逻辑。"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据用户ID获取用户信息。
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象
        """
        return self.db_session.query(User).filter(User.id == user_id).first()
```

### 函数定义规范
```python
def create_user(username: str, email: str, password: str) -> User:
    """创建新用户。
    
    Args:
        username: 用户名
        email: 邮箱地址
        password: 密码
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValueError: 用户名或邮箱已存在
    """
    # 验证用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        raise ValueError("用户名已存在")
    
    if User.query.filter_by(email=email).first():
        raise ValueError("邮箱已存在")
    
    # 创建用户
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return user
```

### 异常处理规范
```python
try:
    user = create_user(username, email, password)
    return jsonify({"success": True, "user_id": user.id})
except ValueError as e:
    return jsonify({"success": False, "error": str(e)}), 400
except Exception as e:
    # 记录未预期的异常
    current_app.logger.error(f"创建用户失败: {str(e)}")
    return jsonify({"success": False, "error": "服务器内部错误"}), 500
```

### 数据库操作规范
```python
# 使用上下文管理器确保数据库会话正确关闭
from contextlib import contextmanager

@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器。"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 使用示例
with get_db_session() as session:
    user = User(username="test", email="test@example.com")
    session.add(user)
```

### API路由规范
```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录。"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "请求数据为空"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    
    # 登录逻辑
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401
    
    # 登录用户
    login_user(user)
    
    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })
```

## HTML/CSS编码标准

### HTML规范
- 使用语义化HTML5标签
- 保持良好的缩进结构
- 使用双引号包裹属性
- 为所有图片添加alt属性

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码文档自动生成系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">代码文档生成系统</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                <h1>欢迎使用</h1>
                <p>这是一个代码文档自动生成系统</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### CSS规范
- 使用BEM命名规范
- 避免过度嵌套
- 使用CSS变量
- 保持样式的一致性

```css
/* CSS变量定义 */
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --error-color: #ef4444;
    --border-radius: 6px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
}

/* BEM命名规范 */
.card {
    border: 1px solid var(--secondary-color);
    border-radius: var(--border-radius);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.card__header {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
}

.card__content {
    color: var(--secondary-color);
    line-height: 1.5;
}

.card--highlight {
    border-color: var(--primary-color);
    background-color: rgba(37, 99, 235, 0.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .card {
        padding: var(--spacing-sm);
    }
}
```

## JavaScript编码标准

### 基本规范
- 使用ES6+语法
- 使用const和let，避免使用var
- 使用箭头函数
- 使用模板字符串

```javascript
// 使用const和let
const API_BASE_URL = '/api';
let currentUser = null;

// 使用箭头函数
const login = async (username, password) => {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            showNotification('登录成功', 'success');
            window.location.href = '/dashboard';
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('登录失败:', error);
        showNotification('登录失败，请稍后重试', 'error');
    }
};

// 使用模板字符串
const showMessage = (message, type = 'info') => {
    const alertClass = type === 'success' ? 'alert-success' : 
                       type === 'error' ? 'alert-danger' : 'alert-info';
    
    return `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
};
```

### 事件处理规范
```javascript
// 使用事件委托
document.addEventListener('DOMContentLoaded', () => {
    // 登录表单提交
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        await login(username, password);
    });
    
    // 删除仓库按钮
    document.getElementById('repositoryList').addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-repo')) {
            const repoId = e.target.dataset.repoId;
            
            if (confirm('确定要删除这个仓库吗？')) {
                await deleteRepository(repoId);
            }
        }
    });
});
```

### API调用规范
```javascript
// API客户端类
class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('token');
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...this.token ? { 'Authorization': `Bearer ${this.token}` } : {}
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// 使用示例
const api = new ApiClient();
```

## 文档规范

### 注释规范
- 使用文档字符串（docstring）
- 注释要简洁明了
- 复杂逻辑要有注释说明

```python
def generate_documentation(repository_id: int, version: str = None) -> Document:
    """为指定仓库生成技术文档。
    
    这个函数会分析仓库的代码结构，调用LLM API生成技术文档，
    并将结果保存到数据库中。
    
    Args:
        repository_id: 仓库ID
        version: 文档版本号，如果为None则自动生成
        
    Returns:
        Document: 生成的文档对象
        
    Raises:
        RepositoryNotFoundError: 仓库不存在
        GenerationError: 文档生成失败
        
    Example:
        >>> doc = generate_documentation(1, "v1.0")
        >>> print(doc.title)
        "项目技术文档 v1.0"
    """
    # 1. 验证仓库存在
    repository = Repository.query.get(repository_id)
    if not repository:
        raise RepositoryNotFoundError(f"仓库 {repository_id} 不存在")
    
    # 2. 克隆仓库到临时目录
    temp_dir = clone_repository(repository.url)
    
    # 3. 分析代码结构
    code_structure = analyze_code_structure(temp_dir)
    
    # 4. 调用LLM生成文档
    try:
        documentation = call_llm_api(code_structure)
    except Exception as e:
        raise GenerationError(f"LLM API调用失败: {str(e)}")
    
    # 5. 保存文档到数据库
    document = Document(
        repository_id=repository_id,
        version=version or generate_version(),
        content=documentation,
        status='published'
    )
    
    db.session.add(document)
    db.session.commit()
    
    return document
```

## 测试规范

### 单元测试规范
```python
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    
    def setup_method(self):
        """测试前设置。"""
        self.user_service = UserService()
        self.mock_session = Mock()
    
    def test_create_user_success(self):
        """测试创建用户成功的情况。"""
        # 准备测试数据
        username = "testuser"
        email = "test@example.com"
        password = "password123"
        
        # Mock数据库查询
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # 执行测试
        with patch('app.services.user_service.db.session', self.mock_session):
            user = self.user_service.create_user(username, email, password)
        
        # 验证结果
        assert user.username == username
        assert user.email == email
        assert self.mock_session.add.called
        assert self.mock_session.commit.called
    
    def test_create_user_duplicate_username(self):
        """测试创建用户时用户名重复的情况。"""
        # 准备测试数据
        username = "existinguser"
        email = "test@example.com"
        password = "password123"
        
        # Mock数据库查询返回已存在的用户
        existing_user = Mock()
        self.mock_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        # 执行测试并验证异常
        with patch('app.services.user_service.db.session', self.mock_session):
            with pytest.raises(ValueError, match="用户名已存在"):
                self.user_service.create_user(username, email, password)
```

## 代码质量工具

### 必需的工具
- **flake8:** 代码风格检查
- **black:** 代码格式化
- **isort:** 导入排序
- **mypy:** 类型检查（可选）

### 配置文件示例

**setup.cfg:**
```ini
[flake8]
max-line-length = 120
exclude = migrations,.git,__pycache__,build,dist
ignore = E203,W503

[isort]
profile = black
multi_line_output = 3
line_length = 120
known_first_party = app

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short --cov=app --cov-report=html --cov-report=term-missing
```

## Git提交规范

### 提交消息格式
```
<类型>: <描述>

[可选的详细描述]

[可选的引用]
```

### 提交类型
- **feat:** 新功能
- **fix:** 修复bug
- **docs:** 文档更新
- **style:** 代码格式化
- **refactor:** 重构
- **test:** 测试相关
- **chore:** 构建或工具相关

### 提交消息示例
```
feat: 添加用户注册功能

实现了完整的用户注册流程，包括：
- 用户名和邮箱验证
- 密码加密存储
- 数据库记录创建

Closes #123
```

## 安全规范

### 输入验证
- 所有用户输入必须验证
- 使用白名单验证
- 避免SQL注入

### 密码安全
- 使用bcrypt加密密码
- 密码强度验证
- 避免明文存储

### API安全
- 使用HTTPS
- 实现认证和授权
- 限制API调用频率

### 数据保护
- 敏感数据加密
- 避免日志泄露敏感信息
- 定期备份数据