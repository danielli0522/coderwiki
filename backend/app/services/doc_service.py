"""
文档服务
"""
from app.models.document import Document
from app.models.repository import Repository
from app.models.user import User
from app import db
from sqlalchemy import and_, or_
from datetime import datetime
from app.utils.logger import get_logger
import threading
import time

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

    def create_document(self, user_id, title, repository_id, document_type, description=''):
        """创建新文档"""
        try:
            # 验证仓库是否存在
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
                status='pending',
                content='',  # 初始为空内容
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

            # 更新状态为处理中
            document.status = 'processing'
            document.updated_at = datetime.utcnow()
            db.session.commit()

            # 启动异步文档生成任务
            thread = threading.Thread(
                target=self._generate_document_async,
                args=(document_id, user_id)
            )
            thread.daemon = True
            thread.start()

            logger.info(f"启动文档生成任务: {document_id}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"生成文档失败: {e}")
            return False

    def _generate_document_async(self, document_id, user_id):
        """异步生成文档内容"""
        try:
            # 模拟文档生成过程
            time.sleep(2)  # 模拟处理时间

            document = Document.query.get(document_id)
            if not document:
                logger.error(f"文档 {document_id} 不存在")
                return

            # 生成示例文档内容
            content = self._generate_sample_content(document)

            # 更新文档内容
            document.content = content
            document.status = 'completed'
            document.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"文档 {document_id} 生成完成")

        except Exception as e:
            logger.error(f"异步生成文档失败: {e}")
            # 更新状态为错误
            try:
                document = Document.query.get(document_id)
                if document:
                    document.status = 'error'
                    document.updated_at = datetime.utcnow()
                    db.session.commit()
            except Exception as update_error:
                logger.error(f"更新文档状态失败: {update_error}")

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
