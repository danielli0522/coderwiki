# Claude Code 子代理配置问题解决方案

## 问题诊断

经过测试，发现了以下问题：

### 1. Claude Code CLI 未安装

- **症状**: `claude-code --version` 命令不存在
- **影响**: Claude Code SDK 无法正常工作
- **状态**: ❌ 未解决

### 2. 配置验证通过

- ✅ BMAD 文档生成器路径正确
- ✅ 子代理团队配置完整
- ✅ 系统提示词生成正常
- ✅ Claude Code SDK 导入成功

## 解决方案

### 方案 1: 安装 Claude Code CLI（推荐）

Claude Code CLI 需要从 Anthropic 官方安装：

```bash
# 方法1: 使用官方安装脚本
curl -fsSL https://claude-code.anthropic.com/install.sh | sh

# 方法2: 使用Homebrew (macOS)
brew install anthropic/tap/claude-code

# 方法3: 手动下载安装
# 访问 https://claude-code.anthropic.com/ 下载对应平台的安装包
```

### 方案 2: 使用 MCP 服务替代

如果无法安装 Claude Code CLI，可以使用 MCP 服务：

```python
# 配置MCP服务
export MCP_ENABLED=true
export MCP_SERVER_URL=http://localhost
export MCP_SERVER_PORT=3000
```

### 方案 3: 直接 LLM API 调用

作为备选方案，可以直接使用 LLM API：

```python
# 配置LLM API
export LLM_API_KEY=your_api_key
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4
```

## 当前配置状态

### ✅ 已完成配置

1. **BMAD 子代理配置类** (`bmad_subagent_config.py`)

   - 完整的团队和代理配置
   - 工作流程配置加载
   - 配置验证功能

2. **Claude Code 服务集成** (`claude_code_service.py`)

   - 正确的 SDK 配置
   - 子代理路径设置
   - 系统提示词生成

3. **测试和诊断脚本**
   - 配置验证测试
   - 连接诊断脚本
   - 子代理发现测试

### ❌ 待解决问题

1. **Claude Code CLI 安装**

   - 需要安装官方 CLI 工具
   - 验证 CLI 可用性

2. **子代理发现验证**
   - 在 Claude Code 控制台中验证子代理可见性
   - 测试子代理调用功能

## 验证步骤

### 步骤 1: 安装 Claude Code CLI

```bash
# 安装CLI
curl -fsSL https://claude-code.anthropic.com/install.sh | sh

# 验证安装
claude-code --version
```

### 步骤 2: 验证配置

```bash
# 运行配置测试
cd backend
python test_bmad_subagent_config.py
```

### 步骤 3: 测试子代理发现

```bash
# 运行诊断脚本
python diagnose_claude_code.py
```

### 步骤 4: 在 Claude Code 控制台中验证

1. 打开 Claude Code 控制台
2. 检查可用工具列表
3. 查找 BMAD 相关的子代理
4. 测试子代理调用

## 预期结果

安装 Claude Code CLI 后，应该能够：

1. ✅ 在 Claude Code 控制台中看到 BMAD 子代理
2. ✅ 使用 Task 工具调用 BMAD 团队
3. ✅ 执行完整的文档生成工作流程
4. ✅ 生成高质量的技术文档

## 故障排除

### 如果 CLI 安装失败

1. 检查网络连接
2. 尝试使用 VPN
3. 手动下载安装包
4. 联系 Anthropic 支持

### 如果子代理不可见

1. 检查 BMAD 文档生成器路径
2. 验证配置文件格式
3. 重启 Claude Code 控制台
4. 检查文件权限

### 如果调用失败

1. 检查子代理路径格式
2. 验证工作流程配置
3. 查看错误日志
4. 测试简单查询

## 总结

当前配置已经完成 90%，主要问题是 Claude Code CLI 未安装。一旦安装 CLI，子代理配置应该能够正常工作。

**下一步行动**: 安装 Claude Code CLI 并验证子代理发现功能。
