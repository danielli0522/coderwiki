# Module 5: Claude Agent SDK——从一行代码到 SRE 值班员

### Teaching Arc
- **Metaphor:** 钢琴学习的进阶 (piano learning progression)。
  - **Notebook 00 (Research Agent) = 第一首练习曲**：右手单音、左手 do-mi-sol。一行代码，5 分钟弹会。
  - **Notebook 01 (Chief of Staff) = 巴赫小品**：左右手协奏，加上踏板（CLAUDE.md / Output Styles / Plan Mode / Hooks / Subagents）。要练几个月。
  - **Notebook 03 (SRE Agent) = 拉赫玛尼诺夫**：八度大跳、复杂踏板、还要现场即兴（MCP 工具 / 自动远程修配置 / 安全 hook）。要练几年。
  - 同一个琴（Claude Agent SDK），同一双手，难度从入门到大师级。
- **Opening hook:** "上一模块我们手写了 agentic loop——70 行 Python 才让 Claude 学会用一个计算器。Anthropic 自己也觉得太麻烦，于是把它打包成了 SDK——**从 70 行变 7 行**。但这个 SDK 真正的厉害之处不是省代码，而是它把 Claude Code 这个产品里所有 agent 工程经验都开放给了你。"
- **Key insight:**
  - **Claude Agent SDK = Claude Code 的内核以 SDK 形式开放**。所有让 Claude Code 在本地编程时显得"聪明"的能力——长期记忆、工具调度、子 agent、安全 hook、Plan Mode——都能拿来构建任何领域的 agent，不只是编程。
  - 进阶路径很清晰：研究助手 → 公司参谋长 → 可观测性 agent → SRE 值班员。**每一步只多加 1-2 个 SDK 特性**。
- **"Why should I care?":**
  - vibe coder 用 Claude Code 时其实就在用这套 SDK，只是不知道。理解 SDK = 理解你天天在用的工具。
  - 想自己做一个"AI 律师 / AI 销售 / AI 数据分析师"？不必从 0 写——拿 SDK，把 Claude Code 那套内核嫁接到你的领域，最快 1 天有 demo。

### Code Snippets (pre-extracted)

**Snippet A — One-liner research agent（来自 `claude_agent_sdk/00_The_one_liner_research_agent.ipynb#cell-6`，全部代码）：**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

messages = []
async for msg in query(
    prompt="Research the latest trends in AI agents and give me a brief summary and relevant citiations links.",
    options=ClaudeAgentOptions(model=MODEL, allowed_tools=["WebSearch"]),
):
    print_activity(msg)
    messages.append(msg)
```

中文逐行翻译：
- `from claude_agent_sdk import ClaudeAgentOptions, query` — 从官方 SDK 拿"提问"和"配置"。
- `async for msg in query(...):` — 流式接收 agent 的每一条动作和输出。**异步迭代**——意味着你能像看直播一样看 agent 在干什么。
- `prompt="Research..."` — 任务订单。
- `ClaudeAgentOptions(model=MODEL, allowed_tools=["WebSearch"])` — 关键配置：**只**给它一个工具——网页搜索。`allowed_tools` 是 SDK 的安全围栏：你能精确控制 agent 能动什么、不能动什么。
- 整个 agent 7 行。**和模块 4 手写的 70 行 agentic loop 一对比，你会发现 SDK 把 while loop / tool dispatch / 对话历史管理全包圆了**。

**Snippet B — Chief of Staff 用 ClaudeSDKClient 配 CLAUDE.md（来自 `claude_agent_sdk/01_The_chief_of_staff_agent.ipynb#cell-4`）：**

```python
async with ClaudeSDKClient(
    options=ClaudeAgentOptions(
        model=MODEL,
        cwd="chief_of_staff_agent",  # Points to subdirectory with our CLAUDE.md
        setting_sources=["project"],
    )
) as agent:
    await agent.query("What's our current runway?")
    async for msg in agent.receive_response():
        print_activity(msg)
        messages.append(msg)
```

中文逐行翻译：
- `async with ClaudeSDKClient(options=...) as agent:` — 创建一个**有状态**的会话 agent（不像 query() 是一次性的）。`async with` 保证用完自动关闭连接，不会泄露资源。
- `cwd="chief_of_staff_agent"` — 把 agent 的"工作目录"指到一个子文件夹。**关键魔法**：那个文件夹里有一个 `CLAUDE.md`，agent 启动时会自动读它当背景知识。
- `setting_sources=["project"]` — 告诉 SDK：去那个项目目录里把 `.claude/output-styles/`、`.claude/commands/` 也一起加载。
- `await agent.query("What's our current runway?")` — 像跟同事问话一样发问。
- `async for msg in agent.receive_response():` — 一句一句接收回话。
- **核心洞察**：`CLAUDE.md` 在 SDK 里就是**"项目级长期记忆"**。把公司财务数据、团队规则、历史决策写进 `CLAUDE.md`，agent 每次启动都自带这份"入职 onboarding 文档"。

