# 代码文档自动生成系统 - 系统架构设计

## 1. 项目概述

### 1.1 项目目标

构建一个轻量级的代码文档自动生成系统，让开发团队能够自主、按需地为代码仓库生成技术设计文档。

### 1.2 技术约束

- 架构：单体架构
- 数据库：MySQL
- 后端：Python
- 前端：简单 HTML/JavaScript
- 支持 10 人同时在线

## 2. 系统架构 - 五视图设计

### 2.1 逻辑视图 (Logical View)

#### 2.1.1 核心模块划分

```
代码文档自动生成系统
├── 用户管理模块 (User Management)
│   ├── 用户认证
│   ├── 用户注册
│   └── 会话管理
├── 仓库管理模块 (Repository Management)
│   ├── 仓库添加/删除
│   ├── 仓库信息同步
│   └── 仓库状态监控
├── 智能文档生成模块 (Intelligent Document Generation)
│   ├── Claude Code SDK集成器
│   ├── BMAD代理编排引擎
│   └── 文档结果处理器
├── 任务管理模块 (Task Management)
│   ├── 任务调度
│   ├── 进度跟踪
│   └── 错误处理
├── 文档管理模块 (Document Management)
│   ├── 版本控制
│   ├── 文档存储
│   └── 文档检索
└── 前端展示模块 (Frontend Display)
    ├── 页面路由
    ├── 用户界面
    └── 交互处理
```

#### 2.1.2 模块间依赖关系

- 用户管理模块 → 仓库管理模块
- 仓库管理模块 → 任务管理模块
- 任务管理模块 → 智能文档生成模块
- 智能文档生成模块 → 文档管理模块
- 所有模块 → 数据库访问层

### 2.2 开发视图 (Development View)

#### 2.2.1 项目结构

```
coderwiki/
├── backend/                    # 后端应用
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置文件
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── repository.py
│   │   │   ├── document.py
│   │   │   └── task.py
│   │   ├── services/           # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── repo_service.py
│   │   │   ├── doc_service.py
│   │   │   ├── task_service.py
│   │   │   └── claude_service.py  # Claude Code集成服务
│   │   ├── api/                # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── repository.py
│   │   │   ├── document.py
│   │   │   └── task.py
│   │   ├── utils/              # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── git_utils.py
│   │   │   ├── claude_client.py    # Claude Code客户端
│   │   │   ├── bmad_orchestrator.py # BMAD代理编排器
│   │   │   └── doc_formatter.py
│   │   └── static/             # 静态文件
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   ├── migrations/             # 数据库迁移
│   ├── tests/                  # 测试文件
│   ├── requirements.txt        # 依赖包
│   └── run.py                  # 启动文件
├── frontend/                   # 前端文件
│   ├── templates/              # HTML模板
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── repository.html
│   │   └── document.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── dashboard.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── dashboard.js
│   │       └── document.js
├── bmad-docs-generator/        # BMAD文档生成器
│   ├── agents/                 # 代理定义
│   │   ├── code-analyst.md     # 代码分析师 (Alex)
│   │   ├── architecture-analyst.md # 架构分析师
│   │   ├── flow-analyst.md     # 流程分析师 (Jordan)
│   │   ├── problem-solver.md   # 问题解决专家 (Dr. Morgan)
│   │   ├── doc-engineer.md     # 文档工程师 (Maya)
│   │   ├── tech-architect.md   # 技术架构师 (空)
│   │   ├── pattern-recognition-expert.md # 模式识别专家 (空)
│   │   ├── tech-stack-expert.md # 技术栈专家 (空)
│   │   ├── code-analyzer.md    # 代码分析器 (空)
│   │   └── sre-engineer.md     # SRE工程师 (空)
│   ├── agent-teams/            # 代理团队配置
│   │   └── enhanced-docs-generation-team.yaml
│   ├── workflows/              # 工作流定义
│   │   └── enhanced-docs-generation.yaml
│   ├── tasks/                  # 任务定义
│   ├── templates/              # 文档模板
│   ├── checklists/             # 质量检查清单
│   └── config.yaml             # 配置文件
├── database/                   # 数据库相关
│   ├── schema.sql              # 数据库结构
│   └── init_data.sql           # 初始数据
├── docs/                       # 项目文档
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── config/                     # 配置文件
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── scripts/                    # 脚本文件
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
└── README.md
```

