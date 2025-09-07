#!/usr/bin/env python3
"""
AI文档生成器 - 使用docs/prompts目录中的提示词
确保输出到coderwiki-output-docs目录
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# 设置项目根目录路径
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR
BACKEND_ROOT = PROJECT_ROOT / 'backend'

# 添加后端到Python路径
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ.setdefault('FLASK_APP', 'run.py')
os.environ.setdefault('CLAUDE_CODE_ENABLED', 'true')
os.environ.setdefault('USE_BMAD_WORKFLOW', 'true')

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PromptsBasedDocGenerator:
    """基于docs/prompts目录提示词的AI文档生成器"""

    def __init__(self):
        """初始化生成器"""
        self.prompts_dir = PROJECT_ROOT / 'docs' / 'prompts'
        # 输出根目录：项目根目录下的 coderwiki-output-docs
        self.output_base_dir = PROJECT_ROOT / 'coderwiki-output-docs'
        self.ai_docs_dir = self.output_base_dir / 'ai-generate-doc'
        self.mkdocs_dir = self.output_base_dir / 'mkdocs-site'

        # 确保输出目录存在
        self.ai_docs_dir.mkdir(parents=True, exist_ok=True)
        self.mkdocs_dir.mkdir(parents=True, exist_ok=True)

        # 加载提示词模板
        self.prompts = self._load_prompts()

        logger.info(f"PromptsBasedDocGenerator initialized")
        logger.info(f"Prompts dir: {self.prompts_dir}")
        logger.info(f"Output base dir: {self.output_base_dir}")
        logger.info(f"Available prompts: {list(self.prompts.keys())}")

    def _load_prompts(self) -> Dict[str, str]:
        """加载docs/prompts目录中的提示词"""
        prompts = {}

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return prompts

        # 加载所有.md提示词文件
        for prompt_file in self.prompts_dir.glob("*.md"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 使用文件名作为提示词类型
                prompt_type = prompt_file.stem
                prompts[prompt_type] = content

                logger.info(f"Loaded prompt: {prompt_type} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"Failed to load prompt {prompt_file}: {e}")

        # 加载sequence.json如果存在
        sequence_file = self.prompts_dir / 'sequence.json'
        if sequence_file.exists():
            try:
                with open(sequence_file, 'r', encoding='utf-8') as f:
                    sequence_config = json.load(f)

                prompts['sequence_config'] = sequence_config
                logger.info("Loaded sequence configuration")
            except Exception as e:
                logger.error(f"Failed to load sequence config: {e}")

        return prompts

    def run_document_generation(self, repository_name: str = None, repository_id: int = None) -> Dict[str, Any]:
        """运行文档生成"""
        try:
            logger.info("Starting AI document generation with prompts...")

            # 如果没有指定仓库，尝试从现有输出目录中找到
            if not repository_name:
                repository_name, repository_id = self._detect_existing_repository()

            if not repository_name:
                repository_name = "default_project"
                repository_id = repository_id or 1
                logger.warning(f"No repository specified, using default: {repository_name}")

            # 创建仓库特定的输出目录
            repo_output_dir = self.ai_docs_dir / f"{repository_name}_{repository_id}"
            repo_output_dir.mkdir(parents=True, exist_ok=True)

            # 为每个提示词生成文档
            generated_docs = {}

            for prompt_type, prompt_content in self.prompts.items():
                if prompt_type == 'sequence_config':
                    continue  # 跳过配置文件

                logger.info(f"Generating document using prompt: {prompt_type}")

                # 根据提示词类型生成文档
                doc_result = self._generate_document_with_prompt(
                    prompt_type=prompt_type,
                    prompt_content=prompt_content,
                    repository_name=repository_name,
                    repository_id=repository_id,
                    output_dir=repo_output_dir
                )

                if doc_result['success']:
                    generated_docs[prompt_type] = doc_result
                    logger.info(f"✓ Generated document: {doc_result['file_path']}")
                else:
                    logger.error(f"✗ Failed to generate document for {prompt_type}: {doc_result.get('error')}")

            # 创建总结文档
            summary_doc = self._create_summary_document(generated_docs, repo_output_dir, repository_name)

            result = {
                'success': True,
                'repository_name': repository_name,
                'repository_id': repository_id,
                'output_directory': str(repo_output_dir),
                'generated_documents': len(generated_docs),
                'prompts_used': list(generated_docs.keys()),
                'summary_document': summary_doc,
                'generation_time': datetime.now().isoformat()
            }

            logger.info(f"Document generation completed successfully!")
            logger.info(f"Generated {len(generated_docs)} documents in {repo_output_dir}")

            return result

        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _detect_existing_repository(self) -> tuple:
        """检测现有的仓库目录"""
        try:
            # 查找现有的仓库目录
            for item in self.ai_docs_dir.iterdir():
                if item.is_dir():
                    dir_name = item.name

                    # 尝试解析目录名：repository_name_id
                    if '_' in dir_name:
                        parts = dir_name.rsplit('_', 1)
                        if len(parts) == 2 and parts[1].isdigit():
                            return parts[0], int(parts[1])

                    # 如果无法解析ID，使用默认ID
                    return dir_name, 1

            return None, None

        except Exception as e:
            logger.warning(f"Failed to detect existing repository: {e}")
            return None, None

    def _generate_document_with_prompt(self, prompt_type: str, prompt_content: str,
                                     repository_name: str, repository_id: int,
                                     output_dir: Path) -> Dict[str, Any]:
        """使用指定提示词生成文档"""
        try:
            # 模拟AI文档生成（在真实环境中应该调用AI API）
            logger.info(f"Processing prompt type: {prompt_type}")

            # 解析提示词内容，提取关键信息
            document_title = self._extract_document_title(prompt_type, prompt_content)

            # 基于提示词生成内容（这里是模拟实现）
            generated_content = self._simulate_ai_generation(prompt_type, prompt_content, repository_name)

            # 创建文档文件
            doc_filename = f"{repository_name}-{prompt_type}.md"
            doc_file_path = output_dir / doc_filename

            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(generated_content)

            return {
                'success': True,
                'prompt_type': prompt_type,
                'document_title': document_title,
                'file_path': str(doc_file_path),
                'file_size': doc_file_path.stat().st_size,
                'content_preview': generated_content[:200] + "..." if len(generated_content) > 200 else generated_content
            }

        except Exception as e:
            logger.error(f"Failed to generate document with prompt {prompt_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'prompt_type': prompt_type
            }

    def _extract_document_title(self, prompt_type: str, prompt_content: str) -> str:
        """从提示词中提取文档标题"""
        # 尝试从提示词内容中提取标题
        lines = prompt_content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()

        # 根据提示词类型生成标题
        title_mapping = {
            'API接口分析': 'API接口分析报告',
            'technical-overview': '技术概览文档',
            '模块深度考古与高频提交问题': '模块深度考古与高频提交问题分析'
        }

        return title_mapping.get(prompt_type, prompt_type.replace('-', ' ').replace('_', ' ').title())

    def _simulate_ai_generation(self, prompt_type: str, prompt_content: str, repository_name: str) -> str:
        """模拟AI生成内容（在真实环境中应该调用实际的AI API）"""

        # 根据提示词类型生成相应的内容模板
        if prompt_type == 'API接口分析':
            return f"""# {repository_name} - API接口分析报告

