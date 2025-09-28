# CoderWiki常用代码模式

## API端点标准模式

### REST API设计模式
```python
# 文件位置: backend/app/api/{resource}.py
from flask import Blueprint, request, jsonify
from app.services import {resource}_service
from app.utils.auth import require_auth
from app.utils.validation import validate_request

bp = Blueprint('{resource}', __name__)

@bp.route('/api/{resources}', methods=['POST'])
@require_auth
def create_{resource}():
    """创建{resource}的标准模式"""
    try:
        # 1. 获取并验证请求数据
        data = request.get_json()
        validate_request(data, '{resource}_create_schema')

        # 2. 调用业务服务层
        result = {resource}_service.create(data, current_user.id)

        # 3. 返回标准响应
        return jsonify(result.to_dict()), 201

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/api/{resources}/<int:{resource}_id>', methods=['GET'])
@require_auth
def get_{resource}({resource}_id):
    """获取单个{resource}的标准模式"""
    try:
        result = {resource}_service.get_by_id({resource}_id, current_user.id)
        if not result:
            return jsonify({'error': '{resource} not found'}), 404
        return jsonify(result.to_dict())
    except PermissionError:
        return jsonify({'error': 'Access denied'}), 403
```

### 参考实现
- **仓库API**: `backend/app/api/repository.py`
- **认证API**: `backend/app/api/auth.py`

## 业务服务层模式

### Service类标准结构
```python
# 文件位置: backend/app/services/{resource}_service.py
from typing import List, Optional, Dict, Any
from app.models import {Resource}
from app.utils.database import db
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class {Resource}Service:
    """
    {Resource}业务逻辑服务
    负责处理{resource}相关的业务规则和数据操作
    """

    @staticmethod
    def create(data: Dict[str, Any], user_id: int) -> {Resource}:
        """创建新{resource}"""
        try:
            # 1. 业务规则验证
            {Resource}Service._validate_create_data(data, user_id)

            # 2. 创建实体对象
            {resource} = {Resource}(
                user_id=user_id,
                **data
            )

            # 3. 数据库操作
            db.session.add({resource})
            db.session.commit()

            logger.info(f"{Resource} created successfully: {{{resource}.id}}")
            return {resource}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create {resource}: {{e}}")
            raise

    @staticmethod
    def get_by_id({resource}_id: int, user_id: int) -> Optional[{Resource}]:
        """根据ID获取{resource}"""
        return {Resource}.query.filter_by(
            id={resource}_id,
            user_id=user_id
        ).first()

    @staticmethod
    def _validate_create_data(data: Dict[str, Any], user_id: int) -> None:
        """验证创建{resource}的数据"""
        # 实现具体的业务验证逻辑
        pass
```

### 参考实现
- **仓库服务**: `backend/app/services/repository_service.py`
- **分析服务**: `backend/app/services/analysis_service.py`

## 数据模型标准模式

### SQLAlchemy模型基础结构
```python
# 文件位置: backend/app/models/{resource}.py
from app.utils.database import db
from datetime import datetime
from typing import Dict, Any

class {Resource}(db.Model):
    """
    {Resource}数据模型

    业务描述: {业务描述}
    """
    __tablename__ = '{resources}'

    # 主键字段
    id = db.Column(db.Integer, primary_key=True)

    # 业务字段
    name = db.Column(db.String(255), nullable=False)

    # 关联字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 审计字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    user = db.relationship('User', backref='{resources}')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<{Resource} {{self.id}}: {{self.name}}>'
```

### 参考实现
- **仓库模型**: `backend/app/models/repository.py`
- **用户模型**: `backend/app/models/user.py`

## 测试用例标准模式