**Snippet C — SRE Agent 用 MCP 工具（来自 `claude_agent_sdk/03_The_site_reliability_agent.ipynb#cell-3` 节选）：**

```python
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)

MODEL = "claude-opus-4-6"
```

中文翻译要点：SRE agent 多了一组消息类型 import——`AssistantMessage / TextBlock / ToolUseBlock / ResultMessage`。这是因为它要**精细监控** agent 在每一刻在做什么：是在思考（TextBlock）、在调用一个修配置的工具（ToolUseBlock）、还是在给最终结论（ResultMessage）。**生产级 agent = 你看得见每一步在干什么，并且能在某一步打断它**。

### Interactive Elements

- [x] **Code↔English translation** — Snippet A（one-liner）+ Snippet B（CoS with cwd）做两个翻译块
- [x] **Numbered Step Cards** — SDK 4 阶进阶路径：
  - 1. **Research Agent** — query() + 1 个工具（WebSearch）
  - 2. **Chief of Staff** — ClaudeSDKClient + CLAUDE.md + Subagents + Output Styles
  - 3. **Observability Agent** — + MCP（外部系统）+ Hooks（合规审计）
  - 4. **SRE Agent** — + 写权限 + 安全 PreToolUse 钩子 + 生产环境集成
- [x] **Interactive Architecture Diagram (or pattern-cards as substitute)** — Claude Agent SDK 的 6 大模块卡片：
  - `query()` — 无状态一次性问答
  - `ClaudeSDKClient` — 有状态会话
  - `ClaudeAgentOptions` — 配置中枢（model / allowed_tools / cwd / hooks / mcpServers）
  - `CLAUDE.md` — 项目级长期记忆
  - `Subagents` — 派生子 agent（财务分析师、招聘官等）
  - `Hooks` — 工具调用前后的拦截器，做审计 / 安全 / 限流
- [x] **Group Chat Animation** — Chief of Staff 内部分工演示：
  - CEO（用户）：给我一份重组工程团队的方案。
  - Chief of Staff（主 agent）：好的，让我协调一下。 → 派给 financial-analyst 子 agent
  - Financial Analyst：当前 burn rate $500K，新增 5 名工程师后 runway 会从 20 个月压到 15 个月。
  - Chief of Staff：→ 同时派给 recruiter 子 agent
  - Recruiter：在 $180-220K 区间能找到 5 个 senior。优先级排序：①AI infra ②MLOps ③前端架构。
  - Chief of Staff（汇总）：综合建议——分两批招聘，控 burn 在 $580K 以内，runway 仍保 17 个月以上。
- [x] **Quiz** — 3 道
  - Q1：你想让 agent 在用一个"删数据库"工具前必须暂停让你确认。SDK 里用什么机制？（Hooks，特别是 PreToolUse hook）
  - Q2：你的 agent 经常忘记公司的"绝不直接联系客户"规则。最干净的解法？（写入 CLAUDE.md，而不是每次 prompt 里复述）
  - Q3：你看到 SRE agent 的 demo 后想做一个 "AI 律师助手"——查法规、起草合同、提交客户审批。从哪个 notebook 开始最合适？（02 Observability，因为律师助手主要是"读外部系统 + 给建议"，写权限要谨慎；从 read-only 的 02 起步比直接学有写权限的 03 安全）
- [x] **Callout box** — "Aha! Claude Agent SDK 不是新发明的工具——它是 **Claude Code 这个产品的内核以库的形式开放出来**。意思是：你每天用 Claude Code 时见到的所有'魔法'（自动用工具、记得对话、规划再执行），都能复制到你自己的领域 agent 里。"
- [x] **Glossary tooltips**: SDK / async / MCP / hook / subagent / CLAUDE.md / Plan Mode / Output Style / runway

### Reference Files to Read
- `references/content-philosophy.md` — 全文
- `references/gotchas.md` — 全文
- `references/interactive-elements.md` — Code↔English / Multiple-Choice / Group Chat / Numbered Step Cards / Pattern Cards / Callout Boxes
- `references/design-system.md` — Color Palette / Module Structure

### Connections
- **Previous module:** 模块 4 手写了 agentic loop——理解了底层机制后再看 SDK 才知道"它到底替你封装了什么"。
- **Next module:** 模块 6 收束——Extended Thinking / Prompt Caching / Skills 三个进阶火候，是任何 agent 都能受益的"调味料"。
- **Tone/style notes:**
  - 偶数模块，背景用 `--color-bg`
  - actor 色：CEO/用户 = actor-2，主 agent (Chief of Staff) = actor-1（teal），财务子 agent = actor-3，招聘子 agent = actor-4，工具/MCP = actor-5
  - 该模块约 5 屏：①开场（钢琴隐喻 + 4 阶进阶卡）②one-liner research agent（翻译块 A）③Chief of Staff 配 CLAUDE.md（翻译块 B + 群聊动画）④SDK 6 大模块卡 + SRE agent 走到生产级 ⑤quiz + callout
