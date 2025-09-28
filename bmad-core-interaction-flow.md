# .bmad-core 人机交互流程图

## 1. 整体交互架构图

```mermaid
graph TB
    subgraph "用户交互层"
        U[用户] --> UI[用户界面]
        UI --> CMD[命令输入]
        CMD --> ORCH[BMAD Orchestrator]
    end
    
    subgraph "代理编排层"
        ORCH --> AM[代理管理器]
        ORCH --> WE[工作流引擎]
        ORCH --> RA[结果聚合器]
    end
    
    subgraph "代理执行层"
        AM --> CA[Code Analyst<br/>Alex]
        AM --> TA[Tech Architect<br/>Sarah]
        AM --> FA[Flow Analyst<br/>Jordan]
        AM --> PS[Problem Solver<br/>Dr. Morgan]
        AM --> DE[Doc Engineer<br/>Maya]
    end
    
    subgraph "资源管理层"
        WE --> TASKS[任务定义]
        WE --> TEMPLATES[文档模板]
        WE --> CHECKLISTS[质量检查清单]
        WE --> DATA[知识库数据]
    end
    
    subgraph "产物输出层"
        RA --> DOC1[技术总览文档]
        RA --> DOC2[复杂流程分析]
        RA --> DOC3[问题诊断方案]
        RA --> KB[知识库更新]
    end
    
    style U fill:#e1f5fe
    style ORCH fill:#fff3e0
    style CA fill:#f3e5f5
    style TA fill:#f3e5f5
    style FA fill:#f3e5f5
    style PS fill:#f3e5f5
    style DE fill:#f3e5f5
```

## 2. 详细工作流程时序图

```mermaid
sequenceDiagram
    participant U as 用户
    participant O as BMAD Orchestrator
    participant CA as Code Analyst
    participant TA as Tech Architect
    participant FA as Flow Analyst
    participant PS as Problem Solver
    participant DE as Doc Engineer
    
    U->>O: 启动文档生成请求
    Note over U,O: 输入: 项目信息、分析深度(1-9)、输出格式
    
    O->>CA: 激活代码分析任务
    Note over O,CA: 传递: 项目上下文、代码库位置
    
    CA->>CA: 深度代码扫描
    CA->>CA: 技术栈识别
    CA->>CA: 复杂流程发现
    CA->>CA: 架构模式分析
    
    CA->>O: 返回分析报告
    Note over CA,O: 输出: codebase-analysis-report.md
    
    O->>U: 展示分析结果
    U->>O: 确认分析质量
    
    O->>TA: 激活架构设计任务
    Note over O,TA: 传递: 分析报告、技术栈清单
    
    TA->>TA: 创建五视图架构
    TA->>TA: 生成技术总览
    TA->>TA: 创建架构图表
    
    TA->>O: 返回技术总览
    Note over TA,O: 输出: 项目名-Technical-Overview.md
    
    O->>U: 展示技术总览
    U->>O: 确认架构设计
    
    O->>FA: 激活流程分析任务
    Note over O,FA: 传递: 技术总览、复杂流程列表
    
    FA->>FA: 分析复杂流程
    FA->>FA: 创建增强时序图
    FA->>FA: 提取业务规则
    
    FA->>O: 返回流程分析
    Note over FA,O: 输出: 项目名-Complex-Flow-Analysis.md
    
    O->>U: 展示流程分析
    U->>O: 确认流程分析
    
    O->>PS: 激活问题诊断任务
    Note over O,PS: 传递: 流程分析、架构分析
    
    PS->>PS: 预测潜在问题
    PS->>PS: 创建解决方案矩阵
    PS->>PS: 制定诊断指南
    
    PS->>O: 返回问题诊断
    Note over PS,O: 输出: 项目名-Problem-Diagnosis-Solution.md
    
    O->>U: 展示问题诊断
    U->>O: 确认诊断方案
    
    O->>DE: 激活文档工程任务
    Note over O,DE: 传递: 所有分析结果
    
    DE->>DE: 组装最终文档
    DE->>DE: 质量验证
    DE->>DE: 知识库更新
    
    DE->>O: 返回最终文档包
    Note over DE,O: 输出: 完整文档包
    
    O->>U: 交付最终成果
    Note over U,O: 完成: 3天内理解项目的完整文档
```

## 3. 代理切换与上下文传递图

```mermaid
graph LR
    subgraph "代理切换流程"
        A[Code Analyst] -->|分析报告| B[Tech Architect]
        B -->|技术总览| C[Flow Analyst]
        C -->|流程分析| D[Problem Solver]
        D -->|问题诊断| E[Doc Engineer]
    end
    
    subgraph "上下文传递内容"
        F[项目上下文] --> A
        F --> B
        F --> C
        F --> D
        F --> E
        
        G[用户偏好] --> A
        G --> B
        G --> C
        G --> D
        G --> E
        
        H[质量要求] --> A
        H --> B
        H --> C
        H --> D
        H --> E
    end
    
    subgraph "产物传递链"
        I[代码库分析报告] --> J[技术总览文档]
        J --> K[复杂流程分析]
        K --> L[问题诊断方案]
        L --> M[最终文档包]
    end
    
    style A fill:#f3e5f5
    style B fill:#f3e5f5
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#f3e5f5
```

## 4. 质量门控与用户确认点

```mermaid
graph TD
    A[开始工作流] --> B[代码库分析]
    B --> C{质量门控1<br/>分析完整性}
    C -->|通过| D[用户确认1<br/>分析结果]
    C -->|失败| B
    
    D --> E[架构设计]
    E --> F{质量门控2<br/>架构视图}
    F -->|通过| G[用户确认2<br/>技术总览]
    F -->|失败| E
    
    G --> H[流程分析]
    H --> I{质量门控3<br/>流程分析}
    I -->|通过| J[用户确认3<br/>流程分析]
    I -->|失败| H
    
    J --> K[问题诊断]
    K --> L{质量门控4<br/>问题诊断}
    L -->|通过| M[用户确认4<br/>诊断方案]
    L -->|失败| K
    
    M --> N[文档工程]
    N --> O{质量门控5<br/>最终质量}
    O -->|通过| P[完成交付]
    O -->|失败| N
    
    style C fill:#ffeb3b
    style F fill:#ffeb3b
    style I fill:#ffeb3b
    style L fill:#ffeb3b
    style O fill:#ffeb3b
    style D fill:#4caf50
    style G fill:#4caf50
    style J fill:#4caf50
    style M fill:#4caf50
    style P fill:#2196f3
```

## 5. 交互式验证机制图

```mermaid
graph TB
    subgraph "用户交互选项"
        A[分析深度选择<br/>1-9级别] --> B[概览模式<br/>1-3]
        A --> C[详细模式<br/>4-6]
        A --> D[深度模式<br/>7-9]
    end
    
    subgraph "阶段性确认"
        E[阶段1完成] --> F[展示结果]
        F --> G[用户反馈]
        G --> H{确认通过?}
        H -->|是| I[继续下一阶段]
        H -->|否| J[调整分析方向]
        J --> E
    end
    
    subgraph "反馈循环"
        K[用户建议] --> L[分析调整]
        L --> M[重新分析]
        M --> N[更新结果]
        N --> O[再次确认]
    end
    
    style A fill:#e1f5fe
    style H fill:#fff3e0
    style K fill:#f3e5f5
```

## 6. 产物依赖关系图

```mermaid
graph TD
    A[项目输入] --> B[代码库分析报告]
    B --> C[技术总览文档]
    C --> D[复杂流程分析]
    D --> E[问题诊断方案]
    E --> F[最终文档包]
    
    subgraph "中间产物"
        G[技术栈清单]
        H[架构模式分析]
        I[依赖关系图]
        J[复杂流程列表]
        K[五视图架构]
        L[增强时序图]
        M[业务规则分析]
        N[问题预测矩阵]
        O[解决方案映射]
    end
    
    B --> G
    B --> H
    B --> I
    B --> J
    
    C --> K
    D --> L
    D --> M
    E --> N
    E --> O
    
    style A fill:#e1f5fe
    style F fill:#4caf50
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
```

## 7. 错误处理与恢复机制

```mermaid
graph TD
    A[任务执行] --> B{执行成功?}
    B -->|是| C[继续下一任务]
    B -->|否| D[错误分析]
    
    D --> E{错误类型}
    E -->|超时| F[重试机制]
    E -->|依赖缺失| G[依赖检查]
    E -->|质量不达标| H[质量改进]
    E -->|用户拒绝| I[用户反馈处理]
    
    F --> J[简化分析]
    G --> K[补充依赖]
    H --> L[重新分析]
    I --> M[调整方向]
    
    J --> A
    K --> A
    L --> A
    M --> A
    
    C --> N{所有任务完成?}
    N -->|是| O[工作流完成]
    N -->|否| A
    
    style B fill:#ffeb3b
    style E fill:#ffeb3b
    style N fill:#ffeb3b
    style O fill:#4caf50
```

## 8. 性能优化与并行处理

```mermaid
graph TB
    subgraph "并行执行策略"
        A[代码分析任务] --> B[模式识别任务]
        A --> C[依赖分析任务]
        B --> D[架构分析任务]
        C --> D
    end
    
    subgraph "缓存机制"
        E[分析结果缓存] --> F[模板渲染缓存]
        F --> G[知识库缓存]
    end
    
    subgraph "增量更新"
        H[知识库增量更新] --> I[文档增量更新]
        I --> J[状态增量保存]
    end
    
    style A fill:#f3e5f5
    style B fill:#f3e5f5
    style C fill:#f3e5f5
    style D fill:#f3e5f5
```

## 9. 用户界面交互设计

```mermaid
graph LR
    subgraph "用户界面组件"
        A[项目设置面板] --> B[分析进度显示]
        B --> C[结果展示区域]
        C --> D[确认按钮组]
        D --> E[反馈输入框]
    end
    
    subgraph "交互状态"
        F[等待输入] --> G[处理中]
        G --> H[等待确认]
        H --> I[用户反馈]
        I --> F
    end
    
    subgraph "可视化元素"
        J[进度条] --> K[状态指示器]
        K --> L[结果预览]
        L --> M[质量指标]
    end
    
    style A fill:#e1f5fe
    style H fill:#fff3e0
    style I fill:#f3e5f5
```

## 10. 总结

.bmad-core 的人机交互机制通过以下关键特性实现了类似 Manus 的智能协作：

1. **渐进式确认**: 每个阶段都有用户确认点
2. **智能代理切换**: 基于上下文的代理切换机制
3. **质量门控**: 多层次的质量保证机制
4. **产物传递**: 清晰的产物依赖和传递链
5. **错误恢复**: 完善的错误处理和恢复机制
6. **性能优化**: 并行处理和缓存机制
7. **用户友好**: 直观的界面和交互设计

这种设计确保了高质量的技术文档生成，同时提供了优秀的用户体验。


