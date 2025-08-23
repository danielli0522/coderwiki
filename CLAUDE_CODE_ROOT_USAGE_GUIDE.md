# Claude Code 根目录使用指南

## 配置状态

✅ **根目录配置已完成**

- Claude Code 配置文件已创建在项目根目录
- BMAD 文档生成器路径已正确配置
- 所有关键文件已验证存在

## 正确的使用步骤

### 1. 在项目根目录启动 Claude Code

```bash
cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki
claude
```

### 2. 验证配置

在 Claude Code 中运行以下命令验证配置：

```
/status
```

### 3. 调用 BMAD 子代理

#### 激活增强文档生成团队

```
/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

#### 查看 BMAD 配置

```
/read bmad-docs-generator/config.yaml
```

#### 查看工作流程

```
/read bmad-docs-generator/workflows/enhanced-docs-generation.yaml
```

#### 调用单个代理

```
/task bmad-docs-generator/agents/code-analyst.md
/task bmad-docs-generator/agents/tech-architect.md
/task bmad-docs-generator/agents/flow-analyst.md
/task bmad-docs-generator/agents/problem-solver.md
/task bmad-docs-generator/agents/doc-engineer.md
```

## 配置详情

### Claude Code 配置

- **工作目录**: `/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki`
- **BMAD 路径**: `/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/bmad-docs-generator`
- **允许工具**: Read, Grep, WebSearch, Task
- **最大轮次**: 10

### 可用的 BMAD 子代理

#### 增强文档生成团队

- **路径**: `bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml`
- **包含代理**: 5 个专业代理

#### 基础文档生成团队

- **路径**: `bmad-docs-generator/agent-teams/docs-generation-team.yaml`
- **包含代理**: 3 个核心代理

## 使用示例

### 生成技术设计文档

```
请使用BMAD增强文档生成团队为当前项目生成技术设计文档，包括：
1. 项目架构分析
2. 技术栈评估
3. 复杂流程分析
4. 潜在问题诊断
5. 完整的文档输出
```

### 生成 API 文档

```
请使用BMAD文档生成团队分析当前项目的API接口，生成详细的API文档
```

### 生成架构文档

```
请使用BMAD团队分析当前项目的系统架构，生成架构设计文档
```

## 故障排除

### 如果子代理仍然不可见

1. **确认在根目录启动**:

   ```bash
   cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki
   claude
   ```

2. **检查文件路径**:

   ```
   /read bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
   ```

3. **查看目录结构**:

   ```
   /read bmad-docs-generator/
   ```

4. **诊断安装**:
   ```
   /doctor
   ```

### 如果调用失败

1. **检查文件格式**:

   ```
   /read bmad-docs-generator/config.yaml
   ```

2. **验证工作流程**:

   ```
   /read bmad-docs-generator/workflows/enhanced-docs-generation.yaml
   ```

3. **查看错误信息**: 注意 Claude Code 的错误提示

## 最佳实践

1. **始终在根目录启动**: 确保在项目根目录启动 Claude Code
2. **分步骤执行**: 将复杂的文档生成任务分解为多个步骤
3. **明确指令**: 在调用子代理时提供清晰的指令和上下文
4. **验证结果**: 检查生成的文档质量和完整性

## 总结

现在你可以在项目根目录成功启动 Claude Code 并调用 BMAD 子代理了！

**关键步骤**:

1. 在根目录启动: `cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki && claude`
2. 调用团队: `/task bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml`
3. 开始生成文档

**配置状态**: ✅ 完全就绪，立即可用！
