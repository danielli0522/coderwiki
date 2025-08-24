#!/usr/bin/env python3
"""
简单的调试版本技术架构文档生成器
在调用Claude Code SDK时设置断点
"""

import os
import sys
import json
import asyncio
import pdb
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class SimpleDebugGenerator:
    """简单的调试版本文档生成器"""

    def __init__(self):
        self.project_path = os.getcwd()
        self.bmad_path = "bmad-docs-generator"
        self.output_dir = Path(self.project_path) / "generated_docs"
        self.output_dir.mkdir(exist_ok=True)

        print("🐛 简单调试版本技术架构文档生成器")
        print(f"📁 项目路径: {self.project_path}")
        print(f"🔧 BMAD路径: {self.bmad_path}")

    async def generate_with_debug(self):
        """生成文档（带调试）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_title = f"CoderWiki_Debug_{timestamp}"

            print(f"\n📋 开始生成技术架构文档: {doc_title}")

            # 1. 验证BMAD文档生成器
            print("🔍 调试: 验证BMAD文档生成器...")
            if not self._validate_bmad_generator():
                return {'success': False, 'error': 'BMAD验证失败'}

            # 2. 准备BMAD调用指令
            print("🔍 调试: 准备BMAD调用指令...")
            bmad_instructions = self._prepare_bmad_instructions(doc_title)
            print(f"🔍 调试: BMAD指令长度: {len(bmad_instructions)} 字符")

            # 3. 构建系统提示词
            print("🔍 调试: 构建系统提示词...")
            system_prompt = self._build_system_prompt(bmad_instructions, doc_title)
            user_prompt = self._build_user_prompt()

            print("🔍 调试: 系统提示词长度:", len(system_prompt))
            print("🔍 调试: 用户提示词长度:", len(user_prompt))

            # 4. 关键断点位置 - 调用Claude Code SDK之前
            print("\n🔍 调试: 即将调用Claude Code SDK...")
            print("🔍 调试: 在这里设置断点，您可以检查以下变量:")
            print("  - system_prompt: 系统提示词")
            print("  - user_prompt: 用户提示词")
            print("  - bmad_instructions: BMAD指令")
            print("  - self.project_path: 项目路径")
            print("  - self.bmad_path: BMAD路径")
            print("\n🔍 调试: 按 'c' 继续执行，或使用其他pdb命令...")

            # 设置断点
            pdb.set_trace()

            # 5. 调用Claude Code SDK（模拟）
            print("🤖 调用Claude Code SDK...")
            result = await self._simulate_claude_call(system_prompt, user_prompt)

            if result['success']:
                # 6. 保存文档
                doc_filename = f"{doc_title}.md"
                doc_path = self.output_dir / doc_filename

                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])

                print(f"✅ 文档生成成功!")
                print(f"📄 文档路径: {doc_path}")

                return {
                    'success': True,
                    'doc_path': str(doc_path),
                    'content': result['content']
                }
            else:
                return result

        except Exception as e:
            print(f"❌ 生成文档时发生错误: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _validate_bmad_generator(self) -> bool:
        """验证BMAD文档生成器"""
        try:
            bmad_dir = Path(self.bmad_path)
            if not bmad_dir.exists():
                print(f"❌ BMAD文档生成器目录不存在: {self.bmad_path}")
                return False

            required_files = [
                "agent-teams/enhanced-docs-generation-team.yaml",
                "workflows/enhanced-docs-generation.yaml",
                "agents/code-analyst.md",
                "agents/tech-architect.md"
            ]

            for file_path in required_files:
                full_path = bmad_dir / file_path
                if not full_path.exists():
                    print(f"❌ 缺少必要文件: {file_path}")
                    return False

            print("✅ BMAD文档生成器验证通过")
            return True

        except Exception as e:
            print(f"❌ BMAD文档生成器验证失败: {str(e)}")
            return False

    def _prepare_bmad_instructions(self, doc_title: str) -> str:
        """准备BMAD调用指令"""
        return f"""
# BMAD文档生成器调用指令

## 项目信息
- 项目名称: CoderWiki
- 项目路径: {self.project_path}
- 文档标题: {doc_title}

## BMAD团队调用
请使用以下指令调用BMAD文档生成器团队：

### 1. 调用增强文档生成团队
```
/task {self.bmad_path}/agent-teams/enhanced-docs-generation-team.yaml
```

### 2. 查看工作流程配置
```
/read {self.bmad_path}/workflows/enhanced-docs-generation.yaml
```

### 3. 调用各个专业代理

#### 代码分析师
```
/task {self.bmad_path}/agents/code-analyst.md
```

#### 技术架构师
```
/task {self.bmad_path}/agents/tech-architect.md
```

#### 流程分析师
```
/task {self.bmad_path}/agents/flow-analyst.md
```

#### 问题解决者
```
/task {self.bmad_path}/agents/problem-solver.md
```

#### 文档工程师
```
/task {self.bmad_path}/agents/doc-engineer.md
```

## 分析要求

### 1. 代码库分析
- 扫描项目结构
- 识别技术栈
- 分析依赖关系
- 识别设计模式

