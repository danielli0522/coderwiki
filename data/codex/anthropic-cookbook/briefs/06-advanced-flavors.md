# Module 6: 进阶火候——思考、缓存、Skills

### Teaching Arc
- **Metaphor:** 米其林餐厅的 mise en place + 慢炖锅 + 标准化 SOP（**注意：这里只用"准备工序 / 慢炖 / SOP" 这三个具体子比喻，不要把整个模块退回到"餐厅"——餐厅是被禁的隐喻**）。
  - 等等，换一个干净的：**长跑选手的三件训练外挂**：
    - **Extended Thinking = 起跑前的呼吸调整**（赛前那 30 秒深呼吸，让大脑预热再开跑）
    - **Prompt Caching = 训练中的肌肉记忆**（同一段路跑过 100 次后，肌肉自动反应，不用再思考动作）
    - **Skills = 教练给的训练计划包**（一份现成的、能直接套用的 SOP，比如"全马备赛 16 周计划"）
  - 三件外挂对应三种"提速"——**思考更深 / 重复更快 / 复用更广**。每一件都是任何 agent 都能加挂的。
- **Opening hook:** "前 5 个模块教的是 agent 的'骨架和肌肉'。这一模块是'训练外挂'——三个不同维度的优化，把同一个 agent 从'能用'推到'生产可用'。它们的共同点：**只加几行代码，但效果立刻显著**。"
- **Key insight:**
  - Extended Thinking 不是模型变聪明了，是**给模型一段不被打扰的草稿纸**——它把推理过程写在 `thinking` 块里，最后才给结论。**复杂推理任务直接受益**。
  - Prompt Caching 不是新模型，是**API 的一个 flag**——把长的、不变的前缀（一本书、一份代码库、一份 system prompt）缓存住。**第二次调用同一前缀时，输入 token 价格降到 1/10、延迟降一半。**
  - Skills 是 Anthropic 最新的"代码 + 提示词 + 资源"打包格式——**让 Claude 学会一种新的本领（做 PPT / Excel / PDF）**，并且这本领能在所有客户端复用。
- **"Why should I care?":**
  - vibe coder 经常被吓到的"AI 太贵 / 太慢 / 不够准"——这三件外挂分别治这三个症。
  - 当你听到产品经理说"AI 调用成本下不来"，你能立刻问"接 prompt caching 了吗？"——这是 CTO 级别的对话词汇。

### Code Snippets (pre-extracted)

**Snippet A — Extended Thinking 一行打开（来自 `extended_thinking/extended_thinking.ipynb#cell-5`）：**

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4000,
    thinking={
        "type": "enabled",
        "budget_tokens": 2000
    },
    messages=[{
        "role": "user",
        "content": "Solve this puzzle: Three people check into a hotel..."
    }]
)
```

中文逐行翻译：
- `client.messages.create(model="claude-sonnet-4-6", ...)` — 普通的 API 调用，model 选 Sonnet（也支持 Opus）。
- `max_tokens=4000` — 最终输出最多 4000 token。
- `thinking={"type": "enabled", "budget_tokens": 2000}` — **关键开关**！打开扩展思考，并给它 2000 token 的"草稿纸预算"。模型会把推理过程写进一个独立的 `thinking` 块，再写最终答案。
- `messages=[{...}]` — 你的问题。
- 调用回来后，`response.content` 里会有两类块：`thinking` 块（推理过程）和 `text` 块（最终答案）。**你能看到模型的"内心独白"**——这对调试 agent 行为是金子。

**Snippet B — Prompt Caching 一行打开（来自 `misc/prompt_caching.ipynb#cell-12`）：**

```python
write_response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=300,
    cache_control={"type": "ephemeral"},  # <-- one-line change
    messages=[
        {
            "role": "user",
            "content": str(TIMESTAMP)
            + "<book>"
            + book_content
            + "</book>"
            + "\n\nWhat is the title of this book? Only output the title.",
        }
    ],
)
```

中文逐行翻译：
- `cache_control={"type": "ephemeral"}` — **就这一行**！加在 `messages.create` 的顶层。意思是"我允许系统把这次输入的可缓存部分缓存起来"。
- `<book>` + `book_content` + `</book>` — 把整本《傲慢与偏见》（约 187k token）塞进 prompt 里。
- 第一次调用：缓存被写入，时间和不缓存差不多（baseline）。
- **第二次调用相同前缀**：API 直接从缓存读，**输入 token 价格降到 1/10，延迟降一半以上**。
- 真实生产场景：你的 agent 每次都带相同的 system prompt（几千 token）和工具列表？打开 caching，立刻省钱。

**Snippet C — Extended Thinking 的输出结构（概念展示）：**

