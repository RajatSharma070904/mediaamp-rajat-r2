FROM python:3.9-slim
# Flask Task Manager API

A high-performance task management system with Flask, Celery, PostgreSQL, and Redis.

## Features

- User authentication with JWT
- Role-based access control (Admin, Manager, User)
- Task management with status tracking
- Daily task logging with Celery
- Audit logging for all changes
- CSV import/export
- Redis caching for performance
- Rate limiting for API protection

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flask-task-manager.git
   cd flask-task-manager