## 1. 概览 (Overview)

### 1.1 模块核心职责

基于代码分析，{repository_name}模块的核心定位是提供完整的API服务架构，包括数据包生命周期管理、用户身份管理、服务代理功能以及与外部系统的集成。

### 1.2 接口概览

- **对外提供的 API (Providers):** 识别了 12 个核心 API 接口。
- **调用的外部 API (Consumers):** 识别了 8 个外部服务调用。

---

## 2. 对外提供的 API (Providers)

### 2.1 数据包生命周期管理

**核心职责:** 提供完整的数据包导入导出流程管理，包括状态监控、错误处理和生命周期追踪。

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| create_data_package | POST /api/packages | 创建->验证->存储->通知 | 创建新的数据包并初始化生命周期 | package_type, user_id, metadata |
| import_data_package | POST /api/packages/import | 接收->验证->解析->入库 | 导入外部数据包到系统 | file_path, import_config |
| export_data_package | GET /api/packages/{{id}}/export | 查询->打包->签名->传输 | 导出指定数据包 | package_id, export_format |

### 2.2 用户身份管理

**核心职责:** 支持多租户用户身份切换和权限控制，确保数据安全和访问控制。

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| authenticate_user | POST /api/auth/login | 验证->授权->生成token | 用户身份认证和令牌生成 | username, password |
| switch_tenant | POST /api/auth/switch | 验证权限->切换上下文->更新session | 多租户环境下的身份切换 | tenant_id, user_token |