#### 2.2.2 技术栈选择

- **Web 框架**: Flask (轻量级，易于部署)
- **ORM**: SQLAlchemy (数据库操作)
- **数据库**: MySQL 8.0 (稳定可靠)
- **前端**: Bootstrap + jQuery (快速开发)
- **Claude Code 集成**: Anthropic Claude Code SDK
- **BMAD 代理系统**: 自定义代理编排引擎
- **任务队列**: Python threading (简单任务处理)
- **认证**: Flask-Login (会话管理)

### 2.3 进程视图 (Process View)

#### 2.3.1 系统进程架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │   Worker Pool   │    │   Claude Code   │
│   (Flask App)   │    │                 │    │   Orchestrator  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Main Thread │ │    │ │ Worker 1    │ │    │ │ Claude Code │ │
│ │             │ │    │ │             │ │    │ │ SDK Client  │ │
│ │ - HTTP Req  │ │    │ │ - Doc Gen   │ │    │ │             │ │
│ │ - Auth      │ │    │ │ - BMAD      │ │    │ │ - Session   │ │
│ │ - Static    │ │    │ │ Orchestrator│ │    │ │ - Request   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Background  │ │    │ │ Worker 2    │ │    │ │ BMAD Agent  │ │
│ │             │ │    │ │             │ │    │ │ Orchestrator│ │
│ │ - Task Mon  │ │    │ │ - Doc Gen   │ │    │ │             │ │
│ │ - Clean Up  │ │    │ │ - BMAD      │ │    │ │ - Agent 1   │ │
│ │ - Health    │ │    │ │ Orchestrator│ │    │ │ - Agent 2   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ MySQL       │ │
                    │ │             │ │
                    │ │ - Users     │ │
                    │ │ - Repos     │ │
                    │ │ - Docs      │ │
                    │ │ - Tasks     │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

#### 2.3.2 关键流程时序

**智能文档生成流程:**

```
用户 → 点击生成 → API请求 → 创建任务 → Claude Code SDK → 初始化会话 → 配置BMAD代理 → 上传代码 → 启动编排引擎 → 执行代理工作流 → 聚合结果 → 保存文档 → 更新状态 → 通知用户
```

**BMAD 代理工作流:**

```
代码分析师(Alex) → 架构分析师 → 流程分析师(Jordan) → 问题解决专家(Dr. Morgan) → 文档工程师(Maya) → 质量检查 → 最终文档
```

### 2.4 物理视图 (Physical View)

#### 2.4.1 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Server                              │
│                  (Single Instance)                         │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Nginx        │  │   Flask App     │  │   Worker    │ │
│  │                 │  │                 │  │             │ │
│  │ - Static Files │  │ - API Routes    │  │ - Task Proc  │ │
│  │ - Reverse Proxy│  │ - Auth          │  │ - Background │ │
│  │ - SSL Terminate│  │ - Business Logic│  │ - Monitoring │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Database Server                        │
│                  (MySQL 8.0)                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 MySQL Instance                         │ │
│  │                                                         │ │
│  │  - coderwiki_db                                         │ │
│  │  ├── users                                              │ │
│  │  ├── repositories                                       │ │
│  │  ├── documents                                          │ │
│  │  └── tasks                                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  External Services                          │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   GitHub API    │  │   Claude Code   │  │   BMAD      │ │
│  │                 │  │   API           │  │   Agents    │ │
│  │ - Repo Clone    │  │                 │  │             │ │
│  │ - Info Fetch    │  │ - Session Mgmt  │  │ - Code      │ │
│  │ - Webhook       │  │ - Agent Exec    │  │   Analyst   │ │
│  │                 │  │ - Result Agg    │  │ - Arch      │ │
│  │                 │  │                 │  │   Analyst   │ │
│  │                 │  │                 │  │ - Flow      │ │
│  │                 │  │                 │  │   Analyst   │ │
│  │                 │  │                 │  │ - Problem   │ │
│  │                 │  │                 │  │   Solver    │ │
│  │                 │  │                 │  │ - Doc       │ │
│  │                 │  │                 │  │   Engineer  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 2.4.2 硬件需求

