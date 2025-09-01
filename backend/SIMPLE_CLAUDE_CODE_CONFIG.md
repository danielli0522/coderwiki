# Claude Code直接配置子代理最简方案

## 1. 最简单直接的方法

### 在Claude Code中设置默认代理

```python
# 在你的项目CLAUDE.md文件中添加
DEFAULT_SUBAGENT: architect  # 默认使用架构师
FORCE_SINGLE_AGENT: true      # 强制单代理模式
```

## 2. 直接在代码中调用

```python
# 最简单的调用方式 - 不需要复杂配置
import subprocess
import json

def generate_architecture_doc(repo_path):
    """直接生成架构文档 - 无需复杂配置"""
    
    # 方案A：直接调用architect代理
    command = f"""
    使用architect代理分析 {repo_path}
    生成架构设计文档
    """
    
    # 执行（伪代码，实际在Claude Code中会自动处理）
    return execute_architect_agent(command)

# 或者更简单的Shell命令
# claude-code --agent architect --task "生成架构文档" --repo ./
```

## 3. 为什么CoderWiki配置复杂？

CoderWiki的配置复杂是因为它是一个**完整的Web服务**，需要：
- 管理多用户
- 处理并发请求
- 维护数据库状态
- 提供API接口
- 错误处理和重试

**但在Claude Code中，你不需要这些！**

## 4. Claude Code中的极简配置

### 步骤1：创建.claude-config文件

```yaml
# .claude-config 或 .claude/config.yaml
default_agent: architect
agents:
  architect:
    enabled: true
    auto_trigger: true
    tasks:
      - generate_architecture
      - create_diagrams
      - analyze_tech_stack
```

### 步骤2：直接使用

```bash
# 就这么简单！
claude analyze --architecture-only
```

## 5. 最直接的Python脚本

```python
#!/usr/bin/env python3
"""
最简单的架构文档生成器
不需要复杂配置，直接运行
"""

def generate_architecture_doc_simple():
    """极简版架构文档生成"""
    
    # 就这几行代码！
    from claude_code import Agent
    
    architect = Agent(type="architect")
    doc = architect.analyze("./")
    
    with open("architecture.md", "w") as f:
        f.write(doc)
    
    print("✅ 架构文档已生成")

if __name__ == "__main__":
    generate_architecture_doc_simple()
```

## 6. 在Claude Code界面中配置

1. **设置 > 代理配置**
   ```
   默认代理: architect
   ☑️ 仅使用默认代理
   ☑️ 跳过确认提示
   ```

2. **快捷键绑定**
   ```
   Cmd+Shift+A = 生成架构文档
   ```

## 7. 环境变量最简配置

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export CLAUDE_DEFAULT_AGENT=architect
export CLAUDE_SINGLE_AGENT_MODE=true

# 然后任何项目都会默认使用架构师代理
```

## 8. VS Code集成

```json
// .vscode/settings.json
{
  "claude.defaultAgent": "architect",
  "claude.autoTriggerAgent": true,
  "claude.agentTasks": {
    "architect": ["generate_docs", "analyze_architecture"]
  }
}
```

## 总结：真正需要的配置

**实际上，你只需要：**

1. 告诉Claude Code使用architect代理
2. 运行分析命令
3. 完成！

```bash
# 一行命令搞定
claude --agent architect analyze ./ > architecture.md
```

**不需要**：
- ❌ 复杂的Python类
- ❌ 多层配置文件
- ❌ API调用
- ❌ 数据库设置
- ❌ Web服务器

## 为什么这样最好？

1. **Claude Code已经内置了代理管理**
2. **不需要额外的配置层**
3. **直接利用Claude Code的原生能力**
4. **维护成本为零**

## 立即可用的命令

```bash
# 生成架构文档
echo "DEFAULT_AGENT=architect" > .claude
claude analyze

# 或者一行命令
CLAUDE_AGENT=architect claude analyze ./

# 或者在Claude Code聊天中
"请使用architect代理分析当前项目"
```

就是这么简单！不需要那些复杂的配置。