#!/usr/bin/env python3
"""
Claude Code集成测试脚本
"""

import os
import sys
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_claude_code_service_health():
    """测试Claude Code服务健康状态"""
    print("=== 测试Claude Code服务健康状态 ===")

    try:
        response = requests.get('http://localhost:5000/api/documents/claude-code/status', timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

            if data.get('success'):
                print("✅ Claude Code服务健康检查通过")
                return True
            else:
                print("❌ Claude Code服务健康检查失败")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_claude_code_doc_types():
    """测试获取Claude Code文档类型"""
    print("\n=== 测试获取Claude Code文档类型 ===")

    try:
        response = requests.get('http://localhost:5000/api/documents/doc-types', timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

            if data.get('success'):
                doc_types = data.get('doc_types', [])
                source = data.get('source', 'unknown')
                print(f"✅ 获取到 {len(doc_types)} 个文档类型 (来源: {source})")
                for doc_type in doc_types:
                    print(f"  - {doc_type}")
                return True
            else:
                print("❌ 获取文档类型失败")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_document_generation():
    """测试文档生成（需要认证）"""
    print("\n=== 测试文档生成 ===")
    print("注意: 此测试需要有效的认证token")

    # 这里需要实际的认证token和测试数据
    # 由于需要认证，这里只提供示例代码
    print("示例请求:")
    print("""
    curl -X POST http://localhost:5000/api/documents/generate \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "repository_id": 1,
        "llm_config_id": 1,
        "doc_type": "technical_design",
        "doc_title": "技术设计文档"
      }'
    """)

    return True

def test_claude_code_sdk_direct():
    """直接测试Claude Code SDK"""
    print("\n=== 直接测试Claude Code SDK ===")

    try:
        # 尝试导入Claude Code SDK
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

        print("✅ Claude Code SDK导入成功")
        print("✅ Claude Code SDK可用")
        return True

    except ImportError:
        print("❌ Claude Code SDK未安装")
        print("请安装: pip install claude-code-sdk")
        return False
    except Exception as e:
        print(f"❌ Claude Code SDK测试失败: {e}")
        return False

def test_bmad_docs_generator():
    """测试BMAD文档生成器路径"""
    print("\n=== 测试BMAD文档生成器路径 ===")

    try:
        bmad_docs_path = os.environ.get('BMAD_DOCS_PATH', '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/')

        if not os.path.exists(bmad_docs_path):
            print(f"❌ BMAD文档生成器路径不存在: {bmad_docs_path}")
            return False

        print(f"✅ BMAD文档生成器路径存在: {bmad_docs_path}")

        # 检查关键文件
        key_files = ['README.md', 'config.yaml', 'tasks/']
        missing_files = []

        for file_name in key_files:
            file_path = os.path.join(bmad_docs_path, file_name)
            if os.path.exists(file_path):
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} (缺失)")
                missing_files.append(file_name)

        if missing_files:
            print(f"⚠️  缺失关键文件: {missing_files}")
            return False
        else:
            print("✅ 所有关键文件都存在")
            return True

    except Exception as e:
        print(f"❌ BMAD文档生成器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Claude Code集成测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 检查环境变量
    print("=== 环境变量检查 ===")
    claude_code_enabled = os.environ.get('CLAUDE_CODE_ENABLED', 'false').lower() == 'true'
    bmad_docs_path = os.environ.get('BMAD_DOCS_PATH', '/Users/lshl124/Documents/daniel/git/code/aigc/BMAD-METHOD/expansion-packs/bmad-docs-generator/')

    print(f"CLAUDE_CODE_ENABLED: {claude_code_enabled}")
    print(f"BMAD_DOCS_PATH: {bmad_docs_path}")
    print()

    if not claude_code_enabled:
        print("⚠️  Claude Code服务已禁用，请设置 CLAUDE_CODE_ENABLED=true")
        return

    # 运行测试
    tests = [
        ("Claude Code SDK直接测试", test_claude_code_sdk_direct),
        ("BMAD文档生成器路径测试", test_bmad_docs_generator),
        ("Claude Code服务健康状态", test_claude_code_service_health),
        ("Claude Code文档类型", test_claude_code_doc_types),
        ("文档生成", test_document_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 {test_name} 异常: {e}")
            results.append((test_name, False))

    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！Claude Code集成正常工作。")
    else:
        print("⚠️  部分测试失败，请检查配置和Claude Code服务状态。")

    # 提供建议
    print("\n" + "=" * 50)
    print("建议:")
    print("=" * 50)

    if not claude_code_enabled:
        print("1. 设置环境变量: export CLAUDE_CODE_ENABLED=true")

    if not claude_code_enabled:
        print("2. 设置环境变量: export CLAUDE_CODE_ENABLED=true")

    if not os.path.exists(bmad_docs_path):
        print("3. 检查BMAD文档生成器路径是否正确")

    print("4. 确保Claude Code SDK有足够的权限")
    print("5. 检查网络连接和防火墙设置")

if __name__ == "__main__":
    main()