- **服务器**: 1 台虚拟机 (2 核 4G 内存)
- **存储**: 50GB SSD (代码仓库临时存储)
- **数据库**: 20GB (文档数据存储)
- **网络**: 10Mbps 带宽
- **操作系统**: Ubuntu 20.04 LTS

### 2.5 场景视图 (Scenarios View)

#### 2.5.1 关键使用场景

**场景 1: 用户首次使用智能文档生成系统**

```
1. 用户访问系统首页
2. 系统重定向到登录页面
3. 用户注册新账户
4. 系统创建用户记录
5. 用户登录成功
6. 系统显示仓库管理页面
7. 用户添加第一个GitHub仓库
8. 系统验证并克隆仓库
9. 用户点击"智能生成文档"按钮
10. 系统创建Claude Code会话
11. 系统配置BMAD代理团队
12. 系统上传代码到Claude Code
13. 启动BMAD代理编排引擎
14. 执行5个核心代理的工作流
15. 系统聚合所有代理结果
16. 生成高质量技术文档
17. 用户查看生成的文档
```

**场景 2: BMAD 代理协作生成文档**

```
1. 用户触发文档生成
2. Claude Code SDK初始化会话
3. 配置BMAD代理团队
4. 代码分析师(Alex)开始工作
   - 扫描代码库结构
   - 识别技术栈
   - 分析依赖关系
   - 生成代码分析报告
5. 架构分析师开始工作
   - 分析系统架构
   - 识别设计模式
   - 评估架构质量
   - 生成架构分析报告
6. 流程分析师(Jordan)开始工作
   - 分析复杂业务流程
   - 创建序列图
   - 识别关键流程
   - 生成流程分析报告
7. 问题解决专家(Dr. Morgan)开始工作
   - 诊断潜在问题
   - 预测故障点
   - 生成解决方案
   - 创建故障排除指南
8. 文档工程师(Maya)开始工作
   - 整合所有分析结果
   - 应用文档模板
   - 生成最终文档
   - 质量验证
9. 系统保存生成的文档
10. 通知用户生成完成
```

**场景 3: 多用户并发使用智能生成**

```
1. 用户A同时生成文档X
2. 用户B同时生成文档Y
3. 用户C添加新仓库Z
4. 系统为每个用户创建独立的Claude Code会话
5. 每个会话配置独立的BMAD代理团队
6. 代理团队并行执行工作流
7. 系统监控所有会话状态
8. 各用户独立获得生成结果
9. 系统保持稳定响应
```

#### 2.5.2 异常处理场景

**场景 4: Claude Code API 调用失败**

```
1. 系统调用Claude Code API
2. API返回错误响应
3. 系统捕获异常并记录
4. 系统重试API调用(最多3次)
5. 如果仍然失败，标记任务失败
6. 保存错误信息到数据库
7. 通知用户生成失败
8. 提供重试选项
```

**场景 5: BMAD 代理执行失败**

```
1. 系统启动BMAD代理工作流
2. 某个代理执行失败
3. 系统记录失败原因
4. 系统尝试重新执行该代理
5. 如果重试失败，跳过该代理
6. 继续执行后续代理
7. 在最终文档中标记缺失部分
8. 通知用户部分生成失败
```

## 3. BMAD 代理系统详细设计

### 3.1 核心代理架构

#### 3.1.1 代理团队配置

