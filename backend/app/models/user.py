"""
User model definition.
"""

import re
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model for authentication and user management."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    repositories = db.relationship('Repository', backref='user', lazy='dynamic',
                                  cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic',
                           cascade='all, delete-orphan')

    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        """String representation of user."""
        return f'<User {self.username}>'

    @staticmethod
    def validate_username(username):
        """Validate username format.

        Args:
            username (str): Username to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not username or len(username) < 3 or len(username) > 20:
            return False

        # 只允许字母、数字、下划线
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

    @staticmethod
    def validate_email(email):
        """Validate email format.

        Args:
            email (str): Email to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not email:
            return False

        # 基本邮箱格式验证
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password):
        """Validate password strength.

        Args:
            password (str): Password to validate

        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if not password:
            return False, "密码不能为空"

        if len(password) < 6:
            return False, "密码长度至少为6位"

        if len(password) > 128:
            return False, "密码长度不能超过128位"

        # 更宽松的密码强度要求
        has_letter = re.search(r'[a-zA-Z]', password) is not None
        has_digit = re.search(r'\d', password) is not None

        if not has_letter:
            return False, "密码必须包含至少一个字母"

        if not has_digit:
            return False, "密码必须包含至少一个数字"

        return True, ""

    @staticmethod
    def is_username_taken(username):
        """Check if username is already taken.

        Args:
            username (str): Username to check

        Returns:
            bool: True if taken, False otherwise
        """
        return User.query.filter_by(username=username).first() is not None

    @staticmethod
    def is_email_taken(email):
        """Check if email is already taken.

        Args:
            email (str): Email to check

        Returns:
            bool: True if taken, False otherwise
        """
        return User.query.filter_by(email=email).first() is not None
