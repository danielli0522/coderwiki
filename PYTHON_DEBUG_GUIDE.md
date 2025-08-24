# Python 调试指南 - Claude Code SDK 断点调试

## 📋 概述

本指南详细说明如何在 Python 中调试技术架构文档生成器，特别是在调用 Claude Code SDK 时设置断点。

## 🔧 调试方法

### 方法 1：使用 pdb 调试器（推荐）

我已经创建了一个带调试功能的文档生成器 `debug_architecture_generator.py`，它会在关键位置设置断点。

#### 运行调试版本

```bash
python debug_architecture_generator.py
```

#### 断点位置

在 `debug_architecture_generator.py` 中，断点设置在以下位置：

```python
# 在调用Claude Code SDK之前设置断点
if self.enable_debug:
    print("🔍 调试: 准备调用Claude Code SDK...")
    print("🔍 调试: 即将进入Claude Code SDK调用，按 'c' 继续...")

    # 在这里设置断点
    pdb.set_trace()
```

#### pdb 调试命令

当程序在断点处停止时，您可以使用以下命令：

- `c` 或 `continue` - 继续执行
- `n` 或 `next` - 执行下一行
- `s` 或 `step` - 步入函数
- `l` 或 `list` - 显示当前代码
- `p variable_name` - 打印变量值
- `pp variable_name` - 美化打印变量值
- `w` 或 `where` - 显示调用栈
- `h` 或 `help` - 显示帮助
- `q` 或 `quit` - 退出调试器

### 方法 2：使用 VS Code 调试

#### 1. 创建 launch.json 配置

在 `.vscode/launch.json` 中添加以下配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Architecture Generator",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/debug_architecture_generator.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      },
      "stopOnEntry": false,
      "justMyCode": false
    }
  ]
}
```

#### 2. 设置断点

1. 在 VS Code 中打开 `debug_architecture_generator.py`
2. 在需要调试的行号左侧点击设置断点
3. 按 F5 启动调试

### 方法 3：使用 IPython 调试器（ipdb）

#### 安装 ipdb

```bash
pip install ipdb
```

#### 在代码中使用

```python
import ipdb

# 在需要调试的地方添加
ipdb.set_trace()
```

## 🎯 关键调试位置

### 1. Claude Code SDK 调用前

```python
# 在 backend/app/services/claude_code_service.py 的第93行
result = await self._execute_with_retry(system_prompt, query_content)
```

### 2. 系统提示词构建

```python
# 在 _prepare_system_prompt 方法中
system_prompt = self._prepare_system_prompt(doc_type, doc_title, additional_params)
```

### 3. 用户提示词构建

```python
# 在 _prepare_query_content 方法中
query_content = self._prepare_query_content(repository_path, doc_type, doc_title)
```

### 4. BMAD 指令准备

```python
# 在 _prepare_bmad_instructions 方法中
bmad_instructions = self._prepare_bmad_instructions(doc_type, doc_title)
```

## 🔍 调试技巧

### 1. 检查变量值

在断点处，您可以检查以下关键变量：

```python
# 检查系统提示词
p system_prompt

# 检查用户提示词
p user_prompt

# 检查BMAD指令
p bmad_instructions

# 检查项目路径
p self.project_path

# 检查BMAD路径
p self.bmad_path
```

### 2. 检查文件路径

```python
# 检查BMAD文档生成器是否存在
p os.path.exists(self.bmad_path)

# 检查必要的文件
p [os.path.exists(f"{self.bmad_path}/{file}") for file in required_files]
```

### 3. 检查配置

```python
# 检查BMAD配置
p self.bmad_config.get_subagent_teams()
p self.bmad_config.get_subagent_agents()
```

## 🐛 常见问题调试

### 1. BMAD 文档生成器验证失败

**问题**：BMAD 文档生成器目录不存在或缺少必要文件

**调试步骤**：

```python
# 检查目录是否存在
p os.path.exists(self.bmad_path)

# 列出目录内容
p os.listdir(self.bmad_path)

# 检查必要文件
for file_path in required_files:
    full_path = os.path.join(self.bmad_path, file_path)
    p f"{file_path}: {os.path.exists(full_path)}"
```

### 2. Claude Code SDK 调用失败

**问题**：SDK 导入失败或调用异常

**调试步骤**：

```python
# 检查SDK是否可用
try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
    p "SDK导入成功"
except ImportError as e:
    p f"SDK导入失败: {e}"

# 检查配置选项
p options.system_prompt[:100]  # 显示前100个字符
p options.add_dirs
p options.cwd
```

### 3. 提示词构建问题

**问题**：系统提示词或用户提示词格式错误

**调试步骤**：

```python
# 检查提示词长度
p len(system_prompt)
p len(user_prompt)

# 检查提示词内容
p system_prompt[:200]  # 显示前200个字符
p user_prompt[:200]

# 检查是否包含关键信息
p "BMAD" in system_prompt
p "Claude Code" in system_prompt
```

## 📊 调试日志

### 1. 启用详细日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 查看日志文件

```bash
# 查看实时日志
tail -f debug_architecture_generation.log

# 查看错误日志
grep "ERROR" debug_architecture_generation.log

# 查看调试信息
grep "DEBUG" debug_architecture_generation.log
```

## 🛠️ 自定义调试

### 1. 添加自定义断点

```python
def custom_debug_point(self, message: str, variables: dict = None):
    """自定义调试点"""
    if self.enable_debug:
        print(f"🔍 调试: {message}")
        if variables:
            for name, value in variables.items():
                print(f"  {name}: {value}")

        # 询问是否继续
        response = input("按回车继续，输入 'pdb' 进入调试器: ").strip()
        if response.lower() == 'pdb':
            pdb.set_trace()
```

### 2. 条件断点

```python
# 只在特定条件下设置断点
if self.enable_debug and len(system_prompt) > 1000:
    print("🔍 调试: 系统提示词过长，设置断点")
    pdb.set_trace()
```

### 3. 性能调试

```python
import time

start_time = time.time()
# ... 执行代码 ...
end_time = time.time()
print(f"🔍 调试: 执行时间: {end_time - start_time:.2f}秒")
```

## 📝 调试检查清单

### 运行前检查

- [ ] BMAD 文档生成器目录存在
- [ ] 必要文件存在
- [ ] Python 路径正确
- [ ] 依赖包已安装

### 运行时检查

- [ ] 系统提示词构建成功
- [ ] 用户提示词构建成功
- [ ] BMAD 指令包含正确
- [ ] Claude Code SDK 调用正常

### 输出检查

- [ ] 文档生成成功
- [ ] 内容格式正确
- [ ] 元数据完整
- [ ] 调试信息记录

## 🚀 快速调试命令

### 1. 快速运行调试版本

```bash
# 启用调试模式
echo "y" | python debug_architecture_generator.py

# 禁用调试模式
echo "n" | python debug_architecture_generator.py
```

### 2. 检查环境

```bash
# 检查Python版本
python --version

# 检查依赖
pip list | grep claude

# 检查BMAD目录
ls -la bmad-docs-generator/
```

### 3. 清理调试文件

```bash
# 删除调试日志
rm -f debug_architecture_generation.log

# 删除生成的文档
rm -f generated_docs/CoderWiki_*_debug_*.md
```

---

_本指南帮助您有效调试 Python 代码，特别是在调用 Claude Code SDK 时设置断点_
