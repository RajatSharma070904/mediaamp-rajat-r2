from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.exceptions import UnauthorizedAccess

def role_required(required_role):
    """Decorator to require specific role for access."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['role'] != required_role and claims['role'] != 'admin':
                raise UnauthorizedAccess()
            return fn(*args, **kwargs)
        return wrapper
    return decorator