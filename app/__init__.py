from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt, cache, limiter
from .blueprints.auth.routes import auth_bp
from .blueprints.tasks.routes import tasks_bp
from .config import Config
from .tasks.celery import init_celery, celery  

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    CORS(app)
    
    
    from .extensions import initialize_extensions
    initialize_extensions(app)
    
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
 
    @app.after_request
    def inject_x_rate_headers(response):
        return response

   
    init_celery(app)

    return app