### 单元测试结构
```python
# 文件位置: backend/tests/unit/test_{resource}_model.py
import pytest
from app.models import {Resource}
from tests.fixtures.test_data_factories import {Resource}Factory

class Test{Resource}ModelBasic:
    """测试{Resource}模型基础功能"""

    def test_create_{resource}_with_valid_data(self, db_session):
        """{resource}创建成功测试"""
        # Arrange
        data = {Resource}Factory.build_dict()

        # Act
        {resource} = {Resource}(**data)
        db_session.add({resource})
        db_session.commit()

        # Assert
        assert {resource}.id is not None
        assert {resource}.name == data['name']

    def test_to_dict_conversion(self, sample_{resource}):
        """测试to_dict方法"""
        # Act
        result = sample_{resource}.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert 'id' in result
        assert 'name' in result

class Test{Resource}ModelValidation:
    """测试{Resource}模型验证逻辑"""

    def test_required_fields_validation(self, db_session):
        """测试必填字段验证"""
        with pytest.raises(ValidationError):
            {resource} = {Resource}()  # 缺少必填字段
            db_session.add({resource})
            db_session.commit()
```

### 参考实现
- **仓库模型测试**: `backend/tests/unit/test_repository_model.py`

## 错误处理标准模式

### 统一异常处理
```python
# 文件位置: backend/app/utils/exceptions.py
class CoderWikiException(Exception):
    """CoderWiki基础异常类"""
    pass

class ValidationError(CoderWikiException):
    """数据验证错误"""
    pass

class BusinessLogicError(CoderWikiException):
    """业务逻辑错误"""
    pass

class ResourceNotFoundError(CoderWikiException):
    """资源未找到错误"""
    pass

# API层错误处理装饰器
def handle_exceptions(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except BusinessLogicError as e:
            return jsonify({'error': str(e)}), 422
        except ResourceNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper
```

## AI集成标准模式

### LLM客户端调用模式
```python
# 文件位置: backend/app/utils/llm_client.py 参考
from app.utils.llm_client import get_llm_client

def generate_documentation(analysis_data: Dict) -> str:
    """使用AI生成文档的标准模式"""
    try:
        # 1. 准备提示词
        prompt = f"""
        基于以下代码分析结果生成技术文档:

        项目结构: {analysis_data['structure']}
        技术栈: {analysis_data['tech_stack']}
        复杂度: {analysis_data['complexity']}

        请生成包含以下部分的文档:
        1. 项目概述
        2. 架构设计
        3. 核心模块说明
        4. 部署指南
        """

        # 2. 调用AI服务
        client = get_llm_client()
        response = client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3
        )

        # 3. 后处理
        return response.strip()

    except Exception as e:
        logger.error(f"AI documentation generation failed: {e}")
        raise AIServiceError(f"Failed to generate documentation: {e}")
```

## 配置管理模式

### 环境配置模式
```python
# 文件位置: backend/app/config.py 参考
import os
from typing import Dict, Any

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///coderwiki.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI服务配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    @classmethod
    def get_ai_config(cls) -> Dict[str, Any]:
        return {
            'openai_key': cls.OPENAI_API_KEY,
            'anthropic_key': cls.ANTHROPIC_API_KEY,
            'default_model': 'gpt-4',
            'max_tokens': 2000
        }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## 日志记录模式

### 标准日志格式
```python
# 在服务类中使用日志
from app.utils.logger import get_logger

logger = get_logger(__name__)

def some_business_method():
    logger.info("Starting business operation")
    try:
        # 业务逻辑
        result = process_data()
        logger.info(f"Operation completed successfully: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

## 使用指南

### 新增功能开发流程
1. **数据模型**: 参考`repository.py`创建数据模型
2. **服务层**: 参考`repository_service.py`创建业务服务
3. **API层**: 参考`repository.py`(API)创建REST端点
4. **测试**: 参考`test_repository_model.py`编写测试用例

### 代码风格要求
- 使用Type Hints进行类型注解
- 遵循PEP 8代码规范
- 必须编写单元测试，覆盖率>90%
- 使用Google风格的docstring
- 错误信息使用英文，用户界面使用中文