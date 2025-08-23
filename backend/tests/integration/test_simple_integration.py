#!/usr/bin/env python3
"""
Simple integration test to verify basic functionality
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

def test_basic_functionality():
    """Test basic app functionality."""
    print("🧪 Testing Basic App Functionality...")
    
    try:
        from app import create_app
        from config import config
        
        # Create app with testing config
        app = create_app(config['testing'])
        
        with app.test_client() as client:
            # Test basic pages
            pages = [
                ('/', 'Home'),
                ('/login', 'Login'),
                ('/register', 'Register'),
                ('/about', 'About'),
                ('/contact', 'Contact'),
                ('/help', 'Help'),
            ]
            
            results = []
            
            for path, name in pages:
                try:
                    response = client.get(path)
                    status = response.status_code
                    success = status in [200, 302]  # 302 is OK for redirects
                    results.append({
                        'page': name,
                        'path': path,
                        'status': status,
                        'success': success
                    })
                    
                    if success:
                        print(f"✅ {name}: {status}")
                    else:
                        print(f"❌ {name}: {status}")
                        
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
                    results.append({
                        'page': name,
                        'path': path,
                        'status': 'ERROR',
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate success rate
            successful_tests = sum(1 for r in results if r['success'])
            total_tests = len(results)
            success_rate = (successful_tests / total_tests) * 100
            
            print(f"\n📊 Basic Functionality Results: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            
            return success_rate >= 80
            
    except Exception as e:
        print(f"❌ Error testing basic functionality: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🔌 Testing API Endpoints...")
    
    try:
        from app import create_app
        from config import config
        
        app = create_app(config['testing'])
        
        with app.test_client() as client:
            # Test API endpoints
            endpoints = [
                ('/api/auth/status', 'Auth Status'),
                ('/api/system/status', 'System Status'),
            ]
            
            results = []
            
            for endpoint, name in endpoints:
                try:
                    response = client.get(endpoint)
                    status = response.status_code
                    success = status == 200
                    results.append({
                        'endpoint': name,
                        'path': endpoint,
                        'status': status,
                        'success': success
                    })
                    
                    if success:
                        print(f"✅ {name}: {status}")
                    else:
                        print(f"❌ {name}: {status}")
                        
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
                    results.append({
                        'endpoint': name,
                        'path': endpoint,
                        'status': 'ERROR',
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate success rate
            successful_tests = sum(1 for r in results if r['success'])
            total_tests = len(results)
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"\n📊 API Endpoints Results: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            
            return success_rate >= 50
            
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

def test_static_files():
    """Test static files."""
    print("\n📁 Testing Static Files...")
    
    try:
        from app import create_app
        from config import config
        
        app = create_app(config['testing'])
        
        with app.test_client() as client:
            # Test static files
            static_files = [
                ('/static/css/style.css', 'Main CSS'),
                ('/static/js/main.js', 'Main JavaScript'),
                ('/static/images/icon.svg', 'Icon Image'),
            ]
            
            results = []
            
            for file_path, name in static_files:
                try:
                    response = client.get(file_path)
                    status = response.status_code
                    success = status == 200
                    results.append({
                        'file': name,
                        'path': file_path,
                        'status': status,
                        'success': success
                    })
                    
                    if success:
                        print(f"✅ {name}: {status}")
                    else:
                        print(f"❌ {name}: {status}")
                        
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
                    results.append({
                        'file': name,
                        'path': file_path,
                        'status': 'ERROR',
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate success rate
            successful_tests = sum(1 for r in results if r['success'])
            total_tests = len(results)
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"\n📊 Static Files Results: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            
            return success_rate >= 80
            
    except Exception as e:
        print(f"❌ Error testing static files: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Starting Simple Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Run test suites
    test_suites = [
        ("Basic Functionality", test_basic_functionality),
        ("API Endpoints", test_api_endpoints),
        ("Static Files", test_static_files)
    ]
    
    for suite_name, suite_func in test_suites:
        try:
            success = suite_func()
            results.append({
                'suite': suite_name,
                'success': success
            })
        except Exception as e:
            print(f"❌ Error running {suite_name}: {e}")
            results.append({
                'suite': suite_name,
                'success': False,
                'error': str(e)
            })
    
    # Overall result
    overall_success = all(r['success'] for r in results)
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 All integration tests passed!")
        print("✅ Frontend-backend integration is working correctly")
    else:
        print("❌ Some integration tests failed")
        print("🔧 Please check the test results for details")
    
    print("=" * 60)
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)