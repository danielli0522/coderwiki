#!/usr/bin/env python3
"""
系统性405错误修复脚本
按照BMAD QA修复流程进行系统性修复
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def fix_405_errors():
    """系统性修复405错误"""
    print("🔧 系统性405错误修复")
    print("=" * 50)

    # 1. 检查并修复路由冲突
    print("\n📋 1. 修复路由冲突")
    print("-" * 30)

    # 检查repository API路由
    repository_file = "backend/app/api/repository.py"
    if os.path.exists(repository_file):
        print(f"检查文件: {repository_file}")
        with open(repository_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查PUT和DELETE路由定义
        put_routes = re.findall(r'@repository_bp\.route\(.*methods=\[.*PUT.*\]\)', content)
        delete_routes = re.findall(r'@repository_bp\.route\(.*methods=\[.*DELETE.*\]\)', content)

        print(f"PUT路由数: {len(put_routes)}")
        print(f"DELETE路由数: {len(delete_routes)}")

        if put_routes:
            print("PUT路由定义:")
            for route in put_routes:
                print(f"  {route}")

        if delete_routes:
            print("DELETE路由定义:")
            for route in delete_routes:
                print(f"  {route}")

    # 2. 检查CORS配置
    print("\n📋 2. 检查CORS配置")
    print("-" * 30)

    config_file = "config.py"
    if os.path.exists(config_file):
        print(f"检查文件: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        cors_configs = re.findall(r'CORS_.*?=.*?', content)
        if cors_configs:
            print("CORS配置:")
            for config in cors_configs:
                print(f"  {config}")
        else:
            print("⚠️  未找到CORS配置")

    # 3. 检查Flask应用配置
    print("\n📋 3. 检查Flask应用配置")
    print("-" * 30)

    app_file = "backend/app/__init__.py"
    if os.path.exists(app_file):
        print(f"检查文件: {app_file}")
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查蓝图注册顺序
        blueprint_registrations = re.findall(r'app\.register_blueprint\((\w+)\)', content)
        print("蓝图注册顺序:")
        for i, blueprint in enumerate(blueprint_registrations, 1):
            print(f"  {i}. {blueprint}")

        # 检查错误处理器
        error_handlers = re.findall(r'@app\.errorhandler\((\d+)\)', content)
        print("错误处理器:")
        for handler in error_handlers:
            print(f"  {handler}")

        if '405' not in error_handlers:
            print("⚠️  缺少405错误处理器")

    # 4. 生成修复建议
    print("\n📋 4. 生成修复建议")
    print("-" * 30)

    print("🔧 建议的修复步骤:")
    print("  1. 添加405错误处理器")
    print("  2. 配置CORS支持")
    print("  3. 检查路由装饰器")
    print("  4. 验证HTTP方法支持")
    print("  5. 添加调试日志")

    return True

def apply_fixes():
    """应用修复"""
    print("\n🔧 应用修复")
    print("=" * 50)

    # 1. 添加405错误处理器
    print("\n📋 1. 添加405错误处理器")

    app_file = "backend/app/__init__.py"
    if os.path.exists(app_file):
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已有405错误处理器
        if '@app.errorhandler(405)' not in content:
            print("添加405错误处理器...")

            # 在现有错误处理器后添加405处理器
            error_handler_pattern = r'(@app\.errorhandler\(500\)\s+def internal_error\(error\):.*?return \'内部服务器错误\', 500\s+)'

            new_405_handler = '''
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({'error': '方法不被允许', 'method': request.method, 'url': request.url}), 405
'''

            # 替换内容
            new_content = re.sub(error_handler_pattern, r'\1' + new_405_handler, content, flags=re.DOTALL)

            if new_content != content:
                with open(app_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ 405错误处理器已添加")
            else:
                print("⚠️  无法添加405错误处理器")
        else:
            print("✅ 405错误处理器已存在")

    # 2. 添加CORS配置
    print("\n📋 2. 添加CORS配置")

    config_file = "config.py"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已有CORS配置
        if 'CORS_ORIGINS' not in content:
            print("添加CORS配置...")

            # 在配置类中添加CORS设置
            class_pattern = r'(class Config:.*?)(\s+def __init__\(self\):)'

            cors_config = '''
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:5001', 'http://127.0.0.1:5001']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'Accept']
'''

            # 替换内容
            new_content = re.sub(class_pattern, r'\1' + cors_config + r'\2', content, flags=re.DOTALL)

            if new_content != content:
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ CORS配置已添加")
            else:
                print("⚠️  无法添加CORS配置")
        else:
            print("✅ CORS配置已存在")

    # 3. 添加调试日志
    print("\n📋 3. 添加调试日志")

    # 在repository API中添加调试日志
    repository_file = "backend/app/api/repository.py"
    if os.path.exists(repository_file):
        with open(repository_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已有调试日志
        if 'print.*PUT.*DELETE' not in content:
            print("添加调试日志...")

            # 在PUT和DELETE路由中添加调试日志
            put_pattern = r'(@repository_bp\.route\(.*methods=\[.*PUT.*\]\)\s+@login_required\s+def update_repository\(repository_id\):.*?def update_repository\(repository_id\):)'

            debug_log = '''
    print(f"DEBUG: PUT /api/repositories/{repository_id} - Method: {request.method}")
'''

            # 替换内容
            new_content = re.sub(put_pattern, r'\1' + debug_log, content, flags=re.DOTALL)

            if new_content != content:
                with open(repository_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ 调试日志已添加")
            else:
                print("⚠️  无法添加调试日志")
        else:
            print("✅ 调试日志已存在")

    print("\n✅ 修复应用完成")

if __name__ == '__main__':
    print("🔧 系统性405错误修复工具")
    print("=" * 50)

    # 分析问题
    fix_405_errors()

    # 应用修复
    apply_fixes()

    print("\n🎉 修复完成！请重启Flask应用以应用更改。")
