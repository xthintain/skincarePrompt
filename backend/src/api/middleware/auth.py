"""
JWT Authentication Middleware
Handles JWT token validation and user authentication
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from src.config import config


def generate_access_token(user_id):
    """Generate JWT access token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def generate_refresh_token(user_id):
    """Generate JWT refresh token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_REFRESH_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def decode_token(token):
    """
    Decode and validate JWT token
    Returns payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """
    Decorator to require authentication for endpoints
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user_id = g.user_id
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401

        # Extract token (format: "Bearer <token>")
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401

        # Decode and validate token
        payload = decode_token(token)

        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Check token type
        if payload.get('type') != 'access':
            return jsonify({'error': 'Invalid token type'}), 401

        # Store user_id in Flask's g object for use in the route
        g.user_id = payload['user_id']

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication
    Sets g.user_id if token is valid, otherwise continues without authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                payload = decode_token(token)

                if payload and payload.get('type') == 'access':
                    g.user_id = payload['user_id']
                else:
                    g.user_id = None
            except (IndexError, KeyError):
                g.user_id = None
        else:
            g.user_id = None

        return f(*args, **kwargs)

    return decorated_function
