"""
Main Flask Application
Entry point for the Cosmetics Recommendation System backend
"""
from flask import Flask, jsonify
from src.config import config
from src.utils.logger import setup_logging
from src.utils.errors import register_error_handlers
from src.api.middleware.cors import init_cors
from src.api.v1 import init_api_routes


def create_app():
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config)

    # Setup logging
    setup_logging(app)

    # Initialize CORS
    init_cors(app)

    # Register error handlers
    register_error_handlers(app)

    # Register API routes
    init_api_routes(app)

    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'version': '1.0.0'}), 200

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Cosmetics Analysis and Recommendation System API',
            'version': '1.0.0',
            'endpoints': {
                'recommendations': '/api/v1/recommendations',
                'products': '/api/v1/products',
                'analytics': '/api/v1/analytics/dashboard',
                'health': '/api/v1/health',
            }
        }), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )
