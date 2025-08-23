# BMAD 子代理配置指南

## 概述

本指南详细说明如何配置 bmad-docs-generator 成为 Claude Code 的子代理，实现高级文档生成功能。

## 配置状态

✅ **配置已完成**

- BMAD 文档生成器路径已配置
- 子代理团队已定义
- 工作流程已集成
- 测试验证通过

## 配置详情

### 1. 路径配置

**BMAD 文档生成器路径**: `../bmad-docs-generator/`

```python
# 在 claude_code_service.py 中
self.bmad_docs_path = bmad_docs_path or "../bmad-docs-generator/"
```

### 2. 子代理团队配置

#### 增强文档生成团队 (推荐)

- **团队 ID**: `enhanced-docs-generation-team`
- **路径**: `/bmad//bmadDocs:teams:enhanced-docs-generation-team`
- **包含代理**: 5 个专业代理
  - Code Analyst (Alex) - 代码分析师
  - Tech Architect (Sarah) - 技术架构师
  - Flow Analyst (Jordan) - 流程分析师
  - Problem Solver (Dr. Morgan) - 问题诊断专家
  - Doc Engineer (Maya) - 文档工程师

#### 基础文档生成团队

- **团队 ID**: `docs-generation-team`
- **路径**: `/bmad//bmadDocs:teams:docs-generation-team`
- **包含代理**: 3 个核心代理
  - Code Analyst (Alex) - 代码分析师
  - Tech Architect (Sarah) - 技术架构师
  - Doc Engineer (Maya) - 文档工程师

### 3. 工作流程配置

#### 增强文档生成工作流程

- **工作流程 ID**: `enhanced-docs-generation`
- **版本**: 2.0
- **阶段数量**: 6 个阶段
  1. 初始化 (Initialization)
  2. 代码分析 (Code Analysis)
  3. 架构分析 (Architecture Analysis)
  4. 文档生成 (Documentation Generation)
  5. 知识库更新 (Knowledge Base Update)
  6. 最终化 (Finalization)

### 4. 支持的文档类型

系统支持以下 8 种文档类型：

- `technical_design` - 技术设计文档
- `api_docs` - API 文档
- `architecture` - 架构文档
- `database_design` - 数据库设计文档
- `deployment_guide` - 部署指南
- `user_manual` - 用户手册
- `developer_guide` - 开发者指南
- `system_overview` - 系统概览文档

## 使用方法

### 1. 基本调用

```python
from app.services.claude_code_service import ClaudeCodeService

# 创建服务实例
service = ClaudeCodeService()

# 生成技术设计文档
result = await service.generate_technical_document(
    repository_path="/path/to/repository",
    doc_type="technical_design",
    doc_title="项目技术设计文档"
)
```

### 2. 子代理调用指令

系统会自动生成以下调用指令：

```
**BMAD子代理调用指令**

1. **激活团队**: /bmad//bmadDocs:teams:enhanced-docs-generation-team
   - 团队名称: Enhanced Documentation Generation Team
   - 描述: Advanced team for generating comprehensive technical documentation

2. **工作流程**: enhanced-docs-generation
   - 包含 5 个专业代理
   - 支持多阶段文档生成

3. **可用代理**:
   - Code Analyst (Alex) (代码分析师): /bmad//bmadDocs:agents:code-analyst
   - Tech Architect (Sarah) (技术架构师): /bmad//bmadDocs:agents:tech-architect
   - Flow Analyst (Jordan) (流程分析师): /bmad//bmadDocs:agents:flow-analyst
   - Problem Solver (Dr. Morgan) (问题诊断专家): /bmad//bmadDocs:agents:problem-solver
   - Doc Engineer (Maya) (文档工程师): /bmad//bmadDocs:agents:doc-engineer

4. **调用方式**:
   - 使用Task工具调用BMAD子代理
   - 指定代理路径和任务
   - 传递必要的参数和上下文

5. **输出格式**:
   - Markdown格式文档
   - 包含架构图和代码示例
   - 支持交互式验证
```

### 3. 工作流程执行

BMAD 工作流程按以下顺序执行：

1. **代码分析师** 扫描代码库

   - 分析项目结构
   - 识别技术栈
   - 发现依赖关系

2. **技术架构师** 生成技术总览

   - 创建架构视图
   - 评估技术选型
   - 生成架构图

3. **流程分析师** 分析复杂流程

   - 识别业务流程
   - 生成时序图
   - 分析性能影响

4. **问题诊断专家** 诊断潜在问题

   - 预测系统风险
   - 提供解决方案
   - 制定监控策略

5. **文档工程师** 整合最终文档
   - 组装所有内容
   - 质量验证
   - 格式优化

## 配置验证

### 1. 运行测试脚本

```bash
cd backend
python test_bmad_subagent_config.py
```

### 2. 验证结果

测试脚本会验证以下内容：

- ✅ BMAD 配置类功能
- ✅ Claude Code SDK 可用性
- ✅ BMAD 文档生成器可用性
- ✅ 子代理团队配置
- ✅ 工作流程配置
- ✅ 系统提示词生成

### 3. 预期输出

```
配置验证结果: 成功
BMAD可用性: 是
团队数量: 2
代理数量: 5
工作流程: enhanced-docs-generation
版本: 2.0
阶段数量: 6
```

## 高级配置

### 1. 自定义 BMAD 路径

```python
# 使用自定义路径
service = ClaudeCodeService(bmad_docs_path="/custom/path/to/bmad-docs-generator/")
```

### 2. 获取子代理信息

```python
# 获取所有子代理信息
subagent_info = service.get_bmad_subagent_info()

# 获取工作流程配置
workflow_config = service.get_bmad_workflow_config("enhanced-docs-generation")
```

### 3. 检查配置状态

```python
# 检查BMAD文档生成器状态
bmad_status = service.check_bmad_docs_generator()

# 检查Claude Code SDK状态
sdk_status = service.check_claude_code_availability()
```

## 故障排除

### 1. 常见问题

#### 问题：BMAD 路径不存在

**解决方案**：

- 确认 bmad-docs-generator 目录存在
- 检查路径配置是否正确
- 确保目录包含必要的子目录

#### 问题：配置文件缺失

**解决方案**：

- 检查 config.yaml 文件是否存在
- 确保 workflows、agents、tasks 目录完整
- 验证文件权限

#### 问题：子代理调用失败

**解决方案**：

- 确认 Claude Code SDK 已安装
- 检查网络连接
- 验证 API 密钥配置

### 2. 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 运行配置测试
python test_bmad_subagent_config.py
```

## 最佳实践

### 1. 路径管理

- 使用相对路径便于部署
- 确保路径在所有环境中一致
- 定期验证路径有效性

### 2. 配置验证

- 在启动时验证配置完整性
- 定期运行测试脚本
- 监控配置变更

### 3. 错误处理

- 实现优雅的错误处理
- 提供有意义的错误信息
- 记录详细的调试日志

### 4. 性能优化

- 缓存配置信息
- 避免重复加载配置文件
- 优化子代理调用频率

## 总结

BMAD 子代理配置已完成并验证通过。系统现在可以：

1. ✅ 自动调用 BMAD 子代理团队
2. ✅ 执行完整的文档生成工作流程
3. ✅ 生成高质量的技术文档
4. ✅ 支持多种文档类型
5. ✅ 提供详细的配置信息

配置状态：**完全就绪**
