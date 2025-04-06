import pytest
from app import create_app
from app.extensions import db as _db
from flask_migrate import upgrade

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        upgrade()
    yield _db
    _db.session.close()
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()