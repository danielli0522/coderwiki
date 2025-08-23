"""
登录API集成测试
"""

import pytest
import json
from app import create_app, db
from app.models.user import User
from app.services.auth_service import AuthService

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('TestPassword123!')
        db.session.add(user)
        db.session.commit()
        return user

class TestLoginAPI:
    
    def test_login_success(self, client, test_user):
        """测试登录成功"""
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert 'password_hash' not in data['user']
    
    def test_login_with_email(self, client, test_user):
        """测试使用邮箱登录"""
        login_data = {
            'username': 'test@example.com',
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_with_remember(self, client, test_user):
        """测试登录并记住我"""
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!',
            'remember': True
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_login_wrong_password(self, client, test_user):
        """测试密码错误"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_login_user_not_found(self, client):
        """测试用户不存在"""
        login_data = {
            'username': 'nonexistent',
            'password': 'password'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_login_missing_username(self, client):
        """测试缺少用户名"""
        login_data = {
            'password': 'password'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_missing_password(self, client):
        """测试缺少密码"""
        login_data = {
            'username': 'testuser'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_empty_data(self, client):
        """测试空数据"""
        response = client.post('/api/auth/login', 
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_invalid_json(self, client):
        """测试无效JSON"""
        response = client.post('/api/auth/login', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_logout_success(self, client, test_user):
        """测试登出成功"""
        # 先登录
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        login_response = client.post('/api/auth/login', 
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        assert login_response.status_code == 200
        
        # 再登出
        logout_response = client.post('/api/auth/logout')
        assert logout_response.status_code == 200
        data = json.loads(logout_response.data)
        assert data['success'] is True
    
    def test_logout_without_login(self, client):
        """测试未登录时登出"""
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_status_not_logged_in(self, client):
        """测试未登录时的状态"""
        response = client.get('/api/auth/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['logged_in'] is False
        assert data['user'] is None
    
    def test_status_logged_in(self, client, test_user):
        """测试登录后的状态"""
        # 先登录
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        client.post('/api/auth/login', 
                   data=json.dumps(login_data),
                   content_type='application/json')
        
        # 检查状态
        response = client.get('/api/auth/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['logged_in'] is True
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_inactive_user(self, app, client):
        """测试登录未激活用户"""
        with app.app_context():
            # 创建未激活用户
            user = User(username='inactive', email='inactive@example.com', is_active=False)
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
        
        login_data = {
            'username': 'inactive',
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert '禁用' in data['error']
    
    def test_multiple_login_attempts(self, client, test_user):
        """测试多次登录尝试"""
        # 第一次登录成功
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        response1 = client.post('/api/auth/login', 
                              data=json.dumps(login_data),
                              content_type='application/json')
        assert response1.status_code == 200
        
        # 第二次登录也应该成功
        response2 = client.post('/api/auth/login', 
                              data=json.dumps(login_data),
                              content_type='application/json')
        assert response2.status_code == 200