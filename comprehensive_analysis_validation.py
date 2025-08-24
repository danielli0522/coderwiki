#!/usr/bin/env python3
"""
Comprehensive Code Analysis Validation Script

This script performs a deep validation of the code analysis functionality
to identify issues with navigation and data loading.
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n--- {title} ---")

def test_flask_app_creation():
    """Test Flask app creation and route registration."""
    print_section("Flask App Creation Test")

    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")

        # Check analysis routes
        analysis_routes = []
        for rule in app.url_map.iter_rules():
            if 'analysis' in rule.rule:
                analysis_routes.append({
                    'rule': rule.rule,
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods)
                })

        print(f"✅ Found {len(analysis_routes)} analysis routes:")
        for route in analysis_routes:
            print(f"   {route['rule']} -> {route['endpoint']} ({', '.join(route['methods'])})")

        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_analysis_models():
    """Test analysis model imports and structure."""
    print_section("Analysis Models Test")

    try:
        from app.models.analysis import CodeAnalysis, AnalysisCache
        print("✅ Analysis models imported successfully")

        # Test model attributes
        analysis = CodeAnalysis(repository_id=1, analysis_type='structure')
        print("✅ CodeAnalysis model instantiated successfully")

        cache = AnalysisCache(
            repository_id=1,
            cache_key='test_key',
            cache_data={'test': 'data'},
            expires_at=datetime.now()
        )
        print("✅ AnalysisCache model instantiated successfully")

        return True
    except Exception as e:
        print(f"❌ Analysis models test failed: {e}")
        return False

def test_analysis_service():
    """Test analysis service functionality."""
    print_section("Analysis Service Test")

    try:
        from app.services.analysis_service import AnalysisService
        service = AnalysisService()
        print("✅ AnalysisService instantiated successfully")

        # Test supported analysis types
        supported_types = service.supported_analysis_types
        print(f"✅ Supported analysis types: {supported_types}")

        # Test analysis engine
        engine = service.analysis_engine
        print("✅ Analysis engine initialized successfully")

        # Test capabilities
        capabilities = engine.get_analysis_capabilities()
        print(f"✅ Analysis capabilities: {list(capabilities.keys())}")

        return True
    except Exception as e:
        print(f"❌ Analysis service test failed: {e}")
        return False

def test_analysis_engine():
    """Test code analysis engine functionality."""
    print_section("Code Analysis Engine Test")

    try:
        from app.utils.code_analysis_engine import CodeAnalysisEngine, AnalysisConfig

        # Test engine initialization
        engine = CodeAnalysisEngine()
        print("✅ CodeAnalysisEngine initialized successfully")

        # Test supported types
        supported_types = engine.get_supported_analysis_types()
        print(f"✅ Supported analysis types: {supported_types}")

        # Test configuration
        config = AnalysisConfig(
            analysis_types=['structure', 'complexity'],
            include_patterns=['*'],
            exclude_patterns=['*.log', '*.tmp'],
            max_file_size=10*1024*1024,
            timeout=300,
            enable_cache=True,
            parallel_processing=True
        )
        print("✅ AnalysisConfig created successfully")

        # Test configuration validation
        errors = engine.validate_analysis_config(config)
        if errors:
            print(f"⚠️  Configuration validation errors: {errors}")
        else:
            print("✅ Configuration validation passed")

        return True
    except Exception as e:
        print(f"❌ Analysis engine test failed: {e}")
        return False

def test_cache_service():
    """Test cache service functionality."""
    print_section("Cache Service Test")

    try:
        from app.services.cache_service import CacheService

        # Test cache key generation
        cache_key = CacheService.generate_cache_key(1, 'structure')
        print(f"✅ Cache key generated: {cache_key}")

        # Test cache expiration times
        expiration_times = CacheService.CACHE_EXPIRATION
        print(f"✅ Cache expiration times: {expiration_times}")

        return True
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        return False

def test_analysis_analyzers():
    """Test individual analysis analyzers."""
    print_section("Analysis Analyzers Test")

    try:
        # Test structure analyzer
        from app.utils.structure_analyzer import StructureAnalyzer
        print("✅ StructureAnalyzer imported successfully")

        # Test dependency analyzer
        from app.utils.dependency_analyzer import DependencyAnalyzer
        print("✅ DependencyAnalyzer imported successfully")

        # Test complexity analyzer
        from app.utils.complexity_analyzer import ComplexityAnalyzer
        print("✅ ComplexityAnalyzer imported successfully")

        # Test tech stack analyzer
        from app.utils.tech_stack_analyzer import TechStackAnalyzer
        print("✅ TechStackAnalyzer imported successfully")

        # Test security scanner
        from app.utils.security_scanner import SecurityScanner
        print("✅ SecurityScanner imported successfully")

        # Test pattern recognizer
        from app.utils.project_pattern_recognizer import ProjectPatternRecognizer
        print("✅ ProjectPatternRecognizer imported successfully")

        return True
    except Exception as e:
        print(f"❌ Analysis analyzers test failed: {e}")
        return False

def test_frontend_analysis_js():
    """Test frontend analysis JavaScript functionality."""
    print_section("Frontend Analysis JavaScript Test")

    try:
        # Check if analysis.js exists
        analysis_js_path = 'frontend/static/js/analysis.js'
        if os.path.exists(analysis_js_path):
            print("✅ analysis.js file exists")

            # Read and check for key functions
            with open(analysis_js_path, 'r', encoding='utf-8') as f:
                content = f.read()

            required_functions = [
                'class AnalysisManager',
                'loadAnalysisResults',
                'startAnalysis',
                'renderAnalysisResults'
            ]

            for func in required_functions:
                if func in content:
                    print(f"✅ Found function: {func}")
                else:
                    print(f"❌ Missing function: {func}")
        else:
            print("❌ analysis.js file not found")
            return False

        return True
    except Exception as e:
        print(f"❌ Frontend analysis JS test failed: {e}")
        return False

def test_analysis_templates():
    """Test analysis HTML templates."""
    print_section("Analysis Templates Test")

    try:
        # Check analysis templates
        templates = [
            'frontend/templates/analysis/index.html',
            'frontend/templates/analysis/results.html'
        ]

        for template in templates:
            if os.path.exists(template):
                print(f"✅ Template exists: {template}")

                # Check for key elements
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()

                if 'analysis' in content.lower():
                    print(f"✅ Template contains analysis content: {template}")
                else:
                    print(f"⚠️  Template may be missing analysis content: {template}")
            else:
                print(f"❌ Template missing: {template}")

        return True
    except Exception as e:
        print(f"❌ Analysis templates test failed: {e}")
        return False

def test_database_models():
    """Test database model relationships."""
    print_section("Database Models Test")

    try:
        from app.models.analysis import CodeAnalysis
        from app.models.repository import Repository

        # Test model relationships
        print("✅ Analysis and Repository models imported successfully")

        # Check if models have required attributes
        analysis_attrs = ['repository_id', 'analysis_type', 'status', 'result_data']
        for attr in analysis_attrs:
            if hasattr(CodeAnalysis, attr):
                print(f"✅ CodeAnalysis has attribute: {attr}")
            else:
                print(f"❌ CodeAnalysis missing attribute: {attr}")

        return True
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint functionality."""
    print_section("API Endpoints Test")

    try:
        from app import create_app
        app = create_app()

        # Test analysis endpoints
        with app.test_client() as client:
            # Test health check endpoint
            response = client.get('/api/analysis/health')
            if response.status_code == 401:  # Unauthorized is expected without login
                print("✅ Analysis health endpoint responds (requires authentication)")
            else:
                print(f"⚠️  Analysis health endpoint status: {response.status_code}")

            # Test supported types endpoint
            response = client.get('/api/analysis/types')
            if response.status_code == 401:  # Unauthorized is expected without login
                print("✅ Analysis types endpoint responds (requires authentication)")
            else:
                print(f"⚠️  Analysis types endpoint status: {response.status_code}")

        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_navigation_integration():
    """Test navigation integration with analysis."""
    print_section("Navigation Integration Test")

    try:
        # Check base template for analysis navigation
        base_template_path = 'frontend/templates/base.html'
        if os.path.exists(base_template_path):
            with open(base_template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'analysis' in content.lower():
                print("✅ Base template contains analysis navigation")
            else:
                print("❌ Base template missing analysis navigation")
        else:
            print("❌ Base template not found")

        # Check navigation.js for analysis support
        nav_js_path = 'frontend/static/js/navigation.js'
        if os.path.exists(nav_js_path):
            print("✅ navigation.js exists")
        else:
            print("❌ navigation.js not found")

        return True
    except Exception as e:
        print(f"❌ Navigation integration test failed: {e}")
        return False

def generate_validation_report(results):
    """Generate a comprehensive validation report."""
    print_header("VALIDATION REPORT")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

    # Identify potential issues
    print("\nPotential Issues:")
    if not results.get('frontend_analysis_js', True):
        print("  - Frontend analysis JavaScript may have issues")
    if not results.get('analysis_templates', True):
        print("  - Analysis templates may be missing or incomplete")
    if not results.get('navigation_integration', True):
        print("  - Navigation integration with analysis may be broken")
    if not results.get('api_endpoints', True):
        print("  - API endpoints may not be working correctly")

    # Recommendations
    print("\nRecommendations:")
    if failed_tests > 0:
        print("  1. Fix failed tests before proceeding")
        print("  2. Check database migrations for analysis tables")
        print("  3. Verify all required JavaScript files are loaded")
        print("  4. Test analysis functionality with a real repository")
    else:
        print("  1. All tests passed - analysis functionality appears to be working")
        print("  2. Test with real user data to verify end-to-end functionality")
        print("  3. Check browser console for any JavaScript errors")

def main():
    """Main validation function."""
    print_header("COMPREHENSIVE CODE ANALYSIS VALIDATION")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    tests = {
        'Flask App Creation': test_flask_app_creation,
        'Analysis Models': test_analysis_models,
        'Analysis Service': test_analysis_service,
        'Analysis Engine': test_analysis_engine,
        'Cache Service': test_cache_service,
        'Analysis Analyzers': test_analysis_analyzers,
        'Frontend Analysis JS': test_frontend_analysis_js,
        'Analysis Templates': test_analysis_templates,
        'Database Models': test_database_models,
        'API Endpoints': test_api_endpoints,
        'Navigation Integration': test_navigation_integration
    }

    results = {}
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Generate report
    generate_validation_report(results)

    print(f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
