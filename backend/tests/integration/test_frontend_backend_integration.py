"""
Comprehensive integration tests for frontend-backend page accessibility and button interactions.
Tests ensure each page can be opened and each button click responds properly.
"""

import pytest
import json
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.task import Task


class TestPageAccessibility:
    """Test suite for verifying all pages are accessible."""
    
    def test_login_page_access(self, client):
        """Test login page is accessible without authentication."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
        assert b'loginForm' in response.data
    
    def test_register_page_access(self, client):
        """Test register page is accessible without authentication."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()
    
    def test_dashboard_page_requires_auth(self, client):
        """Test dashboard page requires authentication."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_dashboard_page_authenticated_access(self, auth_client):
        """Test dashboard page is accessible with authentication."""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()
        assert b'quickAddRepoBtn' in response.data
        assert b'quickGenerateDocBtn' in response.data
    
    def test_repositories_page_authenticated_access(self, auth_client):
        """Test repositories page is accessible with authentication."""
        response = auth_client.get('/repositories')
        assert response.status_code == 200
        assert b'repository' in response.data.lower()
    
    def test_tasks_page_authenticated_access(self, auth_client):
        """Test tasks page is accessible with authentication."""
        response = auth_client.get('/tasks')
        assert response.status_code == 200
        assert b'task' in response.data.lower()
    
    def test_analysis_page_authenticated_access(self, auth_client):
        """Test analysis page is accessible with authentication."""
        response = auth_client.get('/analysis')
        assert response.status_code == 200
        assert b'analysis' in response.data.lower()
    
    def test_settings_page_authenticated_access(self, auth_client):
        """Test settings page is accessible with authentication."""
        response = auth_client.get('/settings')
        assert response.status_code == 200
        assert b'settings' in response.data.lower()
    
    def test_documents_page_authenticated_access(self, auth_client):
        """Test documents page is accessible with authentication."""
        response = auth_client.get('/documents')
        assert response.status_code == 200
        assert b'document' in response.data.lower()
    
    def test_profile_page_authenticated_access(self, auth_client):
        """Test profile page is accessible with authentication."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
    
    def test_about_page_access(self, client):
        """Test about page is accessible without authentication."""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_contact_page_access(self, client):
        """Test contact page is accessible without authentication."""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_help_page_access(self, client):
        """Test help page is accessible without authentication."""
        response = client.get('/help')
        assert response.status_code == 200
    
    def test_analysis_results_page_requires_auth(self, client):
        """Test analysis results page requires authentication."""
        response = client.get('/analysis/1')
        assert response.status_code == 302  # Redirect to login
    
    def test_analysis_results_page_authenticated_access(self, auth_client, test_repository):
        """Test analysis results page is accessible with authentication."""
        response = auth_client.get(f'/analysis/{test_repository.id}')
        assert response.status_code == 200