```python
# response.content 大致长这样：
[
    ThinkingBlock(thinking="让我分析这个旅馆问题。$30 = $25 房费 + $3 退给客人 + $2 服务员私吞。所以 $27（客人付）= $25 房费 + $2 服务员，逻辑一致。'$27 + $2 = $29' 是错误的相加方式..."),
    TextBlock(text="这是一个经典的语言陷阱。客人付的 $27 已经包含了服务员私吞的 $2，不应该再加 $2。"),
]
```

中文翻译：模型对外吐两类内容——**thinking（草稿）**和 **text（终稿）**。你的程序可以选择只展示 text 给用户、或者把 thinking 一起展示出来做"AI 推理透明化"产品。

### Interactive Elements

- [x] **Code↔English translation** — Snippet A（thinking）+ Snippet B（caching）做两个翻译块
- [x] **Pattern cards** — 3 张：Extended Thinking / Prompt Caching / Skills——每张写"治什么病 / 怎么打开 / 适合什么场景 / 注意事项"
- [x] **Drag-and-drop matching** — 把 4 个真实场景与"该用哪个外挂"配对：
  - chips（要拖的）：Extended Thinking / Prompt Caching / 都用 / 都不用
  - zones：
    - "复杂数学推理 / 多步规划任务" → Extended Thinking
    - "客服 agent，每次对话开头都贴 5000 token 的 KB" → Prompt Caching
    - "RAG agent，长文档 + 复杂多跳问答" → 都用
    - "一个简单的'今天星期几' 问答" → 都不用
- [x] **Group Chat Animation** — 演示 Extended Thinking 的"内心独白"：
  - 用户：旅馆账单悖论——为什么 $27 + $2 不等于 $30？
  - Claude（thinking 内心独白，灰色泡泡）：让我仔细拆账……$30 总付 = $25 房费 + $3 退还 + $2 服务员。客人实际付 $27 = $25 房费 + $2 服务员。所以"$27 + $2 = $29"是把服务员的 $2 加了两次……
  - Claude（text 正式回答）：这是一个语言陷阱。$27 = $25 + $2，不应该再加 $2。
- [x] **Quiz** — 3 道
  - Q1：你的 agent 每次对话开头都要贴一份 8000 token 的 system prompt + 工具说明，对话本身只有几百 token。账单很贵。最优一招？（开 prompt caching——缓存那 8000 token 的前缀）
  - Q2：你的 agent 在做"分析三季度财务报告，识别 5 个潜在风险"。回答经常浅尝辄止。最该试的开关？（开 Extended Thinking——给它草稿空间做深度推理）
  - Q3：你想让 Claude 在网页应用里**直接生成 PowerPoint 文件**。最适合的机制？（Skills——这正是 Skills 的设计目标，把"做 PPT"这种本领以可复用包形式提供给 Claude）
- [x] **Callout box (closing)** — "**这门课结束了，但 Cookbook 还在更新。** 整本食谱的脉络是：先认识 Augmented LLM 这个最小单元（模块 1），学会三种基础工序（模块 2）和两种高阶工序（模块 3），把'动手'机制（模块 4）打通后，用 SDK 把所有这些封装成产品级 agent（模块 5），最后用三件训练外挂（模块 6）把 agent 推到生产可用。回到 cookbook 仓库后，你不再是看 random 一堆 notebook——你能认出每个 notebook 在这张地图上的坐标。"
- [x] **Glossary tooltips**: extended thinking / thinking budget / token / cache_control / ephemeral cache / Skills / mise en place（如果有人不知道）/ MCP

### Reference Files to Read
- `references/content-philosophy.md` — 全文
- `references/gotchas.md` — 全文
- `references/interactive-elements.md` — Code↔English / Multiple-Choice / Drag-and-Drop / Group Chat / Pattern Cards / Callout Boxes
- `references/design-system.md` — Color Palette / Module Structure

### Connections
- **Previous module:** 模块 5 教完了 SDK 的进阶路径——任何模块 5 里搭出来的 agent，都能加挂模块 6 的三件外挂。
- **Next module:** 无（这是最后一模块，要做收束 + 给学员一张"全课地图"）。
- **Tone/style notes:**
  - 奇数模块，背景用 `--color-bg-warm`
  - actor 色：用户 = actor-2，Claude（thinking）= actor-1（teal）但**用浅色 bubble 标"内心独白"**，Claude（text 终稿）= 同一个 actor-1（teal）正常 bubble
  - 该模块约 5 屏：①开场（长跑训练外挂隐喻 + 3 张 pattern card）②Extended Thinking（翻译块 A + 群聊"内心独白"动画）③Prompt Caching（翻译块 B + 数字对比卡：第一次 vs 第二次的 token & 时间）④4 场景拖拽配对 ⑤quiz + 全课收束 callout
