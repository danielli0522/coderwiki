# 技术栈

## 后端技术栈

### 核心框架
- **Web框架:** Flask 2.3+
- **数据库:** MySQL 8.0
- **ORM:** SQLAlchemy 2.0+
- **认证:** Flask-Login
- **迁移:** Flask-Migrate
- **API文档:** Flask-RESTX (可选)

### 辅助工具
- **环境管理:** python-dotenv
- **表单验证:** Flask-WTF
- **邮件支持:** Flask-Mail (可选)
- **缓存:** Flask-Caching (可选)

## 前端技术栈

### 核心框架
- **CSS框架:** Bootstrap 5.3
- **JavaScript库:** jQuery 3.6+
- **图标库:** Font Awesome 6
- **模板引擎:** Jinja2 (Flask内置)

### 辅助工具
- **代码高亮:** Prism.js 或 highlight.js
- **表单验证:** jQuery Validation Plugin
- **通知组件:** Toast 或 Alert 组件

## 开发工具

### 版本控制
- **Git:** 版本控制系统
- **GitHub/GitLab:** 代码托管平台

### 数据库管理
- **MySQL Workbench:** 数据库管理工具
- **phpMyAdmin:** Web数据库管理工具 (可选)

### API测试
- **Postman:** API测试工具
- **curl:** 命令行HTTP客户端

### 代码编辑器
- **VS Code:** 主要代码编辑器
- **推荐插件:** Python, MySQL, Docker, Git

### 部署工具
- **Docker:** 容器化部署 (可选)
- **Nginx:** Web服务器
- **Gunicorn:** WSGI HTTP服务器

## 测试工具

### 后端测试
- **pytest:** Python测试框架
- **pytest-cov:** 测试覆盖率
- **factory-boy:** 测试数据生成
- **mock:** 模拟对象

### 前端测试
- **Jest:** JavaScript测试框架 (可选)
- **Selenium:** 端到端测试 (可选)

## 版本要求

### Python版本
- **Python:** 3.8+
- **pip:** 最新版本

### 数据库版本
- **MySQL:** 8.0+
- **MySQL Connector:** 8.0+

### 浏览器支持
- **Chrome:** 90+
- **Firefox:** 88+
- **Safari:** 14+
- **Edge:** 90+

## 包管理

### Python包管理
- **requirements.txt:** 生产环境依赖
- **requirements-dev.txt:** 开发环境依赖

### 前端包管理
- **CDN:** 通过CDN加载前端资源
- **本地资源:** 关键资源本地化部署

## 安全要求

### 后端安全
- **密码加密:** bcrypt
- **会话管理:** Flask-Login + Flask-Session
- **CSRF保护:** Flask-WTF CSRF保护
- **SQL注入防护:** SQLAlchemy ORM

### 前端安全
- **XSS防护:** Jinja2自动转义
- **HTTPS:** 生产环境强制HTTPS
- **CSP:** 内容安全策略 (可选)