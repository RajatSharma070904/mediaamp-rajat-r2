from app.extensions import db
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class TaskManager(db.Model):
    __tablename__ = 'task_manager'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = db.Column(db.Integer, default=1)
    due_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    logs = db.relationship('TaskLogger', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_task_manager_status', 'status'),
        db.Index('idx_task_manager_due_date', 'due_date'),
        db.Index('idx_task_manager_priority', 'priority'),
    )
    
    def __repr__(self):
        return f'<TaskManager {self.title}>'

class TaskLogger(db.Model):
    __tablename__ = 'task_logger'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_manager.id'), nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False)
    log_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_task_logger_task_id', 'task_id'),
        db.Index('idx_task_logger_log_date', 'log_date'),
        db.UniqueConstraint('task_id', 'log_date', name='uq_task_logger_task_date'),
    )
    
    def __repr__(self):
        return f'<TaskLogger task_id={self.task_id} date={self.log_date}>'

class TaskAuditLog(db.Model):
    __tablename__ = 'task_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task_manager.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref='audit_logs')
    
    __table_args__ = (
        db.Index('idx_task_audit_task_id', 'task_id'),
        db.Index('idx_task_audit_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<TaskAuditLog task_id={self.task_id} action={self.action}>'