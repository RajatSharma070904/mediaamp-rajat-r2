from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
import time
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def initialize_db(app):
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
           
            engine = create_engine(
                app.config['SQLALCHEMY_DATABASE_URI'],
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            db.init_app(app)
            migrate.init_app(app, db)
            break
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(retry_delay)
            retry_delay *= 2

def initialize_extensions(app):
    initialize_db(app)
    jwt.init_app(app)
    
    
    app.config['CACHE_REDIS_URL'] = app.config['REDIS_URL']
    cache.init_app(app)
    
   
    limiter.init_app(app)