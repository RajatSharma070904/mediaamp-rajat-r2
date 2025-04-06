# # app/tasks/celery.py
# from celery import Celery

# celery = Celery('myapp')

# def init_celery(app):
#     celery.conf.update(app.config)
#     TaskBase = celery.Task

#     class ContextTask(TaskBase):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)

#     celery.Task = ContextTask

from celery import Celery

celery = Celery('myapp', broker='redis://redis:6379/0')  # 👈 use Docker service name

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
