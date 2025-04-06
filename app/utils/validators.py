import re
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class TaskCreateSchema(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[int] = 1
    due_date: Optional[str] = None
    
    @validator('title')
    def title_length(cls, v):
        if len(v) < 3 or len(v) > 120:
            raise ValueError('Title must be between 3 and 120 characters')
        return v
    
    @validator('priority')
    def priority_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Priority must be between 1 and 5')
        return v
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid date format. Use ISO format (YYYY-MM-DD)')
        return v

def validate_task_data(data, update=False):
    try:
        if update:
            TaskCreateSchema(**data)
        else:
            if 'title' not in data:
                return ["Title is required"]
            TaskCreateSchema(**data)
        return []
    except ValueError as e:
        return [str(err) for err in e.errors()]

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password meets minimum requirements."""
    return len(password) >= 8