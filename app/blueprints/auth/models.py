from app.extensions import db
from datetime import datetime
from enum import Enum

class RoleEnum(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tasks_created = db.relationship('TaskManager', backref='creator', lazy='dynamic', foreign_keys='TaskManager.created_by')
    tasks_updated = db.relationship('TaskManager', backref='updater', lazy='dynamic', foreign_keys='TaskManager.updated_by')
    
    def __repr__(self):
        return f'<User {self.username}>'