"""
Recommendation Service
High-level service providing unified interface to the recommendation engine
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from src.config import SessionLocal
from src.models import User, Product, UserRating, UserConcern, Recommendation
from src.services.recommendation.hybrid_engine import HybridRecommendationEngine

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Unified recommendation service
    Handles data loading, model training, and recommendation generation
    """

    def __init__(self):
        self.engine = HybridRecommendationEngine(cf_weight=0.6, cb_weight=0.4)
        self.is_trained = False

    def load_training_data(self, session=None):
        """Load ratings and products from database for training"""
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True

        try:
            # Load all ratings
            ratings_query = session.query(UserRating).all()
            ratings = [
                {
                    'user_id': r.user_id,
                    'product_id': r.product_id,
                    'rating': float(r.rating),
                }
                for r in ratings_query
            ]

            # Load all products
            products_query = session.query(Product).all()
            products = [p.to_dict() for p in products_query]

            logger.info(f"Loaded {len(ratings)} ratings and {len(products)} products")

            return ratings, products

        finally:
            if close_session:
                session.close()

    def train_models(self, session=None):
        """Train recommendation models with data from database"""
        logger.info("Training recommendation models...")

        ratings, products = self.load_training_data(session)

        if not products:
            logger.warning("No products found, cannot train models")
            return False

        self.engine.train(ratings, products)
        self.is_trained = True

        logger.info("✅ Models trained successfully")
        return True

    def get_user_profile(self, user_id: int, session=None) -> Optional[Dict]:
        """Load user profile from database"""
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True

        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return None

            # Get user concerns
            concerns = session.query(UserConcern).filter(UserConcern.user_id == user_id).all()

            profile = {
                'user_id': user.user_id,
                'username': user.username,
                'skin_type': user.skin_type,
                'concerns': [c.to_dict() for c in concerns],
                'budget_range': user.budget_range,
            }

            return profile

        finally:
            if close_session:
                session.close()

    def get_user_ratings(self, user_id: int, session=None) -> List[Dict]:
        """Load user's rating history from database"""
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True

        try:
            ratings = session.query(UserRating).filter(UserRating.user_id == user_id).all()
            return [
                {
                    'user_id': r.user_id,
                    'product_id': r.product_id,
                    'rating': float(r.rating),
                }
                for r in ratings
            ]

        finally:
            if close_session:
                session.close()

    def generate_recommendations(
        self,
        user_id: int,
        n_recommendations: int = 10,
        filters: Optional[Dict] = None,
        save_to_db: bool = True
    ) -> List[Dict]:
        """
        Generate recommendations for a user

        Args:
            user_id: User ID
            n_recommendations: Number of recommendations to generate
            filters: Optional filters (category, price_range, etc.)
            save_to_db: Whether to save recommendations to database

        Returns:
            List of recommendations with product details
        """
        if not self.is_trained:
            logger.warning("Models not trained, training now...")
            self.train_models()

        session = SessionLocal()

        try:
            # Get user profile and ratings
            user_profile = self.get_user_profile(user_id, session)
            if not user_profile:
                logger.error(f"User {user_id} not found")
                return []

            user_ratings = self.get_user_ratings(user_id, session)

            # Generate recommendations
            recommendations = self.engine.recommend(
                user_id=user_id,
                user_profile=user_profile,
                user_ratings=user_ratings,
                n_recommendations=n_recommendations,
                exclude_rated=True
            )

            # Enrich recommendations with product details
            enriched_recs = []

            for rec in recommendations:
                product = session.query(Product).filter(
                    Product.product_id == rec['product_id']
                ).first()

                if not product:
                    continue

                enriched_rec = {
                    'recommendation_id': None,  # Will be set if saved to DB
                    'product': product.to_dict(),
                    'relevance_score': rec['score'],
                    'confidence_score': rec['score'],  # Use same for now
                    'rank': len(enriched_recs) + 1,
                    'algorithm_used': rec['reasoning'].get('algorithm', 'hybrid'),
                    'reasoning': rec['reasoning'],
                }

                enriched_recs.append(enriched_rec)

            # Save to database if requested
            if save_to_db and enriched_recs:
                self._save_recommendations(user_id, enriched_recs, session)

            logger.info(f"Generated {len(enriched_recs)} recommendations for user {user_id}")

            return enriched_recs

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}", exc_info=True)
            return []

        finally:
            session.close()

    def _save_recommendations(self, user_id: int, recommendations: List[Dict], session):
        """Save recommendations to database"""
        try:
            for rec in recommendations:
                db_rec = Recommendation(
                    user_id=user_id,
                    product_id=rec['product']['product_id'],
                    relevance_score=rec['relevance_score'],
                    confidence_score=rec['confidence_score'],
                    rank=rec['rank'],
                    algorithm_used=rec['algorithm_used'],
                    reasoning=rec['reasoning'],
                    recommended_at=datetime.utcnow(),
                )
                session.add(db_rec)

            session.commit()
            logger.info(f"Saved {len(recommendations)} recommendations to database")

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving recommendations: {e}")

    def record_feedback(self, recommendation_id: int, feedback: str, session=None):
        """Record user feedback on a recommendation"""
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True

        try:
            rec = session.query(Recommendation).filter(
                Recommendation.recommendation_id == recommendation_id
            ).first()

            if rec:
                rec.feedback = feedback
                rec.feedback_timestamp = datetime.utcnow()
                session.commit()
                logger.info(f"Recorded feedback '{feedback}' for recommendation {recommendation_id}")
                return True
            else:
                logger.warning(f"Recommendation {recommendation_id} not found")
                return False

        finally:
            if close_session:
                session.close()


# Global service instance
recommendation_service = RecommendationService()
