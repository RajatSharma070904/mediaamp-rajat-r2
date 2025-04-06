# from celery import Celery
# from app.extensions import db, cache
# from app.blueprints.tasks.models import TaskManager, TaskLogger
# from datetime import datetime, date
# from sqlalchemy.exc import SQLAlchemyError
# import time

# celery = Celery(__name__)

# @celery.task(bind=True, max_retries=3)
# def daily_task_loader(self):
#     """Celery task to transfer active tasks from TaskManager to TaskLogger daily."""
#     try:
#         today = date.today()
        
#         # Get all active tasks
#         active_tasks = TaskManager.query.filter_by(is_active=True).all()
        
#         for task in active_tasks:
#             # Check if log already exists for today
#             existing_log = TaskLogger.query.filter_by(
#                 task_id=task.id,
#                 log_date=today
#             ).first()
            
#             if not existing_log:
#                 # Create new log entry
#                 log_entry = TaskLogger(
#                     task_id=task.id,
#                     status=task.status,
#                     log_date=today,
#                     notes=f"Automated daily log for {today}"
#                 )
#                 db.session.add(log_entry)
        
#         db.session.commit()
#         cache.clear()  # Clear cache to reflect new logs
        
#         return {"status": "success", "tasks_processed": len(active_tasks)}
    
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
#         return {"status": "error", "message": str(e)}


# new code
# app/tasks/daily_task_loader.py
from app.tasks.celery import celery
from app.extensions import db, cache
from app.blueprints.tasks.models import TaskManager, TaskLogger
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

@celery.task(bind=True, max_retries=3)
def daily_task_loader(self):
    try:
        today = date.today()
        active_tasks = TaskManager.query.filter_by(is_active=True).all()

        for task in active_tasks:
            existing_log = TaskLogger.query.filter_by(task_id=task.id, log_date=today).first()

            if not existing_log:
                log_entry = TaskLogger(
                    task_id=task.id,
                    status=task.status,
                    log_date=today,
                    notes=f"Automated daily log for {today}"
                )
                db.session.add(log_entry)

        db.session.commit()
        cache.clear()

        return {"status": "success", "tasks_processed": len(active_tasks)}

    except SQLAlchemyError as e:
        db.session.rollback()
        self.retry(exc=e, countdown=60 * 5)
        return {"status": "error", "message": str(e)}
