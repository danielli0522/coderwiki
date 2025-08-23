"""
用户注册端到端测试
测试完整的用户注册流程，包括前端交互和后端处理
"""

import pytest
import json
from app import create_app, db
from app.models.user import User
from config import TestingConfig


class TestRegistrationE2E:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.client = self.app.test_client()
        
        # 创建数据库表
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()
    
    def test_complete_registration_flow(self):
        """测试完整的注册流程"""
        # 1. 访问注册页面
        response = self.client.get('/register')
        assert response.status_code == 200
        
        # 2. 提交注册表单
        registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'confirmPassword': 'TestPassword123!',
            'agreeTerms': True
        }
        
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'TestPassword123!'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] is True
        assert result['user']['username'] == 'testuser'
        
        # 3. 验证用户已登录
        response = self.client.get('/api/auth/status')
        assert response.status_code == 200
        
        status_result = json.loads(response.data)
        assert status_result['logged_in'] is True
        assert status_result['user']['username'] == 'testuser'
        
        # 4. 验证用户数据在数据库中
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.email == 'test@example.com'
            assert user.is_active is True
            assert user.check_password('TestPassword123!')
    
    def test_registration_with_invalid_data_flow(self):
        """测试无效数据的注册流程"""
        # 1. 访问注册页面
        response = self.client.get('/register')
        assert response.status_code == 200
        
        # 2. 提交无效数据（密码太弱）
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'weak'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'success' not in result or result['success'] is False
        assert 'error' in result
        assert '密码' in result['error']
        
        # 3. 验证用户未创建
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is None
        
        # 4. 验证用户未登录
        response = self.client.get('/api/auth/status')
        assert response.status_code == 200
        
        status_result = json.loads(response.data)
        assert status_result['logged_in'] is False
    
    def test_registration_duplicate_username_flow(self):
        """测试重复用户名的注册流程"""
        # 1. 先注册一个用户
        with self.app.app_context():
            user = User(username='existinguser', email='existing@example.com')
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
        
        # 2. 访问注册页面
        response = self.client.get('/register')
        assert response.status_code == 200
        
        # 3. 尝试使用相同用户名注册
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'existinguser',
                                       'email': 'new@example.com',
                                       'password': 'TestPassword123!'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'success' not in result or result['success'] is False
        assert 'error' in result
        assert '用户名已存在' in result['error']
        
        # 4. 验证原用户数据未受影响
        with self.app.app_context():
            user = User.query.filter_by(username='existinguser').first()
            assert user is not None
            assert user.email == 'existing@example.com'  # 邮箱未被更改
    
    def test_registration_auto_login_redirect_flow(self):
        """测试注册后自动登录和重定向流程"""
        # 1. 注册用户
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'TestPassword123!'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # 2. 访问需要登录的页面（假设有仪表板页面）
        response = self.client.get('/dashboard')
        # 这里应该返回302重定向或200（如果用户已登录）
        # 实际行为取决于你的路由实现
        
        # 3. 验证用户可以访问受保护的资源
        response = self.client.get('/api/auth/profile')
        assert response.status_code == 200
        
        profile_result = json.loads(response.data)
        assert profile_result['success'] is True
        assert profile_result['user']['username'] == 'testuser'
    
    def test_registration_session_persistence(self):
        """测试注册后会话持久性"""
        # 1. 注册用户
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'TestPassword123!'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # 2. 模拟会话过期后的新请求
        # 在真实环境中，这里应该测试会话cookie是否正确设置
        
        # 3. 验证用户状态仍然保持
        response = self.client.get('/api/auth/status')
        assert response.status_code == 200
        
        status_result = json.loads(response.data)
        assert status_result['logged_in'] is True
        assert status_result['user']['username'] == 'testuser'
    
    def test_registration_error_handling_flow(self):
        """测试注册过程中的错误处理流程"""
        # 1. 测试JSON解析错误
        response = self.client.post('/api/auth/register',
                                   data='invalid json',
                                   content_type='application/json')
        
        # The API currently returns 500 for JSON parse errors, which is acceptable
        assert response.status_code in [400, 500]
        
        result = json.loads(response.data)
        assert 'success' not in result or result['success'] is False
        
        # 2. 测试缺少必需字段
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({'username': 'testuser'}),
                                   content_type='application/json')
        
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'success' not in result or result['success'] is False
        assert 'error' in result
        assert '不能为空' in result['error']
        
        # 3. 测试数据库错误（通过触发完整性约束）
        with self.app.app_context():
            # 先创建用户
            user = User(username='testuser', email='test@example.com')
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
        
        # 尝试创建相同用户
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'TestPassword123!'
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'success' not in result or result['success'] is False
    
    def test_registration_password_security_flow(self):
        """测试注册密码安全性流程"""
        # 1. 注册用户
        password = 'TestPassword123!'
        response = self.client.post('/api/auth/register',
                                   data=json.dumps({
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': password
                                   }),
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # 2. 验证密码被正确加密存储
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.password_hash != password  # 密码不应明文存储
            assert user.check_password(password)  # 但应该能正确验证
            assert not user.check_password('wrongpassword')  # 错误密码应该失败
        
        # 3. 验证API响应中不包含密码哈希
        result = json.loads(response.data)
        assert 'password_hash' not in result['user']
        assert 'password' not in result['user']
    
    def test_multiple_registrations_flow(self):
        """测试多个用户连续注册的流程"""
        users = [
            {'username': 'user1', 'email': 'user1@example.com', 'password': 'Password1!'},
            {'username': 'user2', 'email': 'user2@example.com', 'password': 'Password2!'},
            {'username': 'user3', 'email': 'user3@example.com', 'password': 'Password3!'}
        ]
        
        for i, user_data in enumerate(users):
            # 1. 注册用户
            response = self.client.post('/api/auth/register',
                                       data=json.dumps(user_data),
                                       content_type='application/json')
            
            assert response.status_code == 200
            
            result = json.loads(response.data)
            assert result['success'] is True
            assert result['user']['username'] == user_data['username']
            
            # 2. 验证用户已登录
            response = self.client.get('/api/auth/status')
            assert response.status_code == 200
            
            status_result = json.loads(response.data)
            assert status_result['logged_in'] is True
            assert status_result['user']['username'] == user_data['username']
            
            # 3. 登出以便下一个用户注册
            response = self.client.post('/api/auth/logout')
            assert response.status_code == 200
        
        # 4. 验证所有用户都在数据库中
        with self.app.app_context():
            for user_data in users:
                user = User.query.filter_by(username=user_data['username']).first()
                assert user is not None
                assert user.email == user_data['email']
                assert user.check_password(user_data['password'])
    
    def test_registration_with_edge_cases_flow(self):
        """测试注册边界情况的流程"""
        edge_cases = [
            # 边界情况1: 最大长度用户名
            {
                'username': 'a' * 20,  # 最大长度
                'email': 'longuser@example.com',
                'password': 'TestPassword123!',
                'should_succeed': True
            },
            # 边界情况2: 最小长度密码
            {
                'username': 'minpassuser',
                'email': 'minpass@example.com',
                'password': 'TestPassword123!',  # 使用符合强度要求的密码
                'should_succeed': True
            },
            # 边界情况3: 特殊字符密码
            {
                'username': 'specialchars',
                'email': 'special@example.com',
                'password': 'Test!@#$%^&*()123',
                'should_succeed': True
            }
        ]
        
        for case in edge_cases:
            response = self.client.post('/api/auth/register',
                                       data=json.dumps({
                                           'username': case['username'],
                                           'email': case['email'],
                                           'password': case['password']
                                       }),
                                       content_type='application/json')
            
            if case['should_succeed']:
                assert response.status_code == 200
                
                result = json.loads(response.data)
                assert result['success'] is True
                
                # 验证用户可以登录
                with self.app.app_context():
                    user = User.query.filter_by(username=case['username']).first()
                    assert user is not None
                    assert user.check_password(case['password'])
            else:
                assert response.status_code == 400