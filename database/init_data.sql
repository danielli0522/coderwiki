-- CoderWiki 初始数据
USE coderwiki;

-- 创建默认管理员用户
-- 密码: admin123
INSERT INTO users (username, email, password_hash, is_admin, is_active) VALUES 
('admin', 'admin@coderwiki.com', 'pbkdf2:sha256:260000$OZk5b2x5$7a5e9b5a8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f', TRUE, TRUE);

-- 创建示例用户
INSERT INTO users (username, email, password_hash, is_admin, is_active) VALUES 
('demo', 'demo@coderwiki.com', 'pbkdf2:sha256:260000$OZk5b2x5$7a5e9b5a8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f', FALSE, TRUE),
('testuser', 'test@example.com', 'pbkdf2:sha256:260000$OZk5b2x5$7a5e9b5a8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f', FALSE, TRUE);

-- 创建示例仓库
INSERT INTO repositories (user_id, name, url, description, language, status) VALUES 
(1, 'coderwiki-frontend', 'https://github.com/coderwiki/coderwiki-frontend.git', 'CoderWiki前端项目', 'JavaScript', 'active'),
(1, 'coderwiki-backend', 'https://github.com/coderwiki/coderwiki-backend.git', 'CoderWiki后端项目', 'Python', 'active'),
(2, 'example-python-project', 'https://github.com/examples/python-project.git', '示例Python项目', 'Python', 'active'),
(3, 'example-javascript-project', 'https://github.com/examples/javascript-project.git', '示例JavaScript项目', 'JavaScript', 'active');

-- 创建示例文档
INSERT INTO documents (repository_id, user_id, title, content, version, status, file_path, language) VALUES 
(1, 1, '项目介绍', '# CoderWiki项目介绍\n\nCoderWiki是一个智能代码文档生成与管理平台，旨在帮助开发者快速生成高质量的代码文档。\n\n## 功能特性\n\n- 智能代码分析\n- 自动文档生成\n- 多语言支持\n- 版本控制集成\n- 协作功能\n\n## 技术栈\n\n- 前端：HTML, CSS, JavaScript\n- 后端：Python Flask\n- 数据库：MySQL\n- 缓存：Redis\n\n## 快速开始\n\n1. 克隆项目\n2. 安装依赖\n3. 配置环境\n4. 运行项目', '1.0.0', 'published', 'README.md', 'Markdown'),
(2, 1, 'API文档', '# CoderWiki API文档\n\n## 认证\n\n### 登录\n\n```http\nPOST /api/auth/login\nContent-Type: application/json\n\n{\n    "username": "string",\n    "password": "string"\n}\n```\n\n### 注册\n\n```http\nPOST /api/auth/register\nContent-Type: application/json\n\n{\n    "username": "string",\n    "email": "string",\n    "password": "string"\n}\n```', '1.0.0', 'published', 'docs/api.md', 'Markdown'),
(3, 2, '开发指南', '# CoderWiki开发指南\n\n## 开发环境搭建\n\n### 前置条件\n\n- Python 3.8+\n- MySQL 8.0+\n- Node.js 14+\n\n### 安装步骤\n\n1. 克隆项目\n2. 创建虚拟环境\n3. 安装依赖\n4. 配置数据库\n5. 初始化数据库\n6. 启动服务', '1.0.0', 'published', 'docs/development.md', 'Markdown');

-- 创建示例任务
INSERT INTO tasks (user_id, repository_id, type, status, progress, result) VALUES 
(1, 1, 'generate_document', 'completed', 100, '文档生成成功'),
(2, 2, 'sync_repository', 'running', 60, '同步进行中'),
(3, 3, 'analyze_code', 'pending', 0, NULL);

-- 初始化数据创建完成