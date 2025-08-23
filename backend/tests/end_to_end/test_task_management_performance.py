"""
Performance-focused end-to-end tests for task management system.
"""

import pytest
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from config import TestingConfig


class TestTaskManagementPerformance:
    """Performance-focused end-to-end tests."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create Flask app
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        self.user = User(username='perfuser', email='perf@example.com')
        self.user.set_password('perftest123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test repositories
        self.repositories = []
        for i in range(10):
            repo = Repository(
                user_id=self.user.id,
                name=f'perf-repo-{i+1}',
                url=f'https://github.com/test/perf-repo-{i+1}.git',
                description=f'Performance test repository {i+1}'
            )
            db.session.add(repo)
            self.repositories.append(repo)
        db.session.commit()
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Start Flask app
        self.flask_thread = threading.Thread(target=self._run_flask_app)
        self.flask_thread.daemon = True
        self.flask_thread.start()
        time.sleep(2)
        
        # Performance metrics
        self.performance_metrics = {}
    
    def _run_flask_app(self):
        """Run Flask app for testing."""
        self.app.run(host='127.0.0.1', port=5000, debug=False)
    
    def teardown_method(self):
        """Cleanup test environment."""
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def measure_performance(self, operation_name, operation_func, iterations=10):
        """Measure performance of an operation."""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            operation_func()
            end_time = time.time()
            times.append(end_time - start_time)
        
        metrics = {
            'operation': operation_name,
            'iterations': iterations,
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'total_time': sum(times),
            'throughput': iterations / sum(times) if sum(times) > 0 else 0
        }
        
        self.performance_metrics[operation_name] = metrics
        return metrics
    
    def test_page_load_performance(self):
        """Test page load performance."""
        print("\n📊 Testing page load performance...")
        
        pages = [
            ('/', 'Dashboard'),
            ('/tasks', 'Tasks'),
            ('/statistics', 'Statistics'),
            ('/performance', 'Performance'),
            ('/repositories', 'Repositories')
        ]
        
        for url, page_name in pages:
            def load_page():
                self.driver.get(f'http://127.0.0.1:5000{url}')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            
            metrics = self.measure_performance(f'load_{page_name.lower()}', load_page, iterations=5)
            
            print(f"  {page_name}: {metrics['avg_time']:.3f}s avg, "
                  f"{metrics['min_time']:.3f}s min, {metrics['max_time']:.3f}s max")
            
            # Performance assertions
            assert metrics['avg_time'] < 3.0, f"{page_name} page load too slow: {metrics['avg_time']:.3f}s"
    
    def test_task_creation_performance(self):
        """Test task creation performance."""
        print("\n📊 Testing task creation performance...")
        
        # Login first
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('perfuser')
        self.driver.find_element(By.NAME, 'password').send_keys('perftest123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        
        def create_task():
            # Navigate to tasks page
            self.driver.get('http://127.0.0.1:5000/tasks')
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tasks-container'))
            )
            
            # Click create button
            create_button = self.driver.find_element(By.ID, 'create-task-btn')
            create_button.click()
            
            # Wait for form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'task-form'))
            )
            
            # Fill form
            task_type_select = self.driver.find_element(By.NAME, 'task_type')
            task_type_select.send_keys('generate_document')
            
            title_input = self.driver.find_element(By.NAME, 'title')
            title_input.send_keys(f'Performance Test Task {time.time()}')
            
            description_input = self.driver.find_element(By.NAME, 'description')
            description_input.send_keys('Performance test task')
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Wait for task creation
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
            )
        
        metrics = self.measure_performance('create_task', create_task, iterations=5)
        
        print(f"  Task Creation: {metrics['avg_time']:.3f}s avg, "
              f"{metrics['throughput']:.2f} tasks/sec")
        
        # Performance assertions
        assert metrics['avg_time'] < 5.0, f"Task creation too slow: {metrics['avg_time']:.3f}s"
        assert metrics['throughput'] > 0.2, f"Task creation throughput too low: {metrics['throughput']:.2f} tasks/sec"
    
    def test_batch_task_creation_performance(self):
        """Test batch task creation performance."""
        print("\n📊 Testing batch task creation performance...")
        
        # Login first
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('perfuser')
        self.driver.find_element(By.NAME, 'password').send_keys('perftest123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        
        def create_batch_tasks():
            # Navigate to batch tasks page
            self.driver.get('http://127.0.0.1:5000/tasks/batch')
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'batch-task-form'))
            )
            
            # Select all repositories
            repo_checkboxes = self.driver.find_elements(By.NAME, 'repositories')
            for checkbox in repo_checkboxes:
                if not checkbox.is_selected():
                    checkbox.click()
            
            # Select task type
            task_type_select = self.driver.find_element(By.NAME, 'task_type')
            task_type_select.send_keys('sync_repository')
            
            # Submit batch form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Wait for batch creation
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'batch-summary'))
            )
        
        metrics = self.measure_performance('create_batch_tasks', create_batch_tasks, iterations=3)
        
        print(f"  Batch Creation (10 tasks): {metrics['avg_time']:.3f}s avg, "
              f"{metrics['throughput']:.2f} batches/sec")
        
        # Performance assertions
        assert metrics['avg_time'] < 10.0, f"Batch task creation too slow: {metrics['avg_time']:.3f}s"
    
    def test_task_list_loading_performance(self):
        """Test task list loading performance."""
        print("\n📊 Testing task list loading performance...")
        
        # Create test tasks
        test_tasks = []
        for i in range(50):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repositories[i % len(self.repositories)].id,
                type=['generate_document', 'sync_repository', 'analyze_code'][i % 3],
                status=['pending', 'running', 'completed', 'failed'][i % 4],
                progress=[0, 25, 50, 75, 100][i % 5],
                title=f'Performance Test Task {i+1}',
                description=f'Performance test task {i+1}'
            )
            if task.status == 'completed':
                task.completed_at = datetime.utcnow()
            test_tasks.append(task)
        
        db.session.add_all(test_tasks)
        db.session.commit()
        
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('perfuser')
        self.driver.find_element(By.NAME, 'password').send_keys('perftest123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        def load_task_list():
            self.driver.get('http://127.0.0.1:5000/tasks')
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tasks-container'))
            )
            
            # Wait for tasks to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: len(driver.find_elements(By.CLASS_NAME, 'task-item')) >= 10
            )
        
        metrics = self.measure_performance('load_task_list', load_task_list, iterations=5)
        
        print(f"  Task List (50 tasks): {metrics['avg_time']:.3f}s avg, "
              f"{metrics['throughput']:.2f} lists/sec")
        
        # Performance assertions
        assert metrics['avg_time'] < 3.0, f"Task list loading too slow: {metrics['avg_time']:.3f}s"
    
    def test_search_performance(self):
        """Test search performance."""
        print("\n📊 Testing search performance...")
        
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('perfuser')
        self.driver.find_element(By.NAME, 'password').send_keys('perftest123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        
        def perform_search():
            self.driver.get('http://127.0.0.1:5000/tasks')
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tasks-container'))
            )
            
            # Perform search
            search_input = self.driver.find_element(By.NAME, 'search')
            search_input.send_keys('performance')
            search_input.send_keys(Keys.RETURN)
            
            # Wait for search results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'search-results'))
            )
        
        metrics = self.measure_performance('search_tasks', perform_search, iterations=5)
        
        print(f"  Search: {metrics['avg_time']:.3f}s avg, "
              f"{metrics['throughput']:.2f} searches/sec")
        
        # Performance assertions
        assert metrics['avg_time'] < 2.0, f"Search too slow: {metrics['avg_time']:.3f}s"
    
    def test_statistics_generation_performance(self):
        """Test statistics generation performance."""
        print("\n📊 Testing statistics generation performance...")
        
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('perfuser')
        self.driver.find_element(By.NAME, 'password').send_keys('perftest123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        def load_statistics():
            self.driver.get('http://127.0.0.1:5000/statistics')
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'statistics-container'))
            )
            
            # Wait for statistics to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: len(driver.find_elements(By.CLASS_NAME, 'stat-value')) > 0
            )
        
        metrics = self.measure_performance('load_statistics', load_statistics, iterations=5)
        
        print(f"  Statistics: {metrics['avg_time']:.3f}s avg, "
              f"{metrics['throughput']:.2f} stats/sec")
        
        # Performance assertions
        assert metrics['avg_time'] < 3.0, f"Statistics generation too slow: {metrics['avg_time']:.3f}s"
    
    def test_concurrent_user_performance(self):
        """Test concurrent user performance."""
        print("\n📊 Testing concurrent user performance...")
        
        def simulate_user_session():
            # Create new driver instance
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Login
                driver.get('http://127.0.0.1:5000/auth/login')
                driver.find_element(By.NAME, 'username').send_keys('perfuser')
                driver.find_element(By.NAME, 'password').send_keys('perftest123')
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'h1'))
                )
                
                # Navigate to tasks
                driver.get('http://127.0.0.1:5000/tasks')
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'tasks-container'))
                )
                
                # Create task
                create_button = driver.find_element(By.ID, 'create-task-btn')
                create_button.click()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'task-form'))
                )
                
                task_type_select = driver.find_element(By.NAME, 'task_type')
                task_type_select.send_keys('generate_document')
                
                title_input = driver.find_element(By.NAME, 'title')
                title_input.send_keys(f'Concurrent Test Task {time.time()}')
                
                description_input = driver.find_element(By.NAME, 'description')
                description_input.send_keys('Concurrent test task')
                
                submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
                )
                
                return True
                
            except Exception as e:
                print(f"Concurrent user session failed: {e}")
                return False
            finally:
                driver.quit()
        
        # Test with different numbers of concurrent users
        concurrent_users = [2, 5, 10]
        
        for num_users in concurrent_users:
            print(f"  Testing with {num_users} concurrent users...")
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(simulate_user_session) for _ in range(num_users)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            successful_sessions = sum(results)
            
            print(f"    {successful_sessions}/{num_users} successful sessions in {total_time:.3f}s")
            
            # Performance assertions
            success_rate = successful_sessions / num_users
            assert success_rate > 0.8, f"Low success rate for {num_users} concurrent users: {success_rate:.2%}"
            
            # Store metrics
            self.performance_metrics[f'concurrent_{num_users}_users'] = {
                'total_time': total_time,
                'successful_sessions': successful_sessions,
                'total_sessions': num_users,
                'success_rate': success_rate,
                'throughput': successful_sessions / total_time if total_time > 0 else 0
            }
    
    def test_memory_usage_performance(self):
        """Test memory usage during operations."""
        print("\n📊 Testing memory usage performance...")
        
        import psutil
        process = psutil.Process()
        
        def measure_memory_during_operation(operation_func):
            """Measure memory usage during operation."""
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            operation_func()
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            return {
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_increase': memory_increase
            }
        
        # Test memory usage during task creation
        def create_multiple_tasks():
            for i in range(10):
                task = Task(
                    user_id=self.user.id,
                    repository_id=self.repositories[i % len(self.repositories)].id,
                    type='generate_document',
                    status='pending',
                    progress=0,
                    title=f'Memory Test Task {i+1}',
                    description=f'Memory test task {i+1}'
                )
                db.session.add(task)
            db.session.commit()
        
        memory_metrics = measure_memory_during_operation(create_multiple_tasks)
        
        print(f"  Memory Usage: {memory_metrics['memory_before']:.1f}MB -> "
              f"{memory_metrics['memory_after']:.1f}MB "
              f"(+{memory_metrics['memory_increase']:.1f}MB)")
        
        # Performance assertions
        assert memory_metrics['memory_increase'] < 50, f"Memory increase too high: {memory_metrics['memory_increase']:.1f}MB"
        
        self.performance_metrics['memory_usage'] = memory_metrics
    
    def test_performance_summary(self):
        """Print performance summary."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        for operation, metrics in self.performance_metrics.items():
            if 'avg_time' in metrics:
                print(f"{operation.replace('_', ' ').title()}:")
                print(f"  Average Time: {metrics['avg_time']:.3f}s")
                print(f"  Min Time: {metrics['min_time']:.3f}s")
                print(f"  Max Time: {metrics['max_time']:.3f}s")
                if 'throughput' in metrics:
                    print(f"  Throughput: {metrics['throughput']:.2f} ops/sec")
                print()
            elif 'successful_sessions' in metrics:
                print(f"{operation.replace('_', ' ').title()}:")
                print(f"  Success Rate: {metrics['success_rate']:.2%}")
                print(f"  Total Time: {metrics['total_time']:.3f}s")
                print(f"  Throughput: {metrics['throughput']:.2f} sessions/sec")
                print()
            elif 'memory_increase' in metrics:
                print(f"Memory Usage:")
                print(f"  Memory Before: {metrics['memory_before']:.1f}MB")
                print(f"  Memory After: {metrics['memory_after']:.1f}MB")
                print(f"  Memory Increase: {metrics['memory_increase']:.1f}MB")
                print()
        
        print("=" * 60)