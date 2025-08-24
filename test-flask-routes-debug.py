#!/usr/bin/env python3
"""
Flask路由调试脚本
检查Flask应用的路由注册情况
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app

def debug_flask_routes():
    """调试Flask路由注册"""
    print("🔍 Flask路由调试")
    print("=" * 50)

    # 创建Flask应用
    app = create_app()

    print(f"Flask应用创建成功: {app.name}")
    print(f"调试模式: {app.debug}")
    print(f"测试模式: {app.testing}")

    # 检查所有注册的路由
    print("\n📋 注册的路由:")
    print("-" * 50)

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })

    # 按规则排序
    routes.sort(key=lambda x: x['rule'])

    # 查找API路由
    api_routes = [r for r in routes if r['rule'].startswith('/api/')]

    print(f"总路由数: {len(routes)}")
    print(f"API路由数: {len(api_routes)}")

    print("\n🔧 API路由详情:")
    print("-" * 50)

    for route in api_routes:
        methods = ', '.join(sorted(route['methods']))
        print(f"{route['rule']:<40} {methods}")

        # 特别检查PUT和DELETE方法
        if 'PUT' in route['methods'] or 'DELETE' in route['methods']:
            print(f"  ✅ 支持PUT/DELETE: {route['endpoint']}")

    # 检查蓝图注册
    print("\n📋 蓝图注册:")
    print("-" * 50)

    for blueprint_name, blueprint in app.blueprints.items():
        print(f"蓝图: {blueprint_name}")
        print(f"  URL前缀: {blueprint.url_prefix}")

        # 检查蓝图中的路由
        blueprint_routes = [r for r in routes if r['endpoint'].startswith(f'{blueprint_name}.')]
        print(f"  路由数: {len(blueprint_routes)}")

        for route in blueprint_routes:
            methods = ', '.join(sorted(route['methods']))
            print(f"    {route['rule']} -> {methods}")

    # 检查是否有路由冲突
    print("\n🔍 路由冲突检查:")
    print("-" * 50)

    rule_patterns = {}
    for route in routes:
        pattern = route['rule']
        if pattern in rule_patterns:
            print(f"⚠️  路由冲突: {pattern}")
            print(f"    现有: {rule_patterns[pattern]}")
            print(f"    新: {route['endpoint']}")
        else:
            rule_patterns[pattern] = route['endpoint']

    # 检查特定API端点的路由
    print("\n🎯 特定API端点检查:")
    print("-" * 50)

    test_endpoints = [
        '/api/repositories/1',
        '/api/tasks/1',
        '/api/documents/1'
    ]

    for endpoint in test_endpoints:
        matching_routes = [r for r in routes if r['rule'] == endpoint]
        if matching_routes:
            for route in matching_routes:
                methods = ', '.join(sorted(route['methods']))
                print(f"{endpoint:<30} -> {methods} ({route['endpoint']})")
        else:
            print(f"{endpoint:<30} -> 未找到路由")

    # 检查CORS和OPTIONS方法
    print("\n🔍 CORS和OPTIONS方法分析:")
    print("-" * 50)

    options_routes = [r for r in api_routes if 'OPTIONS' in r['methods']]
    print(f"包含OPTIONS方法的路由数: {len(options_routes)}")

    # 检查PUT/DELETE路由的OPTIONS支持
    put_delete_routes = [r for r in api_routes if 'PUT' in r['methods'] or 'DELETE' in r['methods']]
    print(f"支持PUT/DELETE的路由数: {len(put_delete_routes)}")

    for route in put_delete_routes:
        has_options = 'OPTIONS' in route['methods']
        print(f"{route['rule']:<40} OPTIONS: {'✅' if has_options else '❌'}")

    # 检查应用配置
    print("\n⚙️  应用配置:")
    print("-" * 50)

    config_keys = ['CORS_ORIGINS', 'CORS_METHODS', 'CORS_HEADERS']
    for key in config_keys:
        value = app.config.get(key, '未设置')
        print(f"{key}: {value}")

    print("\n✅ 路由调试完成")

if __name__ == '__main__':
    debug_flask_routes()