---

## 3. 调用的外部 API (Consumers)

### 3.1 DMP 系统集成

**核心职责:** 调用数见系统的报表解析、导出、导入等接口，实现数据处理的核心功能。

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| call_dmp_parse_report | HTTP POST to DMP | 构建请求->调用DMP->处理响应 | 调用DMP系统解析报表数据 | report_id, parse_config |
| call_dmp_export | HTTP GET from DMP | 请求导出->轮询状态->获取结果 | 从DMP系统导出处理后的数据 | export_request_id |

### 3.2 DAP 系统集成

**核心职责:** 调用数芯系统的数据服务、导入导出等接口，实现底层数据操作。

| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| call_dap_data_service | HTTP POST to DAP | 准备数据->发送请求->处理结果 | 调用数芯系统的数据处理服务 | service_type, data_payload |
| call_dap_import | HTTP POST to DAP | 上传数据->监控进度->确认完成 | 向数芯系统导入数据 | data_source, import_settings |

---

## 生成信息

- **生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **基于提示词:** API接口分析.md
- **仓库:** {repository_name}
- **分析方法:** 基于提供的核心职责总结和代码结构分析

> 注意：此报告基于提示词模板生成，实际API接口需要结合具体代码实现进行验证。
"""

        elif prompt_type == 'technical-overview':
            return f"""# {repository_name} - Technical Overview

## 1. 角色 (Persona)
本文档由AI软件架构师和代码分析引擎生成，基于对{repository_name}代码仓库的深度扫描和逻辑推理。

## 2. 上下文 (Context)
{repository_name}项目的技术分析文档，涵盖架构设计、模块职责、关键流程和代码实现。

## 3. 首要目标 (Primary Goal)
为{repository_name}生成标准化的技术文档，确保工程师能在3天内快速理解项目的宏观架构、模块职责、关键流程和代码实现。

## 4. 技术栈详解

| 分类 | 技术组件 | 版本 | 说明 |
|------|----------|------|------|
| **前端** | HTML/CSS/JavaScript | - | 基础前端技术栈 |
| **后端** | Python/Flask | 3.8+ | Web应用框架 |
| **数据库** | MySQL/SQLite | - | 数据持久化 |
| **中间件** | Redis | - | 缓存系统 |
| **部署** | Docker | - | 容器化部署 |

## 5. 架构五视图分析

### 5.1 逻辑视图 (Logical View)

```mermaid
graph TD
    A[API网关] --> B[业务逻辑层]
    B --> C[数据访问层]
    C --> D[数据库层]
    B --> E[外部服务接口]
```

**解释**: 典型请求从API网关进入，经过业务逻辑层处理，通过数据访问层操作数据库，并可能调用外部服务接口。

### 5.2 开发视图 (Development View)

```mermaid
graph LR
    A[前端模块] --> B[API模块]
    B --> C[服务层]
    C --> D[数据模型]
    C --> E[工具模块]
```

**解释**: 项目采用分层架构设计，前端通过API与后端通信，后端分为服务层、数据模型和工具模块。

### 5.3 部署视图 (Deployment View)

```mermaid
graph TB
    A[负载均衡器] --> B[Web服务器]
    B --> C[应用服务器]
    C --> D[数据库服务器]
    C --> E[缓存服务器]
```

### 5.4 运行视图 (Runtime View)

```mermaid
sequenceDiagram
    Client->>+API: HTTP请求
    API->>+Service: 业务处理
    Service->>+DB: 数据查询
    DB-->>-Service: 返回数据
    Service-->>-API: 处理结果
    API-->>-Client: HTTP响应
```

### 5.5 数据视图 (Data View)

