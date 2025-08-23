#!/usr/bin/env python3
"""
End-to-end test runner for task management system.
"""

import sys
import os
import argparse
import time
import json
from datetime import datetime
import subprocess
from pathlib import Path
import threading
import requests


class EndToEndTestRunner:
    """Runner for end-to-end tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_results': [],
            'performance_metrics': {},
            'accessibility_results': {},
            'mobile_results': {},
            'api_results': {},
            'errors': []
        }
        
        # Server configuration
        self.server_host = '127.0.0.1'
        self.server_port = 5000
        self.server_url = f'http://{self.server_host}:{self.server_port}'
        self.server_process = None
        
    def start_flask_server(self):
        """Start Flask server for testing."""
        backend_dir = self.test_dir.parent.parent
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'
        env['FLASK_DEBUG'] = 'false'
        
        # Start server in background
        self.server_process = subprocess.Popen(
            ['python', '-m', 'flask', 'run', '--host', self.server_host, '--port', str(self.server_port)],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(f'{self.server_url}/health', timeout=5)
                if response.status_code == 200:
                    print(f"✅ Flask server started on {self.server_url}")
                    return True
            except:
                time.sleep(1)
        
        return False
    
    def stop_flask_server(self):
        """Stop Flask server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Flask server stopped")
    
    def run_tests(self, test_type='all', verbose=False, headless=True, performance_only=False):
        """Run end-to-end tests."""
        print(f"🚀 Starting End-to-End Tests")
        print(f"📅 Test Run: {self.results['start_time']}")
        print(f"🎯 Test Type: {test_type}")
        print(f"🌐 Server URL: {self.server_url}")
        print("-" * 50)
        
        # Start Flask server
        if not self.start_flask_server():
            print("❌ Failed to start Flask server")
            self.results['errors'].append("Failed to start Flask server")
            return False
        
        try:
            # Build pytest command
            backend_dir = self.test_dir.parent.parent
            pytest_cmd = ['python', '-m', 'pytest', 'tests/end_to_end/']
            
            if test_type != 'all':
                if test_type == 'workflow':
                    pytest_cmd.append('-k')
                    pytest_cmd.append('test_complete_task_workflow or test_batch_task_workflow')
                elif test_type == 'api':
                    pytest_cmd.append('-k')
                    pytest_cmd.append('test_task_api_workflow')
                elif test_type == 'mobile':
                    pytest_cmd.append('-k')
                    pytest_cmd.append('test_task_mobile_workflow')
                elif test_type == 'accessibility':
                    pytest_cmd.append('-k')
                    pytest_cmd.append('test_task_accessibility_workflow')
                elif test_type == 'performance':
                    pytest_cmd.append('-k')
                    pytest_cmd.append('test_task_performance_workflow')
            
            if verbose:
                pytest_cmd.append('-v')
            
            if performance_only:
                pytest_cmd.append('-m')
                pytest_cmd.append('performance')
            
            # Add environment variables
            env = os.environ.copy()
            env['TEST_SERVER_URL'] = self.server_url
            env['TEST_HEADLESS'] = str(headless).lower()
            
            pytest_cmd.extend(['--tb=short', '--color=yes'])
            
            # Run tests
            result = subprocess.run(
                pytest_cmd,
                cwd=backend_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            self.results['end_time'] = datetime.utcnow().isoformat()
            
            # Parse results
            self._parse_test_output(result.stdout, result.stderr)
            
            # Run additional tests
            self._run_additional_tests()
            
            # Print summary
            self._print_summary()
            
            # Save results
            self._save_results()
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 10 minutes")
            self.results['errors'].append("Test execution timed out")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            self.results['errors'].append(str(e))
            return False
        finally:
            self.stop_flask_server()
    
    def _parse_test_output(self, stdout, stderr):
        """Parse pytest output to extract results."""
        lines = stdout.split('\n')
        
        for line in lines:
            if 'collected' in line and 'items' in line:
                # Extract total test count
                self.results['total_tests'] = int(line.split('collected')[1].split('items')[0].strip())
            elif '=' in line and 'passed' in line:
                # Extract passed count
                parts = line.split('=')
                for part in parts:
                    if 'passed' in part:
                        self.results['passed_tests'] = int(part.split('passed')[0].strip())
                    elif 'failed' in part:
                        self.results['failed_tests'] = int(part.split('failed')[0].strip())
                    elif 'skipped' in part:
                        self.results['skipped_tests'] = int(part.split('skipped')[0].strip())
            elif 'FAILED' in line:
                # Extract failed test details
                test_name = line.split('FAILED')[1].strip()
                self.results['test_results'].append({
                    'name': test_name,
                    'status': 'FAILED'
                })
            elif 'PASSED' in line and '::' in line:
                # Extract passed test details
                test_name = line.split('PASSED')[1].strip()
                self.results['test_results'].append({
                    'name': test_name,
                    'status': 'PASSED'
                })
    
    def _run_additional_tests(self):
        """Run additional performance and accessibility tests."""
        print("\n🔍 Running additional tests...")
        
        # Test API endpoints
        self._test_api_endpoints()
        
        # Test basic accessibility
        self._test_accessibility()
        
        # Test performance
        self._test_performance()
    
    def _test_api_endpoints(self):
        """Test API endpoints."""
        print("📡 Testing API endpoints...")
        
        api_endpoints = [
            '/api/tasks',
            '/api/tasks/statistics',
            '/api/repositories',
            '/api/health'
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(f'{self.server_url}{endpoint}', timeout=10)
                self.results['api_results'][endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'success': response.status_code == 200
                }
            except Exception as e:
                self.results['api_results'][endpoint] = {
                    'error': str(e),
                    'success': False
                }
    
    def _test_accessibility(self):
        """Test basic accessibility features."""
        print("♿ Testing accessibility...")
        
        try:
            # Test basic page load
            response = requests.get(f'{self.server_url}/', timeout=10)
            if response.status_code == 200:
                self.results['accessibility_results']['page_load'] = {
                    'success': True,
                    'response_time': response.elapsed.total_seconds()
                }
                
                # Check for basic accessibility features in HTML
                content = response.text
                self.results['accessibility_results']['html_features'] = {
                    'has_aria_labels': 'aria-label' in content,
                    'has_alt_text': 'alt=' in content,
                    'has_headings': '<h' in content,
                    'has_form_labels': '<label' in content
                }
            else:
                self.results['accessibility_results']['page_load'] = {
                    'success': False,
                    'status_code': response.status_code
                }
        except Exception as e:
            self.results['accessibility_results']['page_load'] = {
                'success': False,
                'error': str(e)
            }
    
    def _test_performance(self):
        """Test basic performance metrics."""
        print("⚡ Testing performance...")
        
        # Test page load times
        pages = ['/', '/tasks', '/statistics', '/api/tasks']
        
        for page in pages:
            try:
                start_time = time.time()
                response = requests.get(f'{self.server_url}{page}', timeout=10)
                end_time = time.time()
                
                self.results['performance_metrics'][page] = {
                    'load_time': end_time - start_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200
                }
            except Exception as e:
                self.results['performance_metrics'][page] = {
                    'error': str(e),
                    'success': False
                }
        
        # Test concurrent requests
        try:
            import concurrent.futures
            
            def make_request():
                return requests.get(f'{self.server_url}/api/tasks', timeout=10)
            
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
            
            successful_requests = sum(1 for r in results if r.status_code == 200)
            
            self.results['performance_metrics']['concurrent_requests'] = {
                'total_time': end_time - start_time,
                'successful_requests': successful_requests,
                'total_requests': len(results),
                'success_rate': successful_requests / len(results) * 100
            }
        except Exception as e:
            self.results['performance_metrics']['concurrent_requests'] = {
                'error': str(e),
                'success': False
            }
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 End-to-End Test Summary")
        print("=" * 50)
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        print(f"⏭️  Skipped: {self.results['skipped_tests']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📡 API Test Results:")
        for endpoint, result in self.results['api_results'].items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"  {status} {endpoint}: {result.get('status_code', 'N/A')}")
        
        print("\n♿ Accessibility Results:")
        accessibility = self.results['accessibility_results']
        if 'page_load' in accessibility:
            status = "✅" if accessibility['page_load'].get('success', False) else "❌"
            print(f"  {status} Page Load: {accessibility['page_load'].get('response_time', 'N/A')}s")
        
        print("\n⚡ Performance Results:")
        for page, result in self.results['performance_metrics'].items():
            status = "✅" if result.get('success', False) else "❌"
            load_time = result.get('load_time', 'N/A')
            print(f"  {status} {page}: {load_time:.3f}s")
        
        if self.results['errors']:
            print("\n❌ Errors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print("\n📋 Failed Tests:")
        failed_tests = [r for r in self.results['test_results'] if r['status'] == 'FAILED']
        if failed_tests:
            for test in failed_tests[:10]:  # Show first 10 failed tests
                print(f"  - {test['name']}")
            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more")
        else:
            print("  No failed tests")
        
        print("\n" + "=" * 50)
    
    def _save_results(self):
        """Save test results to file."""
        results_file = self.test_dir / 'e2e_test_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
    
    def generate_report(self):
        """Generate detailed test report."""
        report_file = self.test_dir / 'e2e_test_report.md'
        
        with open(report_file, 'w') as f:
            f.write("# End-to-End Test Report\n\n")
            f.write(f"**Date:** {self.results['start_time']}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {self.results['total_tests']}\n")
            f.write(f"- **Passed:** {self.results['passed_tests']}\n")
            f.write(f"- **Failed:** {self.results['failed_tests']}\n")
            f.write(f"- **Skipped:** {self.results['skipped_tests']}\n")
            
            if self.results['total_tests'] > 0:
                success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
                f.write(f"- **Success Rate:** {success_rate:.1f}%\n")
            
            f.write("\n## API Test Results\n\n")
            f.write("| Endpoint | Status | Response Time |\n")
            f.write("|----------|--------|---------------|\n")
            for endpoint, result in self.results['api_results'].items():
                status = "✅" if result.get('success', False) else "❌"
                response_time = result.get('response_time', 'N/A')
                f.write(f"| {endpoint} | {status} | {response_time} |\n")
            
            f.write("\n## Performance Results\n\n")
            f.write("| Page | Load Time | Status |\n")
            f.write("|------|-----------|--------|\n")
            for page, result in self.results['performance_metrics'].items():
                status = "✅" if result.get('success', False) else "❌"
                load_time = result.get('load_time', 'N/A')
                f.write(f"| {page} | {load_time:.3f}s | {status} |\n")
            
            f.write("\n## Accessibility Results\n\n")
            accessibility = self.results['accessibility_results']
            if 'html_features' in accessibility:
                features = accessibility['html_features']
                f.write("- **ARIA Labels:** " + ("✅" if features['has_aria_labels'] else "❌") + "\n")
                f.write("- **Alt Text:** " + ("✅" if features['has_alt_text'] else "❌") + "\n")
                f.write("- **Headings:** " + ("✅" if features['has_headings'] else "❌") + "\n")
                f.write("- **Form Labels:** " + ("✅" if features['has_form_labels'] else "❌") + "\n")
            
            f.write("\n## Failed Tests\n\n")
            failed_tests = [r for r in self.results['test_results'] if r['status'] == 'FAILED']
            if failed_tests:
                for test in failed_tests:
                    f.write(f"- {test['name']}\n")
            else:
                f.write("No failed tests.\n")
            
            if self.results['errors']:
                f.write("\n## Errors\n\n")
                for error in self.results['errors']:
                    f.write(f"- {error}\n")
        
        print(f"📄 Detailed report generated: {report_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run end-to-end tests for task management system')
    parser.add_argument('--type', choices=['all', 'workflow', 'api', 'mobile', 'accessibility', 'performance'],
                       default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-headless', action='store_true', help='Run tests with browser visible')
    parser.add_argument('--performance-only', action='store_true', help='Run only performance tests')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    runner = EndToEndTestRunner()
    
    try:
        success = runner.run_tests(
            test_type=args.type,
            verbose=args.verbose,
            headless=not args.no_headless,
            performance_only=args.performance_only
        )
        
        if args.report:
            runner.generate_report()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()