### 2. 架构分析
- 系统整体架构
- 组件关系
- 数据流设计
- 接口设计

### 3. 文档生成
- 技术架构文档
- 系统设计文档
- 部署架构文档
- 安全架构文档

## 输出要求
- 使用Markdown格式
- 包含架构图
- 提供代码示例
- 包含最佳实践
- 使用中文编写
- 结构清晰完整

## 工作流程
1. 使用code-analyst扫描代码库
2. 使用tech-architect生成技术总览
3. 使用flow-analyst分析复杂流程
4. 使用problem-solver诊断潜在问题
5. 使用doc-engineer整合最终文档

请按照BMAD方法论进行深度分析，确保文档的专业性和完整性。
"""

    def _build_system_prompt(self, bmad_instructions: str, doc_title: str) -> str:
        """构建系统提示词"""
        return f"""你是一个专业的技术架构文档生成专家，专门负责生成高质量的技术架构文档。

你的任务是：
1. 分析CoderWiki项目的代码结构和架构设计
2. 理解项目的技术栈、设计模式和架构模式
3. 生成结构清晰、内容详实的技术架构文档
4. 使用中文编写，保持专业性和可读性
5. 包含架构图、代码示例和最佳实践建议

**重要：使用BMAD文档生成器作为子代理**
- BMAD文档生成器已添加到你的工作空间: {self.bmad_path}
- 你可以直接访问BMAD文档生成器的所有文件和配置
- 使用Task工具调用BMAD子代理团队和工作流程

**BMAD调用指令：**
{bmad_instructions}

**文档要求：**
- 使用Markdown格式
- 包含目录结构
- 提供详细的说明和示例
- 遵循技术文档的最佳实践
- 确保内容的准确性和完整性
- 包含BMAD方法的深度分析和模式识别
- 重点关注技术架构、系统设计、数据流、接口设计等方面

文档标题: {doc_title}
项目名称: CoderWiki"""

    def _build_user_prompt(self) -> str:
        """构建用户提示词"""
        return f"""请分析CoderWiki项目的技术架构，并生成一份全面的技术架构文档。

项目路径: {self.project_path}

请按照以下步骤进行：

1. **使用BMAD文档生成器团队**：
   - 调用 enhanced-docs-generation-team 团队
   - 让各个专业代理协作分析项目

2. **分析项目结构**：
   - 扫描代码库结构
   - 识别技术栈和框架
   - 分析架构模式

3. **生成技术架构文档**：
   - 系统整体架构
   - 组件关系图
   - 数据流设计
   - 接口设计
   - 部署架构
   - 安全架构

4. **包含以下内容**：
   - 执行摘要
   - 技术栈总览
   - 系统架构图
   - 组件详细说明
   - 数据模型
   - API设计
   - 部署方案
   - 性能考虑
   - 安全考虑
   - 扩展性设计

请使用BMAD方法论进行深度分析，确保文档的专业性和完整性。"""

    async def _simulate_claude_call(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """模拟Claude Code SDK调用"""
        try:
            print("📊 模拟BMAD团队协作分析...")
            print("🔍 代码分析师扫描代码库...")
            print("🏗️ 技术架构师分析系统架构...")
            print("🔄 流程分析师分析数据流...")
            print("🔧 问题解决者诊断潜在问题...")
            print("📝 文档工程师整合最终文档...")

            # 生成模拟的架构文档内容
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"""# CoderWiki 技术架构文档 - 调试版本

*生成时间: {timestamp}*
*使用BMAD文档生成器 + Claude Code SDK生成*

## 📋 执行摘要

CoderWiki是一个基于Flask的智能代码文档管理系统，集成了AI文档生成、代码分析、版本控制等功能。本文档采用BMAD方法论进行深度分析，详细描述了系统的技术架构、组件设计、数据流和部署方案。

## 🏗️ 系统整体架构

### 1. 架构概览

CoderWiki采用分层架构设计，主要包含以下层次：

- **表示层**: Flask Web应用，提供用户界面和API接口
- **业务逻辑层**: 核心业务服务，包括文档生成、代码分析、用户管理等
- **数据访问层**: 数据库访问和文件系统操作
- **外部服务层**: AI服务、Git服务、第三方API集成

### 2. 技术栈分析

**后端技术栈:**
- Python 3.8+
- Flask (Web框架)
- SQLAlchemy (ORM)
- SQLite/PostgreSQL (数据库)
- Redis (缓存)

**前端技术栈:**
- HTML5/CSS3/JavaScript
- Bootstrap (UI框架)
- jQuery (JavaScript库)

**AI服务集成:**
- Claude Code SDK
- BMAD文档生成器
- OpenAI API

**开发工具:**
- Git (版本控制)
- Docker (容器化)
- pytest (测试框架)

## 🔧 核心组件设计

### 1. 文档生成服务

```python
class DocumentGenerator:
    def __init__(self, bmad_docs_path: str):
        self.bmad_docs_path = bmad_docs_path
        self.claude_service = ClaudeCodeService()

    async def generate_technical_doc(self, repo_path: str, doc_type: str):
        # 使用BMAD文档生成器生成技术文档
        pass
```

### 2. 代码分析服务

