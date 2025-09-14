from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def require_role(required_roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Require admin role"""
    return require_role(['admin'])(f)

def warehouse_manager_required(f):
    """Require warehouse_manager or admin role"""
    return require_role(['admin', 'warehouse_manager'])(f)

def clerk_required(f):
    """Require clerk, warehouse_manager or admin role"""
    return require_role(['admin', 'warehouse_manager', 'clerk'])(f)





