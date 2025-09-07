# 任务：生成带概览的分类化模块 API 分析报告

**重要：这是一个自动化执行任务。项目名称是 `{project_name}`，项目路径是 `{repository_path}`，请直接开始分析该项目的 API 并生成分析报告，无需等待任何输入或确认。**

## 一、背景 (Background)

你是一位顶级的软件架构师，精通代码审查和系统设计。你的核心任务是深入分析位于 **`{repository_path}`** 目录下的源代码，该项目名为 **`{project_name}`**。

你的首要任务是理解我提供的 **“核心职责总结”**，并以此为基础，深入分析源代码，生成一份包含**概览总结**和**详细分类**的 API 分析报告，并严格按照指定的 Markdown 格式输出。

## 二、核心职责总结 (Core Responsibilities Summary)

[ **重要提示**：本提示词是领域无关模板。分类采用“可配置 + 自动归类”的双模式来分析 API，适配任何项目。]

- 分类策略:

  1. 若提供可选的 `{category_profile}`（YAML/JSON，见下），严格按配置分类与输出。
  2. 若未提供 `{category_profile}`，则自动基于代码结构与依赖进行归类：
     - **提供者职责 (Providers):**
       - 认证与授权 (Authentication & Authorization)
       - 数据读写与查询 (CRUD & Query)
       - 文件与对象存储 (File & Object Storage)
       - 任务/作业与异步处理 (Jobs/Tasks & Background Processing)
       - 观测性与健康检查 (Observability & Health)
       - 配置与特性开关 (Configuration & Feature Flags)
       - 实时通信/推送 (Realtime/WebSocket)
     - **调用者职责 (Consumers):**
       - 数据库/ORM 客户端 (Databases/ORM)
       - 缓存服务 (Redis/Memory Cache)
       - 消息队列/事件流 (MQ/Streaming)
       - 对象存储/文件服务 (Object Storage)
       - 外部 HTTP/SDK 服务 (External Services)
       - 身份提供商/认证服务 (IdP/OAuth/SAML)
       - 云服务 SDK (Cloud SDKs)

- 可选 `{category_profile}` 示例（YAML）：
  ```yaml
  providers:
    - name: "数据读写与查询"
      match:
        - path_regex: "(controllers|views|routers|api)"
        - symbol_regex: "(create|update|delete|list|get|query)"
    - name: "文件与对象存储"
      match:
        - import_regex: "(boto3|oss2|@aws-sdk|google.cloud.storage)"
  consumers:
    - name: "外部 HTTP/SDK 服务"
      match:
        - import_regex: "(requests|axios|httpx|fetch)"
        - url_regex: "https?://"
  ```

## 三、任务指令 (Mission)

请基于上述总结和下方提供的源代码，分步执行以下分析任务：

1.  **初步分析与计数 (Initial Analysis & Counting):**

    - 首先，全面扫描所有代码，识别出所有的“提供者 API”和“调用者 API”。
    - 分别统计出“提供者”和“调用者”的总 API 数量。

2.  **生成概览报告 (Generate Overview Report):**

    - 根据“分类策略”，简要重述模块核心职责与分类依据（说明使用了 `{category_profile}` 还是自动归类）。
    - 使用上一步的统计结果，生成接口概览，明确指出识别出的提供者和调用者 API 的数量。

3.  **生成详细分类报告 (Generate Detailed Classified Report):**
    - **API 提供者分析 (Providers Analysis):** 按照已确定的提供者分类（来自 `{category_profile}` 或自动归类）输出，每类提供职责描述与 API 表格。
    - **API 调用者分析 (Consumers Analysis):** 按照已确定的调用者分类输出，每类提供职责描述与调用点表格。

## 四、最终输出要求 (Final Output Requirement)

将所有分析结果整合到一个名为 **`[YOUR_PROJECT_NAME]-api接口分析报告.md`** 的 Markdown 文件中。文件内容必须严格遵循以下结构（分类按实际识别结果动态生成）：

```markdown
# API 分析报告: [YOUR_PROJECT_NAME]

## 1. 概览 (Overview)

### 1.1 模块核心职责

[AI 根据“核心职责总结”和代码分析，在此处总结模块的核心定位与职责]

### 1.2 接口概览

- **对外提供的 API (Providers):** 识别了 [AI 填充数量] 个核心 API 接口。
- **调用的外部 API (Consumers):** 识别了 [AI 填充数量] 个外部服务调用。

---

## 2. 对外提供的 API (Providers)

<!-- 对每一个识别到的“提供者分类”生成一个小节，如下所示，按重要性排序 -->

### 2.x [提供者分类名称]

**核心职责:** [AI 填充该分类的职责描述]
| 函数名称 (Function Name) | 函数路由 (API Route) | 核心流程 (Process Flow) | 核心职责 (Core Responsibility) | 必传关键参数 (Key Required Parameters) |
| :--- | :--- | :--- | :--- | :--- |
| _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ |

... [其余提供者分类依次展开] ...

<br>

## 3. 调用的外部 API (Consumers)

<!-- 对每一个识别到的“调用者分类”生成一个小节，如下所示，按重要性排序 -->

### 3.x [调用者分类名称]

**核心职责:** [AI 填充该分类的职责描述]
| 调用位置 (Call Site) | 被调服务/库 (Service/SDK) | 调用方式 (HTTP/SDK) | 核心流程 (Process Flow) | 关键参数 (Key Params) |
| :--- | :--- | :--- | :--- | :--- |
| _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ | _[AI 填充]_ |

... [其余调用者分类依次展开] ...
```
