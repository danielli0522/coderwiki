# Claude Code SDK 无头模式运行器

## 项目简介

本项目提供了一个 Python 脚本，用于通过 Claude Code SDK 的无头模式运行命令，等待最终反馈后返回成功状态。

## 主要文件

- `claude_headless_runner.py` - 主要的无头模式运行器
- `example_headless_usage.py` - 使用示例脚本
- `test_claude_headless.py` - 简单测试脚本

## 功能特性

### ✨ 核心功能

1. **无头模式执行** - 支持 Claude Code CLI 的非交互式运行
2. **完整参数支持** - 支持所有主要的 Claude CLI 参数
3. **超时控制** - 可配置执行超时时间
4. **错误处理** - 完善的异常处理和错误报告
5. **调试模式** - 支持详细的调试输出
6. **JSON 输出** - 支持结构化的 JSON 格式输出

### 🛠️ 支持的参数

| 参数              | CLI 参数            | 说明                    |
| ----------------- | ------------------- | ----------------------- |
| `prompt`          | `-p`                | 提示内容                |
| `allowed_tools`   | `--allowedTools`    | 允许的工具列表          |
| `denied_tools`    | `--disallowedTools` | 禁止的工具列表          |
| `permission_mode` | `--permission-mode` | 权限模式                |
| `cwd`             | `--add-dir`         | 工作目录                |
| `model`           | `--model`           | 使用的模型              |
| `max_tokens`      | `--max-tokens`      | 最大 token 数           |
| `temperature`     | `--temperature`     | 温度参数                |
| `timeout`         | -                   | 超时时间（Python 级别） |
| `session_id`      | `--session-id`      | 会话 ID                 |
| `debug`           | `--debug`           | 调试模式                |

## 安装要求

### 前置条件

1. **Python 3.7+**
2. **Claude Code CLI** - 需要先安装 Claude Code

```bash
# 检查 Claude CLI 是否已安装
claude --version
```

### 安装 Claude Code

如果没有安装 Claude Code，请访问 [Claude.ai](https://claude.ai/) 下载安装。

## 使用方法

### 基本用法

```bash
# 简单查询
python claude_headless_runner.py -p "请列出该项目目录结构" --tools "Read" --permission-mode acceptEdits

# 分析代码架构
python claude_headless_runner.py \
  -p "请分析这个项目的代码架构" \
  --tools "Read,Grep" \
  --permission-mode acceptEdits \
  --timeout 300

# 生成文档
python claude_headless_runner.py \
  -p "请生成项目技术文档" \
  --tools "Read,Write" \
  --permission-mode acceptEdits \
  --timeout 600 \
  --debug
```

### 完整命令行参数

```bash
python claude_headless_runner.py \
  -p "提示内容" \
  --tools "Bash,Read,Write" \
  --permission-mode acceptEdits \
  --model claude-3-haiku-20240307 \
  --max-tokens 4000 \
  --temperature 0.3 \
  --timeout 600 \
  --debug \
  --json-output
```

### Python API 使用

```python
from claude_headless_runner import ClaudeHeadlessRunner, ClaudeHeadlessOptions

# 配置选项
options = ClaudeHeadlessOptions(
    prompt="请分析这个项目的主要功能",
    allowed_tools=["Read", "Grep"],
    permission_mode="acceptEdits",
    cwd="/path/to/project",
    timeout=300,
    debug=True
)

# 创建运行器并执行
runner = ClaudeHeadlessRunner(options)
result = runner.run()

if result['success']:
    print(f"执行成功! 耗时: {result['execution_time']:.2f}s")
    print(f"输出: {result['output']}")
else:
    print(f"执行失败: {result['error']}")
```

## 示例脚本

### 运行所有示例

```bash
python example_headless_usage.py
```

这将运行以下示例：

1. **列出项目结构** - 分析并列出项目目录结构
2. **分析代码架构** - 深入分析代码架构和设计模式
3. **生成项目文档** - 自动生成完整的技术文档
4. **调试模式运行** - 演示调试模式的使用
5. **自定义模型参数** - 展示如何使用不同的模型和参数

### 运行测试

```bash
python test_claude_headless.py
```

## 输出格式

### 标准输出

```
✅ 执行成功! (耗时: 31.54s)
==================================================
输出结果:
==================================================
CoderWiki 是一个基于 Flask 的智能代码文档生成与管理平台...
```

### JSON 输出

```json
{
  "success": true,
  "output": "CoderWiki 是一个基于 Flask 的智能代码文档生成与管理平台...",
  "error": "",
  "execution_time": 31.54,
  "exit_code": 0
}
```

## 权限模式

| 模式                | 说明                   |
| ------------------- | ---------------------- |
| `acceptEdits`       | 自动接受所有编辑操作   |
| `bypassPermissions` | 绕过所有权限检查       |
| `default`           | 使用默认权限设置       |
| `plan`              | 仅制定计划，不执行操作 |

## 常用工具列表

| 工具        | 功能           |
| ----------- | -------------- |
| `Read`      | 读取文件内容   |
| `Write`     | 写入文件       |
| `Bash`      | 执行 Bash 命令 |
| `Grep`      | 文本搜索       |
| `WebSearch` | Web 搜索       |

## 错误处理

脚本提供了完善的错误处理机制：

1. **CLI 未找到** - 检查 Claude Code 是否正确安装
2. **执行超时** - 可调整 timeout 参数
3. **权限错误** - 检查文件和目录权限
4. **参数错误** - 验证输入参数的有效性

## 日志记录

所有执行日志会保存到 `claude_headless.log` 文件中，包括：

- 执行开始时间
- 参数配置
- 执行进度
- 错误信息
- 执行结果

## 最佳实践

1. **合理设置超时时间** - 根据任务复杂度调整 timeout 参数
2. **选择合适的工具** - 只启用必要的工具以提高安全性
3. **使用调试模式** - 开发时启用 debug 模式获取详细信息
4. **错误重试机制** - 在自动化脚本中加入重试逻辑
5. **结果验证** - 检查 success 标志和输出内容的合理性

## 故障排除

### 常见问题

1. **Claude CLI not found**

   ```bash
   # 检查安装
   which claude
   claude --version
   ```

2. **权限被拒绝**

   ```bash
   # 使用更宽松的权限模式
   --permission-mode bypassPermissions
   ```

3. **执行超时**

   ```bash
   # 增加超时时间
   --timeout 1200
   ```

4. **工具不可用**
   ```bash
   # 检查工具名称拼写
   --tools "Read,Write"  # 注意大小写
   ```

## 许可证

本项目基于项目根目录的许可证条款。

## 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个工具。

