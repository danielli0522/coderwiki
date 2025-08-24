# CoderWiki 技术架构文档生成指南

## 📋 概述

本指南详细说明如何使用 `bmad-docs-generator` 和 `Claude Code SDK` 生成高质量的技术架构文档。

## 🚀 快速开始

### 1. 环境准备

确保您的环境中已安装以下组件：

- Python 3.8+
- bmad-docs-generator
- Claude Code SDK
- 项目代码库

### 2. 运行文档生成器

```bash
# 运行简化版本
python simple_architecture_generator.py

# 运行完整版本（推荐）
python bmad_claude_architecture_generator.py
```

## 🔧 生成器说明

### 1. SimpleArchitectureGenerator

**特点：**

- 简化版本，快速生成基础架构文档
- 不依赖外部 API 调用
- 适合快速原型和测试

**使用方法：**

```python
from simple_architecture_generator import SimpleArchitectureGenerator

generator = SimpleArchitectureGenerator()
result = generator.generate_architecture_doc()
```

### 2. BMADClaudeArchitectureGenerator

**特点：**

- 完整版本，集成 BMAD 方法论
- 模拟 Claude Code SDK 调用
- 包含 BMAD 团队协作分析
- 生成更专业和全面的文档

**使用方法：**

```python
from bmad_claude_architecture_generator import BMADClaudeArchitectureGenerator

generator = BMADClaudeArchitectureGenerator()
result = await generator.generate_architecture_doc("technical_architecture")
```

## 📊 BMAD 方法论集成

### 1. BMAD 团队配置

项目使用以下 BMAD 团队进行文档生成：

- **enhanced-docs-generation-team**: 增强文档生成团队
- **docs-generation-team**: 基础文档生成团队

### 2. 专业代理分工

- **code-analyst**: 代码分析师，负责扫描代码库
- **tech-architect**: 技术架构师，负责生成技术总览
- **flow-analyst**: 流程分析师，负责分析复杂流程
- **problem-solver**: 问题解决者，负责诊断潜在问题
- **doc-engineer**: 文档工程师，负责整合最终文档

### 3. 工作流程

1. 验证 BMAD 文档生成器
2. 准备 BMAD 调用指令
3. 调用 Claude Code SDK
4. 执行 BMAD 团队协作分析
5. 生成技术架构文档
6. 保存文档和元数据

## 📁 输出文件结构

```
generated_docs/
├── CoderWiki_Technical_Architecture_YYYYMMDD_HHMMSS.md
├── CoderWiki_Technical_Architecture_YYYYMMDD_HHMMSS_metadata.json
└── ...
```

### 文档内容结构

生成的文档包含以下主要部分：

1. **执行摘要** - 项目概述和文档目的
2. **系统整体架构** - 架构概览和技术栈分析
3. **核心组件设计** - 主要服务组件设计
4. **数据模型设计** - 数据库模型和关系
5. **API 设计** - 接口设计和规范
6. **部署架构** - 开发和生产环境架构
7. **安全架构** - 安全设计和防护措施
8. **性能优化** - 性能优化策略
9. **扩展性设计** - 系统扩展方案
10. **BMAD 方法论分析** - BMAD 分析结果
11. **总结** - 关键特性和技术亮点

### 元数据文件

包含以下信息：

```json
{
  "doc_title": "文档标题",
  "doc_type": "文档类型",
  "generated_at": "生成时间",
  "doc_path": "文档路径",
  "project_path": "项目路径",
  "bmad_path": "BMAD路径",
  "generator": "生成器类型",
  "claude_code_used": true,
  "bmad_team_used": "使用的BMAD团队"
}
```

## 🔍 配置选项

### 1. 项目路径配置

```python
# 自定义项目路径
generator = BMADClaudeArchitectureGenerator(project_path="/path/to/your/project")
```

### 2. BMAD 路径配置

```python
# 自定义BMAD路径
generator.bmad_path = "custom/bmad/path"
```

### 3. 输出目录配置

```python
# 自定义输出目录
generator.output_dir = Path("/custom/output/path")
```

## 🛠️ 自定义扩展

### 1. 添加新的文档类型

```python
class CustomArchitectureGenerator(BMADClaudeArchitectureGenerator):
    def generate_custom_doc(self, doc_type: str):
        # 自定义文档生成逻辑
        pass
```

### 2. 扩展 BMAD 团队

```python
# 在bmad-docs-generator/agent-teams/中添加新的团队配置
# 在bmad-docs-generator/agents/中添加新的代理配置
```

### 3. 自定义分析流程

```python
def _custom_analysis_workflow(self):
    # 自定义分析工作流程
    pass
```

## 📈 性能优化

### 1. 异步处理

所有文档生成操作都使用异步处理，提高性能：

```python
async def generate_architecture_doc(self):
    # 异步生成文档
    pass
```

### 2. 缓存机制

可以添加缓存机制避免重复分析：

```python
def _get_cached_analysis(self, project_path: str):
    # 获取缓存的分析结果
    pass
```

### 3. 并行处理

可以并行调用多个 BMAD 代理：

```python
async def _parallel_agent_analysis(self):
    # 并行调用多个代理
    pass
```

## 🔒 安全考虑

### 1. 路径验证

所有文件路径都经过验证，防止路径遍历攻击：

```python
def _validate_paths(self):
    # 验证路径安全性
    pass
```

### 2. 输入验证

所有用户输入都经过验证和清理：

```python
def _validate_input(self, user_input: str):
    # 验证用户输入
    pass
```

### 3. 权限控制

确保只有授权用户可以生成文档：

```python
def _check_permissions(self):
    # 检查用户权限
    pass
```

## 🐛 故障排除

### 1. BMAD 验证失败

**问题：** BMAD 文档生成器验证失败

**解决方案：**

- 检查 bmad-docs-generator 目录是否存在
- 确认必要的配置文件存在
- 验证文件权限

### 2. Claude Code 调用失败

**问题：** Claude Code SDK 调用失败

**解决方案：**

- 检查网络连接
- 验证 API 密钥配置
- 确认 SDK 版本兼容性

### 3. 文档生成失败

**问题：** 文档生成过程中出现错误

**解决方案：**

- 检查项目路径是否正确
- 确认输出目录权限
- 查看详细错误日志

## 📚 最佳实践

### 1. 文档生成

- 定期生成文档，保持文档最新
- 使用版本控制管理文档
- 为不同环境生成不同版本的文档

### 2. 配置管理

- 使用环境变量管理敏感配置
- 为不同项目使用不同的配置
- 定期备份配置文件

### 3. 质量保证

- 验证生成的文档内容
- 检查文档格式和结构
- 确保文档的可读性和准确性

## 🔮 未来规划

### 1. 功能增强

- 支持更多文档类型
- 集成更多 AI 服务
- 添加可视化图表生成

### 2. 性能优化

- 实现真正的并行处理
- 添加智能缓存机制
- 优化内存使用

### 3. 用户体验

- 提供 Web 界面
- 添加实时进度显示
- 支持批量文档生成

## 📞 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看项目文档
2. 提交 Issue 到项目仓库
3. 联系开发团队

---

_本指南由 BMAD 文档生成器自动生成_
