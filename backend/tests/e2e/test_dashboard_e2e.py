"""
End-to-end tests for dashboard functionality.
"""

import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.repository import Repository
from app.models.document import Document
from config import TestingConfig


class TestDashboardE2E:
    """End-to-end tests for dashboard functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(self.user)
        db.session.commit()
        
        self.client = self.app.test_client()
        
        # Mock login
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id
            sess['_fresh'] = True
    
    def teardown_method(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_dashboard_page_loads(self):
        """Test that dashboard page loads successfully."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert b'CoderWiki' in response.data
        assert '欢迎使用 CoderWiki' in response.data.decode('utf-8')
        assert '仪表板' in response.data.decode('utf-8')
    
    def test_dashboard_renders_repository_list(self):
        """Test that dashboard renders repository list section."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '我的仓库' in response.data.decode('utf-8')
        assert '搜索仓库' in response.data.decode('utf-8')
        assert '添加仓库' in response.data.decode('utf-8')
    
    def test_dashboard_renders_statistics_cards(self):
        """Test that dashboard renders statistics cards."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '仓库总数' in response.data.decode('utf-8')
        assert '文档总数' in response.data.decode('utf-8')
        assert '进行中任务' in response.data.decode('utf-8')
        assert '本月生成' in response.data.decode('utf-8')
    
    def test_dashboard_renders_recent_activity(self):
        """Test that dashboard renders recent activity section."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '最近活动' in response.data.decode('utf-8')
        assert '欢迎加入' in response.data.decode('utf-8')
    
    def test_dashboard_renders_quick_actions(self):
        """Test that dashboard renders quick actions section."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '快速操作' in response.data.decode('utf-8')
        assert '添加仓库' in response.data.decode('utf-8')
        assert '生成文档' in response.data.decode('utf-8')
        assert '系统设置' in response.data.decode('utf-8')
    
    def test_dashboard_renders_quick_start(self):
        """Test that dashboard renders quick start section."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '快速开始' in response.data.decode('utf-8')
        assert '第一步：创建仓库' in response.data.decode('utf-8')
        assert '第二步：上传代码' in response.data.decode('utf-8')
        assert '第三步：生成文档' in response.data.decode('utf-8')
    
    def test_dashboard_shows_empty_state(self):
        """Test that dashboard shows empty state when no repositories."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert '暂无仓库' in response.data.decode('utf-8')
        assert '点击"添加仓库"按钮开始添加您的第一个代码仓库' in response.data.decode('utf-8')
    
    def test_dashboard_includes_javascript(self):
        """Test that dashboard includes necessary JavaScript files."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert b'dashboard.js' in response.data
    
    def test_dashboard_repository_template_included(self):
        """Test that dashboard includes repository list template."""
        response = self.client.get('/dashboard')
        
        assert response.status_code == 200
        assert b'repositoryItemTemplate' in response.data
    
    def test_dashboard_api_endpoint_accessible(self):
        """Test that dashboard API endpoint is accessible."""
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_repositories' in data
        assert 'total_documents' in data
        assert 'active_tasks' in data
        assert 'monthly_generated' in data
    
    def test_dashboard_with_repositories(self):
        """Test dashboard with existing repositories."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='test-repo-1',
            url='https://github.com/user/test-repo-1',
            status='active',
            clone_status='completed',
            repo_size=1024,
            file_count=10
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='test-repo-2',
            url='https://github.com/user/test-repo-2',
            status='error',
            clone_status='failed',
            repo_size=0,
            file_count=0
        )
        
        db.session.add_all([repo1, repo2])
        db.session.commit()
        
        # Test API response
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 2
        assert data['active_repositories'] == 1
        assert data['error_repositories'] == 1
        assert data['total_size_bytes'] == 1024
        assert data['total_files'] == 10
    
    def test_dashboard_with_documents(self):
        """Test dashboard with existing documents."""
        # Create test repository and documents
        repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/user/test-repo',
            status='active',
            clone_status='completed'
        )
        
        db.session.add(repo)
        db.session.commit()
        
        # Create test documents
        doc1 = Document(
            repository_id=repo.id,
            title='Document 1',
            content='Content 1',
            status='completed'
        )
        doc2 = Document(
            repository_id=repo.id,
            title='Document 2',
            content='Content 2',
            status='processing'
        )
        
        db.session.add_all([doc1, doc2])
        db.session.commit()
        
        # Test API response
        response = self.client.get('/api/repositories/enhanced-statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_repositories'] == 1
        assert data['total_documents'] == 2
        assert data['active_tasks'] == 1
    
    def test_dashboard_pagination_works(self):
        """Test that repository pagination works in dashboard."""
        # Create test repositories
        for i in range(15):
            repo = Repository(
                user_id=self.user.id,
                name=f'repo{i}',
                url=f'https://github.com/user/repo{i}',
                status='active',
                clone_status='completed'
            )
            db.session.add(repo)
        
        db.session.commit()
        
        # Test first page
        response = self.client.get('/api/repositories?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 10
        assert data['current_page'] == 1
        assert data['total_pages'] == 2
        
        # Test second page
        response = self.client.get('/api/repositories?page=2&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 5
        assert data['current_page'] == 2
        assert data['total_pages'] == 2
    
    def test_dashboard_search_functionality(self):
        """Test that search functionality works in dashboard."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='python-project',
            url='https://github.com/user/python-project',
            status='active',
            clone_status='completed'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='javascript-app',
            url='https://github.com/user/javascript-app',
            status='active',
            clone_status='completed'
        )
        repo3 = Repository(
            user_id=self.user.id,
            name='python-script',
            url='https://github.com/user/python-script',
            status='active',
            clone_status='completed'
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        # Test search for 'python'
        response = self.client.get('/api/repositories?search=python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 2
        repo_names = [repo['name'] for repo in data['repositories']]
        assert 'python-project' in repo_names
        assert 'python-script' in repo_names
        assert 'javascript-app' not in repo_names
    
    def test_dashboard_status_filter(self):
        """Test that status filter works in dashboard."""
        # Create test repositories
        repo1 = Repository(
            user_id=self.user.id,
            name='active-repo',
            url='https://github.com/user/active-repo',
            status='active',
            clone_status='completed'
        )
        repo2 = Repository(
            user_id=self.user.id,
            name='error-repo',
            url='https://github.com/user/error-repo',
            status='error',
            clone_status='failed'
        )
        repo3 = Repository(
            user_id=self.user.id,
            name='inactive-repo',
            url='https://github.com/user/inactive-repo',
            status='inactive',
            clone_status='completed'
        )
        
        db.session.add_all([repo1, repo2, repo3])
        db.session.commit()
        
        # Test filter for 'active' status
        response = self.client.get('/api/repositories?status=active')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['repositories']) == 1
        assert data['repositories'][0]['name'] == 'active-repo'