#!/usr/bin/env python3
"""
Integration test runner for task management system.
"""

import sys
import os
import argparse
import time
import json
from datetime import datetime
import subprocess
from pathlib import Path


class IntegrationTestRunner:
    """Runner for integration tests."""
    
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
            'errors': []
        }
    
    def run_tests(self, test_type='all', verbose=False, performance_only=False):
        """Run integration tests."""
        print(f"🚀 Starting Integration Tests")
        print(f"📅 Test Run: {self.results['start_time']}")
        print(f"🎯 Test Type: {test_type}")
        print("-" * 50)
        
        # Change to backend directory
        backend_dir = self.test_dir.parent.parent
        os.chdir(backend_dir)
        
        # Build pytest command
        pytest_cmd = ['python', '-m', 'pytest', 'tests/integration/']
        
        if test_type != 'all':
            if test_type == 'system':
                pytest_cmd.append('-k')
                pytest_cmd.append('test_task_system_integration')
            elif test_type == 'api':
                pytest_cmd.append('-k')
                pytest_cmd.append('test_task_api_integration')
            elif test_type == 'database':
                pytest_cmd.append('-k')
                pytest_cmd.append('test_task_database_integration')
            elif test_type == 'performance':
                pytest_cmd.append('-k')
                pytest_cmd.append('test_task_performance_integration')
        
        if verbose:
            pytest_cmd.append('-v')
        
        if performance_only:
            pytest_cmd.append('-m')
            pytest_cmd.append('performance')
        
        pytest_cmd.extend(['--tb=short', '--color=yes'])
        
        # Run tests
        try:
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            self.results['end_time'] = datetime.utcnow().isoformat()
            
            # Parse results
            self._parse_test_output(result.stdout, result.stderr)
            
            # Print summary
            self._print_summary()
            
            # Save results
            self._save_results()
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 5 minutes")
            self.results['errors'].append("Test execution timed out")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            self.results['errors'].append(str(e))
            return False
    
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
            elif 'Performance Metrics:' in line:
                # Extract performance metrics
                self._extract_performance_metrics(lines[lines.index(line) + 1:])
    
    def _extract_performance_metrics(self, lines):
        """Extract performance metrics from output."""
        metrics = {}
        for line in lines:
            if line.strip() and ':' in line and not line.startswith(' '):
                break
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to extract numeric values
                try:
                    if 'tasks/second' in value:
                        numeric_value = float(value.split()[0])
                        metrics[key] = numeric_value
                    elif 'seconds' in value and 'for' not in value:
                        numeric_value = float(value.split()[0])
                        metrics[key] = numeric_value
                    elif 'MB' in value:
                        numeric_value = float(value.split()[0])
                        metrics[key] = numeric_value
                    else:
                        metrics[key] = value
                except (ValueError, IndexError):
                    metrics[key] = value
        
        self.results['performance_metrics'] = metrics
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 Integration Test Summary")
        print("=" * 50)
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        print(f"⏭️  Skipped: {self.results['skipped_tests']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n⚡ Performance Metrics:")
        if self.results['performance_metrics']:
            for key, value in self.results['performance_metrics'].items():
                print(f"  {key}: {value}")
        else:
            print("  No performance metrics collected")
        
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
        results_file = self.test_dir / 'test_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
    
    def generate_report(self):
        """Generate detailed test report."""
        report_file = self.test_dir / 'test_report.md'
        
        with open(report_file, 'w') as f:
            f.write("# Integration Test Report\n\n")
            f.write(f"**Date:** {self.results['start_time']}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {self.results['total_tests']}\n")
            f.write(f"- **Passed:** {self.results['passed_tests']}\n")
            f.write(f"- **Failed:** {self.results['failed_tests']}\n")
            f.write(f"- **Skipped:** {self.results['skipped_tests']}\n")
            
            if self.results['total_tests'] > 0:
                success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
                f.write(f"- **Success Rate:** {success_rate:.1f}%\n")
            
            f.write("\n## Performance Metrics\n\n")
            if self.results['performance_metrics']:
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")
                for key, value in self.results['performance_metrics'].items():
                    f.write(f"| {key} | {value} |\n")
            else:
                f.write("No performance metrics collected.\n")
            
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
    parser = argparse.ArgumentParser(description='Run integration tests for task management system')
    parser.add_argument('--type', choices=['all', 'system', 'api', 'database', 'performance'],
                       default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--performance-only', action='store_true', help='Run only performance tests')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner()
    
    try:
        success = runner.run_tests(
            test_type=args.type,
            verbose=args.verbose,
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