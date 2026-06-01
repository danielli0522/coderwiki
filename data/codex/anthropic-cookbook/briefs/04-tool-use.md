# Module 4: 工具调用——让模型动手

### Teaching Arc
- **Metaphor:** 国际象棋大师 + 棋钟 (chess grandmaster with a chess clock)。
  - 大师（Claude）只能"想棋"，不能离开桌子去查棋谱。
  - 你给他配几张"工具卡"——查开局库、查残局库、问引擎评分。每张卡上写清楚"这张牌能干什么、需要什么参数"。
  - 他想用哪张就抬手按下棋钟、说出工具名和参数。**他不亲自查，他叫你去查**。
  - 你查完把结果递回去，他接着想下一步。
  - 整盘棋下来可能按好几次钟（多轮工具调用）——这就是 **agentic loop**。
- **Opening hook:** "Claude 自己不能看时间、不能查数据库、不能发邮件。但你可以教他**叫别人去做这些事**——这就是 'tool use' 的全部秘密。在这一模块，我们会拆解一个会算账、能查订单的客服机器人是怎么搭出来的。"
- **Key insight:**
  - **工具调用 = 模型不动手，模型动嘴**。Claude 输出的不是结果，是一段结构化指令"请帮我调用 calculator 工具，参数是 '17 * 23'"。**真正执行的是你的程序**，不是 Claude。
  - 这一刻 Claude 从"作家"变成"指挥官"。
  - 整个 agentic loop = while (模型还想用工具) { 调模型 → 执行工具 → 把结果喂回去 }。直到模型说"我够了，给最终答案"。
- **"Why should I care?":** 当 vibe coder 让 AI 工具"接入数据库 / 接 Stripe / 接 Slack"时，背后基本都是 tool use。理解了这个机制，你就能：①明白为什么有时候 AI"幻觉"出一个不存在的订单号——它没真的查过；②学会写"工具描述"让 AI 用对工具；③知道为什么有的 agent 来回跑 10 次——它在 loop 里还没拿到能交差的信息。

### Code Snippets (pre-extracted)

**Snippet A — 定义一个工具的"说明书"（来自 `tool_use/calculator_tool.ipynb#cell-5`）：**

```python
tools = [
    {
        "name": "calculator",
        "description": "A simple calculator that performs basic arithmetic operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4').",
                }
            },
            "required": ["expression"],
        },
    }
]
```

中文逐行翻译：
- `tools = [{...}]` — 工具是一个列表，意味着你可以一次给 Claude 配多张卡。
- `"name": "calculator"` — 工具的"卡名"，Claude 会用这个名字来召唤它。
- `"description": "A simple calculator..."` — 工具说明书。**这是 tool use 里最重要的一行**——Claude 是看着这句话决定"要不要用这个工具"的。说明书写不清楚，Claude 就会用错或者不用。
- `"input_schema": {...}` — 用 JSON Schema 描述参数的形状：要一个叫 `expression` 的字符串，必填。
- `"required": ["expression"]` — 强制 Claude 必须填这个参数，不许偷懒。
- **写给 vibe coder 的一句话：tool 的 description 不是写给程序员看的，是写给 Claude 看的。要写得像在跟一个聪明但没上下文的实习生交代任务。**

**Snippet B — agentic loop 的核心（来自 `tool_use/calculator_tool.ipynb#cell-8`，简化版）：**

```python
message = client.messages.create(
    model=MODEL_NAME,
    max_tokens=4096,
    messages=[{"role": "user", "content": user_message}],
    tools=tools,
)

if message.stop_reason == "tool_use":
    tool_use = next(block for block in message.content if block.type == "tool_use")
    tool_result = process_tool_call(tool_use.name, tool_use.input)

    response = client.messages.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": message.content},
            {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_result,
            }]},
        ],
        tools=tools,
    )
```

中文逐行翻译：
- `client.messages.create(...tools=tools)` — 第一次调 Claude，把"工具说明书清单"一起递过去。
- `if message.stop_reason == "tool_use":` — Claude 没直接回答，而是说"我要用工具"。停下来等你执行。
- `tool_use = next(block ... type == "tool_use")` — 从 Claude 的回复里挑出"要用工具的那块"。
- `tool_result = process_tool_call(tool_use.name, tool_use.input)` — **真正干活的一行**：你的程序按 Claude 给的工具名和参数去执行，拿到结果。
- `response = client.messages.create(messages=[...原对话, {"role": "user", "content": [{"type": "tool_result", ...}]}])` — 第二次调 Claude，把工具结果**用 `tool_result` 这个特殊角色**塞回对话历史。这一步是关键——必须保留完整对话上下文，Claude 才知道"哦我刚才让查的结果回来了"。
- 真实场景里这个过程可能循环多次：Claude 用完一个工具又想用下一个，直到 `stop_reason != "tool_use"`，才算完。

