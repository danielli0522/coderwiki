#!/usr/bin/env python3
"""
Quick End-to-End Validation Check
Fast validation of critical workflow components
"""

import os
import requests
import json

def quick_validation():
    """Quick validation of workflow components"""
    results = {}
    
    print("🚀 Quick End-to-End Workflow Check")
    print("=" * 50)
    
    # 1. CoderWiki Service
    try:
        response = requests.get('http://localhost:5001/system-status', timeout=5)
        results['coderwiki_service'] = response.status_code == 200
        print(f"✅ CoderWiki Service: {'RUNNING' if results['coderwiki_service'] else 'DOWN'}")
    except:
        results['coderwiki_service'] = False
        print("❌ CoderWiki Service: DOWN")
    
    # 2. Repository Files
    repo_path = "backend/repos/deepwiki-open"
    results['repository_cloned'] = os.path.exists(repo_path)
    print(f"✅ Repository Cloned: {'YES' if results['repository_cloned'] else 'NO'}")
    
    # 3. Claude Client
    claude_client_exists = os.path.exists("claude_robust_client.py")
    results['claude_client'] = claude_client_exists
    print(f"✅ Enhanced Claude Client: {'AVAILABLE' if claude_client_exists else 'MISSING'}")
    
    # 4. Generated Analysis
    analysis_exists = os.path.exists("robust_deepwiki_analysis.md")
    results['claude_analysis'] = analysis_exists
    print(f"✅ Claude Analysis Generated: {'YES' if analysis_exists else 'NO'}")
    
    # 5. MkDocs Capability
    try:
        import subprocess
        result = subprocess.run(['mkdocs', '--version'], capture_output=True, text=True, timeout=5)
        results['mkdocs_available'] = result.returncode == 0
        print(f"✅ MkDocs Available: {'YES' if results['mkdocs_available'] else 'NO'}")
    except:
        results['mkdocs_available'] = False
        print("❌ MkDocs Available: NO")
    
    # 6. Authentication Check
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post('http://localhost:5001/api/auth/login', json=login_data, timeout=5)
        results['authentication'] = response.status_code == 200
        print(f"✅ Authentication: {'WORKING' if results['authentication'] else 'FAILED'}")
    except:
        results['authentication'] = False
        print("❌ Authentication: FAILED")
    
    # Summary
    total_checks = len(results)
    passed_checks = sum(results.values())
    success_rate = passed_checks / total_checks
    
    print("\n" + "=" * 50)
    print("📊 QUICK VALIDATION SUMMARY")
    print(f"✅ Success Rate: {success_rate:.1%} ({passed_checks}/{total_checks})")
    print(f"🎯 Workflow Status: {'READY' if success_rate >= 0.8 else 'NEEDS ATTENTION'}")
    
    # Detailed status
    print("\n📋 Component Status:")
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component.replace('_', ' ').title()}")
    
    return results, success_rate >= 0.8

if __name__ == "__main__":
    results, overall_success = quick_validation()
    exit(0 if overall_success else 1)