```yaml
team:
  id: enhanced-docs-generation-team
  name: Enhanced Documentation Generation Team
  description: Advanced team for generating comprehensive technical documentation using BMAD-Method framework
  version: "1.0.0"

  agents:
    - id: code-analyst
      name: "Code Analyst (Alex)"
      role: "Senior Code Analyst & Architecture Detective"
      capabilities:
        - "Deep codebase scanning"
        - "Pattern recognition"
        - "Technology stack analysis"
        - "Dependency mapping"
        - "Complex flow identification"
      primary_tasks:
        - "scan-codebase"
        - "validate-analysis"

    - id: architecture-analyst
      name: "Architecture Analyst"
      role: "Software Architecture Specialist"
      capabilities:
        - "Architecture pattern recognition"
        - "Component relationship analysis"
        - "Quality assessment"
        - "Scalability evaluation"
      primary_tasks:
        - "create-architecture-views"
        - "generate-technical-overview"

    - id: flow-analyst
      name: "Flow Analyst (Jordan)"
      role: "Business Flow & Process Analyst"
      capabilities:
        - "Complex flow analysis"
        - "Sequence diagram creation"
        - "Process documentation"
        - "Business rule extraction"
      primary_tasks:
        - "analyze-complex-flows"
        - "validate-flow-analysis"

    - id: problem-solver
      name: "Problem Solver (Dr. Morgan)"
      role: "Site Reliability Engineer & Problem Diagnostician"
      capabilities:
        - "Problem prediction"
        - "Root cause analysis"
        - "Solution development"
        - "Troubleshooting documentation"
      primary_tasks:
        - "diagnose-potential-problems"
        - "validate-problem-diagnosis"

    - id: doc-engineer
      name: "Doc Engineer (Maya)"
      role: "Technical Documentation Engineer & Content Architect"
      capabilities:
        - "Documentation creation"
        - "Content formatting"
        - "Quality assurance"
        - "Visual enhancement"
      primary_tasks:
        - "generate-flow-analysis-doc"
        - "generate-problem-diagnosis-doc"
        - "final-quality-validation"
```

#### 3.1.2 工作流编排

```yaml
workflow:
  id: enhanced-docs-generation
  name: Enhanced Documentation Generation
  version: 2.0

  phases:
    - name: initialization
      description: Initialize the documentation generation process
      tasks:
        - id: setup-project-context
          name: Setup Project Context
          agent: doc-engineer

    - name: code-analysis
      description: Analyze the codebase structure and patterns
      tasks:
        - id: scan-codebase
          name: Scan Codebase
          agent: code-analyst

        - id: analyze-dependencies
          name: Analyze Dependencies
          agent: code-analyst

        - id: identify-patterns
          name: Identify Patterns
          agent: architecture-analyst

    - name: architecture-analysis
      description: Perform comprehensive architecture analysis
      tasks:
        - id: analyze-architecture
          name: Analyze Architecture
          agent: architecture-analyst

        - id: identify-arch-patterns
          name: Identify Architectural Patterns
          agent: architecture-analyst

        - id: assess-tech-stack
          name: Assess Technology Stack
          agent: code-analyst

    - name: flow-analysis
      description: Analyze complex business flows
      tasks:
        - id: analyze-complex-flows
          name: Analyze Complex Flows
          agent: flow-analyst

        - id: create-sequence-diagrams
          name: Create Sequence Diagrams
          agent: flow-analyst

    - name: problem-diagnosis
      description: Diagnose potential problems
      tasks:
        - id: diagnose-potential-problems
          name: Diagnose Potential Problems
          agent: problem-solver

        - id: create-solution-matrix
          name: Create Solution Matrix
          agent: problem-solver

    - name: documentation-generation
      description: Generate comprehensive documentation
      tasks:
        - id: generate-arch-documentation
          name: Generate Architecture Documentation
          agent: doc-engineer

        - id: create-architecture-diagrams
          name: Create Architecture Diagrams
          agent: doc-engineer

        - id: generate-enhanced-sequence-diagrams
          name: Generate Enhanced Sequence Diagrams
          agent: flow-analyst

        - id: validate-documentation
          name: Validate Documentation
          agent: doc-engineer

    - name: finalization
      description: Finalize documentation and generate reports
      tasks:
        - id: assemble-final-documentation
          name: Assemble Final Documentation
          agent: doc-engineer

        - id: generate-executive-summary
          name: Generate Executive Summary
          agent: doc-engineer
```

### 3.2 Claude Code SDK 集成设计

#### 3.2.1 SDK 客户端实现

```python
class ClaudeCodeClient:
    def __init__(self, api_key, workspace_id):
        self.client = anthropic.Client(api_key)
        self.workspace_id = workspace_id
        self.session = None

    def create_session(self):
        """创建Claude Code会话"""
        self.session = self.client.beta.workspaces.sessions.create(
            workspace_id=self.workspace_id
        )
        return self.session

    def configure_bmad_agents(self, session_id, config):
        """配置BMAD代理团队"""
        # 上传代理配置文件
        self.client.beta.workspaces.sessions.files.create(
            session_id=session_id,
            file_path="bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml"
        )

        # 上传工作流配置
        self.client.beta.workspaces.sessions.files.create(
            session_id=session_id,
            file_path="bmad-docs-generator/workflows/enhanced-docs-generation.yaml"
        )

    def upload_codebase(self, session_id, repo_path):
        """上传代码库到Claude Code"""
        # 递归上传代码文件
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if self._should_upload_file(file):
                    file_path = os.path.join(root, file)
                    self.client.beta.workspaces.sessions.files.create(
                        session_id=session_id,
                        file_path=file_path
                    )

    def trigger_bmad_workflow(self, session_id):
        """触发BMAD工作流执行"""
        message = self.client.beta.workspaces.sessions.messages.create(
            session_id=session_id,
            content="Execute the enhanced-docs-generation workflow with BMAD agents"
        )
        return message

    def get_workflow_results(self, session_id):
        """获取工作流执行结果"""
        messages = self.client.beta.workspaces.sessions.messages.list(
            session_id=session_id
        )
        return messages
```

#### 3.2.2 BMAD 代理编排器

```python
class BMADOrchestrator:
    def __init__(self, claude_client):
        self.claude_client = claude_client
        self.agents = {
            'code-analyst': 'Alex',
            'architecture-analyst': 'Architecture Analyst',
            'flow-analyst': 'Jordan',
            'problem-solver': 'Dr. Morgan',
            'doc-engineer': 'Maya'
        }

    def execute_workflow(self, repo_path, config):
        """执行完整的BMAD工作流"""
        # 1. 创建Claude Code会话
        session = self.claude_client.create_session()

        # 2. 配置BMAD代理
        self.claude_client.configure_bmad_agents(session.id, config)

        # 3. 上传代码库
        self.claude_client.upload_codebase(session.id, repo_path)

        # 4. 触发工作流
        message = self.claude_client.trigger_bmad_workflow(session.id)

        # 5. 监控执行进度
        results = self._monitor_execution(session.id)

        # 6. 聚合结果
        final_document = self._aggregate_results(results)

        return final_document

    def _monitor_execution(self, session_id):
        """监控工作流执行进度"""
        max_wait_time = 300  # 5分钟超时
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            messages = self.claude_client.get_workflow_results(session_id)

            # 检查是否完成
            if self._is_workflow_complete(messages):
                return messages

            time.sleep(10)  # 每10秒检查一次

        raise TimeoutError("BMAD workflow execution timeout")

    def _aggregate_results(self, messages):
        """聚合所有代理的结果"""
        # 解析各个代理的输出
        code_analysis = self._extract_agent_output(messages, 'code-analyst')
        arch_analysis = self._extract_agent_output(messages, 'architecture-analyst')
        flow_analysis = self._extract_agent_output(messages, 'flow-analyst')
        problem_analysis = self._extract_agent_output(messages, 'problem-solver')
        final_doc = self._extract_agent_output(messages, 'doc-engineer')

        # 组合成最终文档
        return {
            'code_analysis': code_analysis,
            'architecture_analysis': arch_analysis,
            'flow_analysis': flow_analysis,
            'problem_analysis': problem_analysis,
            'final_documentation': final_doc
        }
```

