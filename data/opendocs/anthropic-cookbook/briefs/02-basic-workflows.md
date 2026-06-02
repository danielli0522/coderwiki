# Module 2: 三种最基础的工序——链式 / 路由 / 并行

### Teaching Arc
- **Metaphor:** 现代化奶茶吧台 (modern milk-tea bar)。
  - **Prompt Chaining = 流水线**：茶水间的工人有固定 5 步——煮茶、加糖、加奶、放珍珠、封口，前一步的产物喂给下一步。少一步漏一步，整杯都废。
  - **Routing = 排队分流员**：店员看你点的是水果茶就往左边水果工位送，是奶盖就往右边奶盖工位送。每条窗口的师傅只擅长一种品类，分流让专业的人干专业的事。
  - **Parallelization = 多窗口同时出杯**：你点了 4 杯不同饮料，4 个工位同时开工，最后一起打包。比一个人挨个做快 4 倍。
  - 三种工序都是"奶茶吧台"这一个大隐喻下的子比喻——彼此区别清晰、又有家族相似性。
- **Opening hook:** "上一模块我们看到 Augmented LLM 是基础单元——但一个单元能干的事有限。这一模块要回答的问题是：**当任务太复杂，一个 LLM 一次答不完时，你怎么把多个 LLM 调用编排起来？**Anthropic 工程师在 *Building Effective Agents* 这篇研究里给出了三种最基础的编排方式。"
- **Key insight:** **三种工序对应三种问题形状**。任务能拆成"先 A 再 B 再 C"的固定步骤 → chain。任务一来需要先判类型再处理 → route。任务可以同时处理多个独立子任务 → parallel。**判断哪个工序适合哪类任务，就是 agentic 架构的第一道分水岭。**
- **"Why should I care?":** 当 vibe coder 跟 AI 工具说"帮我做一个客服系统"时，AI 给你的代码大概率是其中之一。能认出"哦这是 routing 模式"，你就能进一步要求："帮我加一条新路由处理退款"，而不是糊涂地复制粘贴。

### Code Snippets (pre-extracted)

**Snippet A — 三个核心函数（来自 `patterns/agents/basic_workflows.ipynb#cell-2`，原代码逐字保留）：**

```python
def chain(input: str, prompts: list[str]) -> str:
    """Chain multiple LLM calls sequentially, passing results between steps."""
    result = input
    for i, prompt in enumerate(prompts, 1):
        print(f"\nStep {i}:")
        result = llm_call(f"{prompt}\nInput: {result}")
        print(result)
    return result
```

中文逐行翻译：
- `def chain(input, prompts):` — 定义一个叫 chain 的"组装机"，吃进一段输入和一串提示词清单。
- `result = input` — 把"当前结果"初始化为最初的用户输入。
- `for i, prompt in enumerate(prompts, 1):` — 按顺序拿每一个 prompt（步骤 1、步骤 2、步骤 3…）。
- `result = llm_call(f"{prompt}\nInput: {result}")` — 关键一行：把"当前结果"塞给下一个 prompt 当输入，再调 LLM。**前一步的输出 = 后一步的输入。**
- `return result` — 全部走完后，把最终产物吐出来。
- 整个 chain 函数一共 5 行有效代码。**这就是 prompt chaining 的全部魔法**。

```python
def parallel(prompt: str, inputs: list[str], n_workers: int = 3) -> list[str]:
    """Process multiple inputs concurrently with the same prompt."""
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(llm_call, f"{prompt}\nInput: {x}") for x in inputs]
        return [f.result() for f in futures]
```

中文逐行翻译：
- `def parallel(prompt, inputs):` — 定义"并发分工机"，吃进 1 个共用 prompt 和 N 个待处理输入。
- `with ThreadPoolExecutor(max_workers=n_workers)` — 开 3 个并发工位（线程池）。
- `futures = [executor.submit(llm_call, ...) for x in inputs]` — 把 N 个任务一次性丢给工位，每位工人都拿到同一份 prompt 但处理不同的输入。
- `return [f.result() for f in futures]` — 等所有工位完工，把结果按顺序收齐返回。
- **关键洞察**：`prompt` 不变，`input` 变。这适合"同样的指令，要处理一堆不同对象"的场景，比如对 100 条评论同时打分。

**Snippet B — Route 函数核心（同文件 `cell-2` 后半部分）：**

