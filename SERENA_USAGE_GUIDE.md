# Serena 使用指南

## 概述

Serena 是 Anthropic 开发的一个专业 AI 助手，专门帮助开发者和技术团队。本指南将详细介绍如何在 Claude 和 CoderWiki 项目中使用 Serena。

## 在 Claude 中使用 Serena

### 1. 直接对话方式

在 Claude 的对话界面中，您可以直接与 Serena 交互：

```
用户：你好Serena，我需要帮助优化我的Python代码

Serena：你好！我是Serena，很高兴为你提供帮助。请分享你的代码，我会帮你分析并提供优化建议。
```

### 2. 通过 Claude Code SDK

如果您有 Claude Code SDK 访问权限，可以通过以下方式使用 Serena：

```python
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

# 配置Serena作为系统提示
system_prompt = """
你是Serena，一个专业的AI助手，专门帮助开发者和技术团队：
- 代码分析与优化
- 文档生成协助
- 技术架构分析
- 问题诊断
- 最佳实践推荐
"""

options = ClaudeCodeOptions(
    system_prompt=system_prompt,
    max_turns=10,
    allowed_tools=["Read", "Grep", "WebSearch", "Task"]
)

async with ClaudeSDKClient(options=options) as client:
    response = await client.chat("请帮我分析这段代码的性能问题")
```

## 在 CoderWiki 项目中使用 Serena

### 1. 环境配置

确保您的环境变量配置正确：

```bash
# Claude API配置
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export CLAUDE_CODE_WORKSPACE_ID="your-workspace-id"

# Serena服务配置
export SERENA_ENABLED="true"
```

### 2. API 端点使用

#### 获取 Serena 状态

```bash
curl -X GET http://localhost:5001/api/serena/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 获取 Serena 协助

```bash
curl -X POST http://localhost:5001/api/serena/assist \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "请帮我分析这个Flask应用的安全性",
    "context": {
      "project_type": "web_application",
      "framework": "flask",
      "language": "python"
    }
  }'
```

#### 代码优化

```bash
curl -X POST http://localhost:5001/api/serena/optimize-code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "code_content": "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
    "language": "python"
  }'
```

#### 文档生成

```bash
curl -X POST http://localhost:5001/api/serena/generate-docs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_info": {
      "name": "CoderWiki",
      "description": "智能代码文档生成与管理平台",
      "technology_stack": ["Flask", "Python", "MySQL", "Bootstrap"],
      "doc_type": "technical_architecture"
    }
  }'
```

#### 与 Serena 对话

```bash
curl -X POST http://localhost:5001/api/serena/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "我的项目遇到了性能问题，你能帮我分析一下吗？",
    "history": [],
    "session_id": "session_123"
  }'
```

### 3. 前端集成示例

#### JavaScript 客户端

```javascript
// Serena API客户端
class SerenaClient {
  constructor(baseUrl = "/api/serena") {
    this.baseUrl = baseUrl;
  }

  async getStatus() {
    const response = await fetch(`${this.baseUrl}/status`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    return response.json();
  }

  async getAssistance(query, context = {}) {
    const response = await fetch(`${this.baseUrl}/assist`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, context }),
    });
    return response.json();
  }

  async optimizeCode(codeContent, language = "python") {
    const response = await fetch(`${this.baseUrl}/optimize-code`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code_content: codeContent, language }),
    });
    return response.json();
  }

  async generateDocs(projectInfo) {
    const response = await fetch(`${this.baseUrl}/generate-docs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ project_info: projectInfo }),
    });
    return response.json();
  }

  async chat(message, history = [], sessionId = null) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history,
        session_id: sessionId,
      }),
    });
    return response.json();
  }
}

// 使用示例
const serena = new SerenaClient();

// 获取协助
serena.getAssistance("请帮我优化这个数据库查询").then((response) => {
  if (response.success) {
    console.log("Serena建议:", response.response);
  }
});

// 代码优化
const codeToOptimize = `
def slow_function(n):
    result = 0
    for i in range(n):
        result += i
    return result
`;

serena.optimizeCode(codeToOptimize, "python").then((response) => {
  if (response.success) {
    console.log("优化建议:", response.response);
  }
});
```

#### HTML 界面示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Serena AI助手</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
  </head>
  <body>
    <div class="container mt-5">
      <div class="row">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h5>与Serena对话</h5>
            </div>
            <div class="card-body">
              <div
                id="chat-messages"
                class="mb-3"
                style="height: 400px; overflow-y: auto;"
              >
                <!-- 消息将在这里显示 -->
              </div>
              <div class="input-group">
                <input
                  type="text"
                  id="message-input"
                  class="form-control"
                  placeholder="输入你的问题..."
                />
                <button class="btn btn-primary" onclick="sendMessage()">
                  发送
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <h5>Serena能力</h5>
            </div>
            <div class="card-body">
              <ul id="capabilities-list">
                <!-- 能力列表将在这里显示 -->
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script>
      const serena = new SerenaClient();
      let conversationHistory = [];

      // 加载Serena能力
      async function loadCapabilities() {
        try {
          const response = await serena.getStatus();
          if (response.success) {
            const capabilities = response.data.capabilities;
            const list = document.getElementById("capabilities-list");
            list.innerHTML = capabilities
              .map((cap) => `<li>${cap}</li>`)
              .join("");
          }
        } catch (error) {
          console.error("加载能力列表失败:", error);
        }
      }

      // 发送消息
      async function sendMessage() {
        const input = document.getElementById("message-input");
        const message = input.value.trim();

        if (!message) return;

        // 添加用户消息到界面
        addMessage("user", message);
        input.value = "";

        try {
          const response = await serena.chat(message, conversationHistory);
          if (response.success) {
            addMessage("serena", response.response);
            conversationHistory.push({ role: "user", content: message });
            conversationHistory.push({
              role: "assistant",
              content: response.response,
            });
          } else {
            addMessage("error", "抱歉，我遇到了一些问题，请稍后再试。");
          }
        } catch (error) {
          console.error("发送消息失败:", error);
          addMessage("error", "网络错误，请检查连接。");
        }
      }

      // 添加消息到界面
      function addMessage(sender, content) {
        const messagesDiv = document.getElementById("chat-messages");
        const messageDiv = document.createElement("div");
        messageDiv.className = `mb-2 p-2 rounded ${
          sender === "user" ? "bg-primary text-white" : "bg-light"
        }`;
        messageDiv.style.textAlign = sender === "user" ? "right" : "left";
        messageDiv.textContent = content;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      }

      // 页面加载时初始化
      document.addEventListener("DOMContentLoaded", () => {
        loadCapabilities();

        // 回车发送消息
        document
          .getElementById("message-input")
          .addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          });
      });
    </script>
  </body>
