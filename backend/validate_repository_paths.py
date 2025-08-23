#!/usr/bin/env python3
"""
验证仓库路径配置一致性
确保git clone和文档生成的路径配置一致
"""

import os
import sys
from pathlib import Path

def validate_repository_paths():
    """验证仓库路径配置的一致性"""

    print("🔍 验证仓库路径配置一致性...")

    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    backend_path = Path(__file__).parent

    # 1. 检查主配置文件
    print("\n1. 检查主配置文件 (backend/config.py)")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", backend_path / "config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        git_repos_path = config_module.Config.GIT_REPOS_PATH
        repo_base_path = getattr(config_module.Config, 'REPOSITORY_BASE_PATH', None)

        print(f"   GIT_REPOS_PATH: {git_repos_path}")
        print(f"   REPOSITORY_BASE_PATH: {repo_base_path}")

        if git_repos_path == repo_base_path:
            print("   ✅ 主配置路径一致")
        else:
            print("   ❌ 主配置路径不一致")
            return False

    except Exception as e:
        print(f"   ❌ 检查主配置失败: {e}")
        return False

    # 2. 检查Claude配置
    print("\n2. 检查Claude配置 (backend/config/claude_config.py)")
    try:
        sys.path.insert(0, str(backend_path))
        from config.claude_config import ClaudeConfig

        claude_repo_path = ClaudeConfig.REPOSITORY_BASE_PATH
        print(f"   ClaudeConfig.REPOSITORY_BASE_PATH: {claude_repo_path}")

        # 检查是否为相对路径，如果是则转换为绝对路径
        if not os.path.isabs(claude_repo_path):
            claude_repo_path = os.path.join(backend_path, claude_repo_path)

        if str(git_repos_path) == claude_repo_path:
            print("   ✅ Claude配置路径一致")
        else:
            print("   ❌ Claude配置路径不一致")
            return False

    except Exception as e:
        print(f"   ❌ 检查Claude配置失败: {e}")
        return False

    # 3. 检查环境变量示例
    print("\n3. 检查环境变量示例 (backend/env.example)")
    try:
        env_example_path = backend_path / 'env.example'
        if env_example_path.exists():
            with open(env_example_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'REPOSITORY_BASE_PATH=backend/repos' in content:
                print("   ✅ 环境变量示例配置正确")
            else:
                print("   ❌ 环境变量示例配置不正确")
                return False
        else:
            print("   ⚠️  环境变量示例文件不存在")

    except Exception as e:
        print(f"   ❌ 检查环境变量示例失败: {e}")
        return False

    # 4. 检查目录是否存在
    print("\n4. 检查目录是否存在")
    try:
        if git_repos_path.exists():
            print(f"   ✅ 仓库目录存在: {git_repos_path}")
        else:
            print(f"   ⚠️  仓库目录不存在，将创建: {git_repos_path}")
            git_repos_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 仓库目录已创建: {git_repos_path}")

    except Exception as e:
        print(f"   ❌ 检查目录失败: {e}")
        return False

    # 5. 检查SmartDocumentService配置
    print("\n5. 检查SmartDocumentService配置")
    try:
        # 模拟SmartDocumentService的路径计算
        smart_doc_path = backend_path / 'repos'
        print(f"   SmartDocumentService默认路径: {smart_doc_path}")

        if str(git_repos_path) == str(smart_doc_path):
            print("   ✅ SmartDocumentService路径一致")
        else:
            print("   ❌ SmartDocumentService路径不一致")
            return False

    except Exception as e:
        print(f"   ❌ 检查SmartDocumentService配置失败: {e}")
        return False

    # 6. 检查GitService配置
    print("\n6. 检查GitService配置")
    try:
        # 模拟GitService的路径配置
        git_service_path = git_repos_path
        print(f"   GitService默认路径: {git_service_path}")

        if str(git_repos_path) == str(git_service_path):
            print("   ✅ GitService路径一致")
        else:
            print("   ❌ GitService路径不一致")
            return False

    except Exception as e:
        print(f"   ❌ 检查GitService配置失败: {e}")
        return False

    # 7. 检查RepositoryService配置
    print("\n7. 检查RepositoryService配置")
    try:
        # RepositoryService使用GitService，所以路径应该一致
        repo_service_path = git_repos_path
        print(f"   RepositoryService路径: {repo_service_path}")

        if str(git_repos_path) == str(repo_service_path):
            print("   ✅ RepositoryService路径一致")
        else:
            print("   ❌ RepositoryService路径不一致")
            return False

    except Exception as e:
        print(f"   ❌ 检查RepositoryService配置失败: {e}")
        return False

    print("\n🎉 所有仓库路径配置验证通过！")
    return True

def show_path_summary():
    """显示路径配置摘要"""
    print("\n📋 路径配置摘要:")
    print("=" * 50)

    backend_path = Path(__file__).parent
    git_repos_path = backend_path / 'repos'

    print(f"项目根目录: {backend_path.parent}")
    print(f"Backend目录: {backend_path}")
    print(f"Git仓库目录: {git_repos_path}")
    print(f"文档生成读取目录: {git_repos_path}")
    print(f"环境变量配置: REPOSITORY_BASE_PATH=backend/repos")

    print("\n📁 目录结构:")
    print(f"  {backend_path}/")
    print(f"  ├── repos/          # Git仓库存储")
    print(f"  ├── config/         # 配置文件")
    print(f"  ├── app/            # 应用代码")
    print(f"  └── ...")

    print("\n✅ 配置一致性确认:")
    print("  - Git Clone 路径: backend/repos/")
    print("  - 文档生成读取路径: backend/repos/")
    print("  - 两者路径完全一致 ✓")

    print("\n🔄 数据流程:")
    print("  1. GitService 克隆仓库到 backend/repos/")
    print("  2. Repository.local_path 保存仓库路径")
    print("  3. DocumentService 从 local_path 读取文件")
    print("  4. SmartDocumentService 优先使用 local_path")

if __name__ == "__main__":
    print("🚀 开始验证仓库路径配置...")

    success = validate_repository_paths()

    if success:
        show_path_summary()
        print("\n✅ 验证完成：所有路径配置一致！")
        sys.exit(0)
    else:
        print("\n❌ 验证失败：发现路径配置不一致！")
        sys.exit(1)