```python
def route(input: str, routes: dict[str, str]) -> str:
    """Route input to specialized prompt using content classification."""
    selector_prompt = f"""
    Analyze the input and select the most appropriate support team from these options: {list(routes.keys())}
    First explain your reasoning, then provide your selection in this XML format:
    <reasoning>...</reasoning>
    <selection>The chosen team name</selection>
    Input: {input}""".strip()

    route_response = llm_call(selector_prompt)
    route_key = extract_xml(route_response, "selection").strip().lower()

    selected_prompt = routes[route_key]
    return llm_call(f"{selected_prompt}\nInput: {input}")
```

中文翻译要点：
- 第一次 LLM 调用是"分诊台"——读输入、判断它属于哪一类、用 XML 标签输出选择结果。
- `extract_xml` 从模型输出里把 `<selection>` 标签里的内容拎出来。
- 第二次 LLM 调用是"专科医生"——拿到对应类别的专门 prompt 处理实际工作。
- **两次 LLM 调用，第一次决定"去哪"，第二次干活**。

### Interactive Elements

- [x] **Code↔English translation** — chain 函数 + parallel 函数（两块翻译并列）
- [x] **Pattern cards (3 张)** — Chain / Route / Parallel，每张写"何时用 / 例子 / 不要用"。
- [x] **Message Flow / Data Flow Animation** — 演示 Chain 模式 5 步流水线：
  - actors: `用户输入` / `步骤 1：抽数字` / `步骤 2：转百分比` / `步骤 3：排序` / `步骤 4：转 Markdown 表`
  - steps:
    1. 高亮"用户输入"，label：用户提交一段含数字的报告
    2. 数据包从用户输入飞到步骤 1，label：步骤 1 抽出所有"数值 + 指标"
    3. 数据包从步骤 1 飞到步骤 2，label：步骤 2 把数值统一成百分比
    4. 数据包从步骤 2 飞到步骤 3，label：步骤 3 按数值降序排
    5. 数据包从步骤 3 飞到步骤 4，label：步骤 4 渲染成 Markdown 表
    6. 高亮"步骤 4"，label：完成！返回最终表格
- [x] **Group chat animation** — 演 routing 模式：客户 → 分诊员（Claude） → 三个专员（账单 / 技术 / 安全）
  - 客户：我刷卡被扣了两次钱，请帮我退一次。
  - 分诊员（Claude）：分析中…这是账单类问题。 → 路由到"账单专员"
  - 账单专员：Billing Support Response: 已查到您的重复扣款记录，3 个工作日内退到原卡。
- [x] **Quiz** — 3 道场景题
  - Q1：你要做一个程序，给客户上传的 PDF 自动生成"摘要 → 关键词 → 翻译成英文"。这是 chain / route / parallel？（chain，因为顺序依赖）
  - Q2：你要给一个推文打 5 个不同维度的标签（情绪 / 话题 / 国家 / 是否广告 / 风险）。最佳模式？（parallel，5 个独立子任务）
  - Q3：用户上传一张图，可能是发票、可能是身份证、可能是收据。你要先分类再用对应 prompt 处理。最佳模式？（route）
- [x] **Callout box** — "Aha! 三种模式不是互斥的——真实系统经常是 route → chain → parallel 的嵌套。先按形状判断，再叠在一起。"
- [x] **Glossary tooltips**: prompt / LLM call / 并发 / XML tag / 线程池 / API

### Reference Files to Read
- `references/content-philosophy.md` — 全文
- `references/gotchas.md` — 全文
- `references/interactive-elements.md` — Code↔English / Multiple-Choice / Group Chat / Message Flow / Pattern Cards / Callout Boxes
- `references/design-system.md` — 仅 Color Palette / Module Structure

### Connections
- **Previous module:** 模块 1 已经把"Augmented LLM"这个基础单元讲清楚了。本模块的三种工序，每一种都是"多个 Augmented LLM"之间的不同接线方式。
- **Next module:** 模块 3 会上更高阶的两种——orchestrator-workers（动态拆任务）和 evaluator-optimizer（边写边批改）。它们是"chain + parallel" 的进阶版。
- **Tone/style notes:**
  - 模块 2 是奇数模块，背景用 `--color-bg-warm`。
  - Actor 色：用户 = actor-2（vermillion），分诊员/orchestrator = actor-1（teal），三个专员各取 actor-3/4/5。
  - 这是全课"硬核度"最高的模块之一，但要保持"奶茶吧台"的隐喻贯穿——不要中途切到别的隐喻。
  - 该模块约 6 屏：①开场（奶茶吧台 + 三种工序对照）②chain 详解（含翻译块 + 流程动画）③parallel 详解（含翻译块 + 真实示例）④route 详解（含群聊动画）⑤callout：三种模式可嵌套 ⑥quiz
