# BMAD 文档生成器 - CoderWiki 集成版

## 📋 概述

这是 BMAD (Business Model Architecture Design) 文档生成器的完整文档集，已集成到 CoderWiki 项目中。BMAD 文档生成器是一个基于专业化代理团队的先进技术文档生成系统，能够帮助工程师在3天内快速理解、开发和维护复杂项目。

## 🚀 快速开始

### 目录位置
```
coderwiki/
└── bmad-docs/           # BMAD 文档生成器完整文档集
    ├── README.md         # 本文档
    ├── config.yaml       # 主配置文件
    ├── agent-teams/      # 代理团队配置
    ├── agents/          # 专业化代理定义
    ├── tasks/           # 任务定义
    ├── workflows/       # 工作流程配置
    └── ...              # 其他组件
```

### 核心特性

- 🎯 **基于 bmad-core 架构模式** - 交互式验证、深度控制、证据驱动分析
- 🔍 **专业化代理团队** - 5个专业角色协同工作
- 📋 **三套标准化文档** - 技术总览、流程分析、问题诊断
- 🛠️ **完整工作流程** - 从代码扫描到最终文档生成

## 📁 完整目录结构

```
bmad-docs/
├── README.md                           # CoderWiki集成版说明
├── config.yaml                         # 主配置文件
├── agent-teams/                        # 代理团队配置
│   ├── docs-generation-team.yaml      # 基础文档生成团队
│   └── enhanced-docs-generation-team.yaml # 增强文档生成团队
├── agents/                             # 专业化代理定义
│   ├── code-analyst.md                # 代码分析专家 (Alex)
│   ├── tech-architect.md              # 技术架构师 (Sarah)
│   ├── flow-analyst.md                # 流程分析师 (Jordan)
│   ├── problem-solver.md              # 问题解决专家 (Dr. Morgan)
│   ├── doc-engineer.md                # 文档工程师 (Maya)
│   └── ...                            # 其他专业代理
├── tasks/                              # 任务定义
│   ├── scan-codebase.md               # 代码库扫描任务
│   ├── generate-technical-overview.md  # 技术总览生成
│   ├── analyze-complex-flows.md       # 复杂流程分析
│   ├── diagnose-potential-problems.md  # 潜在问题诊断
│   └── ...                            # 其他任务
├── workflows/                          # 工作流程配置
│   ├── docs-generation-workflow.yaml   # 基础工作流程
│   └── enhanced-docs-generation.yaml  # 增强工作流程
├── templates/                          # 文档模板
│   ├── technical-overview-tmpl.yaml    # 技术总览模板
│   ├── complex-flow-analysis-tmpl.yaml # 流程分析模板
│   └── problem-diagnosis-tmpl.yaml     # 问题诊断模板
├── analysis-reports/                   # 分析报告模板
│   ├── bmad-core-architecture-analysis.md
│   ├── bmad-core-five-views-analysis.md
│   └── ...                            # 其他分析报告
├── checklists/                         # 质量检查清单
│   ├── codebase-analysis-checklist.md
│   └── documentation-quality-checklist.md
├── docs/                              # 实现文档
│   ├── implementation-plan.md
│   └── integration-design.md
└── data/                              # 数据文件
    └── bmad-kb.md                     # BMAD知识库
```

## 🎯 专业化代理团队

### 1. Code Analyst (Alex) - 代码分析专家
- **职责**: 深度代码扫描与架构侦探
- **专长**: 技术栈识别、架构模式分析、复杂流程发现
- **主要任务**: scan-codebase, validate-analysis

### 2. Tech Architect (Sarah) - 技术架构师
- **职责**: 企业级技术架构设计
- **专长**: 架构视图创建、技术总览生成、设计模式识别
- **主要任务**: create-architecture-views, generate-technical-overview

### 3. Flow Analyst (Jordan) - 流程分析师
- **职责**: 业务流程与流程分析
- **专长**: 复杂流程分析、时序图生成、业务规则提取
- **主要任务**: analyze-complex-flows, validate-flow-analysis

### 4. Problem Solver (Dr. Morgan) - 问题解决专家
- **职责**: 站点可靠性工程师与问题诊断
- **专长**: 潜在问题预测、故障诊断、监控策略制定
- **主要任务**: diagnose-potential-problems, validate-problem-diagnosis

### 5. Doc Engineer (Maya) - 文档工程师
- **职责**: 文档工程师与结构化输出专家
- **专长**: 文档结构化、质量验证、格式标准化
- **主要任务**: generate-flow-analysis-doc, generate-problem-diagnosis-doc

## 📋 三套标准化文档

### 1. 技术总览文档 (`项目名-Technical-Overview.md`)
- 项目背景与定位
- 完整技术栈清单
- 五视图架构设计（逻辑、开发、部署、运行时、数据视图）
- 核心设计原则和技术特性