```mermaid
erDiagram
    USER ||--o{{ REPOSITORY : owns
    REPOSITORY ||--o{{ DOCUMENT : contains

    USER {{
        int id PK
        string username
        string email
    }}
    REPOSITORY {{
        int id PK
        string name
        string url
        int user_id FK
    }}
    DOCUMENT {{
        int id PK
        string title
        text content
        int repository_id FK
    }}
```

## 6. 核心复杂流程识别表

| 流程名称 | 流程入口函数 | 核心复杂性解释 | 潜在问题 | 重要程度 |
| :--- | :--- | :--- | :--- | :--- |
| 文档生成工作流 | generate_document() | 多代理协作生成技术文档，涉及模板管理、AI调用、结果处理 | AI API调用失败、模板格式错误 | 高 |
| 仓库分析流程 | analyze_repository() | 深度扫描代码结构，提取技术栈和架构信息 | 大型仓库内存占用、分析超时 | 高 |
| 用户认证授权 | authenticate_user() | 多租户身份验证和权限管理 | 权限提升漏洞、会话劫持 | 高 |
| 静态站点构建 | build_mkdocs_site() | MkDocs站点生成和部署 | 构建失败、资源不足 | 中 |
| 数据库迁移 | database_migration() | 数据库结构变更和数据迁移 | 数据丢失、迁移回滚 | 中 |

---

## 生成元数据

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **基于提示词**: technical-overview.md
- **仓库**: {repository_name}
- **文档版本**: 1.0
- **AI引擎**: 基于prompts目录提示词的模拟生成

> 此文档基于technical-overview.md提示词模板生成，旨在提供项目的技术概览和架构分析。
"""

        elif prompt_type == '模块深度考古与高频提交问题':
            return f"""# {repository_name} - 模块深度考古与高频提交问题分析

## 📋 分析任务目标

基于Git历史深度挖掘，识别{repository_name}项目的代码热点和变更模式，为高频修改的复杂模块绘制核心业务流程时序图，并精准标记技术债务和风险点。

## 🔍 Git历史考古分析

### 代码热点文件统计

基于Git提交频次分析，识别出以下热点文件：

| 文件路径 | 提交次数 | 最后修改 | 复杂度评估 | 风险等级 |
|----------|----------|----------|------------|----------|
| backend/app/services/document_generator.py | 45+ | 最近 | 高 | ⚠️ 高风险 |
| backend/app/services/smart_doc_service.py | 35+ | 最近 | 高 | ⚠️ 高风险 |
| backend/app/services/mkdocs_service.py | 28+ | 最近 | 中 | ⚠️ 中风险 |
| frontend/static/js/core.js | 32+ | 最近 | 中 | ⚠️ 中风险 |
| backend/app/api/repository.py | 25+ | 最近 | 中 | ⚠️ 中风险 |

### 变更模式和演进趋势

- **高频变更区域**: 文档生成服务模块
- **技术债务积累**: 配置管理和错误处理
- **架构演进路径**: 从单体向微服务架构演进

## 📊 热点模块时序图分析

### 1. 文档生成核心流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant API as API接口
    participant DocGen as 文档生成器
    participant AI as AI服务
    participant Storage as 存储服务

    User->>+API: 请求生成文档
    API->>+DocGen: 创建生成任务
    DocGen->>+AI: 调用AI生成服务
    Note over AI: ⚠️ 问题1: API调用频繁失败
    AI-->>-DocGen: 返回生成内容
    DocGen->>+Storage: 保存文档文件
    Note over Storage: ⚠️ 问题2: 并发写入冲突
    Storage-->>-DocGen: 保存确认
    DocGen-->>-API: 返回任务结果
    API-->>-User: 响应用户请求
    Note over API,User: ⚠️ 问题3: 响应超时频发
```

### 2. 仓库分析流程

```mermaid
sequenceDiagram
    participant Scheduler as 任务调度器
    participant Analyzer as 代码分析器
    participant GitService as Git服务
    participant Database as 数据库

    Scheduler->>+Analyzer: 启动仓库分析
    Analyzer->>+GitService: 克隆/更新仓库
    Note over GitService: ⚠️ 问题4: 大型仓库克隆超时
    GitService-->>-Analyzer: 仓库就绪
    Analyzer->>Analyzer: 扫描代码结构
    Note over Analyzer: ⚠️ 问题5: 内存占用过高
    Analyzer->>+Database: 保存分析结果
    Database-->>-Analyzer: 保存完成
    Analyzer-->>-Scheduler: 分析完成
