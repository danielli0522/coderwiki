#!/usr/bin/env bash
# MVP版本的knowledge同步脚本
# 将knowledge目录的核心信息同步到CLAUDE.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MVP_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$MVP_DIR")"
KNOWLEDGE_DIR="$MVP_DIR/knowledge"
CLAUDE_FILE="$REPO_ROOT/CLAUDE.md"

echo "=== Knowledge Sync MVP版本 ==="
echo "Knowledge目录: $KNOWLEDGE_DIR"
echo "目标文件: $CLAUDE_FILE"

# 检查knowledge目录是否存在
if [[ ! -d "$KNOWLEDGE_DIR" ]]; then
    echo "❌ Knowledge目录不存在: $KNOWLEDGE_DIR"
    exit 1
fi

# 备份原CLAUDE.md
if [[ -f "$CLAUDE_FILE" ]]; then
    cp "$CLAUDE_FILE" "$CLAUDE_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✓ 已备份原CLAUDE.md"
fi

# 提取architecture信息
extract_architecture_summary() {
    local arch_file="$KNOWLEDGE_DIR/architecture/system-overview.md"
    if [[ -f "$arch_file" ]]; then
        echo "## 🏗️ 系统架构速览"
        echo ""
        # 提取核心组件职责部分
        sed -n '/## 核心组件职责/,/## 数据流向/p' "$arch_file" | sed '$d'
        echo ""
        # 提取关键设计决策
        sed -n '/## 关键设计决策/,/## 部署架构/p' "$arch_file" | sed '$d'
        echo ""
    fi
}

# 提取business信息
extract_business_summary() {
    local business_file="$KNOWLEDGE_DIR/business/domain-model.md"
    if [[ -f "$business_file" ]]; then
        echo "## 💼 核心业务域"
        echo ""
        # 提取核心实体部分
        sed -n '/## 核心实体/,/## 业务流程/p' "$business_file" | sed '$d'
        echo ""
    fi
}

# 提取patterns信息
extract_patterns_summary() {
    local patterns_file="$KNOWLEDGE_DIR/patterns/common-patterns.md"
    if [[ -f "$patterns_file" ]]; then
        echo "## 🎨 常用代码模式"
        echo ""
        echo "### API端点模式"
        echo "- 参考: \`backend/app/api/repository.py\`"
        echo "- 模式: REST API + 统一错误处理 + 权限验证"
        echo ""
        echo "### 服务层模式"
        echo "- 参考: \`backend/app/services/repository_service.py\`"
        echo "- 模式: 业务逻辑封装 + 数据验证 + 事务管理"
        echo ""
        echo "### 数据模型模式"
        echo "- 参考: \`backend/app/models/repository.py\`"
        echo "- 模式: SQLAlchemy ORM + 审计字段 + 关系定义"
        echo ""
        echo "### 测试模式"
        echo "- 参考: \`backend/tests/unit/test_repository_model.py\`"
        echo "- 模式: pytest + factories + 分层测试"
        echo ""
    fi
}

# 生成增强的CLAUDE.md
generate_enhanced_claude_md() {
    cat > "$CLAUDE_FILE" << 'EOF'
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目架构

CoderWiki 是一个基于 Flask 的智能代码文档生成与管理平台：

### 核心组件结构
- **backend/app/**: Flask 应用核心
  - `api/`: REST API 接口（认证、仓库管理、文档生成）
  - `models/`: SQLAlchemy 数据模型（用户、仓库、文档等）
  - `services/`: 业务逻辑层（仓库服务、分析服务）
  - `utils/`: 工具模块（代码分析引擎、AI客户端、Git服务等）
  - `routes/`: 页面路由
- **frontend/**: 前端静态资源和模板
- **bmad-docs-generator/**: 智能文档生成系统
- **coderwiki-output-docs/**: 生成的文档输出目录

### 关键技术栈
- Flask 2.3.3 + SQLAlchemy（ORM）
- 数据库：SQLite（开发）/ MySQL（生产）
- AI集成：OpenAI GPT + Anthropic Claude
- 前端：Bootstrap 5 + 原生JavaScript

EOF

    # 添加从knowledge提取的信息
    extract_architecture_summary >> "$CLAUDE_FILE"
    extract_business_summary >> "$CLAUDE_FILE"
    extract_patterns_summary >> "$CLAUDE_FILE"

    # 添加常用命令部分
    cat >> "$CLAUDE_FILE" << 'EOF'

## 常用命令

### 开发环境启动
```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 启动应用（推荐端口5001，避免AirPlay冲突）
python run.py
# 或指定端口
PORT=5002 python run.py
```

### 数据库操作
```bash
cd backend
python init_db.py              # 初始化数据库
python create_default_user.py  # 创建默认用户
python manage_users.py list    # 查看用户列表
```

### 测试
```bash
cd backend
python -m pytest tests/unit/        # 单元测试
python -m pytest tests/integration/ # 集成测试
python -m pytest tests/e2e/         # 端到端测试
```

### 代码质量检查
```bash
ruff check .     # 代码检查
black .          # 代码格式化
```

### 诊断工具
```bash
python scripts/diagnose_api_quota.py  # API配额诊断
```

## 开发注意事项

### 目录约定
- **temp/**: 临时生成的文件（测试、诊断）- 不提交到git
- **logs/**: 应用日志文件
- **coderwiki-output-docs/**: 文档生成输出目录

### 重要服务模块
- `app/utils/code_analysis_engine.py`: 核心代码分析引擎
- `app/utils/llm_client.py`: AI客户端封装
- `app/services/repository_service.py`: 仓库管理核心逻辑
- `app/utils/git_service.py`: Git操作封装

### 配置管理
- 开发配置：`backend/app/config.py`
- 环境变量：`.env`文件（参考`.env.example`）
- 生产配置：使用环境变量覆盖

### API端点
- 认证：`/api/auth/*`
- 仓库管理：`/api/repositories/*`
- 文档生成：`/api/repositories/{id}/generate`

### 默认账户（开发环境）
- 管理员：admin/admin123
- 演示用户：demo/demo123
- 测试用户：testuser/test123

### 错误处理
- 同一类缺陷修复3次还没搞定，应该呼叫架构师进行Review
- 临时生成的bug fix的测试文本和诊断方案放在temp目录

## Knowledge Base集成

本项目已集成MVP版本的knowledge base系统：
- **Knowledge目录**: `.speckit-mvp/knowledge/`
- **同步脚本**: `.speckit-mvp/scripts/knowledge-sync.sh`
- **自动更新**: 通过脚本将knowledge信息同步到本文件

### Knowledge结构
- `architecture/`: 系统架构和技术决策
- `business/`: 业务领域模型和流程
- `patterns/`: 常用代码模式和最佳实践

---
*本文件由knowledge-sync.sh自动更新，手动修改可能会被覆盖*
*最后更新: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

}

# 主执行流程
main() {
    echo "📝 开始生成增强版CLAUDE.md..."

    generate_enhanced_claude_md

    echo "✅ Knowledge同步完成！"
    echo ""
    echo "📄 已更新: $CLAUDE_FILE"
    echo "📁 Knowledge源: $KNOWLEDGE_DIR"
    echo ""
    echo "🔍 查看效果:"
    echo "   head -50 $CLAUDE_FILE"
    echo ""
    echo "🚀 测试AI效果:"
    echo "   1. 询问AI项目架构"
    echo "   2. 让AI推荐代码模式"
    echo "   3. 请AI帮助新增功能"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi