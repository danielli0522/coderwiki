# BMAD 代理协作流程图

## 代理团队协作流程图

```mermaid
flowchart TD
    Start([开始BMAD代理协作]) --> Init[初始化代理团队]
    Init --> Config[加载代理配置]
    Config --> Session[创建Claude Code会话]
    Session --> Upload[上传代码库]

    Upload --> Alex[代码分析师Alex启动]
    Alex --> AlexWork[执行代码分析任务]
    AlexWork --> AlexOutput[生成代码分析报告]
    AlexOutput --> AlexComplete{分析完成?}
    AlexComplete -->|否| AlexRetry[重试代码分析]
    AlexRetry --> AlexWork
    AlexComplete -->|是| Arch[架构分析师启动]

    Arch --> ArchWork[执行架构分析任务]
    ArchWork --> ArchOutput[生成架构分析报告]
    ArchOutput --> ArchComplete{分析完成?}
    ArchComplete -->|否| ArchRetry[重试架构分析]
    ArchRetry --> ArchWork
    ArchComplete -->|是| Jordan[流程分析师Jordan启动]

    Jordan --> JordanWork[执行流程分析任务]
    JordanWork --> JordanOutput[生成流程分析报告]
    JordanOutput --> JordanComplete{分析完成?}
    JordanComplete -->|否| JordanRetry[重试流程分析]
    JordanRetry --> JordanWork
    JordanComplete -->|是| Morgan[问题解决专家Dr. Morgan启动]

    Morgan --> MorganWork[执行问题诊断任务]
    MorganWork --> MorganOutput[生成问题诊断报告]
    MorganOutput --> MorganComplete{诊断完成?}
    MorganComplete -->|否| MorganRetry[重试问题诊断]
    MorganRetry --> MorganWork
    MorganComplete -->|是| Maya[文档工程师Maya启动]

    Maya --> MayaWork[执行文档生成任务]
    MayaWork --> MayaOutput[生成最终技术文档]
    MayaOutput --> MayaComplete{文档生成完成?}
    MayaComplete -->|否| MayaRetry[重试文档生成]
    MayaRetry --> MayaWork
    MayaComplete -->|是| Aggregate[聚合所有代理结果]

    Aggregate --> Validate[质量验证]
    Validate --> QualityCheck{质量检查通过?}
    QualityCheck -->|否| MayaRefine[Maya优化文档]
    MayaRefine --> Validate
    QualityCheck -->|是| Final[生成最终文档]
    Final --> End([BMAD协作完成])

    %% 代理间数据流
    AlexOutput -.->|代码分析数据| Arch
    ArchOutput -.->|架构分析数据| Jordan
    JordanOutput -.->|流程分析数据| Morgan
    MorganOutput -.->|问题诊断数据| Maya
    AlexOutput -.->|代码分析数据| Maya
    ArchOutput -.->|架构分析数据| Maya
    JordanOutput -.->|流程分析数据| Maya
```

## 详细代理工作流程

### 1. 代码分析师 Alex (Alex)

```mermaid
flowchart LR
    A1[开始代码分析] --> A2[扫描代码库结构]
    A2 --> A3[识别文件类型和数量]
    A3 --> A4[分析技术栈]
    A4 --> A5[识别依赖关系]
    A5 --> A6[分析代码复杂度]
    A6 --> A7[识别设计模式]
    A7 --> A8[生成代码质量报告]
    A8 --> A9[输出代码分析结果]

    A9 --> A10{分析质量检查}
    A10 -->|不通过| A11[补充分析]
    A11 --> A9
    A10 -->|通过| A12[传递给架构分析师]
```

**具体工作内容:**

- 扫描整个代码库的文件结构
- 识别使用的编程语言和框架
- 分析第三方依赖和版本
- 计算代码复杂度和质量指标
- 识别代码中的设计模式
- 生成详细的代码分析报告

### 2. 架构分析师 (Architecture Analyst)

```mermaid
flowchart LR
    B1[接收代码分析数据] --> B2[分析系统架构]
    B2 --> B3[识别架构模式]
    B3 --> B4[分析组件关系]
    B4 --> B5[评估架构质量]
    B5 --> B6[识别架构问题]
    B6 --> B7[生成架构建议]
    B7 --> B8[输出架构分析结果]

    B8 --> B9{架构分析质量检查}
    B9 -->|不通过| B10[补充架构分析]
    B10 --> B8
    B9 -->|通过| B11[传递给流程分析师]
```

**具体工作内容:**

