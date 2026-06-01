# Module 1: 食谱开张——从一道"加强版 LLM"开始

### Teaching Arc
- **Metaphor:** 户外攀岩者与登山套件 (climber + climbing rack)。一个赤手空拳的攀岩者只能爬最简单的路线；给他/她加上"四件套"——绳索（检索/记忆）、保护塞（工具/动作）、对讲机（多轮交互）、教练（系统提示）——他/她突然就能去挑战更难的山壁。一个普通 LLM 调用是"赤手攀岩"，本课要教的"Augmented LLM"是"装备齐全的攀岩"。这是 Anthropic 论文 *Building Effective Agents* 的开场比喻，也是整本 cookbook 的根基。
- **Opening hook:** "你打开 ChatGPT 问它今天的天气，它说'我没法访问实时信息'——这一秒你就触碰到了'裸 LLM'的边界。Anthropic Cookbook 这本食谱整本书在教的，就是怎么给 LLM 配上四件套，让它能查天气、能用计算器、能记得你昨天问过什么。"
- **Key insight:** Cookbook 不是教你"调用 API"，而是教你"组装智能体"。最小的可用单元就是 **Augmented LLM** —— 一个能检索、能动手、能记忆的 LLM。所有更复杂的模式（链式、路由、Orchestrator）都是这个最小单元的不同**组合方式**。
- **"Why should I care?":** vibe coder 在 AI 工具里看到 "agent / tool / RAG / memory" 这些词时，往往不知道它们是哪一层概念。理解了"Augmented LLM"这个最小单元，你就拿到了整本 cookbook 的钥匙——你能跟 AI 说"给我加一个能查数据库的工具"或者"给它加上记忆"，并且知道你在要什么。

### Cast of characters across the course
- 主角：**Claude**（Anthropic 出的大语言模型）
- 配角：**工具 (Tool)**、**记忆 (Memory)**、**检索器 (Retriever)**、**人类用户**
- 全书围绕这些角色之间不同的协作方式展开。

### Code Snippets (pre-extracted)

**Snippet A — 一行代码的 Research Agent（来自 `claude_agent_sdk/00_The_one_liner_research_agent.ipynb#cell-6`）：**

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
- `from claude_agent_sdk import ...` — 从 Anthropic 的 Agent SDK 里把"提问"函数和"配置项"拿进来。
- `messages = []` — 准备一个空列表，等会儿用来收 agent 的回话。
- `async for msg in query(...)` — 像在和一个真人对话一样，一句一句接收 Claude 的输出（流式）。
- `prompt="Research..."` — 我们的"任务订单"：研究 AI agent 最新趋势，给我摘要和引用链接。
- `options=ClaudeAgentOptions(model=MODEL, allowed_tools=["WebSearch"])` — 配置：选用哪个模型，并且**只**允许它使用一个工具——网页搜索。这就是"Augmented LLM"：LLM + 一件工具。
- `print_activity(msg)` — 把每条消息打印出来，让我们看到它在搜什么、想什么。
- 整段代码 7 行，就是一个能上网做调研的研究员。**这是整本 cookbook 的"Hello World"**。

**Snippet B — 从 Anthropic 工程文章引用的 Augmented LLM 概念（patterns/agents/README.md 摘录）：**
```
Building Effective Agents
- Basic Building Blocks
  - Prompt Chaining
  - Routing
  - Multi-LLM Parallelization
- Advanced Workflows
  - Orchestrator-Subagents
  - Evaluator-Optimizer
```
（这是整本食谱的"目录结构"，不需要做翻译块，作为一个 visual list 展示即可）

### Interactive Elements

- [x] **Code↔English translation** — Snippet A 的一行代码 research agent，全中文逐行翻译
- [x] **Quiz** — 3 道题（场景型）
  - Q1: 你想让 Claude 写一首诗，你要不要给它"工具"或"记忆"？为什么？（考察"什么时候不需要 Augmented LLM"——纯文本生成不需要外部信息）
  - Q2: 你的 AI 助手反复说"我没有实时数据"，你应该给它加什么？（应该加 WebSearch / 检索 工具）
  - Q3: 看一段对话，判断这个"Agent"少了哪一件装备——记忆？工具？检索？
- [x] **Group chat animation** — 演员：用户 / 普通 LLM / Augmented LLM。剧情：
  - 用户：今天上海下雨吗？
  - 普通 LLM：抱歉，我没有实时天气数据。
  - 用户：（叹气）
  - （旁白：现在我们装备一下 LLM）
  - 用户：今天上海下雨吗？
  - Augmented LLM：让我查一下…（调用 WebSearch 工具）→ 上海现在小雨，气温 18°C，建议带伞。
  - 用户：太好了！还能记住我喜欢冷一点的天气吗？
  - Augmented LLM：（写入 Memory）已记下你的偏好。
- [x] **Pattern cards** — 4 张卡片，每张代表"四件套"中的一件：检索 / 工具 / 记忆 / 系统提示
- [x] **Visual file tree** — Cookbook 顶层目录结构注解（patterns/, capabilities/, claude_agent_sdk/, tool_use/, skills/, multimodal/, extended_thinking/, misc/）

### Reference Files to Read
- `references/content-philosophy.md` — 全文（写作总纲）
- `references/gotchas.md` — 全文（每模块都要查）
- `references/interactive-elements.md` — Code↔English Translations / Multiple-Choice Quizzes / Group Chat Animation / Pattern Cards / Visual File Tree / Glossary Tooltips
- `references/design-system.md` — 仅 Module Structure / Color Palette（actor 色用本课的 teal+coral+amber 区分）

### Connections
- **Previous module:** 无（第 1 模块）
- **Next module:** 模块 2 会拆解三种最基础的"组装方式"——把多个 Augmented LLM 串起来 (chain)、按情况分流 (route)、并发跑 (parallel)。本模块要把 Augmented LLM 这个"基础单元"讲透，让模块 2 的"组合"水到渠成。
- **Tone/style notes:**
  - 配色：teal（accent #2A7B9B）。Actor 色：`--color-actor-1`（teal）= Claude，`--color-actor-2`（vermillion-ish）= 用户/外部世界，`--color-actor-3`（plum）= 工具，`--color-actor-4`（amber）= 记忆/检索。
  - 称呼：把 Claude 称为"Claude"或"模型"，不要叫"AI"（太宽泛）。把"agent"翻译为"智能体"或保留英文，第一次用必加 tooltip。
  - 整门课语气：像一个老练的 CTO 给非技术朋友讲他读完一整本食谱后的笔记——有结构、有比喻、不端着。
  - 该模块约 5 屏：①欢迎 + cookbook 是什么 ②什么是 Augmented LLM（4 件套卡片）③一行代码 research agent（翻译块）④群聊动画对比裸 LLM vs Augmented LLM ⑤cookbook 全景 file tree + 模块导览 ⑥quiz
