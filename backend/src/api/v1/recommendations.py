"""
Recommendations API Endpoints
Handles recommendation generation and feedback
"""
from flask import Blueprint, request, jsonify, g
from src.api.middleware.auth import optional_auth
from src.api.middleware.rate_limiter import rate_limit
from src.services.recommendation_service import recommendation_service
from src.utils.errors import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations', methods=['GET'])
@optional_auth
@rate_limit(limit=100)
def get_recommendations():
    """
    Get personalized recommendations for a user

    Query Parameters:
        user_id (int): User ID (required)
        n (int): Number of recommendations (default: 10, max: 50)
        category (str): Filter by product category
        min_price (float): Minimum price
        max_price (float): Maximum price

    Returns:
        JSON response with recommendations
    """
    try:
        # Get user_id from query params
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            raise ValidationError("Missing required parameter: user_id")

        # Get optional parameters
        n = min(request.args.get('n', 10, type=int), 50)
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price

        logger.info(f"Generating recommendations for user {user_id}, n={n}, filters={filters}")

        # Generate recommendations
        recommendations = recommendation_service.generate_recommendations(
            user_id=user_id,
            n_recommendations=n,
            filters=filters if filters else None,
            save_to_db=True
        )

        return jsonify({
            'success': True,
            'user_id': user_id,
            'count': len(recommendations),
            'recommendations': recommendations,
        }), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@recommendations_bp.route('/recommendations/feedback', methods=['POST'])
@optional_auth
@rate_limit(limit=200)
def submit_feedback():
    """
    Submit feedback on a recommendation

    Request Body:
        {
            "recommendation_id": int,
            "feedback": "helpful" | "not_helpful" | "purchased"
        }

    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()

        if not data:
            raise ValidationError("Missing request body")

        recommendation_id = data.get('recommendation_id')
        feedback = data.get('feedback')

        if not recommendation_id:
            raise ValidationError("Missing required field: recommendation_id")

        if not feedback or feedback not in ['helpful', 'not_helpful', 'purchased']:
            raise ValidationError("Invalid feedback value. Must be: helpful, not_helpful, or purchased")

        # Record feedback
        success = recommendation_service.record_feedback(recommendation_id, feedback)

        if not success:
            raise NotFoundError("Recommendation not found")

        logger.info(f"Recorded feedback '{feedback}' for recommendation {recommendation_id}")

        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully'
        }), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error recording feedback: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