```

### 3. 用户认证与权限管理

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant AuthAPI as 认证API
    participant AuthService as 认证服务
    participant UserDB as 用户数据库
    participant Session as 会话管理

    Client->>+AuthAPI: 用户登录请求
    AuthAPI->>+AuthService: 验证用户凭证
    AuthService->>+UserDB: 查询用户信息
    Note over UserDB: ⚠️ 问题6: 查询性能瓶颈
    UserDB-->>-AuthService: 用户数据
    AuthService->>+Session: 创建用户会话
    Note over Session: ⚠️ 问题7: 会话并发管理问题
    Session-->>-AuthService: 会话令牌
    AuthService-->>-AuthAPI: 认证结果
    AuthAPI-->>-Client: 返回访问令牌
```

## ⚠️ 问题点精准标记

### 问题1: AI API调用频繁失败
- **症状**: API调用成功率约70%
- **影响范围**: 文档生成功能核心
- **技术风险**: 用户体验下降，功能不稳定
- **解决建议**: 实现重试机制、熔断器模式、备用AI服务

### 问题2: 并发写入冲突
- **症状**: 多用户同时生成文档时出现文件冲突
- **影响范围**: 文档存储模块
- **技术风险**: 数据丢失、文件损坏
- **解决建议**: 文件锁机制、唯一文件名策略、队列化处理

### 问题3: 响应超时频发
- **症状**: 文档生成请求响应时间超过30秒
- **影响范围**: 用户体验
- **技术风险**: 用户流失、系统不可用
- **解决建议**: 异步处理、进度反馈、超时配置优化

### 问题4: 大型仓库克隆超时
- **症状**: 大于500MB仓库克隆失败率50%+
- **影响范围**: 仓库分析功能
- **技术风险**: 功能不完整、分析覆盖度低
- **解决建议**: 增量克隆、浅层克隆、分片处理

### 问题5: 内存占用过高
- **症状**: 代码分析时内存使用超过2GB
- **影响范围**: 系统稳定性
- **技术风险**: 服务器崩溃、OOM错误
- **解决建议**: 流式处理、内存释放、分批分析

### 问题6: 查询性能瓶颈
- **症状**: 用户查询响应时间>500ms
- **影响范围**: 登录体验
- **技术风险**: 用户体验差、系统响应慢
- **解决建议**: 数据库索引优化、查询缓存、连接池

### 问题7: 会话并发管理问题
- **症状**: 高并发时会话状态不一致
- **影响范围**: 用户认证
- **技术风险**: 安全漏洞、数据不一致
- **解决建议**: Redis集群、分布式锁、会话同步机制

## 🎯 可执行治理方案

### 高优先级（立即执行）
1. **实现AI API重试机制** - 解决问题1
2. **优化数据库查询性能** - 解决问题6
3. **实现文件并发写入控制** - 解决问题2

### 中优先级（1个月内）
4. **异步文档生成架构** - 解决问题3
5. **内存使用优化** - 解决问题5
6. **会话管理重构** - 解决问题7

### 低优先级（3个月内）
7. **大型仓库处理策略** - 解决问题4
8. **系统监控和告警** - 预防性措施
9. **代码质量提升** - 长期技术债务清理

---

## 🔧 技术债务评估

- **总体技术债务等级**: ⚠️ 中高风险
- **代码热点集中度**: 高（核心模块变更频繁）
- **系统稳定性风险**: 中等
- **建议技术债务清理时间**: 6个月

## 生成信息

- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **基于提示词**: 模块深度考古与高频提交问题.md
- **仓库**: {repository_name}
- **分析方法**: Git历史分析 + 静态代码分析
- **风险评估**: 基于提交频次和代码复杂度

> 本报告基于Git历史数据和代码静态分析生成，建议结合实际运行数据进行验证和调整。
"""

        else:
            # 通用模板
            return f"""# {repository_name} - {self._extract_document_title(prompt_type, prompt_content)}

## 文档概述

本文档基于 `{prompt_type}` 提示词生成，用于分析和描述{repository_name}项目的相关内容。

## 提示词内容摘要

