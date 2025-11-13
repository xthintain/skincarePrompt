"""
CORS (Cross-Origin Resource Sharing) Middleware
Handles CORS configuration for Flask application
"""
from flask import Flask
from flask_cors import CORS
from src.config import config


def init_cors(app: Flask):
    """
    Initialize CORS for Flask application
    Args:
        app: Flask application instance
    """
    CORS(
        app,
        resources={r"/api/*": {"origins": config.CORS_ORIGINS}},
        supports_credentials=True,
        allow_headers=[
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'Accept'
        ],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        max_age=3600  # Cache preflight response for 1 hour
    )

    return app


def add_cors_headers(response):
    """
    Manually add CORS headers to response
    Use this if not using flask-cors extension
    """
    response.headers['Access-Control-Allow-Origin'] = ', '.join(config.CORS_ORIGINS)
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response
