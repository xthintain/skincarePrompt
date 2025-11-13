"""
API v1 Package
Contains all API version 1 endpoints
"""
from flask import Blueprint

# Create API v1 blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import and register sub-blueprints
from src.api.v1.recommendations import recommendations_bp
from src.api.v1.products import products_bp
from src.api.v1.analytics import analytics_bp
from src.api.v1.skincare import skincare_bp
from src.api.v1.skincare_ml import skincare_ml_bp
from src.api.v1.admin import admin_bp

# Register blueprints
from flask import current_app


def init_api_routes(app):
    """Initialize all API routes"""
    app.register_blueprint(recommendations_bp, url_prefix='/api/v1')
    app.register_blueprint(products_bp, url_prefix='/api/v1')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1')
    app.register_blueprint(skincare_bp, url_prefix='/api/v1')
    app.register_blueprint(skincare_ml_bp, url_prefix='/api/v1')  # ML推荐API
    app.register_blueprint(admin_bp, url_prefix='/api/v1')  # 管理API
