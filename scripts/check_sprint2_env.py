#!/usr/bin/env python3
"""
Sprint 2 开发环境检查脚本
验证Sprint 2开发所需的各项环境和依赖是否就绪
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要3.8+)")
        return False

def check_virtual_env():
    """检查虚拟环境"""
    print("🔍 检查虚拟环境...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境已激活")
        return True
    else:
        print("❌ 虚拟环境未激活")
        return False

def check_required_packages():
    """检查必需的Python包"""
    print("🔍 检查必需的Python包...")
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'sqlalchemy',
        'werkzeug',
        'celery',
        'redis',
        'requests',
        'gitpython',
        'pytest',
        'pytest-cov'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_project_structure():
    """检查项目结构"""
    print("🔍 检查项目结构...")
    required_dirs = [
        'backend/app',
        'backend/app/models',
        'backend/app/services',
        'backend/app/api',
        'backend/app/utils',
        'backend/migrations',
        'backend/tests',
        'frontend/templates',
        'frontend/static',
        'docs',
        'database'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (缺失)")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def check_database():
    """检查数据库配置"""
    print("🔍 检查数据库配置...")
    db_path = Path('backend/instance/coderwiki_dev.db')
    if db_path.exists():
        print("✅ 开发数据库存在")
        return True
    else:
        print("⚠️ 开发数据库不存在，需要初始化")
        return False

def check_git_repo():
    """检查Git仓库"""
    print("🔍 检查Git仓库...")
    if Path('.git').exists():
        print("✅ Git仓库已初始化")
        return True
    else:
        print("❌ Git仓库未初始化")
        return False

def check_redis():
    """检查Redis服务"""
    print("🔍 检查Redis服务...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis服务运行正常")
        return True
    except ImportError:
        print("❌ Redis包未安装")
        return False
    except Exception as e:
        print(f"❌ Redis服务连接失败: {e}")
        return False

def check_celery():
    """检查Celery配置"""
    print("🔍 检查Celery配置...")
    try:
        import celery
        print("✅ Celery包已安装")
        return True
    except ImportError:
        print("❌ Celery包未安装")
        return False

def check_sprint2_readiness():
    """检查Sprint 2特定准备"""
    print("🔍 检查Sprint 2特定准备...")
    
    # 检查Sprint 2文档
    sprint2_docs = [
        'docs/sprints/sprint-2-plan.md',
        'docs/sprints/sprint-2-kickoff-prep.md',
        'docs/sprints/sprint-2-task-board.md'
    ]
    
    for doc in sprint2_docs:
        if Path(doc).exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} (缺失)")
    
    # 检查Git工具
    try:
        import git
        print("✅ GitPython包已安装")
    except ImportError:
        print("❌ GitPython包未安装")
    
    # 检查代码分析工具
    analyzer_path = Path('backend/app/utils/code_analyzer.py')
    if analyzer_path.exists():
        print("✅ 代码分析工具文件存在")
    else:
        print("⚠️ 代码分析工具文件不存在，需要创建")

def generate_report():
    """生成环境检查报告"""
    print("\n" + "="*50)
    print("📊 Sprint 2 开发环境检查报告")
    print("="*50)
    
    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("必需包", check_required_packages),
        ("项目结构", check_project_structure),
        ("数据库", check_database),
        ("Git仓库", check_git_repo),
        ("Redis服务", check_redis),
        ("Celery配置", check_celery)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        if check_func():
            passed += 1
    
    print(f"\n📈 总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 Sprint 2 开发环境已就绪！")
        print("\n🚀 可以开始Sprint 2的开发工作")
        print("\n📋 下一步建议:")
        print("1. 启动Redis服务")
        print("2. 初始化数据库")
        print("3. 开始Story 2.1和2.2的开发")
    else:
        print("⚠️ Sprint 2 开发环境需要完善")
        print(f"\n❌ 有 {total - passed} 项检查未通过")
        print("\n🔧 请先解决上述问题后再开始开发")

def main():
    """主函数"""
    print("🚀 Sprint 2 开发环境检查")
    print("="*50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"📁 项目目录: {os.getcwd()}")
    print()
    
    # 执行各项检查
    generate_report()
    
    print("\n" + "="*50)
    print("检查完成！")

if __name__ == "__main__":
    main()