**Snippet C — 客服机器人的工具清单（来自 `tool_use/customer_service_agent.ipynb#cell-5`，节选 1 个工具）：**

```python
{
    "name": "get_customer_info",
    "description": "Retrieves customer information based on their customer ID. Returns the customer's name, email, and phone number.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The unique identifier for the customer.",
            }
        },
        "required": ["customer_id"],
    },
}
```

中文翻译：这是客服 demo 里的三件套之一（另外两个是 `get_order_details` 和 `cancel_order`）。**注意 description 的写法**：明确说了"返回什么"——名字、邮箱、电话。Claude 看了就知道"客户问邮箱时要先用这个工具"。

### Interactive Elements

- [x] **Code↔English translation** — Snippet A（工具说明书）+ Snippet B（agentic loop）做两个翻译块
- [x] **Message Flow / Data Flow Animation** — agentic loop 的 5 步：
  - actors: `用户` / `Claude` / `工具：calculator` / `你的程序`
  - steps:
    1. 高亮"用户"，label：用户问 17 乘 23 等于多少
    2. 数据包从用户飞到 Claude，label：Claude 收到问题 + 工具说明书
    3. 数据包从 Claude 飞到"你的程序"，label：Claude 不直接答，而是吐出 "tool_use: calculator(expression='17*23')"
    4. 数据包从"你的程序"飞到"工具：calculator"，label：你的程序真正调用 calculator 函数
    5. 数据包从"工具"飞回"你的程序"，label：calculator 返回 "391"
    6. 数据包从"你的程序"飞回 Claude，label：你把结果作为 tool_result 塞回对话
    7. 数据包从 Claude 飞回用户，label：Claude 看到结果后给出最终回答 "17 × 23 = 391"
- [x] **Spot the Bug** — 一段错误代码，Claude 调用了工具但开发者**忘记把 tool_result 塞回对话**：
  ```python
  if message.stop_reason == "tool_use":
      tool_use = next(...)
      tool_result = process_tool_call(...)
      print(tool_result)  # 直接打印就完事了？
  ```
  正确答案：缺少第二次 `client.messages.create(...)` 把结果回喂给 Claude——结果 Claude 永远不知道工具的返回值，对话断了。**这是 vibe coder 用 Cursor / Claude Code 时最常见的"工具循环没跑完"bug 的根因**。
- [x] **Pattern cards** — 4 张："Tool description 决定生死" / "JSON Schema 是合同" / "tool_result 必须回喂" / "max_iterations 是救命稻草"
- [x] **Quiz** — 3 道
  - Q1：你给 Claude 配了一个 `send_email` 工具，但它从来不用，反而经常自己编邮件内容。最可能原因？（description 写得太模糊或没说清楚什么时候该用）
  - Q2：你的 agent 跑了 30 多次还没结束，账单爆了。你应该加什么？（max_iterations / 步数上限 + 在 loop 里检测重复工具调用）
  - Q3：Claude 调用了 `get_order_details(order_id="ABC123")` 但 ABC123 这个订单不存在。Claude 接下来最可能做什么？（再调用别的工具，比如先 `get_customer_info` 找正确订单号；或者向用户回问"您的订单号是不是写错了"）
- [x] **Callout box** — "Aha! Tool use 是 Claude 唯一**真的能改变外部世界**的方式。它写一段文字 ≠ 它发了一封邮件——只有当你真的在 process_tool_call 里调用了发邮件的代码，邮件才会发出去。**你才是动手的那个，Claude 只是动嘴**。"
- [x] **Glossary tooltips**: tool / function calling / JSON Schema / agentic loop / stop_reason / tool_use / tool_result

### Reference Files to Read
- `references/content-philosophy.md` — 全文
- `references/gotchas.md` — 全文
- `references/interactive-elements.md` — Code↔English / Multiple-Choice / Message Flow / Spot the Bug / Pattern Cards / Callout Boxes
- `references/design-system.md` — Color Palette / Module Structure

### Connections
- **Previous module:** 模块 3 讲了 orchestrator 和 evaluator 这两个高阶模式，但还没真正"动手"。
- **Next module:** 模块 5 会上 Claude Agent SDK——把 tool use 这个底层机制封装成"一行代码就能用"的高级 API，并且看看从 research agent 到 SRE agent 的演进。
- **Tone/style notes:**
  - 奇数模块，背景用 `--color-bg-warm`
  - actor 色：用户 = actor-2，Claude = actor-1（teal），工具 = actor-3（plum），你的程序 = actor-4（amber）
  - 该模块约 5 屏：①开场（棋手 + 棋钟隐喻）②工具说明书（翻译块 A + 4 张 pattern card）③agentic loop（翻译块 B + flow animation）④spot the bug（最常见的工具循环 bug）⑤quiz + 收束 callout
