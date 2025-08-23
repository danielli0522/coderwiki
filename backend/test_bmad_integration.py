#!/usr/bin/env python3
"""
完整的 BMAD 集成测试
测试从 Claude Code SDK 到 BMAD 编排器的完整流程
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 添加 bmad-docs-generator 到路径
bmad_path = project_root.parent / 'bmad-docs-generator'
sys.path.insert(0, str(bmad_path))

from app.utils.claude_client import ClaudeCodeClient
from app.utils.bmad_orchestrator import BMADOrchestrator
from app.services.smart_doc_service import SmartDocumentService


def test_bmad_orchestrator():
    """测试 BMAD 编排器"""
    print("=" * 60)
    print("测试 BMAD 编排器")
    print("=" * 60)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建测试配置目录
        config_dir = os.path.join(temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        # 创建测试文件
        test_files = {
            "config/app.py": """
class Config:
    SECRET_KEY = 'test-secret'
    DEBUG = True
    DATABASE_URL = 'mysql://localhost/test'
""",
            "config/database.py": """
class DatabaseConfig:
    HOST = 'localhost'
    PORT = 3306
    DATABASE = 'test'
""",
            "README.md": """
# Test Project
This is a test project for BMAD integration.
"""
        }

        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # 创建测试输入
        test_input = {
            "repo_path": temp_dir,
            "analysis_depth": "detailed",
            "include_diagrams": True,
            "include_troubleshooting": True,
            "doc_type": "complete"
        }

        # 保存测试输入
        input_file = os.path.join(temp_dir, "test_input.json")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(test_input, f, indent=2)

        # 运行 BMAD 编排器
        print(f"运行 BMAD 编排器...")
        print(f"输入文件: {input_file}")

        # 导入并运行 BMAD 编排器
        bmad_path = os.path.join(os.path.dirname(__file__), '..', 'bmad-docs-generator')
        sys.path.insert(0, bmad_path)
        from bmad_orchestrator import BMADOrchestrator

        orchestrator = BMADOrchestrator()
        result = orchestrator.execute_workflow('enhanced-docs-generation', test_input)

        # 输出结果
        print(f"\n工作流执行结果:")
        print(f"  状态: {result.status}")
        print(f"  执行时间: {result.execution_time:.2f}s")
        print(f"  代理结果数量: {len(result.agent_results) if result.agent_results else 0}")

        if result.final_document:
            print(f"\n生成的文档长度: {len(result.final_document)} 字符")
            print(f"文档预览:")
            print(result.final_document[:500] + "..." if len(result.final_document) > 500 else result.final_document)

        # 保存结果
        output_file = os.path.join(temp_dir, "test_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'workflow_id': result.workflow_id,
                'status': str(result.status),
                'execution_time': result.execution_time,
                'agent_results': result.agent_results,
                'final_document': result.final_document,
                'error_message': result.error_message
            }, f, indent=2, default=str)

        print(f"\n结果已保存到: {output_file}")

        # 验证结果
        assert result.status.value == 'completed', f"工作流应该完成，但状态是: {result.status}"
        assert result.final_document is not None, "应该生成最终文档"
        assert len(result.final_document) > 0, "文档不应该为空"

        print("✅ BMAD 编排器测试通过!")

        return True

    except Exception as e:
        print(f"❌ BMAD 编排器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_claude_bmad_integration():
    """测试 Claude Code 和 BMAD 集成"""
    print("\n" + "=" * 60)
    print("测试 Claude Code 和 BMAD 集成")
    print("=" * 60)

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 创建测试配置目录
        config_dir = os.path.join(temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        # 创建测试文件
        test_files = {
            "config/app.py": """
class Config:
    SECRET_KEY = 'test-secret'
    DEBUG = True
    DATABASE_URL = 'mysql://localhost/test'
""",
            "config/database.py": """
class DatabaseConfig:
    HOST = 'localhost'
    PORT = 3306
    DATABASE = 'test'
""",
            "README.md": """
# Test Project
This is a test project for Claude Code and BMAD integration.
"""
        }

        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # 模拟 Claude Code 客户端
        print("模拟 Claude Code 客户端...")

        # 创建配置
        config = {
            'repo_path': temp_dir,
            'analysis_depth': 'detailed',
            'include_diagrams': True,
            'include_troubleshooting': True,
            'doc_type': 'complete'
        }

        # 测试 BMAD 编排器（模拟 Claude Code 调用）
        print("执行 BMAD 工作流...")

        bmad_path = os.path.join(os.path.dirname(__file__), '..', 'bmad-docs-generator')
        sys.path.insert(0, bmad_path)
        from bmad_orchestrator import BMADOrchestrator

        orchestrator = BMADOrchestrator()
        result = orchestrator.execute_workflow('enhanced-docs-generation', config)

        # 验证结果
        print(f"\n集成测试结果:")
        print(f"  工作流状态: {result.status}")
        print(f"  执行时间: {result.execution_time:.2f}s")
        print(f"  代理数量: {len(result.agent_results) if result.agent_results else 0}")

        # 检查代理结果
        if result.agent_results:
            print(f"\n代理执行结果:")
            for task_id, task_result in result.agent_results.items():
                status = task_result.get('status', 'unknown')
                agent_id = task_result.get('agent_id', 'unknown')
                print(f"  - {task_id}: {agent_id} ({status})")

        # 验证文档生成
        if result.final_document:
            print(f"\n生成的文档包含以下部分:")
            doc_content = result.final_document.lower()
            sections = [
                'code analysis',
                'architecture analysis',
                'flow analysis',
                'problem diagnosis',
                'summary'
            ]

            for section in sections:
                if section in doc_content:
                    print(f"  ✅ {section}")
                else:
                    print(f"  ❌ {section}")

        # 验证成功条件
        assert result.status.value == 'completed', f"工作流应该完成，但状态是: {result.status}"
        assert result.final_document is not None, "应该生成最终文档"
        assert len(result.final_document) > 1000, "文档应该足够详细"

        print("✅ Claude Code 和 BMAD 集成测试通过!")

        return True

    except Exception as e:
        print(f"❌ Claude Code 和 BMAD 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_config_documentation_generation():
    """测试 Config 目录文档生成"""
    print("\n" + "=" * 60)
    print("测试 Config 目录文档生成")
    print("=" * 60)

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 创建真实的 Config 目录结构
        config_dir = os.path.join(temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        # 创建配置文件
        config_files = {
            "config/__init__.py": """
