from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.blueprints.auth.models import User, RoleEnum
from app.extensions import db, limiter
from app.utils.decorators import role_required
from app.utils.validators import validate_email, validate_password
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    data = request.get_json()
    
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({"error": "Missing required fields"}), 400
    
    if not validate_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400
    
    if not validate_password(data['password']):
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 409
    
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=RoleEnum.USER
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    
   
    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role.value},
        expires_delta=timedelta(hours=1)
    )
    
    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "role": user.role.value
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user's profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }), 200