```python
class CodeAnalyzer:
    def analyze_codebase(self, repo_path: str):
        # 分析代码库结构和依赖关系
        pass

    def identify_patterns(self, code_files: List[str]):
        # 识别设计模式和架构模式
        pass
```

### 3. 用户管理系统

```python
class UserManager:
    def authenticate_user(self, credentials: Dict):
        # 用户认证
        pass

    def manage_permissions(self, user_id: str, permissions: List[str]):
        # 权限管理
        pass
```

## 📊 数据模型设计

### 1. 用户模型

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 项目模型

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    repo_path VARCHAR(255),
    owner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

### 3. 文档模型

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    doc_type VARCHAR(50),
    project_id INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

## 🔌 API设计

### 1. 文档生成API

```
POST /api/documents/generate
Content-Type: application/json

{{
    "project_id": 1,
    "doc_type": "technical_architecture",
    "options": {{
        "include_diagrams": true,
        "comprehensive": true
    }}
}}
```

### 2. 代码分析API

```
GET /api/projects/{{project_id}}/analysis
Authorization: Bearer {{token}}

Response:
{{
    "code_structure": {{...}},
    "dependencies": {{...}},
    "patterns": {{...}}
}}
```

### 3. 用户管理API

```
POST /api/auth/login
Content-Type: application/json

{{
    "username": "user@example.com",
    "password": "password"
}}
```

## 🚀 部署架构

### 1. 开发环境

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Flask)       │◄──►│   (Flask)       │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. 生产环境

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Gunicorn      │    │   PostgreSQL    │
│   (Load Balancer)│◄──►│   (WSGI Server) │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis         │
                       │   (Cache)       │
                       └─────────────────┘
```

## 🔒 安全架构

### 1. 认证与授权

- JWT Token认证
- 基于角色的访问控制(RBAC)
- 密码加密存储(BCrypt)

### 2. 数据安全

- SQL注入防护
- XSS攻击防护
- CSRF保护
- 输入验证和清理

### 3. 网络安全

- HTTPS强制
- 安全头部设置
- 请求频率限制
- 日志监控

## 📈 性能优化

### 1. 数据库优化

- 索引优化
- 查询优化
- 连接池管理

### 2. 缓存策略

- Redis缓存
- 页面缓存
- API响应缓存

### 3. 异步处理

- 文档生成异步化
- 代码分析异步化
- 邮件发送异步化

## 🔄 扩展性设计

### 1. 水平扩展

- 无状态服务设计
- 负载均衡
- 数据库读写分离

### 2. 微服务化

- 服务拆分
- API网关
- 服务发现

### 3. 容器化部署

- Docker容器化
- Kubernetes编排
- 自动化部署

## 🧠 BMAD方法论分析

### 1. 代码分析结果

通过BMAD代码分析师的分析，发现以下关键特征：
- 模块化设计良好
- 依赖关系清晰
- 代码结构规范

### 2. 架构模式识别

通过BMAD技术架构师的分析，识别出以下架构模式：
- 分层架构模式
- MVC设计模式
- 依赖注入模式

### 3. 流程分析结果

通过BMAD流程分析师的分析，发现以下数据流：
- 用户认证流程
- 文档生成流程
- 代码分析流程

### 4. 问题诊断结果

通过BMAD问题解决者的分析，发现以下潜在问题：
- 性能优化空间
- 安全加固建议
- 扩展性改进点

## 📝 总结

CoderWiki采用现代化的技术架构，具有良好的可扩展性、安全性和性能。通过BMAD文档生成器的集成，系统能够自动生成高质量的技术文档，大大提高了开发效率。

### 关键特性

- ✅ 分层架构设计
- ✅ 模块化组件
- ✅ 安全认证机制
- ✅ 性能优化
- ✅ 容器化部署
- ✅ AI文档生成
- ✅ 代码分析能力

### 技术亮点

- 🔧 BMAD方法论集成
- 🤖 Claude Code SDK集成
- 📊 智能文档生成
- 🔍 代码模式识别
- 🚀 现代化部署方案

### BMAD分析优势

- 🧠 深度代码分析
- 🏗️ 架构模式识别
- 🔄 流程优化建议
- 🔧 问题诊断能力
- 📝 专业文档生成

---

*本文档由BMAD文档生成器 + Claude Code SDK自动生成*
"""

            return {
                'success': True,
                'content': content
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"模拟调用失败: {str(e)}"
            }

async def main():
    """主函数"""
    print("🐛 简单调试版本技术架构文档生成器")
    print("=" * 60)

    # 初始化生成器
    generator = SimpleDebugGenerator()

    # 生成技术架构文档
    result = await generator.generate_with_debug()

    if result['success']:
        print(f"\n✅ 技术架构文档生成成功!")
        print(f"📄 文档路径: {result['doc_path']}")

        # 显示文档内容预览
        content = result['content']
        preview_lines = content.split('\n')[:30]
        print(f"\n📖 文档预览 (前30行):")
        print("-" * 60)
        for line in preview_lines:
            print(line)
        if len(content.split('\n')) > 30:
            print("...")
    else:
        print(f"❌ 文档生成失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
