"""
Authentication service for user management.
"""

import logging
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User

# 设置日志
logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for handling user authentication operations."""

    def __init__(self):
        """Initialize the authentication service."""
        pass

    def register_user(self, username, email, password):
        """Register a new user.

        Args:
            username (str): Username for the new user
            email (str): Email address for the new user
            password (str): Password for the new user

        Returns:
            User: The created user object

        Raises:
            ValueError: If validation fails or username/email already exists
        """
        logger.info(f"开始注册用户: {username}")

        # Validate username format
        if not User.validate_username(username):
            logger.warning(f"用户名格式不正确: {username}")
            raise ValueError("用户名格式不正确，只能包含字母、数字、下划线，长度3-20位")

        # Validate email format
        if not User.validate_email(email):
            logger.warning(f"邮箱格式不正确: {email}")
            raise ValueError("邮箱格式不正确")

        # Validate password strength
        is_valid, error_msg = User.validate_password(password)
        if not is_valid:
            logger.warning(f"密码强度不够: {error_msg}")
            raise ValueError(error_msg)

        # Check if username already exists
        if User.is_username_taken(username):
            logger.warning(f"用户名已存在: {username}")
            raise ValueError("用户名已存在")

        # Check if email already exists
        if User.is_email_taken(email):
            logger.warning(f"邮箱已存在: {email}")
            raise ValueError("邮箱已存在")

        try:
            # Create new user
            logger.info("创建新用户对象")
            user = User(username=username, email=email)
            user.set_password(password)

            # Save to database
            logger.info("保存用户到数据库")
            db.session.add(user)
            db.session.commit()
            logger.info(f"用户注册成功: {username}")

            return user

        except Exception as e:
            logger.error(f"注册失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"注册失败: {str(e)}")

    def login_user(self, username, password, remember=False):
        """Login a user.

        Args:
            username (str): Username or email
            password (str): User password
            remember (bool): Whether to remember the user

        Returns:
            User: The logged in user object

        Raises:
            ValueError: If username or password is incorrect
            ValueError: If user account is inactive
        """
        logger.info(f"开始登录用户: {username}")

        # Try to find user by username or email
        logger.debug("查询用户")
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            logger.warning(f"用户不存在: {username}")
            raise ValueError("用户名或密码错误")

        logger.debug(f"找到用户: {user.username}")

        if not user.check_password(password):
            logger.warning(f"密码错误: {username}")
            raise ValueError("用户名或密码错误")

        if not user.is_active:
            logger.warning(f"用户账户被禁用: {username}")
            raise ValueError("用户账户已被禁用")

        # Update last login time
        logger.debug("更新最后登录时间")
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Note: login_user() should be called in the API layer, not here
        # to avoid request context issues

        logger.info(f"用户登录成功: {user.username}")
        return user

    def logout_user(self):
        """Logout the current user."""
        logger.info("用户退出登录")
        logout_user()

    def get_current_user(self):
        """Get the current logged in user.

        Returns:
            User: Current user object or None if not logged in
        """
        return current_user

    def update_user_profile(self, user_id, **kwargs):
        """Update user profile information.

        Args:
            user_id (int): User ID
            **kwargs: Fields to update (email, etc.)

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found or email already exists
        """
        logger.info(f"更新用户资料: {user_id}")

        user = User.query.get(user_id)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            raise ValueError("用户不存在")

        # Check email uniqueness if updating email
        if 'email' in kwargs and kwargs['email'] != user.email:
            if User.query.filter_by(email=kwargs['email']).first():
                logger.warning(f"邮箱已存在: {kwargs['email']}")
                raise ValueError("邮箱已存在")
            user.email = kwargs['email']

        # Update other fields
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"用户资料更新成功: {user.username}")
        return user

    def change_password(self, user_id, old_password, new_password):
        """Change user password.

        Args:
            user_id (int): User ID
            old_password (str): Current password
            new_password (str): New password

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found, old password is incorrect
        """
        logger.info(f"修改用户密码: {user_id}")

        user = User.query.get(user_id)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            raise ValueError("用户不存在")

        if not user.check_password(old_password):
            logger.warning(f"当前密码错误: {user_id}")
            raise ValueError("当前密码错误")

        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"密码修改成功: {user.username}")
        return user
