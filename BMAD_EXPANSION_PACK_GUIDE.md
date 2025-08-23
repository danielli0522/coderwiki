# BMAD 文档生成器扩展包使用指南

## 🎉 安装完成！

BMAD 文档生成器扩展包已成功安装并集成到 Claude Code 中。

## 📊 安装状态

- ✅ **扩展包已安装**: `.bmad-docs-generator/`
- ✅ **Claude Code 集成**: 自动配置完成
- ✅ **子代理可用**: 所有 BMAD 子代理已就绪
- ✅ **工作流程就绪**: 文档生成工作流程可用

## 🏗️ 安装结构

```
项目根目录/
├── .bmad-docs-generator/          # BMAD扩展包安装目录
│   ├── agents/                    # 代理定义
│   ├── agent-teams/              # 代理团队
│   ├── workflows/                # 工作流程
│   ├── tasks/                    # 任务定义
│   ├── templates/                # 文档模板
│   ├── checklists/               # 检查清单
│   ├── data/                     # 数据文件
│   ├── utils/                    # 工具函数
│   └── config.yaml              # 扩展包配置
├── .claude/
│   └── settings.json            # Claude Code配置(已更新)
└── bmad-docs-generator/         # 原始源码目录
```

## 🚀 使用方法

### 1. 在 Claude Code 中启动

```bash
cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki
claude
```

### 2. 调用 BMAD 子代理

#### 调用增强文档生成团队

```
/task .bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

#### 调用基础文档生成团队

```
/task .bmad-docs-generator/agent-teams/docs-generation-team.yaml
```

#### 调用单个代理

```
/task .bmad-docs-generator/agents/code-analyst.md
/task .bmad-docs-generator/agents/tech-architect.md
/task .bmad-docs-generator/agents/flow-analyst.md
/task .bmad-docs-generator/agents/problem-solver.md
/task .bmad-docs-generator/agents/doc-engineer.md
```

#### 调用工作流程

```
/task .bmad-docs-generator/workflows/enhanced-docs-generation.yaml
/task .bmad-docs-generator/workflows/docs-generation-workflow.yaml
```

### 3. 查看配置和文档

#### 查看扩展包配置

```
/read .bmad-docs-generator/config.yaml
```

#### 查看工作流程详情

```
/read .bmad-docs-generator/workflows/enhanced-docs-generation.yaml
```

#### 查看代理定义

```
/read .bmad-docs-generator/agents/code-analyst.md
```

## 🛠️ 管理命令

### 检查安装状态

```bash
cd bmad-docs-generator
python install.py status --project-root ..
```

### 卸载扩展包

```bash
cd bmad-docs-generator
python install.py uninstall --project-root ..
```

### 重新安装

```bash
cd bmad-docs-generator
python install.py install --project-root ..
```

## 📋 可用功能

### 代理团队

1. **增强文档生成团队** - 5 个专业代理的完整团队
2. **基础文档生成团队** - 3 个核心代理的基础团队

### 单个代理

1. **代码分析代理** - 分析代码库结构和模式
2. **技术架构代理** - 设计和分析技术架构
3. **流程分析代理** - 分析复杂工作流程
4. **问题诊断代理** - 识别和解决技术问题
5. **文档工程师代理** - 创建和维护技术文档

### 工作流程

1. **增强文档生成** - 全面的文档生成工作流程
2. **基础文档生成** - 基础文档生成工作流程

### 任务

- 代码库扫描
- 架构分析
- 文档生成
- 问题诊断
- 质量检查

## 🎯 使用示例

### 生成项目技术文档

```
请使用BMAD增强文档生成团队为当前项目生成完整的技术文档，包括：
1. 项目架构分析
2. 技术栈评估
3. 代码结构分析
4. 复杂流程分析
5. 潜在问题诊断
6. 完整的文档输出

使用命令：/task .bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

### 分析特定组件

```
请使用BMAD代码分析代理分析backend目录的架构和设计模式：

使用命令：/task .bmad-docs-generator/agents/code-analyst.md
```

### 生成 API 文档

```
请使用BMAD文档工程师代理为当前项目的API接口生成详细文档：

使用命令：/task .bmad-docs-generator/agents/doc-engineer.md
```

## 🔧 配置详情

### Claude Code 配置

- **工作目录**: 项目根目录
- **BMAD 路径**: `.bmad-docs-generator/`
- **允许工具**: Read, Grep, WebSearch, Task
- **系统提示**: 专业文档生成专家
- **环境变量**: BMAD_DOCS_GENERATOR_PATH, BMAD_DOCS_ENABLED

### 扩展包配置

- **版本**: 1.0.0
- **类型**: documentation
- **类别**: development-tools
- **依赖**: bmad-core >= 1.0.0

## 🚨 故障排除

### 如果子代理不可见

1. 确认在项目根目录启动 Claude Code
2. 检查`.claude/settings.json`配置
3. 验证`.bmad-docs-generator/`目录存在
4. 重启 Claude Code

### 如果调用失败

1. 检查文件路径是否正确
2. 验证 YAML 文件格式
3. 查看 Claude Code 错误信息
4. 运行状态检查命令

### 如果需要重新配置

1. 卸载扩展包
2. 清理 Claude Code 配置
3. 重新安装扩展包

## 📈 优势

### 标准化安装

- ✅ 遵循 BMAD Method 标准
- ✅ 自动化配置过程
- ✅ 支持多种 IDE 集成

### 完整功能

- ✅ 所有代理和团队可用
- ✅ 工作流程完整
- ✅ 模板和检查清单

### 易于维护

- ✅ 支持更新和卸载
- ✅ 配置集中管理
- ✅ 状态检查功能

## 🎉 总结

BMAD 文档生成器扩展包已成功集成到你的项目中！

**现在你可以：**

1. 在 Claude Code 中调用 BMAD 子代理
2. 使用专业团队生成文档
3. 执行复杂的技术分析
4. 获得高质量的文档输出

**开始使用：**

```bash
cd /Users/lshl124/Documents/daniel/git/code/aigc/coderwiki
claude
```

然后在 Claude Code 中调用：

```
/task .bmad-docs-generator/agent-teams/enhanced-docs-generation-team.yaml
```

享受 BMAD Method 的强大功能！🚀
