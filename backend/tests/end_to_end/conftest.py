"""
End-to-end test configuration and utilities.
"""

import pytest
import tempfile
import os
import time
import threading
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
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


class EndToEndTestConfig:
    """Configuration for end-to-end tests."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'e2e-test-secret-key'
    WTF_CSRF_ENABLED = False
    
    # Server configuration
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 5000
    SERVER_DEBUG = False
    
    # Selenium configuration
    SELENIUM_TIMEOUT = 30
    SELENIUM_IMPLICIT_WAIT = 10
    
    # Test configuration
    TEST_USER_USERNAME = 'e2e_test_user'
    TEST_USER_EMAIL = 'e2e@test.com'
    TEST_USER_PASSWORD = 'e2e_test_password_123'
    
    # Performance test settings
    PERFORMANCE_TEST_ITERATIONS = 5
    PERFORMANCE_TEST_TIMEOUT = 60


@pytest.fixture(scope='session')
def app():
    """Create application for end-to-end tests."""
    app = create_app(EndToEndTestConfig)
    return app


@pytest.fixture(scope='session')
def test_db(app):
    """Create database for end-to-end tests."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def db_session(app, test_db):
    """Create database session for each test."""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        username=EndToEndTestConfig.TEST_USER_USERNAME,
        email=EndToEndTestConfig.TEST_USER_EMAIL
    )
    user.set_password(EndToEndTestConfig.TEST_USER_PASSWORD)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_repository(db_session, test_user):
    """Create test repository."""
    repo = Repository(
        user_id=test_user.id,
        name='e2e-test-repository',
        url='https://github.com/test/e2e-test-repository.git',
        description='End-to-end test repository'
    )
    db_session.add(repo)
    db_session.commit()
    return repo


@pytest.fixture
def test_tasks(db_session, test_user, test_repository):
    """Create test tasks."""
    tasks = []
    task_data = [
        ('generate_document', 'pending', 0, 'E2E Document Generation'),
        ('sync_repository', 'running', 50, 'E2E Repository Sync'),
        ('analyze_code', 'completed', 100, 'E2E Code Analysis'),
        ('generate_document', 'failed', 75, 'E2E Failed Document'),
        ('sync_repository', 'completed', 100, 'E2E Completed Sync')
    ]
    
    for task_type, status, progress, title in task_data:
        task = Task(
            user_id=test_user.id,
            repository_id=test_repository.id,
            type=task_type,
            status=status,
            progress=progress,
            title=title,
            description=f'E2E test task: {title}'
        )
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        db_session.add(task)
        tasks.append(task)
    
    db_session.commit()
    return tasks


@pytest.fixture
def selenium_driver():
    """Create Selenium WebDriver for testing."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Set implicit wait
    driver.implicitly_wait(EndToEndTestConfig.SELENIUM_IMPLICIT_WAIT)
    
    yield driver
    
    # Cleanup
    driver.quit()


@pytest.fixture
def mobile_driver():
    """Create mobile Selenium WebDriver for testing."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=375,667')  # iPhone 6/7/8
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X)')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.implicitly_wait(EndToEndTestConfig.SELENIUM_IMPLICIT_WAIT)
    
    yield driver
    
    driver.quit()


