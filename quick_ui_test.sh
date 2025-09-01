#!/bin/bash

# Quick UI Test Execution Script
# Usage: ./quick_ui_test.sh [port] [test_suite]

set -e

# Configuration
DEFAULT_PORT=5005
DEFAULT_SUITE="all"
TEST_PORT=${1:-$DEFAULT_PORT}
TEST_SUITE=${2:-$DEFAULT_SUITE}

echo "🚀 Quick UI Test Execution"
echo "=========================="
echo "Port: $TEST_PORT"
echo "Suite: $TEST_SUITE"
echo ""

# Check if application is running
echo "🔍 Checking application status..."
if curl -s --fail "http://127.0.0.1:$TEST_PORT" > /dev/null 2>&1; then
    echo "✅ Application is running on port $TEST_PORT"
else
    echo "❌ Application is not accessible on port $TEST_PORT"
    echo "Please start the application first:"
    echo "  PORT=$TEST_PORT python backend/run.py"
    exit 1
fi

# Create test results directory
mkdir -p test_results

# Set base URL
export BASE_URL="http://127.0.0.1:$TEST_PORT"

case $TEST_SUITE in
    "all")
        echo "🧪 Running all test suites..."
        python run_ui_automation.py --url "http://127.0.0.1:$TEST_PORT"
        ;;
    "playwright")
        echo "🧪 Running Playwright comprehensive tests..."
        python comprehensive_ui_test_suite.py
        ;;
    "puppeteer")
        echo "🧪 Running Puppeteer tests..."
        cd backend/tests/ui
        npm test
        cd ../../..
        ;;
    "accessibility")
        echo "🧪 Running accessibility tests..."
        cd backend/tests/ui
        npm run test:accessibility
        cd ../../..
        ;;
    "performance")
        echo "🧪 Running performance tests..."
        cd backend/tests/ui
        npm run test:performance
        cd ../../..
        ;;
    "quick")
        echo "🧪 Running quick smoke tests..."
        python -c "
import asyncio
from comprehensive_ui_test_suite import CoderWikiUITester

async def quick_test():
    tester = CoderWikiUITester('$BASE_URL')
    await tester.setup()
    try:
        await tester.test_application_availability()
        await tester.test_login_functionality()
        await tester.test_dashboard_loading()
        report = tester.generate_report()
        
        passed = len([r for r in tester.test_results if r['status'] == 'PASS'])
        total = len(tester.test_results)
        
        print(f'\n🎯 Quick Test Results: {passed}/{total} tests passed')
        
        if passed == total:
            print('✅ All quick tests PASSED')
        else:
            print('❌ Some tests FAILED')
            for result in tester.test_results:
                if result['status'] != 'PASS':
                    print(f'  - {result[\"test_name\"]}: {result[\"status\"]}')
                    
    finally:
        await tester.teardown()

asyncio.run(quick_test())
"
        ;;
    *)
        echo "❌ Unknown test suite: $TEST_SUITE"
        echo "Available suites: all, playwright, puppeteer, accessibility, performance, quick"
        exit 1
        ;;
esac

echo ""
echo "✅ Test execution completed!"
echo "📄 Check test_results/ directory for detailed reports"