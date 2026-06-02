# Module 3: 高阶工序——调度官 与 评审官

### Teaching Arc
- **Metaphor:** 纪录片摄制组 (documentary film crew)。
  - **Orchestrator-Workers = 总导演 + 摄影组**：总导演拿到选题后**不预先写好剧本**，而是看现场情况——这场戏值得拍人物特写、拍空镜、还是拍延时？决定后分别派摄影 A、B、C 去拍。每位摄影只负责自己那个镜头，导演最后剪辑成片。
  - **Evaluator-Optimizer = 编剧 + 责编**：编剧写一稿初稿交给责编。责编不动笔，只给反馈："角色动机不清楚 / 第二幕太拖"。编剧拿反馈再改一稿，再交。来回三五次，直到责编打 PASS。
- **Opening hook:** "上一模块的 chain / route / parallel 都有一个共同假设——你提前知道任务的形状。但现实世界里，**有时候你看到任务的瞬间才知道该怎么拆**。模块 3 教的就是处理'未知形状'任务的两种最重要工序。"
- **Key insight:**
  - **Orchestrator** 解决的是"任务到手才知道要拆几瓣、怎么拆"——一个 LLM 当导演动态决策，再派工人去执行。
  - **Evaluator-Optimizer** 解决的是"一次答不对，需要反复打磨"——两个 LLM 互相博弈，一个生成、一个评审，直到达标为止。
  - 两者的共同点：**多了一层"元认知"**——前者是"先想再分"，后者是"先做再批"。这一层就是 agentic system 的核心智慧。
- **"Why should I care?":** 当 vibe coder 让 AI 写一段长文档、做一个市场报告、生成多个变体素材时，**未来主流的"高质量代理产品"基本都是 orchestrator + evaluator 的组合**。理解这两个模式，你就能在产品里指着说"这部分应该加一个评审循环"或"这部分应该用 orchestrator 拆"——这是上市公司 CTO 在和工程团队对话时的标准词汇。

### Code Snippets (pre-extracted)

**Snippet A — Orchestrator 的 prompt 模板（来自 `patterns/agents/orchestrator_workers.ipynb#cell-4`）：**

```python
ORCHESTRATOR_PROMPT = """
Analyze this task and break it down into 2-3 distinct approaches:

Task: {task}

Return your response in this format:

<analysis>
Explain your understanding of the task and which variations would be valuable.
Focus on how each approach serves different aspects of the task.
</analysis>

<tasks>
    <task>
    <type>formal</type>
    <description>Write a precise, technical version that emphasizes specifications</description>
    </task>
    <task>
    <type>conversational</type>
    <description>Write an engaging, friendly version that connects with readers</description>
    </task>
</tasks>
"""
```

中文翻译要点（这是 prompt 不是代码，做"prompt↔解读"翻译块）：
- "Analyze this task and break it down into 2-3 distinct approaches" — 让 Claude 当导演：**看完任务后给我列 2-3 种切入角度**。注意是"distinct"——必须有差异。
- `<analysis>` — 强制导演先讲"为什么这么拆"，避免它跳过思考直接出方案。
- `<tasks><task><type><description>` — 用 XML 标签强约束输出结构，方便后续程序解析。**这是 LLM 编排的标准技巧：用 XML 当结构化合同。**
- 整个 prompt 的核心是"动态拆任务"——具体拆几个、拆什么风格，由 Claude 看到 task 时自己决定。

**Snippet B — Orchestrator 主循环骨架（同文件 `cell-2` 摘取关键段）：**

```python
class FlexibleOrchestrator:
    def process(self, task: str, context: dict | None = None) -> dict:
        # Step 1: Get orchestrator response
        orchestrator_input = self._format_prompt(self.orchestrator_prompt, task=task, **context)
        orchestrator_response = llm_call(orchestrator_input, model=self.model)

        # Parse orchestrator response
        analysis = extract_xml(orchestrator_response, "analysis")
        tasks_xml = extract_xml(orchestrator_response, "tasks")
        tasks = parse_tasks(tasks_xml)

        # Step 2: Process each task
        worker_results = []
        for i, task_info in enumerate(tasks, 1):
            worker_input = self._format_prompt(
                self.worker_prompt,
                original_task=task,
                task_type=task_info["type"],
                task_description=task_info["description"],
            )
            worker_response = llm_call(worker_input, model=self.model)
            worker_results.append({"type": task_info["type"], "result": worker_response})

        return {"analysis": analysis, "worker_results": worker_results}
```

中文逐行翻译：
- `orchestrator_response = llm_call(orchestrator_input, ...)` — 第一次 LLM 调用：导演看任务、决定怎么拆。
- `tasks = parse_tasks(tasks_xml)` — 把导演吐出来的 XML 解析成程序能用的"工单清单"。
- `for task_info in tasks:` — 对每张工单派一个工人。
- `worker_response = llm_call(worker_input, ...)` — 第 N 次 LLM 调用（N = 工单数）：每个工人独立完成自己那一份。
- 整个流程：**1 次导演 + N 次工人 = N+1 次 LLM 调用**。比 parallel 多了那一次"导演看现场"的元认知。

**Snippet C — Evaluator-Optimizer 主循环（来自 `patterns/agents/evaluator_optimizer.ipynb#cell-1`）：**

```python
def loop(task: str, evaluator_prompt: str, generator_prompt: str) -> tuple[str, list[dict]]:
    """Keep generating and evaluating until requirements are met."""
    memory = []
    chain_of_thought = []

    thoughts, result = generate(generator_prompt, task)
    memory.append(result)
    chain_of_thought.append({"thoughts": thoughts, "result": result})

    while True:
        evaluation, feedback = evaluate(evaluator_prompt, result, task)
        if evaluation == "PASS":
            return result, chain_of_thought

        context = "\n".join(
            ["Previous attempts:", *[f"- {m}" for m in memory], f"\nFeedback: {feedback}"]
        )

        thoughts, result = generate(generator_prompt, task, context)
        memory.append(result)
        chain_of_thought.append({"thoughts": thoughts, "result": result})
```

中文逐行翻译：
- `memory = []` — 准备一本"草稿本"，记下每一稿。
- `thoughts, result = generate(generator_prompt, task)` — 编剧先写第一稿。
- `while True:` — 进入打磨循环。
- `evaluation, feedback = evaluate(...)` — 责编看稿，吐出"通过 / 还要改"以及具体反馈。
- `if evaluation == "PASS": return result` — 责编满意了，交付。
- `context = "...Previous attempts...Feedback..."` — 把所有历史草稿和最新反馈打包，告诉编剧"这些你已经写过了，现在按这个反馈改"。
- `thoughts, result = generate(generator_prompt, task, context)` — 编剧带着批注再写一稿。
- 循环直到 PASS。**两个 LLM 互相博弈，自动改稿。**

### Interactive Elements

- [x] **Code↔English translation** — 选 Snippet B（Orchestrator 主循环）+ Snippet C（Evaluator 循环）做两个翻译块
- [x] **Group Chat Animation** — 演 Evaluator-Optimizer 写一个 Min-Stack 的过程：
  - 用户：写一个 push/pop/getMin 都 O(1) 的栈。
  - 编剧（Generator）：第 1 稿——用一个栈 + 每次 getMin 扫一遍找最小值。
  - 责编（Evaluator）：NEEDS_IMPROVEMENT。getMin 是 O(n)，不达标。
  - 编剧（Generator）：第 2 稿——加一个 minStack 同步存当前最小值。
  - 责编（Evaluator）：PASS！三个操作都是 O(1)。
- [x] **Numbered step cards** — Orchestrator 工作流的 4 步（看任务 → 拆任务 → 派工人 → 汇总）
- [x] **Callout box** — "Aha! orchestrator 和 parallel 长得很像——都是'同时跑多个 LLM'。差别在哪？parallel 的工人**任务清单是写死的**，orchestrator 的工人**任务清单是导演现场决定的**。这一字之差，让系统从'流水线'变成了'团队'。"
- [x] **Quiz** — 3 道架构决策题
  - Q1：你要给同一个产品生成 3 种风格的营销文案：技术控版、文艺版、网红版。Orchestrator 还是 Parallel？（Parallel 就够——3 个风格是写死的；除非要让 LLM 自己决定"这个产品适合哪 3 种风格"才用 Orchestrator）
  - Q2：你要让 AI 写一篇高质量的长文，并且严格控制语调。最适合的是 chain / orchestrator / evaluator-optimizer？（Evaluator-optimizer——长文需要多轮打磨）
  - Q3：你的 evaluator 一直说 NEEDS_IMPROVEMENT，循环跑了 20 次还没 PASS，账单爆炸。你应该做什么？（设最大轮数 + 检测"反馈是否在重复"——这是真实生产 bug）
- [x] **Glossary tooltips**: orchestrator / worker / agentic loop / 元认知 / XML tag / chain of thought

### Reference Files to Read
- `references/content-philosophy.md` — 全文
- `references/gotchas.md` — 全文
- `references/interactive-elements.md` — Code↔English / Multiple-Choice / Group Chat / Numbered Step Cards / Callout Boxes
- `references/design-system.md` — 仅 Color Palette / Module Structure

### Connections
- **Previous module:** 模块 2 教了三种"基础工序"——chain / route / parallel。
- **Next module:** 模块 4 切到 Tool Use（工具调用）——上层是 agentic 模式，下层落地到 LLM 怎么真的"动手"调用一个外部函数。
- **Tone/style notes:**
  - 偶数模块，背景用 `--color-bg`（默认）
  - actor 色分配：用户/输入 = actor-2，导演/编剧 = actor-1（teal），工人/责编 = actor-3 或 actor-4
  - 该模块约 5 屏：①开场（摄制组隐喻 + orchestrator vs parallel 对比）②orchestrator prompt 设计（翻译块 A）③orchestrator 主循环（翻译块 B + step cards）④evaluator-optimizer（翻译块 C + 群聊动画）⑤quiz + 收束 callout
