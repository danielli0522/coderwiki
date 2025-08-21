#!/usr/bin/env python3
"""
开发环境检查脚本
用于验证所有开发环境组件是否正确安装和配置
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 符合要求")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.8+")
        return False


def check_pip():
    """检查pip"""
    print("\n📦 检查pip...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pip_version = result.stdout.strip()
            print(f"✅ {pip_version}")
            return True
        else:
            print("❌ pip未正确安装")
            return False
    except Exception as e:
        print(f"❌ pip检查失败: {e}")
        return False


def check_virtualenv():
    """检查虚拟环境"""
    print("\n🏠 检查虚拟环境...")
    venv_path = Path(sys.prefix)
    if 'venv' in str(venv_path) or 'env' in str(venv_path):
        print(f"✅ 虚拟环境已激活: {venv_path}")
        return True
    else:
        print("❌ 虚拟环境未激活")
        return False


def check_packages():
    """检查关键Python包"""
    print("\n📚 检查Python包...")
    required_packages = [
        'flask',
        'sqlalchemy',
        'pytest',
        'black',
        'flake8',
        'isort'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', '未知版本')
            print(f"✅ {package}: {version}")
        except ImportError:
            print(f"❌ {package}: 未安装")
            all_good = False
    
    return all_good


def check_mysql():
    """检查MySQL"""
    print("\n🗄️ 检查MySQL...")
    try:
        # 检查MySQL版本
        result = subprocess.run(['mysql', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            mysql_version = result.stdout.strip()
            print(f"✅ {mysql_version}")
            
            # 检查项目数据库连接
            try:
                db_result = subprocess.run([
                    'mysql', '-u', 'coderwiki_user', 
                    '-pcoderwiki_password', 'coderwiki', 
                    '-e', 'SELECT 1;'
                ], capture_output=True, text=True)
                if db_result.returncode == 0:
                    print("✅ 项目数据库连接成功")
                    return True
                else:
                    print("❌ 项目数据库连接失败")
                    return False
            except Exception as e:
                print(f"❌ 项目数据库连接失败: {e}")
                return False
        else:
            print("❌ MySQL未安装或未在PATH中")
            return False
    except FileNotFoundError:
        print("❌ MySQL未安装或未在PATH中")
        return False
    except Exception as e:
        print(f"❌ MySQL检查失败: {e}")
        return False


def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    required_dirs = [
        'backend',
        'frontend',
        'docs',
        'venv'
    ]
    
    required_files = [
        'requirements.txt',
        'requirements-dev.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'setup.cfg',
        'pyproject.toml'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ 目录: {dir_name}")
        else:
            print(f"❌ 目录: {dir_name}")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ 文件: {file_name}")
        else:
            print(f"❌ 文件: {file_name}")
            all_good = False
    
    return all_good


def check_git():
    """检查Git"""
    print("\n🔧 检查Git...")
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            git_version = result.stdout.strip()
            print(f"✅ {git_version}")
            
            # 检查是否为Git仓库
            if Path('.git').exists():
                print("✅ Git仓库已初始化")
                return True
            else:
                print("❌ 当前目录不是Git仓库")
                return False
        else:
            print("❌ Git未安装")
            return False
    except FileNotFoundError:
        print("❌ Git未安装")
        return False
    except Exception as e:
        print(f"❌ Git检查失败: {e}")
        return False


def check_code_quality_tools():
    """检查代码质量工具"""
    print("\n🔍 检查代码质量工具...")
    tools = [
        ('black', 'black --version'),
        ('flake8', 'flake8 --version'),
        ('isort', 'isort --version')
    ]
    
    all_good = True
    for tool_name, command in tools:
        try:
            result = subprocess.run(command.split(), 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {tool_name}: {version}")
            else:
                print(f"❌ {tool_name}: 未正确安装")
                all_good = False
        except Exception as e:
            print(f"❌ {tool_name}: 检查失败 - {e}")
            all_good = False
    
    return all_good


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 CoderWiki 开发环境检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version),
        ("pip", check_pip),
        ("虚拟环境", check_virtualenv),
        ("Python包", check_packages),
        ("MySQL", check_mysql),
        ("项目结构", check_project_structure),
        ("Git", check_git),
        ("代码质量工具", check_code_quality_tools)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有检查都通过了！开发环境配置完成。")
        return 0
    else:
        print("⚠️  部分检查失败，请根据上述信息进行修复。")
        return 1


if __name__ == "__main__":
    sys.exit(main())