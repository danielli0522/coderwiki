# API 配额问题故障排除指南

## 问题描述

您遇到的错误：

```
API Error: 429 {"type":"error","error":{"type":"1113","message":"Insufficient balance or no resource package. Please recharge."}}
```

这是一个**HTTP 429 错误**，表示"请求过多"或"配额不足"。

## 错误分析

### 错误代码含义

- **HTTP 429**: "Too Many Requests" - 请求频率过高或配额已用完
- **错误类型 1113**: 特定错误代码，表示账户余额不足
- **消息**: "Insufficient balance or no resource package. Please recharge." - 余额不足，需要充值

### 可能的原因

1. **API 配额已用完** - 达到了月度/使用限制
2. **账户余额不足** - API 账户需要充值
3. **请求频率过高** - 短时间内发送了太多请求
4. **API 密钥未配置** - 环境变量未正确设置

## 解决方案

### 1. 立即解决方案

#### 检查 API 密钥配置

```bash
# 运行诊断工具
python scripts/diagnose_api_quota.py
```

#### 设置环境变量

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-openai-api-key-here"

# 设置Anthropic API密钥
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# 或者设置通用LLM API密钥
export LLM_API_KEY="your-llm-api-key-here"
```

#### 检查 API 账户状态

1. **OpenAI**: 访问 https://platform.openai.com/usage
2. **Anthropic**: 访问 https://console.anthropic.com/

### 2. 长期解决方案

#### 实施缓存机制

```python
# 在LLMService中添加缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_chat(self, prompt: str) -> str:
    return self.client.chat(prompt)
```

#### 使用更经济的模型

```bash
# 设置更经济的模型
export LLM_MODEL="gpt-3.5-turbo"  # 比GPT-4便宜很多
export LLM_MODEL="claude-3-haiku-20240307"  # Anthropic最经济的模型
```

#### 实现请求限流

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    def can_make_request(self) -> bool:
        now = time.time()
        # 清理过期的请求记录
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

### 3. 成本优化策略

#### 模型成本对比

| 模型            | 输入成本/1K tokens | 输出成本/1K tokens | 推荐场景           |
| --------------- | ------------------ | ------------------ | ------------------ |
| gpt-3.5-turbo   | $0.0015            | $0.002             | 日常对话、简单任务 |
| gpt-4           | $0.03              | $0.06              | 复杂分析、创意写作 |
| claude-3-haiku  | $0.00025           | $0.00125           | 最经济的选择       |
| claude-3-sonnet | $0.003             | $0.015             | 平衡性能和成本     |

#### 优化建议

1. **使用更小的 max_tokens 值**
2. **实现响应缓存**
3. **批量处理请求**
4. **监控使用情况**
5. **设置使用量告警**

## 预防措施

### 1. 监控和告警

```python
# 在LLMService中添加使用量监控
def track_usage(self, tokens_used: int, cost: float):
    # 记录使用情况
    logger.info(f"API调用: {tokens_used} tokens, 成本: ${cost:.4f}")

    # 检查是否接近限制
    if self.daily_usage > self.daily_limit * 0.8:
        logger.warning("接近每日使用限制!")
```

### 2. 错误处理改进

```python
# 在LLMClient中添加更好的错误处理
def handle_quota_error(self, error_response: dict):
    if error_response.get('error', {}).get('type') == '1113':
        # 余额不足，切换到备用模型或本地模型
        return self.fallback_to_local_model()
    elif error_response.get('status_code') == 429:
        # 频率限制，等待后重试
        time.sleep(60)  # 等待1分钟
        return self.retry_request()
```

### 3. 备用方案

```python
# 实现本地模型作为备用
class LocalModelFallback:
    def __init__(self):
        self.local_model = self.load_local_model()

    def generate_response(self, prompt: str) -> str:
        # 使用本地模型生成响应
        return self.local_model.generate(prompt)
```

## 常见问题

### Q: 如何检查当前 API 使用情况？

A: 运行诊断工具：

```bash
python scripts/diagnose_api_quota.py
```

### Q: 如何降低 API 成本？

A:

1. 使用更经济的模型（gpt-3.5-turbo 或 claude-3-haiku）
2. 实现响应缓存
3. 减少 max_tokens 设置
4. 批量处理请求

### Q: 如何处理 429 错误？

A:

1. 检查账户余额
2. 减少请求频率
3. 实现重试机制
4. 使用备用模型

### Q: 如何设置使用量告警？

A: 在代码中添加监控：

```python
if daily_usage > daily_limit * 0.8:
    send_alert("API使用量接近限制")
```

## 相关资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [项目架构文档](docs/ARCHITECTURE.md)
- [API 配额管理工具](backend/app/utils/api_quota_manager.py)

## 联系支持

如果问题仍然存在，请：

1. 检查 API 提供商的状态页面
2. 联系 API 提供商的客户支持
3. 查看项目的 GitHub Issues
4. 联系项目维护团队