</html>
```

## Serena 的核心能力

### 1. 代码分析与优化

- 性能瓶颈识别
- 代码质量评估
- 重构建议
- 最佳实践推荐

### 2. 文档生成协助

- 技术文档生成
- API 文档编写
- 架构文档创建
- 用户手册制作

### 3. 技术架构分析

- 系统架构评估
- 设计模式建议
- 技术选型指导
- 扩展性分析

### 4. 问题诊断

- 错误分析
- 性能问题诊断
- 安全漏洞识别
- 调试建议

### 5. 最佳实践推荐

- 编码规范
- 设计原则
- 安全最佳实践
- 性能优化技巧

## 使用技巧

### 1. 提供详细上下文

当向 Serena 提问时，提供尽可能详细的上下文信息：

```
❌ 不好的提问：我的代码有问题，能帮我看看吗？

✅ 好的提问：我的Flask应用在处理大量并发请求时响应很慢，这是相关的代码片段和错误日志...
```

### 2. 明确具体需求

清楚地说明您希望 Serena 帮助您解决什么问题：

```
❌ 模糊的需求：帮我优化代码

✅ 明确的需求：请帮我优化这个数据库查询的性能，当前查询需要5秒才能返回结果
```

### 3. 提供完整信息

包括相关的代码、错误信息、环境信息等：

```python
# 提供完整的代码片段
def problematic_function():
    # 您的代码
    pass

# 提供错误信息
# 错误日志：...
# 环境信息：Python 3.8, Flask 2.0, MySQL 8.0
```

## 常见使用场景

### 1. 代码审查

```python
# 向Serena请求代码审查
query = """
请帮我审查这段代码，重点关注：
1. 性能问题
2. 安全问题
3. 代码质量
4. 最佳实践

代码：
[您的代码]
"""
```

### 2. 架构设计

```python
# 向Serena请求架构建议
query = """
我正在设计一个电商系统，需要支持：
- 用户管理
- 商品管理
- 订单处理
- 支付集成
- 库存管理

请帮我设计系统架构，包括：
1. 技术选型
2. 系统架构图
3. 数据库设计
4. API设计
"""
```

### 3. 问题诊断

```python
# 向Serena请求问题诊断
query = """
我的应用遇到了以下问题：
- 错误信息：[错误详情]
- 发生场景：[具体场景]
- 相关代码：[代码片段]
- 环境信息：[环境详情]

请帮我分析可能的原因和解决方案。
"""
```

## 注意事项

1. **API 限制**：注意 Claude API 的调用限制和配额
2. **敏感信息**：不要在对话中分享敏感信息如 API 密钥、密码等
3. **代码安全**：确保分享的代码不包含敏感信息
4. **响应时间**：复杂问题可能需要较长的处理时间
5. **结果验证**：始终验证 Serena 的建议是否符合您的具体需求

## 故障排除

### 常见问题

1. **API 调用失败**

   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 验证 API 配额是否充足

2. **响应质量不佳**

   - 提供更详细的上下文信息
   - 明确具体的问题和需求
   - 尝试重新表述问题

3. **服务不可用**
   - 检查 Serena 服务状态
   - 确认环境配置正确
   - 查看错误日志

### 获取帮助

如果您在使用 Serena 时遇到问题，可以：

1. 查看项目文档
2. 检查错误日志
3. 联系技术支持
4. 在社区论坛寻求帮助

---

_本指南将随着 Serena 功能的更新而持续更新。_

