"""
Hybrid Recommendation Engine
Combines Collaborative Filtering and Content-Based Filtering using weighted average

References:
- Burke, R. (2002).
  "Hybrid recommender systems: Survey and experiments."
  User modeling and user-adapted interaction, 12(4), 331-370.
"""
import numpy as np
from typing import List, Dict, Optional
import logging

from src.services.recommendation.collaborative_filtering import CollaborativeFiltering
from src.services.recommendation.content_based import ContentBasedFiltering

logger = logging.getLogger(__name__)


class HybridRecommendationEngine:
    """
    Hybrid Recommendation Engine

    Combines collaborative filtering and content-based filtering using weighted linear combination.
    Automatically adjusts weights based on data availability (cold start handling).

    Algorithm:
    - For new users/items (cold start): Rely more on content-based
    - For users with rating history: Use both methods with configurable weights
    - Final score = α * CF_score + β * CB_score

    Reference: Burke (2002)
    """

    def __init__(self, cf_weight=0.6, cb_weight=0.4, cold_start_threshold=3):
        """
        Initialize hybrid recommendation engine

        Args:
            cf_weight: Weight for collaborative filtering (default: 0.6)
            cb_weight: Weight for content-based filtering (default: 0.4)
            cold_start_threshold: Minimum ratings before using CF (default: 3)
        """
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight
        self.cold_start_threshold = cold_start_threshold

        # Initialize sub-engines
        self.cf_engine = CollaborativeFiltering(n_neighbors=10, min_rating=3.5)
        self.cb_engine = ContentBasedFiltering()

        logger.info(f"Initialized hybrid engine with CF weight={cf_weight}, CB weight={cb_weight}")

    def train(self, ratings: List[Dict], products: List[Dict]):
        """
        Train both collaborative and content-based models

        Args:
            ratings: List of rating dictionaries
            products: List of product dictionaries
        """
        logger.info("Training hybrid recommendation engine...")

        # Train collaborative filtering
        if ratings:
            try:
                self.cf_engine.train(ratings)
                logger.info("✅ Collaborative filtering model trained")
            except Exception as e:
                logger.error(f"Failed to train CF model: {e}")

        # Train content-based filtering
        if products:
            try:
                self.cb_engine.train(products)
                logger.info("✅ Content-based filtering model trained")
            except Exception as e:
                logger.error(f"Failed to train CB model: {e}")

        logger.info("Hybrid engine training completed")

    def normalize_scores(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Normalize scores to [0, 1] range using min-max normalization

        Args:
            recommendations: List of recommendations with scores

        Returns:
            Recommendations with normalized scores
        """
        if not recommendations:
            return []

        scores = [r['score'] for r in recommendations]
        min_score = min(scores)
        max_score = max(scores)

        # Avoid division by zero
        if max_score == min_score:
            for rec in recommendations:
                rec['score'] = 0.5
            return recommendations

        # Min-max normalization
        for rec in recommendations:
            rec['score'] = (rec['score'] - min_score) / (max_score - min_score)

        return recommendations

    def merge_recommendations(
        self,
        cf_recs: List[Dict],
        cb_recs: List[Dict],
        cf_weight: float,
        cb_weight: float
    ) -> List[Dict]:
        """
        Merge recommendations from CF and CB using weighted average

        Args:
            cf_recs: Collaborative filtering recommendations
            cb_recs: Content-based filtering recommendations
            cf_weight: Weight for CF scores
            cb_weight: Weight for CB scores

        Returns:
            Merged recommendations sorted by hybrid score
        """
        # Normalize scores
        cf_recs_norm = self.normalize_scores(cf_recs.copy())
        cb_recs_norm = self.normalize_scores(cb_recs.copy())

        # Create score dictionaries
        cf_scores = {r['product_id']: r for r in cf_recs_norm}
        cb_scores = {r['product_id']: r for r in cb_recs_norm}

        # Get all product IDs
        all_product_ids = set(cf_scores.keys()).union(set(cb_scores.keys()))

        # Calculate hybrid scores
        hybrid_recs = []

        for product_id in all_product_ids:
            cf_score = cf_scores.get(product_id, {}).get('score', 0.0)
            cb_score = cb_scores.get(product_id, {}).get('score', 0.0)

            # Weighted average
            hybrid_score = cf_weight * cf_score + cb_weight * cb_score

            # Combine reasoning
            reasoning = {
                'algorithm': 'hybrid',
                'cf_weight': cf_weight,
                'cb_weight': cb_weight,
                'cf_score': float(cf_score),
                'cb_score': float(cb_score),
            }

            # Add specific reasoning from each method
            if product_id in cf_scores:
                reasoning['cf_reasoning'] = cf_scores[product_id].get('reasoning', {})
            if product_id in cb_scores:
                reasoning['cb_reasoning'] = cb_scores[product_id].get('reasoning', {})

            hybrid_recs.append({
                'product_id': product_id,
                'score': float(hybrid_score),
                'reasoning': reasoning,
            })

        # Sort by hybrid score
        hybrid_recs.sort(key=lambda x: x['score'], reverse=True)

        return hybrid_recs

    def recommend(
        self,
        user_id: int,
        user_profile: Dict,
        user_ratings: List[Dict],
        n_recommendations: int = 10,
        exclude_rated: bool = True
    ) -> List[Dict]:
        """
        Generate hybrid recommendations for a user

        Args:
            user_id: User ID
            user_profile: User profile dictionary (skin_type, concerns, etc.)
            user_ratings: User's rating history
            n_recommendations: Number of recommendations to generate
            exclude_rated: Whether to exclude already rated items

        Returns:
            List of hybrid recommendations
        """
        logger.info(f"Generating hybrid recommendations for user {user_id}")

        # Determine if user has cold start problem
        num_ratings = len(user_ratings)
        is_cold_start = num_ratings < self.cold_start_threshold

        # Adjust weights based on cold start
        if is_cold_start:
            # Cold start: rely more on content-based
            effective_cf_weight = 0.2
            effective_cb_weight = 0.8
            logger.info(f"Cold start detected ({num_ratings} ratings), using CB-heavy weights")
        else:
            # Normal case: use configured weights
            effective_cf_weight = self.cf_weight
            effective_cb_weight = self.cb_weight

        # Get collaborative filtering recommendations
        cf_recs = []
        if num_ratings > 0:
            try:
                cf_recs = self.cf_engine.recommend(
                    user_id=user_id,
                    user_ratings=user_ratings,
                    n_recommendations=n_recommendations * 2,  # Get more for merging
                    exclude_rated=exclude_rated
                )
                logger.info(f"CF generated {len(cf_recs)} recommendations")
            except Exception as e:
                logger.error(f"CF recommendation failed: {e}")

        # Get content-based recommendations
        cb_recs = []
        try:
            exclude_products = [r['product_id'] for r in user_ratings] if exclude_rated else []
            cb_recs = self.cb_engine.recommend(
                user_profile=user_profile,
                n_recommendations=n_recommendations * 2,
                exclude_products=exclude_products
            )
            logger.info(f"CB generated {len(cb_recs)} recommendations")
        except Exception as e:
            logger.error(f"CB recommendation failed: {e}")

        # Handle edge cases
        if not cf_recs and not cb_recs:
            logger.warning("Both CF and CB failed, returning empty recommendations")
            return []

        if not cf_recs:
            logger.info("CF failed, using CB only")
            return cb_recs[:n_recommendations]

        if not cb_recs:
            logger.info("CB failed, using CF only")
            return cf_recs[:n_recommendations]

        # Merge recommendations
        hybrid_recs = self.merge_recommendations(
            cf_recs, cb_recs,
            effective_cf_weight, effective_cb_weight
        )

        logger.info(f"Generated {len(hybrid_recs)} hybrid recommendations")

        return hybrid_recs[:n_recommendations]