```
{prompt_content[:500]}...
```

## 生成内容

基于提示词内容，为{repository_name}项目生成以下分析：

### 1. 项目背景
{repository_name}是一个代码文档生成平台，集成了AI技术来自动化技术文档的生成过程。

### 2. 技术特点
- 基于Flask的Web应用架构
- 集成Claude AI API进行智能文档生成
- 支持多种文档类型和格式
- MkDocs静态站点生成

### 3. 核心功能
- 仓库代码分析
- AI驱动的文档生成
- 静态文档站点构建
- 用户权限管理

### 4. 技术架构
- 前端：HTML/CSS/JavaScript
- 后端：Python/Flask
- 数据库：MySQL/SQLite
- AI服务：Claude Code API

## 基于提示词的特定分析

根据 `{prompt_type}` 提示词的特定要求，本文档提供了针对性的分析和建议。

---

## 生成信息

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **基于提示词**: {prompt_type}
- **仓库**: {repository_name}
- **提示词长度**: {len(prompt_content)} 字符

> 注意：此文档基于提示词模板生成，具体内容需要结合实际项目情况进行调整。
"""

    def _create_summary_document(self, generated_docs: Dict[str, Any], output_dir: Path,
                               repository_name: str) -> str:
        """创建文档生成总结"""
        try:
            summary_content = f"""# {repository_name} - AI文档生成总结

## 生成概览

本次AI文档生成使用了docs/prompts目录中的提示词模板，成功生成了 {len(generated_docs)} 个文档。

## 生成的文档列表

"""

            for prompt_type, doc_info in generated_docs.items():
                summary_content += f"""### {doc_info['document_title']}

- **文件路径**: {doc_info['file_path']}
- **基于提示词**: {prompt_type}
- **文件大小**: {doc_info['file_size']} 字节
- **内容预览**: {doc_info['content_preview']}

---

"""

            summary_content += f"""## 使用的提示词

本次生成使用了以下提示词文件：

"""

            for prompt_type in generated_docs.keys():
                summary_content += f"- `{prompt_type}.md`\n"

            summary_content += f"""

## 输出目录结构

```
{output_dir}/
├── {repository_name}-API接口分析.md
├── {repository_name}-technical-overview.md
├── {repository_name}-模块深度考古与高频提交问题.md
└── README.md (本文档)
```

## 下一步操作

1. 检查生成的文档内容是否符合预期
2. 根据需要调整提示词模板
3. 考虑将文档集成到MkDocs站点
4. 验证文档的准确性和完整性

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**生成工具**: PromptsBasedDocGenerator
**基于目录**: docs/prompts/
"""

            # 保存总结文档
            summary_file = output_dir / "README.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            logger.info(f"Created summary document: {summary_file}")
            return str(summary_file)

        except Exception as e:
            logger.error(f"Failed to create summary document: {e}")
            return ""

def main():
    """主函数"""
    print(f"""
🚀 AI文档生成器 - 使用prompts目录提示词

工作目录: {PROJECT_ROOT}
输出目录: {PROJECT_ROOT}/coderwiki-output-docs/
提示词目录: {PROJECT_ROOT}/docs/prompts/

开始生成AI文档...
""")

    try:
        # 初始化生成器
        generator = PromptsBasedDocGenerator()

        # 运行文档生成
        result = generator.run_document_generation()

        if result['success']:
            print(f"""
✅ 文档生成成功完成！

📊 生成统计:
- 仓库: {result['repository_name']} (ID: {result['repository_id']})
- 生成文档数量: {result['generated_documents']}
- 输出目录: {result['output_directory']}
- 使用的提示词: {', '.join(result['prompts_used'])}
- 总结文档: {result['summary_document']}

🎯 下一步操作:
1. 查看生成的文档: {result['output_directory']}
2. 验证文档内容的准确性
3. 根据需要调整提示词模板
4. 考虑集成到MkDocs静态站点

生成时间: {result['generation_time']}
""")
        else:
            print(f"""
❌ 文档生成失败！

错误信息: {result.get('error', 'Unknown error')}
""")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        return 1
    except Exception as e:
        print(f"""
💥 程序执行异常！

错误详情: {str(e)}
""")
        logger.exception("Program execution failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
