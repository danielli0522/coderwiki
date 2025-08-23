"""
认证服务单元测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService
from app.models.user import User

class TestAuthService:
    
    def setup_method(self):
        """测试前设置"""
        self.auth_service = AuthService()
    
    def test_create_user_success(self):
        """测试创建用户成功"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        with patch.object(User, 'create_user') as mock_create:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'testuser'
            mock_user.email = 'test@example.com'
            mock_create.return_value = mock_user
            
            result = self.auth_service.create_user(user_data)
            
            assert result is not None
            assert result.username == 'testuser'
            assert result.email == 'test@example.com'
            mock_create.assert_called_once_with(user_data)
    
    def test_create_user_duplicate_username(self):
        """测试创建用户时用户名重复"""
        user_data = {
            'username': 'existinguser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        with patch.object(User, 'create_user') as mock_create:
            mock_create.side_effect = ValueError("用户名已存在")
            
            with pytest.raises(ValueError, match="用户名已存在"):
                self.auth_service.create_user(user_data)
    
    def test_authenticate_user_success(self):
        """测试用户认证成功"""
        username = 'testuser'
        password = 'testpassword123'
        
        with patch.object(User, 'authenticate') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'testuser'
            mock_auth.return_value = mock_user
            
            result = self.auth_service.authenticate_user(username, password)
            
            assert result is not None
            assert result.username == 'testuser'
            mock_auth.assert_called_once_with(username, password)
    
    def test_authenticate_user_invalid_credentials(self):
        """测试用户认证失败"""
        username = 'testuser'
        password = 'wrongpassword'
        
        with patch.object(User, 'authenticate') as mock_auth:
            mock_auth.return_value = None
            
            result = self.auth_service.authenticate_user(username, password)
            
            assert result is None
            mock_auth.assert_called_once_with(username, password)
    
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        user_id = 1
        
        with patch.object(User, 'get_by_id') as mock_get:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'testuser'
            mock_get.return_value = mock_user
            
            result = self.auth_service.get_user_by_id(user_id)
            
            assert result is not None
            assert result.id == user_id
            mock_get.assert_called_once_with(user_id)
    
    def test_get_user_by_id_not_found(self):
        """测试获取不存在的用户"""
        user_id = 999
        
        with patch.object(User, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            result = self.auth_service.get_user_by_id(user_id)
            
            assert result is None
            mock_get.assert_called_once_with(user_id)
    
    def test_update_user_profile(self):
        """测试更新用户资料"""
        user_id = 1
        update_data = {
            'full_name': 'Test User',
            'bio': 'Test bio'
        }
        
        with patch.object(User, 'update_user') as mock_update:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.full_name = 'Test User'
            mock_user.bio = 'Test bio'
            mock_update.return_value = mock_user
            
            result = self.auth_service.update_user_profile(user_id, update_data)
            
            assert result is not None
            assert result.full_name == 'Test User'
            assert result.bio == 'Test bio'
            mock_update.assert_called_once_with(user_id, update_data)
    
    def test_change_password(self):
        """测试修改密码"""
        user_id = 1
        old_password = 'oldpassword'
        new_password = 'newpassword123'
        
        with patch.object(User, 'change_password') as mock_change:
            mock_change.return_value = True
            
            result = self.auth_service.change_password(user_id, old_password, new_password)
            
            assert result is True
            mock_change.assert_called_once_with(user_id, old_password, new_password)
    
    def test_change_password_wrong_old_password(self):
        """测试修改密码时旧密码错误"""
        user_id = 1
        old_password = 'wrongpassword'
        new_password = 'newpassword123'
        
        with patch.object(User, 'change_password') as mock_change:
            mock_change.side_effect = ValueError("旧密码错误")
            
            with pytest.raises(ValueError, match="旧密码错误"):
                self.auth_service.change_password(user_id, old_password, new_password)
    
    def test_delete_user(self):
        """测试删除用户"""
        user_id = 1
        
        with patch.object(User, 'delete_user') as mock_delete:
            mock_delete.return_value = True
            
            result = self.auth_service.delete_user(user_id)
            
            assert result is True
            mock_delete.assert_called_once_with(user_id)
    
    def test_validate_user_data_valid(self):
        """测试验证用户数据 - 有效数据"""
        user_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'validpassword123'
        }
        
        # 应该不抛出异常
        self.auth_service.validate_user_data(user_data)
    
    def test_validate_user_data_invalid_email(self):
        """测试验证用户数据 - 无效邮箱"""
        user_data = {
            'username': 'validuser',
            'email': 'invalid-email',
            'password': 'validpassword123'
        }
        
        with pytest.raises(ValueError, match="邮箱格式不正确"):
            self.auth_service.validate_user_data(user_data)
    
    def test_validate_user_data_short_password(self):
        """测试验证用户数据 - 密码太短"""
        user_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'short'
        }
        
        with pytest.raises(ValueError, match="密码长度至少为8位"):
            self.auth_service.validate_user_data(user_data)
    
    def test_validate_user_data_missing_fields(self):
        """测试验证用户数据 - 缺少字段"""
        user_data = {
            'username': 'validuser'
            # 缺少email和password
        }
        
        with pytest.raises(ValueError, match="缺少必需字段"):
            self.auth_service.validate_user_data(user_data)
    
    def test_login_user_success(self):
        """测试用户登录成功"""
        with patch('app.services.auth_service.User') as mock_user_class, \
             patch('app.services.auth_service.login_user') as mock_login_user, \
             patch('app.services.auth_service.db') as mock_db:
            
            # Mock user
            mock_user = Mock()
            mock_user.check_password.return_value = True
            mock_user.is_active = True
            mock_user.last_login = None
            mock_user_class.query.filter.return_value.first.return_value = mock_user
            
            result = self.auth_service.login_user('testuser', 'TestPassword123!')
            
            assert result == mock_user
            mock_user.check_password.assert_called_once_with('TestPassword123!')
            mock_login_user.assert_called_once_with(mock_user, remember=False)
            mock_db.session.commit.assert_called_once()
    
    def test_login_user_with_remember(self):
        """测试用户登录并记住我"""
        with patch('app.services.auth_service.User') as mock_user_class, \
             patch('app.services.auth_service.login_user') as mock_login_user, \
             patch('app.services.auth_service.db') as mock_db:
            
            # Mock user
            mock_user = Mock()
            mock_user.check_password.return_value = True
            mock_user.is_active = True
            mock_user_class.query.filter.return_value.first.return_value = mock_user
            
            result = self.auth_service.login_user('testuser', 'TestPassword123!', remember=True)
            
            assert result == mock_user
            mock_login_user.assert_called_once_with(mock_user, remember=True)
    
    def test_login_user_not_found(self):
        """测试用户不存在"""
        with patch('app.services.auth_service.User') as mock_user_class:
            mock_user_class.query.filter.return_value.first.return_value = None
            
            with pytest.raises(ValueError, match="用户名或密码错误"):
                self.auth_service.login_user('nonexistent', 'password')
    
    def test_login_user_wrong_password(self):
        """测试密码错误"""
        with patch('app.services.auth_service.User') as mock_user_class:
            mock_user = Mock()
            mock_user.check_password.return_value = False
            mock_user_class.query.filter.return_value.first.return_value = mock_user
            
            with pytest.raises(ValueError, match="用户名或密码错误"):
                self.auth_service.login_user('testuser', 'wrongpassword')
    
    def test_login_user_inactive(self):
        """测试用户未激活"""
        with patch('app.services.auth_service.User') as mock_user_class:
            mock_user = Mock()
            mock_user.check_password.return_value = True
            mock_user.is_active = False
            mock_user_class.query.filter.return_value.first.return_value = mock_user
            
            with pytest.raises(ValueError, match="用户账户已被禁用"):
                self.auth_service.login_user('testuser', 'password')
    
    def test_login_user_email_login(self):
        """测试使用邮箱登录"""
        with patch('app.services.auth_service.User') as mock_user_class, \
             patch('app.services.auth_service.login_user') as mock_login_user, \
             patch('app.services.auth_service.db') as mock_db:
            
            # Mock user
            mock_user = Mock()
            mock_user.check_password.return_value = True
            mock_user.is_active = True
            mock_user_class.query.filter.return_value.first.return_value = mock_user
            
            result = self.auth_service.login_user('test@example.com', 'TestPassword123!')
            
            assert result == mock_user
            mock_user.check_password.assert_called_once_with('TestPassword123!')
    
    def test_logout_user(self):
        """测试用户登出"""
        with patch('app.services.auth_service.logout_user') as mock_logout_user:
            self.auth_service.logout_user()
            mock_logout_user.assert_called_once()
    
    def test_get_current_user(self):
        """测试获取当前用户"""
        with patch('app.services.auth_service.current_user') as mock_current_user:
            mock_user = Mock()
            mock_current_user.__bool__ = lambda: True
            mock_current_user.__eq__ = lambda other: other is mock_user
            
            result = self.auth_service.get_current_user()
            assert result == mock_current_user
    
    def test_get_current_user_none(self):
        """测试获取当前用户 - 未登录"""
        with patch('app.services.auth_service.current_user') as mock_current_user:
            mock_current_user.__bool__ = lambda: False
            mock_current_user.__eq__ = lambda other: other is None
            
            result = self.auth_service.get_current_user()
            assert result == mock_current_user