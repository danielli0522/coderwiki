# BMAD 子代理使用指南

## 概述

本指南说明如何在 Claude Code 中调用 BMAD 子代理来生成技术文档。

## 配置状态

✅ **配置已完成**

- Claude Code CLI 已安装
- BMAD 文档生成器路径已配置
- 子代理团队已定义
- 工作流程已集成

## 在 Claude Code 中调用 BMAD 子代理

### 1. 启动 Claude Code

```bash
cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/backend
claude
```

### 2. 可用的 BMAD 子代理团队

#### 增强文档生成团队（推荐）

- **团队 ID**: `enhanced-docs-generation-team`
- **路径**: `bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml`
- **包含代理**: 5 个专业代理

#### 基础文档生成团队

- **团队 ID**: `docs-generation-team`
- **路径**: `bmad-docs-generator/agent-teams/docs-generation-team.yaml`
- **包含代理**: 3 个核心代理

### 3. 调用方式

#### 方式 1: 使用 Task 工具调用团队

```
/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

#### 方式 2: 直接调用单个代理

```
/task bmad-docs-generator/agents/code-analyst.md
/task bmad-docs-generator/agents/tech-architect.md
/task bmad-docs-generator/agents/flow-analyst.md
/task bmad-docs-generator/agents/problem-solver.md
/task bmad-docs-generator/agents/doc-engineer.md
```

#### 方式 3: 查看工作流程配置

```
/read bmad-docs-generator/workflows/enhanced-docs-generation.yaml
```

### 4. 完整的文档生成流程

#### 步骤 1: 激活增强文档生成团队

```
/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

#### 步骤 2: 执行代码分析

```
请使用code-analyst代理扫描当前代码库，分析项目结构和技术栈
```

#### 步骤 3: 生成技术总览

```
请使用tech-architect代理生成项目的技术总览文档
```

#### 步骤 4: 分析复杂流程

```
请使用flow-analyst代理分析项目中的复杂业务流程
```

#### 步骤 5: 诊断潜在问题

```
请使用problem-solver代理诊断项目中可能存在的问题
```

#### 步骤 6: 整合最终文档

```
请使用doc-engineer代理整合所有分析结果，生成完整的技术文档
```

### 5. 示例调用

#### 生成技术设计文档

```
请使用BMAD增强文档生成团队为当前项目生成技术设计文档，包括：
1. 项目架构分析
2. 技术栈评估
3. 复杂流程分析
4. 潜在问题诊断
5. 完整的文档输出
```

#### 生成 API 文档

```
请使用BMAD文档生成团队分析当前项目的API接口，生成详细的API文档
```

#### 生成架构文档

```
请使用BMAD团队分析当前项目的系统架构，生成架构设计文档
```

### 6. 可用的文档类型

系统支持以下 8 种文档类型：

- `technical_design` - 技术设计文档
- `api_docs` - API 文档
- `architecture` - 架构文档
- `database_design` - 数据库设计文档
- `deployment_guide` - 部署指南
- `user_manual` - 用户手册
- `developer_guide` - 开发者指南
- `system_overview` - 系统概览文档

### 7. 工作流程阶段

BMAD 增强文档生成工作流程包含 6 个阶段：

1. **初始化** (Initialization)
2. **代码分析** (Code Analysis)
3. **架构分析** (Architecture Analysis)
4. **文档生成** (Documentation Generation)
5. **知识库更新** (Knowledge Base Update)
6. **最终化** (Finalization)

### 8. 故障排除

#### 问题 1: 子代理不可见

**解决方案**:

- 确认当前工作目录包含 bmad-docs-generator
- 检查文件路径是否正确
- 重启 Claude Code

#### 问题 2: 调用失败

**解决方案**:

- 检查代理文件是否存在
- 验证 YAML 文件格式
- 查看错误信息

#### 问题 3: 响应超时

**解决方案**:

- 增加 max_turns 设置
- 简化查询内容
- 分步骤执行

### 9. 最佳实践

1. **分步骤执行**: 将复杂的文档生成任务分解为多个步骤
2. **明确指令**: 在调用子代理时提供清晰的指令和上下文
3. **验证结果**: 检查生成的文档质量和完整性
4. **迭代优化**: 根据结果调整和优化调用策略

## 总结

现在你可以在 Claude Code 中成功调用 BMAD 子代理来生成高质量的技术文档了！

**关键命令**:

- 激活团队: `/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml`
- 查看配置: `/read bmad-docs-generator/config.yaml`
- 查看工作流程: `/read bmad-docs-generator/workflows/enhanced-docs-generation.yaml`

**配置状态**: ✅ 完全就绪
