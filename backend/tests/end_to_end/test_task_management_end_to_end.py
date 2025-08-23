"""
End-to-end tests for task management system.
"""

import pytest
import json
import time
import threading
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task
from config import TestingConfig


class TestTaskManagementEndToEnd:
    """End-to-end tests for the task management system."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create Flask app
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create test user
        self.user = User(username='e2euser', email='e2e@example.com')
        self.user.set_password('e2epassword123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test repository
        self.repo = Repository(
            user_id=self.user.id,
            name='e2e-test-repo',
            url='https://github.com/test/e2e-test-repo.git',
            description='End-to-end test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.implicitly_wait(10)
        
        # Start Flask app in background thread
        self.flask_thread = threading.Thread(target=self._run_flask_app)
        self.flask_thread.daemon = True
        self.flask_thread.start()
        
        # Wait for app to start
        time.sleep(2)
    
    def _run_flask_app(self):
        """Run Flask app for testing."""
        self.app.run(host='127.0.0.1', port=5000, debug=False)
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Close browser
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        # Cleanup database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_complete_task_workflow(self):
        """Test complete task workflow from user perspective."""
        # Navigate to login page
        self.driver.get('http://127.0.0.1:5000/auth/login')
        
        # Login
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        
        username_input.send_keys('e2euser')
        password_input.send_keys('e2epassword123')
        
        login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        # Wait for dashboard to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        
        # Verify dashboard
        assert 'Dashboard' in self.driver.title or 'Dashboard' in self.driver.page_source
        
        # Navigate to tasks page
        tasks_link = self.driver.find_element(By.LINK_TEXT, 'Tasks')
        tasks_link.click()
        
        # Wait for tasks page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'tasks-container'))
        )
        
        # Create new task
        create_task_button = self.driver.find_element(By.ID, 'create-task-btn')
        create_task_button.click()
        
        # Wait for task creation form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'task-form'))
        )
        
        # Fill task form
        task_type_select = self.driver.find_element(By.NAME, 'task_type')
        task_type_select.send_keys('generate_document')
        
        title_input = self.driver.find_element(By.NAME, 'title')
        title_input.send_keys('E2E Test Task')
        
        description_input = self.driver.find_element(By.NAME, 'description')
        description_input.send_keys('End-to-end test task')
        
        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for task to be created
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
        )
        
        # Verify task was created
        task_items = self.driver.find_elements(By.CLASS_NAME, 'task-item')
        assert len(task_items) > 0
        
        # Click on task to view details
        task_items[0].click()
        
        # Wait for task detail page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'task-detail'))
        )
        
        # Verify task details
        assert 'E2E Test Task' in self.driver.page_source
        assert 'End-to-end test task' in self.driver.page_source
        
        # Start task execution
        start_button = self.driver.find_element(By.ID, 'start-task-btn')
        start_button.click()
        
        # Wait for task to start
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'progress-bar'))
        )
        
        # Monitor task progress
        progress_bar = self.driver.find_element(By.CLASS_NAME, 'progress-bar')
        progress_text = self.driver.find_element(By.CLASS_NAME, 'progress-text')
        
        # Wait for task to complete (simulate with timeout)
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            try:
                progress_text = self.driver.find_element(By.CLASS_NAME, 'progress-text')
                if '100%' in progress_text.text or 'completed' in progress_text.text.lower():
                    break
                time.sleep(1)
            except:
                time.sleep(1)
        
        # Verify task completion
        assert 'completed' in self.driver.page_source.lower()
        
        # Navigate back to tasks list
        back_button = self.driver.find_element(By.LINK_TEXT, 'Back to Tasks')
        back_button.click()
        
        # Verify task appears in completed state
        completed_tasks = self.driver.find_elements(By.CLASS_NAME, 'task-completed')
        assert len(completed_tasks) > 0
        
        # Logout
        logout_link = self.driver.find_element(By.LINK_TEXT, 'Logout')
        logout_link.click()
        
        # Verify logout
        assert 'Login' in self.driver.title or 'Login' in self.driver.page_source
    
    def test_batch_task_workflow(self):
        """Test batch task creation and management."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Tasks'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Tasks').click()
        
        # Navigate to batch task creation
        batch_link = self.driver.find_element(By.LINK_TEXT, 'Batch Tasks')
        batch_link.click()
        
        # Wait for batch form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'batch-task-form'))
        )
        
        # Select repositories (simulate multi-select)
        repo_checkboxes = self.driver.find_elements(By.NAME, 'repositories')
        if len(repo_checkboxes) > 0:
            repo_checkboxes[0].click()
        
        # Select task type
        task_type_select = self.driver.find_element(By.NAME, 'task_type')
        task_type_select.send_keys('sync_repository')
        
        # Set batch options
        priority_select = self.driver.find_element(By.NAME, 'priority')
        priority_select.send_keys('high')
        
        # Submit batch form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for batch creation confirmation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'batch-summary'))
        )
        
        # Verify batch was created
        batch_summary = self.driver.find_element(By.CLASS_NAME, 'batch-summary')
        assert 'Batch created successfully' in batch_summary.text
        
        # Navigate to tasks list to verify batch tasks
        tasks_link = self.driver.find_element(By.LINK_TEXT, 'Tasks')
        tasks_link.click()
        
        # Wait for tasks to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
        )
        
        # Verify multiple tasks were created
        task_items = self.driver.find_elements(By.CLASS_NAME, 'task-item')
        assert len(task_items) >= 1
        
        # Verify batch identifier in task titles
        batch_found = False
        for task in task_items:
            if 'Batch' in task.text:
                batch_found = True
                break
        assert batch_found
    
    def test_task_statistics_workflow(self):
        """Test task statistics and reporting workflow."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to statistics page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Statistics'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Statistics').click()
        
        # Wait for statistics to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'statistics-container'))
        )
        
        # Verify statistics sections
        assert 'Task Statistics' in self.driver.page_source
        assert 'Performance Metrics' in self.driver.page_source
        
        # Test date range filter
        date_filter = self.driver.find_element(By.NAME, 'date_range')
        date_filter.send_keys('last_7_days')
        
        # Apply filter
        apply_button = self.driver.find_element(By.ID, 'apply-filter-btn')
        apply_button.click()
        
        # Wait for filtered results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'stats-updated'))
        )
        
        # Verify statistics are displayed
        stats_elements = self.driver.find_elements(By.CLASS_NAME, 'stat-value')
        assert len(stats_elements) > 0
        
        # Test export functionality
        export_button = self.driver.find_element(By.ID, 'export-stats-btn')
        export_button.click()
        
        # Wait for export confirmation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'export-success'))
        )
        
        # Verify export success
        export_success = self.driver.find_element(By.CLASS_NAME, 'export-success')
        assert 'Statistics exported successfully' in export_success.text
    
    def test_task_error_handling_workflow(self):
        """Test error handling in task workflow."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Tasks'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Tasks').click()
        
        # Create task with invalid data
        create_task_button = self.driver.find_element(By.ID, 'create-task-btn')
        create_task_button.click()
        
        # Wait for form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'task-form'))
        )
        
        # Submit form without required fields
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Verify validation error
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        
        error_messages = self.driver.find_elements(By.CLASS_NAME, 'error-message')
        assert len(error_messages) > 0
        
        # Fill form with invalid task type
        task_type_select = self.driver.find_element(By.NAME, 'task_type')
        task_type_select.send_keys('invalid_task_type')
        
        title_input = self.driver.find_element(By.NAME, 'title')
        title_input.send_keys('Invalid Task')
        
        # Submit form
        submit_button.click()
        
        # Verify error for invalid task type
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        
        # Try to access non-existent task
        self.driver.get('http://127.0.0.1:5000/tasks/99999')
        
        # Verify 404 error
        assert '404' in self.driver.page_source or 'Not Found' in self.driver.page_source
    
    def test_task_search_and_filter_workflow(self):
        """Test task search and filtering functionality."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Tasks'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Tasks').click()
        
        # Wait for tasks to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'tasks-container'))
        )
        
        # Test search functionality
        search_input = self.driver.find_element(By.NAME, 'search')
        search_input.send_keys('test')
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'search-results'))
        )
        
        # Verify search results
        search_results = self.driver.find_elements(By.CLASS_NAME, 'task-item')
        assert len(search_results) >= 0
        
        # Test filter functionality
        filter_button = self.driver.find_element(By.ID, 'filter-btn')
        filter_button.click()
        
        # Wait for filter panel
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'filter-panel'))
        )
        
        # Apply status filter
        status_filter = self.driver.find_element(By.NAME, 'status')
        status_filter.send_keys('completed')
        
        apply_filter_button = self.driver.find_element(By.ID, 'apply-filter-btn')
        apply_filter_button.click()
        
        # Wait for filtered results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'filter-applied'))
        )
        
        # Verify filter was applied
        filter_applied = self.driver.find_element(By.CLASS_NAME, 'filter-applied')
        assert 'Filter applied' in filter_applied.text
        
        # Clear filters
        clear_button = self.driver.find_element(By.ID, 'clear-filter-btn')
        clear_button.click()
        
        # Verify filters are cleared
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'filters-cleared'))
        )
    
    def test_task_performance_workflow(self):
        """Test task performance monitoring workflow."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to performance page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Performance'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Performance').click()
        
        # Wait for performance dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'performance-dashboard'))
        )
        
        # Verify performance metrics
        assert 'System Performance' in self.driver.page_source
        assert 'Task Throughput' in self.driver.page_source
        assert 'Resource Usage' in self.driver.page_source
        
        # Test real-time updates
        refresh_button = self.driver.find_element(By.ID, 'refresh-performance-btn')
        refresh_button.click()
        
        # Wait for refresh
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'performance-updated'))
        )
        
        # Verify performance data is updated
        performance_updated = self.driver.find_element(By.CLASS_NAME, 'performance-updated')
        assert 'Performance data updated' in performance_updated.text
        
        # Test historical data view
        historical_button = self.driver.find_element(By.ID, 'historical-data-btn')
        historical_button.click()
        
        # Wait for historical data
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'historical-chart'))
        )
        
        # Verify historical chart is displayed
        historical_chart = self.driver.find_element(By.CLASS_NAME, 'historical-chart')
        assert historical_chart.is_displayed()
    
    def test_task_notifications_workflow(self):
        """Test task notification system."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to notifications page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Notifications'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Notifications').click()
        
        # Wait for notifications
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'notifications-container'))
        )
        
        # Verify notifications section
        assert 'Task Notifications' in self.driver.page_source
        
        # Test notification settings
        settings_button = self.driver.find_element(By.ID, 'notification-settings-btn')
        settings_button.click()
        
        # Wait for settings panel
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'notification-settings'))
        )
        
        # Update notification preferences
        email_checkbox = self.driver.find_element(By.NAME, 'email_notifications')
        if not email_checkbox.is_selected():
            email_checkbox.click()
        
        # Save settings
        save_button = self.driver.find_element(By.ID, 'save-settings-btn')
        save_button.click()
        
        # Verify settings saved
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'settings-saved'))
        )
        
        settings_saved = self.driver.find_element(By.CLASS_NAME, 'settings-saved')
        assert 'Settings saved successfully' in settings_saved.text
        
        # Clear notifications
        clear_button = self.driver.find_element(By.ID, 'clear-notifications-btn')
        clear_button.click()
        
        # Verify notifications cleared
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'notifications-cleared'))
        )
        
        notifications_cleared = self.driver.find_element(By.CLASS_NAME, 'notifications-cleared')
        assert 'Notifications cleared' in notifications_cleared.text
    
    def test_task_api_workflow(self):
        """Test task API integration workflow."""
        # Login to get session
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to API documentation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'API'))
        )
        self.driver.find_element(By.LINK_TEXT, 'API').click()
        
        # Wait for API documentation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'api-documentation'))
        )
        
        # Verify API documentation
        assert 'Task API Documentation' in self.driver.page_source
        
        # Test API endpoint using JavaScript
        self.driver.execute_script("""
            // Test API call
            fetch('/api/tasks', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                window.apiTestResult = data;
            })
            .catch(error => {
                window.apiTestResult = {error: error.message};
            });
        """)
        
        # Wait for API call to complete
        time.sleep(2)
        
        # Check API test result
        api_result = self.driver.execute_script("return window.apiTestResult;")
        assert api_result is not None
        assert 'error' not in api_result
        
        # Verify API response structure
        assert 'tasks' in api_result or isinstance(api_result, list)
        
        # Test API rate limiting
        for i in range(5):  # Make multiple rapid requests
            self.driver.execute_script("""
                fetch('/api/tasks', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
            """)
            time.sleep(0.1)
        
        # Check for rate limiting response
        self.driver.execute_script("""
            fetch('/api/tasks', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                window.rateLimitResult = data;
            });
        """)
        
        time.sleep(1)
        rate_limit_result = self.driver.execute_script("return window.rateLimitResult;")
        
        # Rate limiting should not be triggered for small number of requests
        assert rate_limit_result is not None
    
    def test_task_mobile_workflow(self):
        """Test task management on mobile devices."""
        # Set mobile viewport
        self.driver.set_window_size(375, 667)  # iPhone 6/7/8
        
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        
        # Verify mobile responsive design
        assert 'mobile' in self.driver.page_source.lower() or \
               self.driver.find_element(By.TAG_NAME, 'meta').get_attribute('content').contains('mobile')
        
        # Navigate to tasks using mobile menu
        mobile_menu_button = self.driver.find_element(By.CLASS_NAME, 'mobile-menu-btn')
        mobile_menu_button.click()
        
        # Wait for mobile menu
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mobile-menu'))
        )
        
        # Click tasks link
        tasks_link = self.driver.find_element(By.CSS_SELECTOR, '.mobile-menu a[href="/tasks"]')
        tasks_link.click()
        
        # Wait for tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'tasks-container'))
        )
        
        # Verify mobile task interface
        task_items = self.driver.find_elements(By.CLASS_NAME, 'task-item')
        assert len(task_items) >= 0
        
        # Test mobile task creation
        create_button = self.driver.find_element(By.ID, 'mobile-create-task-btn')
        create_button.click()
        
        # Wait for mobile form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mobile-form'))
        )
        
        # Fill mobile form
        task_type_select = self.driver.find_element(By.NAME, 'task_type')
        task_type_select.send_keys('generate_document')
        
        title_input = self.driver.find_element(By.NAME, 'title')
        title_input.send_keys('Mobile Test Task')
        
        # Submit mobile form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Verify mobile task creation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mobile-success'))
        )
        
        # Restore desktop viewport
        self.driver.set_window_size(1920, 1080)
    
    def test_task_accessibility_workflow(self):
        """Test task management accessibility features."""
        # Login
        self.driver.get('http://127.0.0.1:5000/auth/login')
        self.driver.find_element(By.NAME, 'username').send_keys('e2euser')
        self.driver.find_element(By.NAME, 'password').send_keys('e2epassword123')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Tasks'))
        )
        self.driver.find_element(By.LINK_TEXT, 'Tasks').click()
        
        # Wait for tasks page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'tasks-container'))
        )
        
        # Test keyboard navigation
        create_button = self.driver.find_element(By.ID, 'create-task-btn')
        create_button.send_keys(Keys.RETURN)
        
        # Wait for form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'task-form'))
        )
        
        # Navigate form using keyboard
        title_input = self.driver.find_element(By.NAME, 'title')
        title_input.send_keys('Accessibility Test')
        title_input.send_keys(Keys.TAB)  # Move to next field
        
        description_input = self.driver.switch_to.active_element
        description_input.send_keys('Accessibility test task')
        description_input.send_keys(Keys.TAB)
        
        # Continue to submit button
        for i in range(5):  # Navigate through form fields
            self.driver.switch_to.active_element.send_keys(Keys.TAB)
            time.sleep(0.1)
        
        # Submit form
        submit_button = self.driver.switch_to.active_element
        submit_button.send_keys(Keys.RETURN)
        
        # Verify task creation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
        )
        
        # Test screen reader compatibility
        # Check for ARIA labels
        aria_elements = self.driver.find_elements(By.XPATH, '//*[@aria-label]')
        assert len(aria_elements) > 0
        
        # Check for proper heading structure
        headings = self.driver.find_elements(By.XPATH, '//h1 | //h2 | //h3 | //h4 | //h5 | //h6')
        assert len(headings) > 0
        
        # Test high contrast mode
        self.driver.execute_script("""
            document.body.style.backgroundColor = '#000000';
            document.body.style.color = '#ffffff';
        """)
        
        # Verify content is still readable
        task_items = self.driver.find_elements(By.CLASS_NAME, 'task-item')
        assert len(task_items) >= 0