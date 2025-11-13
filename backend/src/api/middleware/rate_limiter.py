"""
Rate Limiting Middleware
Implements token bucket rate limiting using Redis
"""
import redis
from flask import request, jsonify, g
from functools import wraps
from src.config import config


# Initialize Redis client
try:
    redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None


def get_client_identifier():
    """
    Get unique identifier for the client
    Uses user_id if authenticated, otherwise uses IP address
    """
    if hasattr(g, 'user_id') and g.user_id:
        return f"user:{g.user_id}"
    else:
        return f"ip:{request.remote_addr}"


def check_rate_limit(identifier, limit, window=3600):
    """
    Check if request is within rate limit using token bucket algorithm
    Args:
        identifier: Unique client identifier
        limit: Maximum requests allowed in window
        window: Time window in seconds (default: 3600 = 1 hour)
    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    if not config.RATE_LIMIT_ENABLED or not redis_client:
        return True, limit

    key = f"rate_limit:{identifier}"

    try:
        # Get current count
        current = redis_client.get(key)

        if current is None:
            # First request in window
            pipe = redis_client.pipeline()
            pipe.set(key, 1, ex=window)
            pipe.execute()
            return True, limit - 1
        else:
            current = int(current)

            if current >= limit:
                # Rate limit exceeded
                ttl = redis_client.ttl(key)
                return False, 0
            else:
                # Increment counter
                redis_client.incr(key)
                return True, limit - current - 1

    except Exception as e:
        print(f"Rate limiting error: {e}")
        # Fail open - allow request if Redis has issues
        return True, limit


def rate_limit(limit=None):
    """
    Decorator to apply rate limiting to endpoints
    Args:
        limit: Custom rate limit (optional). Defaults to config values based on auth status.

    Usage:
        @app.route('/api/search')
        @rate_limit(limit=500)  # Custom limit of 500/hour
        def search():
            ...

        @app.route('/api/products')
        @rate_limit()  # Use default limits (100 unauth, 1000 auth)
        def products():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine rate limit
            if limit is not None:
                current_limit = limit
            else:
                # Use default limits based on authentication
                if hasattr(g, 'user_id') and g.user_id:
                    current_limit = config.RATE_LIMIT_PER_HOUR_AUTH
                else:
                    current_limit = config.RATE_LIMIT_PER_HOUR_UNAUTH

            # Check rate limit
            identifier = get_client_identifier()
            is_allowed, remaining = check_rate_limit(identifier, current_limit)

            if not is_allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {current_limit} requests per hour allowed'
                }), 429

            # Add rate limit info to response headers
            response = f(*args, **kwargs)

            # If response is a tuple (response, status_code), handle it
            if isinstance(response, tuple):
                resp_obj, status_code = response[0], response[1]
            else:
                resp_obj, status_code = response, 200

            # Add headers if response is not already a Response object
            try:
                if hasattr(resp_obj, 'headers'):
                    resp_obj.headers['X-RateLimit-Limit'] = str(current_limit)
                    resp_obj.headers['X-RateLimit-Remaining'] = str(remaining)
            except Exception:
                pass

            return resp_obj if status_code == 200 else (resp_obj, status_code)

        return decorated_function

    return decorator


def reset_rate_limit(identifier):
    """
    Reset rate limit for a specific client (admin function)
    Args:
        identifier: Client identifier (user:123 or ip:1.2.3.4)
    """
    if redis_client:
        key = f"rate_limit:{identifier}"
        redis_client.delete(key)
