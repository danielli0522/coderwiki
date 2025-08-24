"""
文档服务
"""
from app.models.document import Document
from app.models.repository import Repository
from app.models.user import User
from app import db
from sqlalchemy import and_, or_
from datetime import datetime, timezone
from app.utils.logger import get_logger
import threading
import time
from app.models.task import Task

logger = get_logger(__name__)


class DocumentService:
    """文档服务类"""

    def get_documents(self, user_id, page=1, limit=10, search='', status=''):
        """获取用户文档列表"""
        try:
            query = Document.query.join(Repository).filter(
                Document.user_id == user_id
            )

            # 搜索过滤
            if search:
                query = query.filter(
                    or_(
                        Document.title.contains(search),
                        Document.description.contains(search),
                        Repository.name.contains(search)
                    )
                )

            # 状态过滤
            if status:
                query = query.filter(Document.status == status)

            # 分页
            total = query.count()
            documents = query.order_by(Document.created_at.desc()).offset(
                (page - 1) * limit
            ).limit(limit).all()

            # 转换为字典
            documents_data = []
            for doc in documents:
                doc_data = {
                    'id': doc.id,
                    'title': doc.title,
                    'description': doc.description,
                    'status': doc.status,
                    'document_type': doc.document_type,
                    'repository_id': doc.repository_id,
                    'repository_name': doc.repository.name if doc.repository else None,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None,
                    'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
                }
                documents_data.append(doc_data)

            # 统计信息
            stats = self._get_document_stats(user_id)

            return documents_data, stats

        except Exception as e:
            logger.error(f"获取文档列表失败: {e}")
            return [], {}

    def create_document(self, user_id, title, repository_id, document_type, description='', content='', skip_permission_check=False):
        """创建新文档"""
        try:
            # 验证仓库是否存在
            if skip_permission_check:
                # 系统级操作，跳过用户权限检查
                repository = Repository.query.filter_by(id=repository_id).first()
            else:
                # 用户级操作，检查权限
                repository = Repository.query.filter(
                    and_(
                        Repository.id == repository_id,
                        Repository.user_id == user_id
                    )
                ).first()

            if not repository:
                raise ValueError("仓库不存在或无权限访问")

            # 创建文档
            document = Document(
                title=title,
                description=description,
                document_type=document_type,
                repository_id=repository_id,
                user_id=user_id,
                status='completed' if content else 'pending',
                content=content,  # 使用传入的内容
                version='1.0.0'  # 初始版本
            )

            db.session.add(document)
            db.session.commit()

            logger.info(f"用户 {user_id} 创建文档 {document.id}")

            return {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'status': document.status,
                'document_type': document.document_type,
                'repository_id': document.repository_id,
                'created_at': document.created_at.isoformat() if document.created_at else None
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"创建文档失败: {e}")
            raise

    def get_document(self, document_id, user_id):
        """获取单个文档"""
        try:
            document = Document.query.filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            ).first()

            if not document:
                return None

            return {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'content': document.content,
                'status': document.status,
                'document_type': document.document_type,
                'repository_id': document.repository_id,
                'repository_name': document.repository.name if document.repository else None,
                'created_at': document.created_at.isoformat() if document.created_at else None,
                'updated_at': document.updated_at.isoformat() if document.updated_at else None
            }

        except Exception as e:
            logger.error(f"获取文档失败: {e}")
            return None

    def update_document(self, document_id, user_id, **kwargs):
        """更新文档"""
        try:
            document = Document.query.filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            ).first()

            if not document:
                return None

            # 更新字段
            allowed_fields = ['title', 'description', 'content', 'status', 'document_type']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(document, field):
                    setattr(document, field, value)

            document.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"用户 {user_id} 更新文档 {document_id}")

            return {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'status': document.status,
                'document_type': document.document_type,
                'updated_at': document.updated_at.isoformat() if document.updated_at else None
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"更新文档失败: {e}")
            return None

    def delete_document(self, document_id, user_id):
        """删除文档"""
        try:
            document = Document.query.filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            ).first()

            if not document:
                return False

            db.session.delete(document)
            db.session.commit()

            logger.info(f"用户 {user_id} 删除文档 {document_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"删除文档失败: {e}")
            return False

    def generate_document_content(self, document_id, user_id):
        """生成文档内容"""
        try:
            document = Document.query.filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            ).first()

            if not document:
                return False

            # 创建任务记录
            from app.services.task_service import TaskService
            task_service = TaskService()

            task = Task(
                user_id=user_id,
                repository_id=document.repository_id,
                type='generate_document',
                status='pending',
                progress=0,
                title=f"生成文档: {document.title}",
                description=f"为仓库生成{document.document_type}文档",
                task_type='generate_document'
            )

            db.session.add(task)
            db.session.commit()

            # 更新文档状态为处理中
            document.status = 'processing'
            document.updated_at = datetime.utcnow()
            db.session.commit()

            # 启动异步文档生成任务
            thread = threading.Thread(
                target=self._generate_document_async,
                args=(document_id, user_id, task.id)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"启动文档生成任务: {document_id}, 任务ID: {task.id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"生成文档失败: {e}")
            return False

    def _generate_document_async(self, document_id, user_id, task_id):
        """异步生成文档内容"""
        try:
            # 更新任务状态为运行中
            task = Task.query.get(task_id)
            if task:
                task.status = 'running'
                task.progress = 10
                task.started_at = datetime.now(timezone.utc)
                task.updated_at = datetime.now(timezone.utc)
                db.session.commit()

            # 模拟文档生成过程
            time.sleep(1)  # 模拟处理时间

            # 更新进度
            if task:
                task.progress = 50
                task.updated_at = datetime.now(timezone.utc)
                db.session.commit()

            document = Document.query.get(document_id)
            if not document:
                logger.error(f"文档 {document_id} 不存在")
                return

            # 生成示例文档内容
            content = self._generate_sample_content(document)

            # 更新进度
            if task:
                task.progress = 80
                task.updated_at = datetime.now(timezone.utc)
                db.session.commit()

            # 更新文档内容
            document.content = content
            document.status = 'completed'
            document.generated_at = datetime.now(timezone.utc)
            document.updated_at = datetime.now(timezone.utc)
            db.session.commit()

            # 更新任务状态为完成
            if task:
                task.status = 'completed'
                task.progress = 100
                task.completed_at = datetime.now(timezone.utc)
                task.updated_at = datetime.now(timezone.utc)
                db.session.commit()

            logger.info(f"文档 {document_id} 生成完成")

        except Exception as e:
            logger.error(f"异步生成文档失败: {e}")
            # 更新状态为错误
            try:
                document = Document.query.get(document_id)
                if document:
                    document.status = 'error'
                    document.updated_at = datetime.now(timezone.utc)
                    db.session.commit()

                # 更新任务状态为失败
                task = Task.query.get(task_id)
                if task:
                    task.status = 'failed'
                    task.error_message = str(e)
                    task.updated_at = datetime.now(timezone.utc)
                    db.session.commit()
            except Exception as update_error:
                logger.error(f"更新文档或任务状态失败: {update_error}")

    def _generate_sample_content(self, document):
        """生成示例文档内容"""
        if document.document_type == 'readme':
            return f"""# {document.title}

## 项目概述

这是一个示例README文档，为 {document.title} 项目生成。

## 功能特性

- 功能1
- 功能2
- 功能3

## 安装说明

```bash
npm install
```

## 使用方法

```javascript
const app = require('./app');
app.start();
```

## 贡献指南

欢迎提交Pull Request！

## 许可证

MIT License
"""
        elif document.document_type == 'api':
            return f"""# {document.title} API 文档

## 概述

这是 {document.title} 的API文档。

## 认证

所有API请求都需要在Header中包含认证信息：

```
Authorization: Bearer <token>
```

## 端点

### GET /api/users

获取用户列表

**响应示例：**
```json
{{
  "users": [
    {{"id": 1, "name": "用户1"}},
    {{"id": 2, "name": "用户2"}}
  ]
}}
```

### POST /api/users

创建新用户

**请求体：**
```json
{{
  "name": "新用户",
  "email": "user@example.com"
}}
```
"""
        elif document.document_type == 'architecture':
            return f"""# {document.title} 架构设计文档

## 系统架构概述

这是 {document.title} 的系统架构设计文档。

## 架构风格

### 整体架构
- **架构类型**: 单体架构 / 微服务架构
- **技术栈**: 前端 + 后端 + 数据库
- **部署方式**: 容器化部署

## 核心组件

### 1. 前端层
- **技术栈**: HTML/CSS/JavaScript
- **框架**: 响应式设计
- **功能**: 用户界面展示

### 2. 后端层
- **技术栈**: Python + Flask
- **功能**: 业务逻辑处理
- **API**: RESTful API设计

### 3. 数据层
- **数据库**: MySQL
- **功能**: 数据存储和查询

## 系统架构图

```mermaid
graph TD
    A[用户界面] --> B[API网关]
    B --> C[业务服务]
    C --> D[数据访问层]
    D --> E[数据库]
```

## 技术选型

### 前端技术
- HTML5 + CSS3
- JavaScript ES6+
- Bootstrap 响应式框架

### 后端技术
- Python 3.8+
- Flask Web框架
- SQLAlchemy ORM

### 数据库
- MySQL 8.0
- 支持事务和索引优化

## 部署架构

### 开发环境
- 本地开发服务器
- 热重载支持
- 调试工具集成

### 生产环境
- 容器化部署
- 负载均衡
- 监控和日志

## 安全考虑

- 用户认证和授权
- 数据加密传输
- SQL注入防护
- XSS攻击防护

## 性能优化

- 数据库查询优化
- 缓存策略
- 静态资源压缩
- CDN加速

## 扩展性设计

- 模块化架构
- 插件化设计
- 水平扩展支持
- 微服务拆分准备
"""
        else:
            return f"""# {document.title}

## 文档内容

这是 {document.title} 的文档内容。

### 章节1

这里是第一个章节的内容。

### 章节2

这里是第二个章节的内容。

## 总结

文档生成完成。
"""

    def download_document(self, document_id, user_id):
        """下载文档"""
        try:
            document = Document.query.filter(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id
                )
            ).first()

            if not document:
                return None

            # 根据文档类型确定文件名和内容类型
            file_extensions = {
                'readme': '.md',
                'api': '.md',
                'architecture': '.md',
                'deployment': '.md'
            }

            ext = file_extensions.get(document.document_type, '.md')
            filename = f"{document.title}{ext}"

            return {
                'content': document.content or '',
                'filename': filename,
                'content_type': 'text/markdown'
            }

        except Exception as e:
            logger.error(f"下载文档失败: {e}")
            return None

    def _get_document_stats(self, user_id):
        """获取文档统计信息"""
        try:
            total = Document.query.filter(Document.user_id == user_id).count()
            processing = Document.query.filter(
                and_(
                    Document.user_id == user_id,
                    Document.status == 'processing'
                )
            ).count()
            completed = Document.query.filter(
                and_(
                    Document.user_id == user_id,
                    Document.status == 'completed'
                )
            ).count()
            error = Document.query.filter(
                and_(
                    Document.user_id == user_id,
                    Document.status == 'error'
                )
            ).count()

            return {
                'total': total,
                'processing': processing,
                'completed': completed,
                'error': error
            }

        except Exception as e:
            logger.error(f"获取文档统计失败: {e}")
            return {
                'total': 0,
                'processing': 0,
                'completed': 0,
                'error': 0
            }

    def generate_toc(self, content):
        """从Markdown内容生成目录"""
        try:
            if not content:
                return []

            toc = []
            lines = content.split('\n')

            for line_num, line in enumerate(lines):
                line = line.strip()
                if line.startswith('#'):
                    # 计算标题级别
                    level = 0
                    for char in line:
                        if char == '#':
                            level += 1
                        else:
                            break

                    if level <= 6:  # 只处理1-6级标题
                        # 提取标题文本
                        title = line[level:].strip()

                        # 生成锚点ID
                        anchor = self._generate_anchor(title)

                        toc.append({
                            'title': title,
                            'level': level,
                            'anchor': anchor,
                            'line': line_num + 1
                        })

            return toc

        except Exception as e:
            logger.error(f"生成目录失败: {e}")
            return []

    def _generate_anchor(self, title):
        """生成锚点ID"""
        import re

        # 转换为小写
        anchor = title.lower()

        # 移除特殊字符，保留字母、数字和空格
        anchor = re.sub(r'[^\w\s-]', '', anchor)

        # 将空格替换为连字符
        anchor = re.sub(r'[-\s]+', '-', anchor)

        # 移除首尾连字符
        anchor = anchor.strip('-')

        return anchor