# 配置模块初始化
from .app import Config
from .database import DatabaseConfig

__all__ = ['Config', 'DatabaseConfig']
""",
            "config/app.py": """
# 应用配置
import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = False

    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://localhost/coderwiki')

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True

    # Claude Code 配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_WORKSPACE_ID = os.getenv('CLAUDE_WORKSPACE_ID')

    # BMAD 代理配置
    BMAD_AGENTS_PATH = os.getenv('BMAD_AGENTS_PATH', 'bmad-docs-generator')
    BMAD_WORKFLOW_TIMEOUT = int(os.getenv('BMAD_WORKFLOW_TIMEOUT', '300'))
""",
            "config/database.py": """
# 数据库配置
import os

class DatabaseConfig:
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'coderwiki')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'coderwiki_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'coderwiki_password')

    # 连接池配置
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))

    @classmethod
    def get_database_url(cls):
        return f"mysql+pymysql://{cls.MYSQL_USERNAME}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
""",
            "README.md": """
# CoderWiki - 智能文档生成系统

## 项目概述

CoderWiki 是一个基于 Claude Code SDK 和 BMAD 代理系统的智能文档生成平台。

## 技术架构

### 后端技术栈
- **Web 框架**: Flask
- **数据库**: MySQL + SQLAlchemy
- **AI 集成**: Claude Code SDK
- **代理系统**: BMAD-Docs-Generator

### 配置系统

项目采用模块化配置系统，主要配置模块包括：

#### 1. 应用配置 (`config/app.py`)
- 基础应用设置
- 环境配置
- 数据库连接
- Claude Code 配置

#### 2. 数据库配置 (`config/database.py`)
- MySQL 连接参数
- 连接池配置
- 数据库 URL 生成

## 快速开始

1. 安装依赖
2. 配置环境变量
3. 初始化数据库
4. 启动应用

## 许可证

MIT License
"""
        }

        for file_path, content in config_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # 执行 BMAD 工作流
        print("执行 Config 目录文档生成...")

        config = {
            'repo_path': temp_dir,
            'analysis_depth': 'comprehensive',
            'include_diagrams': True,
            'include_troubleshooting': True,
            'doc_type': 'complete'
        }

        bmad_path = os.path.join(os.path.dirname(__file__), '..', 'bmad-docs-generator')
        sys.path.insert(0, bmad_path)
        from bmad_orchestrator import BMADOrchestrator

        orchestrator = BMADOrchestrator()
        result = orchestrator.execute_workflow('enhanced-docs-generation', config)

        # 验证结果
        print(f"\nConfig 文档生成结果:")
        print(f"  状态: {result.status}")
        print(f"  执行时间: {result.execution_time:.2f}s")

        if result.final_document:
            print(f"  文档长度: {len(result.final_document)} 字符")

            # 检查文档内容
            doc_content = result.final_document.lower()
            expected_sections = [
                'technical documentation',
                'code analysis',
                'architecture analysis',
                'flow analysis',
                'problem diagnosis',
                'summary'
            ]

            print(f"\n文档内容验证:")
            for section in expected_sections:
                if section in doc_content:
                    print(f"  ✅ 包含 {section}")
                else:
                    print(f"  ❌ 缺少 {section}")

        # 验证成功条件
        assert result.status.value == 'completed', f"工作流应该完成，但状态是: {result.status}"
        assert result.final_document is not None, "应该生成最终文档"
        assert len(result.final_document) > 2000, "Config 文档应该足够详细"

        # 检查是否包含 Config 相关内容
        doc_content = result.final_document.lower()
        config_keywords = ['config', 'configuration', 'database', 'app.py', 'database.py']
        config_found = any(keyword in doc_content for keyword in config_keywords)
        assert config_found, "文档应该包含 Config 相关内容"

        print("✅ Config 目录文档生成测试通过!")

        return True

    except Exception as e:
        print(f"❌ Config 目录文档生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """主函数"""
    print("BMAD 集成测试套件")
    print("=" * 60)

    tests = [
        ("BMAD 编排器", test_bmad_orchestrator),
        ("Claude Code 和 BMAD 集成", test_claude_bmad_integration),
        ("Config 目录文档生成", test_config_documentation_generation)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n开始测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"测试 {test_name} 出现异常: {e}")
            results.append((test_name, False))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("🎉 所有测试通过!")
        return True
    else:
        print("⚠️  部分测试失败")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
