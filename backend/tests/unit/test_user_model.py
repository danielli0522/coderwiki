"""
用户模型单元测试
"""
import pytest
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import TestingConfig

class TestUser:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_set_password(self):
        """测试设置密码"""
        user = User()
        password = 'testpassword123'
        
        user.set_password(password)
        
        assert user.password_hash is not None
        assert check_password_hash(user.password_hash, password)
    
    def test_check_password(self):
        """测试验证密码"""
        user = User()
        password = 'testpassword123'
        user.set_password(password)
        
        assert user.check_password(password) is True
        assert user.check_password('wrongpassword') is False
    
    def test_to_dict(self):
        """测试用户转换为字典"""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            is_active=True,
            is_admin=False
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['id'] == 1
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['is_active'] is True
        assert user_dict['is_admin'] is False
        assert 'password_hash' not in user_dict  # 敏感信息不应包含
    
    def test_repr(self):
        """测试用户字符串表示"""
        user = User(username='testuser')
        
        repr_str = repr(user)
        
        assert 'User' in repr_str
        assert 'testuser' in repr_str
    
    def test_validate_username_valid(self):
        """测试用户名验证 - 有效用户名"""
        assert User.validate_username('testuser') is True
        assert User.validate_username('test_user') is True
        assert User.validate_username('test123') is True
        assert User.validate_username('TestUser') is True
    
    def test_validate_username_invalid(self):
        """测试用户名验证 - 无效用户名"""
        assert User.validate_username('') is False
        assert User.validate_username('ab') is False  # 太短
        assert User.validate_username('a' * 21) is False  # 太长
        assert User.validate_username('user@name') is False  # 特殊字符
        assert User.validate_username('user-name') is False  # 连字符
        assert User.validate_username('user name') is False  # 空格
    
    def test_validate_email_valid(self):
        """测试邮箱验证 - 有效邮箱"""
        assert User.validate_email('test@example.com') is True
        assert User.validate_email('user.name@domain.com') is True
        assert User.validate_email('user+tag@example.com') is True
        assert User.validate_email('user123@sub.domain.com') is True
    
    def test_validate_email_invalid(self):
        """测试邮箱验证 - 无效邮箱"""
        assert User.validate_email('') is False
        assert User.validate_email('invalid-email') is False
        assert User.validate_email('user@') is False
        assert User.validate_email('@domain.com') is False
        assert User.validate_email('user@domain') is False
    
    def test_validate_password_valid(self):
        """测试密码验证 - 有效密码"""
        valid_passwords = [
            'TestPassword123!',
            'MySecurePass456',
            'Complex@Pass789',
            'Str0ng!P@ssw0rd'
        ]
        
        for password in valid_passwords:
            is_valid, message = User.validate_password(password)
            assert is_valid is True, f"Password {password} should be valid"
    
    def test_validate_password_invalid(self):
        """测试密码验证 - 无效密码"""
        invalid_passwords = [
            ('', '密码不能为空'),
            ('short', '密码长度至少为8位'),
            ('a' * 129, '密码长度不能超过128位'),
            ('abcdefgh', '密码必须包含大小写字母、数字和特殊字符中的至少三种'),
            ('12345678', '密码必须包含大小写字母、数字和特殊字符中的至少三种'),
            ('!@#$%^&*', '密码必须包含大小写字母、数字和特殊字符中的至少三种'),
            ('password', '密码必须包含大小写字母、数字和特殊字符中的至少三种')
        ]
        
        for password, expected_error in invalid_passwords:
            is_valid, message = User.validate_password(password)
            assert is_valid is False, f"Password {password} should be invalid"
            assert expected_error in message
    
    def test_is_username_taken(self):
        """测试检查用户名是否被占用"""
        # 创建用户
        user = User(username='existinguser', email='existing@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 测试已存在的用户名
        assert User.is_username_taken('existinguser') is True
        
        # 测试不存在的用户名
        assert User.is_username_taken('newuser') is False
    
    def test_is_email_taken(self):
        """测试检查邮箱是否被占用"""
        # 创建用户
        user = User(username='existinguser', email='existing@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 测试已存在的邮箱
        assert User.is_email_taken('existing@example.com') is True
        
        # 测试不存在的邮箱
        assert User.is_email_taken('new@example.com') is False
    
    def test_user_creation_database(self):
        """测试用户创建并保存到数据库"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        
        db.session.add(user)
        db.session.commit()
        
        # 从数据库查询用户
        saved_user = User.query.filter_by(username='testuser').first()
        
        assert saved_user is not None
        assert saved_user.username == 'testuser'
        assert saved_user.email == 'test@example.com'
        assert saved_user.is_active is True
        assert saved_user.is_admin is False
        assert saved_user.check_password('testpassword123') is True
    
    def test_password_hash_not_in_to_dict(self):
        """测试密码哈希不包含在to_dict中"""
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password_here'
        )
        
        user_dict = user.to_dict()
        
        assert 'password_hash' not in user_dict
        assert 'password' not in user_dict