class TestButtonInteractions:
    """Test suite for verifying button interactions work properly."""
    
    def test_login_button_interaction(self, client, test_user):
        """Test login button responds correctly."""
        login_data = {
            'username': test_user.username,
            'password': 'test_password_123'
        }
        
        response = client.post('/api/auth/login', 
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_login_button_invalid_credentials(self, client):
        """Test login button responds correctly to invalid credentials."""
        login_data = {
            'username': 'invalid_user',
            'password': 'invalid_password'
        }
        
        response = client.post('/api/auth/login', 
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_register_button_interaction(self, client):
        """Test register button responds correctly."""
        register_data = {
            'username': 'new_test_user',
            'email': 'newtest@example.com',
            'password': 'new_password_123',
            'confirm_password': 'new_password_123'
        }
        
        response = client.post('/api/auth/register', 
                              data=json.dumps(register_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_register_button_duplicate_user(self, client, test_user):
        """Test register button responds correctly to duplicate user."""
        register_data = {
            'username': test_user.username,
            'email': 'different@example.com',
            'password': 'password_123',
            'confirm_password': 'password_123'
        }
        
        response = client.post('/api/auth/register', 
                              data=json.dumps(register_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_repository_create_button_interaction(self, auth_client):
        """Test repository create button responds correctly."""
        repo_data = {
            'name': 'test_integration_repo',
            'url': 'https://github.com/test/integration-repo.git',
            'description': 'Test integration repository'
        }
        
        response = auth_client.post('/api/repositories', 
                                  data=json.dumps(repo_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_repository_delete_button_interaction(self, auth_client, test_repository):
        """Test repository delete button responds correctly."""
        response = auth_client.delete(f'/api/repositories/{test_repository.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_task_create_button_interaction(self, auth_client, test_repository):
        """Test task create button responds correctly."""
        task_data = {
            'repository_id': test_repository.id,
            'type': 'generate_document',
            'title': 'Integration Test Task',
            'description': 'Test task for integration testing'
        }
        
        response = auth_client.post('/api/tasks', 
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_task_status_button_interaction(self, auth_client, test_repository):
        """Test task status button responds correctly."""
        # Create a task first
        task_data = {
            'repository_id': test_repository.id,
            'type': 'generate_document',
            'title': 'Status Test Task',
            'description': 'Test task for status checking'
        }
        
        create_response = auth_client.post('/api/tasks', 
                                         data=json.dumps(task_data),
                                         content_type='application/json')
        
        task_id = json.loads(create_response.data)['task_id']
        
        # Check task status
        response = auth_client.get(f'/api/tasks/{task_id}/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_api_status_button_interaction(self, client):
        """Test API status button responds correctly."""
        response = client.get('/api/system/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_auth_status_button_interaction(self, client):
        """Test auth status button responds correctly."""
        response = client.get('/api/auth/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'logged_in' in data
    
    def test_document_generation_button_interaction(self, auth_client, test_repository):
        """Test document generation button responds correctly."""
        doc_data = {
            'repository_id': test_repository.id,
            'document_type': 'readme',
            'title': 'Integration Test Document'
        }
        
        response = auth_client.post('/api/documents', 
                                  data=json.dumps(doc_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_search_button_interaction(self, auth_client, test_repository):
        """Test search button responds correctly."""
        search_data = {
            'query': 'test',
            'type': 'repositories'
        }
        
        response = auth_client.post('/api/search', 
                                  data=json.dumps(search_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
    
    def test_export_button_interaction(self, auth_client, test_repository):
        """Test export button responds correctly."""
        export_data = {
            'repository_id': test_repository.id,
            'format': 'pdf',
            'include_analysis': True
        }
        
        response = auth_client.post('/api/export', 
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_user_profile_update_button_interaction(self, auth_client):
        """Test user profile update button responds correctly."""
        profile_data = {
            'email': 'updated@example.com',
            'preferences': {
                'theme': 'dark',
                'language': 'zh-CN'
            }
        }
        
        response = auth_client.put('/api/user/profile', 
                                 data=json.dumps(profile_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_password_change_button_interaction(self, auth_client):
        """Test password change button responds correctly."""
        password_data = {
            'current_password': 'test_password_123',
            'new_password': 'new_password_123',
            'confirm_password': 'new_password_123'
        }
        
        response = auth_client.post('/api/user/change-password', 
                                  data=json.dumps(password_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_logout_button_interaction(self, auth_client):
        """Test logout button responds correctly."""
        response = auth_client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_bulk_operations_button_interaction(self, auth_client, test_repository):
        """Test bulk operations button responds correctly."""
        bulk_data = {
            'action': 'delete',
            'repository_ids': [test_repository.id]
        }
        
        response = auth_client.post('/api/repositories/bulk', 
                                  data=json.dumps(bulk_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True


class TestFrontendJavaScriptIntegration:
    """Test suite for frontend JavaScript integration."""
    
    def test_ui_tests_page_access(self, client):
        """Test UI tests page is accessible."""
        response = client.get('/test-runner')
        assert response.status_code == 200
        assert b'UI Tests' in response.data
    
    def test_performance_tests_page_access(self, client):
        """Test performance tests page is accessible."""
        response = client.get('/test-analysis')
        assert response.status_code == 200
        assert b'Performance Tests' in response.data
    
    def test_ui_components_page_access(self, client):
        """Test UI components page is accessible."""
        response = client.get('/ui-components')
        assert response.status_code == 200
        assert b'UI Components' in response.data
    
    def test_document_viewer_page_access(self, auth_client):
        """Test document viewer page is accessible."""
        response = auth_client.get('/document/viewer')
        assert response.status_code == 200
        assert b'Document Viewer' in response.data
    
    def test_frontend_javascript_files_served(self, client):
        """Test frontend JavaScript files are served correctly."""
        js_files = [
            '/static/js/main.js',
            '/static/js/dashboard.js',
            '/static/js/auth.js',
            '/static/js/navigation.js',
            '/static/js/components.js',
            '/static/js/api_client.js',
            '/static/js/ui-tests.js'
        ]
        
        for js_file in js_files:
            response = client.get(js_file)
            assert response.status_code == 200
    
    def test_frontend_css_files_served(self, client):
        """Test frontend CSS files are served correctly."""
        css_files = [
            '/static/css/style.css',
            '/static/css/dashboard.css',
            '/static/css/navigation.css',
            '/static/css/components.css'
        ]
        
        for css_file in css_files:
            response = client.get(css_file)
            assert response.status_code == 200


class TestErrorHandling:
    """Test suite for error handling in page access and button interactions."""
    
    def test_404_page_handling(self, client):
        """Test 404 page is handled correctly."""
        response = client.get('/non-existent-page')
        assert response.status_code == 404
    
    def test_403_page_handling(self, auth_client, test_repository):
        """Test 403 page is handled correctly for unauthorized access."""
        # Try to access another user's repository analysis
        response = auth_client.get(f'/analysis/{test_repository.id}')
        # This should work since it's the same user
        
        # Create another user and try to access their repository
        other_user = User(
            username='other_user',
            email='other@example.com'
        )
        other_user.set_password('password_123')
        db.session.add(other_user)
        db.session.commit()
        
        # Create repository for other user
        other_repo = Repository(
            user_id=other_user.id,
            name='other_repo',
            url='https://github.com/other/repo.git',
            description='Other user repository'
        )
        db.session.add(other_repo)
        db.session.commit()
        
        # Try to access other user's repository analysis
        response = auth_client.get(f'/analysis/{other_repo.id}')
        assert response.status_code == 302  # Should redirect to repositories page
    
    def test_api_error_handling(self, client):
        """Test API error handling for invalid requests."""
        # Test invalid JSON
        response = client.post('/api/auth/login', 
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400
        
        # Test missing required fields
        response = client.post('/api/auth/login', 
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_database_error_handling(self, auth_client):
        """Test database error handling."""
        # Test with non-existent repository ID
        response = auth_client.get('/analysis/99999')
        assert response.status_code == 404


class TestPerformanceAndLoad:
    """Test suite for performance and load testing."""
    
    def test_page_load_performance(self, client):
        """Test page load performance."""
        import time
        
        pages_to_test = [
            '/login',
            '/register',
            '/about',
            '/contact',
            '/help'
        ]
        
        for page in pages_to_test:
            start_time = time.time()
            response = client.get(page)
            end_time = time.time()
            
            load_time = end_time - start_time
            assert response.status_code == 200
            assert load_time < 2.0  # Page should load in less than 2 seconds
    
    def test_api_response_performance(self, auth_client):
        """Test API response performance."""
        import time
        
        # Test API endpoints
        api_endpoints = [
            '/api/system/status',
            '/api/auth/status',
            '/api/user/profile'
        ]
        
        for endpoint in api_endpoints:
            start_time = time.time()
            response = auth_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 1.0  # API should respond in less than 1 second
    
    def test_concurrent_page_access(self, client):
        """Test concurrent page access."""
        import threading
        import time
        
        def access_page(url, results):
            try:
                start_time = time.time()
                response = client.get(url)
                end_time = time.time()
                results.append({
                    'url': url,
                    'status': response.status_code,
                    'load_time': end_time - start_time
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e)
                })
        
        pages = ['/login', '/register', '/about', '/contact', '/help']
        results = []
        threads = []
        
        for page in pages:
            thread = threading.Thread(target=access_page, args=(page, results))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All pages should be accessible
        for result in results:
            assert 'error' not in result
            assert result['status'] == 200
            assert result['load_time'] < 2.0


@pytest.mark.slow
class TestComprehensiveIntegration:
    """Comprehensive integration tests covering the complete user journey."""
    
    def test_complete_user_journey(self, client):
        """Test complete user journey from registration to dashboard usage."""
        # 1. Register new user
        register_data = {
            'username': 'journey_user',
            'email': 'journey@example.com',
            'password': 'journey_password_123',
            'confirm_password': 'journey_password_123'
        }
        
        response = client.post('/api/auth/register', 
                              data=json.dumps(register_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        register_result = json.loads(response.data)
        assert register_result['success'] == True
        
        # 2. Login with new user
        login_data = {
            'username': 'journey_user',
            'password': 'journey_password_123'
        }
        
        response = client.post('/api/auth/login', 
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        login_result = json.loads(response.data)
        assert login_result['success'] == True
        
        # 3. Access dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()
        
        # 4. Create repository
        repo_data = {
            'name': 'journey_test_repo',
            'url': 'https://github.com/journey/test-repo.git',
            'description': 'Test repository for user journey'
        }
        
        response = client.post('/api/repositories', 
                              data=json.dumps(repo_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        repo_result = json.loads(response.data)
        assert repo_result['success'] == True
        
        # 5. Access repositories page
        response = client.get('/repositories')
        assert response.status_code == 200
        assert b'repository' in response.data.lower()
        
        # 6. Create task
        task_data = {
            'repository_id': repo_result['repository_id'],
            'type': 'generate_document',
            'title': 'Journey Test Task',
            'description': 'Test task created during user journey'
        }
        
        response = client.post('/api/tasks', 
                              data=json.dumps(task_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        task_result = json.loads(response.data)
        assert task_result['success'] == True
        
        # 7. Check task status
        response = client.get(f'/api/tasks/{task_result["task_id"]}/status')
        assert response.status_code == 200
        status_result = json.loads(response.data)
        assert 'status' in status_result
        
        # 8. Access profile page
        response = client.get('/profile')
        assert response.status_code == 200
        
        # 9. Logout
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        logout_result = json.loads(response.data)
        assert logout_result['success'] == True
        
        # 10. Verify logout - should be redirected to login
        response = client.get('/dashboard')
        assert response.status_code == 302