@pytest.fixture
def flask_server(app):
    """Start Flask server for testing."""
    server_thread = threading.Thread(
        target=lambda: app.run(
            host=EndToEndTestConfig.SERVER_HOST,
            port=EndToEndTestConfig.SERVER_PORT,
            debug=EndToEndTestConfig.SERVER_DEBUG
        )
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield f'http://{EndToEndTestConfig.SERVER_HOST}:{EndToEndTestConfig.SERVER_PORT}'
    
    # Server will be stopped when thread exits


@pytest.fixture
def authenticated_session(selenium_driver, flask_server, test_user):
    """Create authenticated browser session."""
    # Navigate to login page
    selenium_driver.get(f'{flask_server}/auth/login')
    
    # Login
    username_input = selenium_driver.find_element(By.NAME, 'username')
    password_input = selenium_driver.find_element(By.NAME, 'password')
    
    username_input.send_keys(test_user.username)
    password_input.send_keys(EndToEndTestConfig.TEST_USER_PASSWORD)
    
    login_button = selenium_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()
    
    # Wait for login to complete
    WebDriverWait(selenium_driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h1'))
    )
    
    return selenium_driver


class EndToEndTestHelpers:
    """Helper utilities for end-to-end tests."""
    
    @staticmethod
    def login(driver, server_url, username, password):
        """Login to the application."""
        driver.get(f'{server_url}/auth/login')
        
        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        WebDriverWait(driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
    
    @staticmethod
    def create_task(driver, task_type='generate_document', title='Test Task', description='Test description'):
        """Create a new task."""
        # Navigate to tasks page
        driver.find_element(By.LINK_TEXT, 'Tasks').click()
        
        WebDriverWait(driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, 'tasks-container'))
        )
        
        # Click create button
        create_button = driver.find_element(By.ID, 'create-task-btn')
        create_button.click()
        
        # Wait for form
        WebDriverWait(driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, 'task-form'))
        )
        
        # Fill form
        task_type_select = driver.find_element(By.NAME, 'task_type')
        task_type_select.send_keys(task_type)
        
        title_input = driver.find_element(By.NAME, 'title')
        title_input.send_keys(title)
        
        description_input = driver.find_element(By.NAME, 'description')
        description_input.send_keys(description)
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for task creation
        WebDriverWait(driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'task-item'))
        )
        
        return driver.find_element(By.CLASS_NAME, 'task-item')
    
    @staticmethod
    def wait_for_task_completion(driver, timeout=60):
        """Wait for task to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                progress_text = driver.find_element(By.CLASS_NAME, 'progress-text')
                if '100%' in progress_text.text or 'completed' in progress_text.text.lower():
                    return True
            except:
                pass
            
            time.sleep(1)
        
        return False
    
    @staticmethod
    def get_task_statistics(driver):
        """Get task statistics from the page."""
        driver.find_element(By.LINK_TEXT, 'Statistics').click()
        
        WebDriverWait(driver, EndToEndTestConfig.SELENIUM_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, 'statistics-container'))
        )
        
        stats = {}
        stat_elements = driver.find_elements(By.CLASS_NAME, 'stat-value')
        
        for element in stat_elements:
            key = element.get_attribute('data-stat-key')
            value = element.text
            if key:
                stats[key] = value
        
        return stats
    
    @staticmethod
    def test_performance(driver, operation_func, iterations=5):
        """Test performance of an operation."""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            operation_func()
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'total_time': sum(times),
            'iterations': iterations
        }
    
    @staticmethod
    def test_accessibility(driver):
        """Test accessibility features."""
        accessibility_results = {
            'aria_labels': 0,
            'headings': 0,
            'alt_text': 0,
            'form_labels': 0,
            'keyboard_navigable': False
        }
        
        # Count ARIA labels
        aria_elements = driver.find_elements(By.XPATH, '//*[@aria-label]')
        accessibility_results['aria_labels'] = len(aria_elements)
        
        # Count headings
        headings = driver.find_elements(By.XPATH, '//h1 | //h2 | //h3 | //h4 | //h5 | //h6')
        accessibility_results['headings'] = len(headings)
        
        # Count alt text
        images = driver.find_elements(By.TAG_NAME, 'img')
        alt_count = 0
        for img in images:
            if img.get_attribute('alt'):
                alt_count += 1
        accessibility_results['alt_text'] = alt_count
        
        # Count form labels
        labels = driver.find_elements(By.TAG_NAME, 'label')
        accessibility_results['form_labels'] = len(labels)
        
        # Test keyboard navigation
        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.TAB)
            accessibility_results['keyboard_navigable'] = True
        except:
            pass
        
        return accessibility_results
    
    @staticmethod
    def test_mobile_responsive(driver):
        """Test mobile responsive design."""
        # Test different screen sizes
        screen_sizes = [
            (375, 667),  # iPhone 6/7/8
            (414, 736),  # iPhone 6/7/8 Plus
            (768, 1024), # iPad
            (1024, 768)  # iPad landscape
        ]
        
        results = {}
        
        for width, height in screen_sizes:
            driver.set_window_size(width, height)
            time.sleep(1)  # Wait for resize
            
            # Check if content is properly scaled
            body = driver.find_element(By.TAG_NAME, 'body')
            page_width = body.size['width']
            
            # Check for mobile-specific elements
            try:
                mobile_menu = driver.find_element(By.CLASS_NAME, 'mobile-menu')
                has_mobile_menu = mobile_menu.is_displayed()
            except:
                has_mobile_menu = False
            
            results[f'{width}x{height}'] = {
                'page_width': page_width,
                'has_mobile_menu': has_mobile_menu,
                'responsive': page_width <= width
            }
        
        return results
    
    @staticmethod
    def capture_screenshot(driver, test_name):
        """Capture screenshot for debugging."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{test_name}_{timestamp}.png'
        
        try:
            driver.save_screenshot(filename)
            return filename
        except:
            return None
    
    @staticmethod
    def get_page_load_time(driver, url):
        """Get page load time."""
        start_time = time.time()
        driver.get(url)
        end_time = time.time()
        
        return end_time - start_time
    
    @staticmethod
    def test_api_endpoints(driver, base_url):
        """Test API endpoints."""
        api_endpoints = [
            '/api/tasks',
            '/api/tasks/statistics',
            '/api/repositories',
            '/api/users/profile'
        ]
        
        results = {}
        
        for endpoint in api_endpoints:
            try:
                # Make API call via JavaScript
                script = f"""
                    fetch('{base_url}{endpoint}', {{
                        method: 'GET',
                        headers: {{
                            'Content-Type': 'application/json'
                        }}
                    }})
                    .then(response => {{
                        window.apiResult = {{
                            status: response.status,
                            ok: response.ok,
                            data: null
                        }};
                        return response.json();
                    }})
                    .then(data => {{
                        window.apiResult.data = data;
                    }})
                    .catch(error => {{
                        window.apiResult = {{
                            status: 0,
                            ok: false,
                            error: error.message
                        }};
                    }});
                """
                
                driver.execute_script(script)
                time.sleep(2)  # Wait for API call
                
                result = driver.execute_script("return window.apiResult;")
                results[endpoint] = result
                
            except Exception as e:
                results[endpoint] = {'error': str(e)}
        
        return results


@pytest.fixture
def test_helpers():
    """End-to-end test helpers fixture."""
    return EndToEndTestHelpers()


# Custom pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "mobile: marks tests as mobile-specific tests"
    )
    config.addinivalue_line(
        "markers", "accessibility: marks tests as accessibility tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark end-to-end tests
        if "end_to_end" in item.name or "e2e" in item.name:
            item.add_marker(pytest.mark.e2e)
        
        # Mark mobile tests
        if "mobile" in item.name:
            item.add_marker(pytest.mark.mobile)
        
        # Mark accessibility tests
        if "accessibility" in item.name:
            item.add_marker(pytest.mark.accessibility)
        
        # Mark performance tests
        if "performance" in item.name:
            item.add_marker(pytest.mark.performance)