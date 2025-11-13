"""
Error Handling Utilities
Custom exceptions and error handlers for the application
"""
from flask import jsonify
import uuid
import logging


class APIError(Exception):
    """Base API Exception"""

    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
        self.trace_id = str(uuid.uuid4())

    def to_dict(self):
        """Convert exception to dictionary for JSON response"""
        rv = dict(self.payload or ())
        rv['error'] = self.message
        if self.status_code >= 500:
            rv['trace_id'] = self.trace_id
        return rv


class ValidationError(APIError):
    """Validation error (400)"""

    def __init__(self, message, details=None):
        super().__init__(message, status_code=400, payload={'details': details or {}})


class UnauthorizedError(APIError):
    """Unauthorized error (401)"""

    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(APIError):
    """Forbidden error (403)"""

    def __init__(self, message="Forbidden"):
        super().__init__(message, status_code=403)


class NotFoundError(APIError):
    """Not found error (404)"""

    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(APIError):
    """Conflict error (409)"""

    def __init__(self, message="Resource already exists"):
        super().__init__(message, status_code=409)


class RateLimitError(APIError):
    """Rate limit exceeded error (429)"""

    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message, status_code=429)


class InternalServerError(APIError):
    """Internal server error (500)"""

    def __init__(self, message="Internal server error"):
        super().__init__(message, status_code=500)


def register_error_handlers(app):
    """
    Register error handlers with Flask app
    Args:
        app: Flask application instance
    """

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code

        # Log server errors
        if error.status_code >= 500:
            logging.error(f"APIError [{error.trace_id}]: {error.message}", exc_info=True)

        return response

    @app.errorhandler(400)
    def bad_request(e):
        """Handle bad request errors"""
        return jsonify({'error': 'Bad request', 'details': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        """Handle unauthorized errors"""
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(404)
    def not_found(e):
        """Handle not found errors"""
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle internal server errors"""
        trace_id = str(uuid.uuid4())
        logging.error(f"Internal Server Error [{trace_id}]: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'trace_id': trace_id
        }), 500

    return app


def validate_request_data(data, required_fields):
    """
    Validate request data contains required fields
    Args:
        data: Request data dictionary
        required_fields: List of required field names
    Raises:
        ValidationError: If validation fails
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise ValidationError(
            'Missing required fields',
            details={'missing_fields': missing_fields}
        )
