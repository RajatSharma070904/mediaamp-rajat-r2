# Flask TodoList API with Celery, PostgreSQL & Redis

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.x-lightgrey.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-13+-blue.svg)
![Redis](https://img.shields.io/badge/redis-7.x-red.svg)

A high-performance task management system with RBAC, daily task logging, and Redis caching.

## 📌 Features

- **Modular Architecture**: Blueprints + Service/Repository pattern
- **JWT Authentication**: Secure endpoints with role-based access
- **Task Management**: CRUD operations with soft deletion
- **Daily Task Logger**: Celery-powered background processing
- **Redis Caching**: Optimized performance for frequent queries
- **CSV Import**: Bulk task creation from uploaded files
- **Alembic Migrations**: Database version control
- **Dockerized**: Ready for deployment

## 🏗️ Architecture