- 基于代码分析结果分析系统架构
- 识别使用的架构模式（MVC、微服务、分层等）
- 分析组件间的依赖关系
- 评估架构的可扩展性和可维护性
- 识别潜在的架构问题
- 生成架构优化建议

### 3. 流程分析师 Jordan (Jordan)

```mermaid
flowchart LR
    C1[接收架构分析数据] --> C2[分析业务流程]
    C2 --> C3[识别关键流程]
    C3 --> C4[创建序列图]
    C4 --> C5[分析数据流]
    C5 --> C6[识别业务规则]
    C6 --> C7[生成流程文档]
    C7 --> C8[输出流程分析结果]

    C8 --> C9{流程分析质量检查}
    C9 -->|不通过| C10[补充流程分析]
    C10 --> C8
    C9 -->|通过| C11[传递给问题解决专家]
```

**具体工作内容:**

- 分析系统的业务流程和用户交互
- 识别关键的业务流程和决策点
- 创建详细的序列图和流程图
- 分析数据在系统中的流动
- 识别业务规则和约束条件
- 生成流程分析文档

### 4. 问题解决专家 Dr. Morgan (Dr. Morgan)

```mermaid
flowchart LR
    D1[接收流程分析数据] --> D2[诊断潜在问题]
    D2 --> D3[识别风险点]
    D3 --> D4[分析故障场景]
    D4 --> D5[生成解决方案]
    D5 --> D6[创建故障排除指南]
    D6 --> D7[输出问题诊断结果]

    D7 --> D8{问题诊断质量检查}
    D8 -->|不通过| D9[补充问题诊断]
    D9 --> D7
    D8 -->|通过| D10[传递给文档工程师]
```

**具体工作内容:**

- 基于前面的分析结果诊断潜在问题
- 识别系统的风险点和薄弱环节
- 分析可能的故障场景和影响
- 生成针对性的解决方案
- 创建详细的故障排除指南
- 提供系统优化建议

### 5. 文档工程师 Maya (Maya)

```mermaid
flowchart LR
    E1[接收所有分析数据] --> E2[整合分析结果]
    E2 --> E3[应用文档模板]
    E3 --> E4[生成技术文档]
    E4 --> E5[添加图表和说明]
    E5 --> E6[进行质量验证]
    E6 --> E7[输出最终文档]

    E7 --> E8{文档质量检查}
    E8 -->|不通过| E9[优化文档内容]
    E9 --> E6
    E8 -->|通过| E10[完成文档生成]
```

**具体工作内容:**

- 整合所有代理的分析结果
- 应用统一的文档模板和格式
- 生成结构化的技术文档
- 添加必要的图表、代码示例和说明
- 进行文档的完整性和准确性验证
- 优化文档的可读性和专业性

## 代理协作机制

### 1. 数据传递机制

- **顺序传递**: 每个代理完成后将结果传递给下一个代理
- **并行处理**: 某些分析任务可以并行执行
- **数据聚合**: 最终由 Maya 聚合所有代理的结果

### 2. 质量保证机制

- **自检**: 每个代理对自己的输出进行质量检查
- **互检**: 后续代理可以验证前面代理的结果
- **终检**: Maya 进行最终的文档质量验证

### 3. 错误处理机制

- **重试机制**: 代理执行失败时自动重试
- **降级处理**: 部分代理失败时继续执行其他代理
- **结果标记**: 在最终文档中标记缺失的分析部分

### 4. 进度监控机制

- **实时更新**: 每个代理完成后更新进度
- **状态跟踪**: 跟踪每个代理的执行状态
- **异常报告**: 及时报告代理执行异常

## 输出文档结构

基于 BMAD 代理协作生成的最终文档包含以下部分：

1. **项目概述**

   - 项目基本信息
   - 技术栈总结
   - 系统架构概览

2. **代码分析报告** (Alex 提供)

   - 代码库结构分析
   - 技术栈详细分析
   - 代码质量评估

3. **架构分析报告** (架构分析师提供)

   - 系统架构设计
   - 组件关系分析
   - 架构质量评估

4. **流程分析报告** (Jordan 提供)

   - 业务流程分析
   - 系统交互流程
   - 数据流分析

5. **问题诊断报告** (Dr. Morgan 提供)

   - 潜在问题识别
   - 风险评估
   - 解决方案建议

6. **技术文档** (Maya 整合)
   - 完整的系统文档
   - 部署指南
   - 维护指南

这个协作流程确保了生成的文档具有全面性、准确性和专业性，每个代理都专注于自己的专业领域，通过协作产生高质量的最终文档。
