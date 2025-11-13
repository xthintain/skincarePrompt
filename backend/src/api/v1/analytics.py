"""
Analytics API Endpoints
Provides dashboard metrics and trend data
"""
from flask import Blueprint, request, jsonify
from src.api.middleware.rate_limiter import rate_limit
from src.config import SessionLocal
from src.models import User, Product, Recommendation, UserRating, UserInteraction
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@rate_limit(limit=100)
def get_dashboard_metrics():
    """
    Get overview metrics for dashboard

    Query Parameters:
        skin_type (str): Filter by skin type

    Returns:
        JSON response with dashboard metrics
    """
    try:
        skin_type = request.args.get('skin_type')

        session = SessionLocal()

        try:
            # Total users
            user_query = session.query(func.count(User.user_id))
            if skin_type:
                user_query = user_query.filter(User.skin_type == skin_type)
            total_users = user_query.scalar()

            # Total products
            total_products = session.query(func.count(Product.product_id)).filter(
                Product.is_available == True
            ).scalar()

            # Total recommendations
            total_recommendations = session.query(func.count(Recommendation.recommendation_id)).scalar()

            # Total ratings
            total_ratings = session.query(func.count(UserRating.rating_id)).scalar()

            # Average rating
            avg_rating = session.query(func.avg(UserRating.rating)).scalar()
            avg_rating = float(avg_rating) if avg_rating else 0.0

            # User distribution by skin type
            skin_type_dist = session.query(
                User.skin_type,
                func.count(User.user_id)
            ).group_by(User.skin_type).all()

            skin_type_distribution = [
                {'skin_type': st, 'count': count}
                for st, count in skin_type_dist if st is not None
            ]

            # Product category distribution
            category_dist = session.query(
                Product.category,
                func.count(Product.product_id)
            ).filter(Product.is_available == True).group_by(Product.category).all()

            category_distribution = [
                {'category': cat, 'count': count}
                for cat, count in category_dist
            ]

            # Top rated products
            top_products = session.query(Product).filter(
                Product.is_available == True,
                Product.avg_rating.isnot(None)
            ).order_by(desc(Product.avg_rating)).limit(5).all()

            top_products_list = [
                {
                    'product_id': p.product_id,
                    'name': p.name,
                    'brand': p.brand,
                    'avg_rating': float(p.avg_rating),
                    'review_count': p.review_count,
                }
                for p in top_products
            ]

            return jsonify({
                'success': True,
                'metrics': {
                    'total_users': total_users,
                    'total_products': total_products,
                    'total_recommendations': total_recommendations,
                    'total_ratings': total_ratings,
                    'average_rating': round(avg_rating, 2),
                },
                'distributions': {
                    'skin_types': skin_type_distribution,
                    'categories': category_distribution,
                },
                'top_products': top_products_list,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@analytics_bp.route('/analytics/trends', methods=['GET'])
@rate_limit(limit=100)
def get_trends():
    """
    Get trending products and ingredients

    Query Parameters:
        days (int): Number of days to look back (default: 30)

    Returns:
        JSON response with trend data
    """
    try:
        days = min(request.args.get('days', 30, type=int), 365)

        session = SessionLocal()

        try:
            # Calculate date threshold
            threshold_date = datetime.utcnow() - timedelta(days=days)

            # Most viewed products (from interactions)
            trending_products = session.query(
                Product.product_id,
                Product.name,
                Product.brand,
                Product.category,
                func.count(UserInteraction.interaction_id).label('view_count')
            ).join(
                UserInteraction, Product.product_id == UserInteraction.product_id
            ).filter(
                UserInteraction.interaction_type == 'view',
                UserInteraction.timestamp >= threshold_date
            ).group_by(
                Product.product_id,
                Product.name,
                Product.brand,
                Product.category
            ).order_by(desc('view_count')).limit(10).all()

            trending_list = [
                {
                    'product_id': p.product_id,
                    'name': p.name,
                    'brand': p.brand,
                    'category': p.category,
                    'view_count': p.view_count,
                }
                for p in trending_products
            ]

            # Recent ratings trend (ratings per day)
            daily_ratings = session.query(
                func.date(UserRating.reviewed_at).label('date'),
                func.count(UserRating.rating_id).label('count'),
                func.avg(UserRating.rating).label('avg_rating')
            ).filter(
                UserRating.reviewed_at >= threshold_date
            ).group_by(
                func.date(UserRating.reviewed_at)
            ).order_by('date').all()

            ratings_trend = [
                {
                    'date': str(r.date),
                    'count': r.count,
                    'avg_rating': round(float(r.avg_rating), 2) if r.avg_rating else 0,
                }
                for r in daily_ratings
            ]

            return jsonify({
                'success': True,
                'period_days': days,
                'trending_products': trending_list,
                'ratings_trend': ratings_trend,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error getting trends: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