### 2. 复杂流程分析文档 (`项目名-Complex-Flow-Analysis.md`)
- 核心复杂流程识别
- 增强的时序图 (含S1/S2/S3阶段标记)
- 详细的业务规则和逻辑分析
- 配置依赖分析
- 性能影响评估

### 3. 问题诊断与解决方案文档 (`项目名-Problem-Diagnosis-Solution.md`)
- 潜在问题预测（从SRE角度）
- 问题-解决方案矩阵
- 故障诊断指南
- 监控和告警策略

## 🛠️ 在 CoderWiki 中使用

### 集成状态
- ✅ **Claude Code SDK 集成** - 已集成到 CoderWiki 后端
- ✅ **BMAD 子代理支持** - 支持调用 BMAD 专业化代理团队
- ✅ **配置文件完整** - 所有必需的配置文件已就绪
- ✅ **工作流程定义** - 完整的文档生成工作流程

### 调用方式

#### 1. 通过 CoderWiki API
```python
# 使用 CoderWiki 的文档生成服务
from app.services.claude_code_service import ClaudeCodeService

service = ClaudeCodeService()
result = await service.generate_technical_document(
    repository_path='/path/to/your/project',
    doc_type='technical_design',
    doc_title='项目技术设计文档'
)
```

#### 2. 直接调用 BMAD 子代理
```bash
# 激活增强版文档生成团队
/bmad//bmadDocs:teams:enhanced-docs-generation-team

# 调用具体代理
/bmadDocs:agents:code-analyst *scan-codebase
/bmadDocs:agents:tech-architect *generate-technical-overview
```

## 📊 质量保证

### 分析完整性检查
- [ ] 至少识别15个复杂流程
- [ ] 技术栈完整目录
- [ ] 项目结构完整映射
- [ ] 数据库设计分析
- [ ] 依赖关系图生成

### 准确性验证
- [ ] 技术栈信息可在代码中验证
- [ ] 复杂流程的入口点可定位
- [ ] 架构模式与实际代码组织一致
- [ ] 依赖关系基于实际代码调用

## ⚡ 性能指标

### 处理时间
- **完整工作流程**: 8-12小时 (复杂系统)
- **快速工作流程**: 4-6小时 (简单系统)
- **单个任务**: 1-3小时

### 质量指标
- 技术准确率 > 95%
- 图表渲染率 100%
- 3天理解目标达成率 > 90%
- 用户审批率 > 90%

## 🔧 配置选项

### 主配置文件 (config.yaml)
```yaml
bmad_docs_generator:
  version: "1.0.0"
  settings:
    default_analysis_depth: "detailed"
    enable_interactive_validation: true
    enable_evidence_driven_analysis: true
    enable_pattern_recognition: true
```

### 分析深度选项
- **概览模式**: 快速了解项目结构
- **详细模式**: 深入理解技术实现
- **深度模式**: 全面掌握系统架构

## 🎯 适用场景

### 使用完整工作流程当
- 复杂企业系统 (>50 KLOC)
- 关键任务应用需要全面文档
- 具有高业务影响的遗留系统
- 具有复杂集成模式的系统
- 需要详细入门文档的团队

### 使用快速工作流程当
- 小型项目 (<20 KLOC)
- 概念验证或原型文档
- 时间紧迫的文档需求
- 简单的微服务或API
- 内部工具，复杂性有限

## 📚 相关文档

### 核心文档
- [BMAD 方法技术总览](analysis-reports/bmad-method-technical-overview.md)
- [架构分析报告](analysis-reports/bmad-core-architecture-analysis.md)
- [五视图分析](analysis-reports/bmad-core-five-views-analysis.md)

### 实现指南
- [实现计划](docs/implementation-plan.md)
- [集成设计](docs/integration-design.md)

### 质量保证
- [代码库分析检查清单](checklists/codebase-analysis-checklist.md)
- [文档质量检查清单](checklists/documentation-quality-checklist.md)

## 🔍 故障排除

### 常见问题

1. **分析深度不匹配**
   - 症状: 用户需要更深入或更简化的分析
   - 解决方案: 使用深度控制选项调整分析级别

2. **技术栈识别不完整**
   - 症状: 遗漏了重要的技术组件
   - 解决方案: 重新扫描相关目录和配置文件

3. **架构模式识别错误**
   - 症状: 架构模式判断不准确
   - 解决方案: 重新分析项目结构和关键配置文件

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证

---

**🔗 集成到 CoderWiki** | **🚀 专为技术文档生成优化** | **🎯 支持 3 天项目理解目标**

*最后更新: 2025-08-23 | 版本: v1.0.0*