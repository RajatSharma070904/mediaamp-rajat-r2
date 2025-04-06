from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.blueprints.tasks.models import TaskManager, TaskLogger, TaskStatus, TaskAuditLog
from app.extensions import db, cache, limiter
from app.utils.decorators import role_required
from app.utils.validators import validate_task_data
from datetime import datetime
import csv
from io import StringIO
from sqlalchemy import or_

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/upload-csv', methods=['POST'])
@jwt_required()
@role_required('manager')
@limiter.limit("10 per minute")
def upload_csv():
    """Upload tasks via CSV file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV"}), 400
    
    user_id = get_jwt_identity()
    
    try:
        
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        tasks = []
        for row in csv_reader:
            
            if not all(k in row for k in ['title', 'description', 'status']):
                continue
            
            
            task = TaskManager(
                title=row['title'],
                description=row['description'],
                status=TaskStatus(row['status']),
                created_by=user_id,
                updated_by=user_id
            )
            
            if 'due_date' in row and row['due_date']:
                task.due_date = datetime.strptime(row['due_date'], '%Y-%m-%d')
            
            if 'priority' in row and row['priority']:
                task.priority = int(row['priority'])
            
            db.session.add(task)
            tasks.append(task)
        
        db.session.commit()
        
       
        for task in tasks:
            audit_log = TaskAuditLog(
                task_id=task.id,
                user_id=user_id,
                action='create',
                new_value=f"Task created via CSV upload: {task.title}"
            )
            db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({"message": f"{len(tasks)} tasks created successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_tasks():
    """Get paginated list of tasks with optional date filter."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_filter = request.args.get('date', None)
    
    query = TaskLogger.query
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(log_date=filter_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
  
    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)
    
    tasks_data = []
    for task in paginated_tasks.items:
        tasks_data.append({
            "id": task.id,
            "task_id": task.task_id,
            "status": task.status.value,
            "log_date": task.log_date.isoformat(),
            "title": task.task.title,
            "description": task.task.description
        })
    
    return jsonify({
        "tasks": tasks_data,
        "total": paginated_tasks.total,
        "pages": paginated_tasks.pages,
        "current_page": page
    }), 200

@tasks_bp.route('/task/<int:task_logger_id>', methods=['GET'])
@jwt_required()
def get_task(task_logger_id):
    """Get details of a specific task."""
    task_log = TaskLogger.query.get_or_404(task_logger_id)
    
    return jsonify({
        "id": task_log.id,
        "task_id": task_log.task_id,
        "status": task_log.status.value,
        "log_date": task_log.log_date.isoformat(),
        "notes": task_log.notes,
        "title": task_log.task.title,
        "description": task_log.task.description,
        "priority": task_log.task.priority,
        "due_date": task_log.task.due_date.isoformat() if task_log.task.due_date else None,
        "created_at": task_log.created_at.isoformat()
    }), 200

@tasks_bp.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task."""
    data = request.get_json()
    user_id = get_jwt_identity()
    

    errors = validate_task_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    try:
      
        new_task = TaskManager(
            title=data['title'],
            description=data.get('description', ''),
            status=TaskStatus(data.get('status', 'pending')),
            priority=data.get('priority', 1),
            created_by=user_id,
            updated_by=user_id
        )
        
        if 'due_date' in data:
            new_task.due_date = datetime.fromisoformat(data['due_date'])
        
        db.session.add(new_task)
        db.session.commit()
        
        
        log_entry = TaskLogger(
            task_id=new_task.id,
            status=new_task.status,
            log_date=datetime.utcnow().date(),
            notes="Initial task creation"
        )
        db.session.add(log_entry)
        
       
        audit_log = TaskAuditLog(
            task_id=new_task.id,
            user_id=user_id,
            action='create',
            new_value=f"Task created: {new_task.title}"
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            "message": "Task created successfully",
            "task_id": new_task.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update an existing task."""
    data = request.get_json()
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    task = TaskManager.query.get_or_404(task_id)
    
  
    if user_role != 'admin' and task.created_by != user_id:
        return jsonify({"error": "Not authorized to update this task"}), 403
    
    
    errors = validate_task_data(data, update=True)
    if errors:
        return jsonify({"errors": errors}), 400
    
    try:
        
        changes = []
        
        if 'title' in data and task.title != data['title']:
            changes.append(f"title: {task.title} → {data['title']}")
            task.title = data['title']
        
        if 'description' in data and task.description != data['description']:
            changes.append(f"description updated")
            task.description = data['description']
        
        if 'status' in data and task.status != TaskStatus(data['status']):
            changes.append(f"status: {task.status.value} → {data['status']}")
            task.status = TaskStatus(data['status'])
        
        if 'priority' in data and task.priority != int(data['priority']):
            changes.append(f"priority: {task.priority} → {data['priority']}")
            task.priority = int(data['priority'])
        
        if 'due_date' in data:
            new_due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
            if task.due_date != new_due_date:
                changes.append(f"due_date: {task.due_date} → {new_due_date}")
                task.due_date = new_due_date
        
        task.updated_by = user_id
        
        if changes:
            
            audit_log = TaskAuditLog(
                task_id=task.id,
                user_id=user_id,
                action='update',
                old_value="\n".join([f"Before: {task.title}"]),
                new_value="Changes:\n" + "\n".join(changes)
            )
            db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({"message": "Task updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@tasks_bp.route('/task/<int:task_id>', methods=['DELETE'])
@jwt_required()
@role_required('manager')
def delete_task(task_id):
    """Soft delete a task."""
    user_id = get_jwt_identity()
    
    task = TaskManager.query.get_or_404(task_id)
    
    if not task.is_active:
        return jsonify({"error": "Task already deleted"}), 400
    
    try:
        
        task.is_active = False
        task.updated_by = user_id
        
        
        audit_log = TaskAuditLog(
            task_id=task.id,
            user_id=user_id,
            action='delete',
            new_value=f"Task marked as inactive: {task.title}"
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({"message": "Task deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500