## 4. 数据模型设计

### 4.1 用户表 (users)

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 4.2 仓库表 (repositories)

```sql
CREATE TABLE repositories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description TEXT,
    status ENUM('active', 'error', 'processing') DEFAULT 'active',
    last_analysis TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 4.3 文档表 (documents)

```sql
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    repository_id INT NOT NULL,
    version INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    doc_type ENUM('technical_overview', 'architecture_analysis', 'flow_analysis', 'problem_diagnosis', 'complete_documentation') NOT NULL,
    claude_session_id VARCHAR(255),
    bmad_workflow_id VARCHAR(255),
    status ENUM('draft', 'published', 'archived') DEFAULT 'published',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
```

### 4.4 任务表 (tasks)

```sql
CREATE TABLE tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    repository_id INT NOT NULL,
    type ENUM('analysis', 'generation', 'update') NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    progress INT DEFAULT 0,
    claude_session_id VARCHAR(255),
    bmad_workflow_id VARCHAR(255),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
```

### 4.5 BMAD 代理执行记录表 (bmad_agent_executions)

```sql
CREATE TABLE bmad_agent_executions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    agent_role VARCHAR(255) NOT NULL,
    execution_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    start_time TIMESTAMP NULL,
    end_time TIMESTAMP NULL,
    output_content LONGTEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

## 5. 接口设计

### 5.1 用户认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息

### 5.2 仓库管理接口

- `GET /api/repositories` - 获取仓库列表
- `POST /api/repositories` - 添加仓库
- `GET /api/repositories/{id}` - 获取仓库详情
- `DELETE /api/repositories/{id}` - 删除仓库
- `POST /api/repositories/{id}/sync` - 同步仓库信息

### 5.3 智能文档生成接口

- `POST /api/repositories/{id}/generate-smart-doc` - 启动智能文档生成
- `GET /api/repositories/{id}/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情
- `GET /api/tasks/{id}/status` - 获取任务状态
- `GET /api/tasks/{id}/bmad-agents` - 获取 BMAD 代理执行状态

### 5.4 Claude Code 集成接口

- `POST /api/claude/sessions` - 创建 Claude Code 会话
- `GET /api/claude/sessions/{id}/status` - 获取会话状态
- `POST /api/claude/sessions/{id}/upload-code` - 上传代码到会话
- `POST /api/claude/sessions/{id}/trigger-bmad` - 触发 BMAD 工作流

### 5.5 系统监控接口

- `GET /api/system/health` - 系统健康检查
- `GET /api/system/stats` - 系统统计信息
- `GET /api/system/bmad-agents` - BMAD 代理状态

## 6. 安全设计

### 6.1 认证安全

- 使用 bcrypt 进行密码哈希
- JWT Token 进行会话管理
- Token 过期时间控制

### 6.2 数据安全

- SQL 注入防护
- XSS 攻击防护
- CSRF 防护
- 敏感数据加密存储

### 6.3 访问控制

- 基于用户 ID 的数据隔离
- API 访问频率限制
- 输入参数验证

### 6.4 Claude Code 安全

- API 密钥安全存储
- 会话隔离
- 代码上传权限控制

## 7. 性能优化

### 7.1 数据库优化

- 合理的索引设计
- 查询优化
- 连接池管理

### 7.2 缓存策略

- Redis 缓存热点数据
- 静态资源 CDN 加速
- 浏览器缓存控制

### 7.3 并发处理

- 异步任务处理
- 数据库连接池
- 请求限流机制

### 7.4 Claude Code 优化

- 会话复用
- 批量文件上传
- 结果缓存

## 8. 监控和日志

### 8.1 系统监控

- 服务器资源监控
- 应用性能监控
- 数据库性能监控

### 8.2 日志管理

- 结构化日志记录
- 日志分级管理
- 错误日志追踪

### 8.3 告警机制

- 系统异常告警
- 任务失败告警
- 性能阈值告警

### 8.4 BMAD 代理监控

- 代理执行状态监控
- 工作流进度跟踪
- 代理性能分析
