"""
Collaborative Filtering Recommendation Engine
Implements Item-based Collaborative Filtering using cosine similarity

References:
- Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001).
  "Item-based collaborative filtering recommendation algorithms."
  Proceedings of the 10th international conference on World Wide Web.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CollaborativeFiltering:
    """
    Item-based Collaborative Filtering Engine

    Algorithm:
    1. Build user-item rating matrix
    2. Calculate item-item similarity using cosine similarity
    3. For target user, find items similar to items they've rated highly
    4. Generate recommendations based on similarity scores

    Reference: Sarwar et al. (2001)
    """

    def __init__(self, n_neighbors=10, min_rating=3.5):
        """
        Initialize collaborative filtering engine

        Args:
            n_neighbors: Number of similar items to consider
            min_rating: Minimum rating threshold to consider as positive feedback
        """
        self.n_neighbors = n_neighbors
        self.min_rating = min_rating
        self.model = None
        self.item_ids = None
        self.user_item_matrix = None

    def build_user_item_matrix(self, ratings: List[Dict]) -> np.ndarray:
        """
        Build user-item rating matrix from rating data

        Args:
            ratings: List of rating dictionaries with keys: user_id, product_id, rating

        Returns:
            User-item matrix (users x items)
        """
        if not ratings:
            logger.warning("No ratings provided for building matrix")
            return np.array([[]])

        # Get unique users and items
        users = sorted(set(r['user_id'] for r in ratings))
        items = sorted(set(r['product_id'] for r in ratings))

        # Create mapping
        user_idx = {user_id: idx for idx, user_id in enumerate(users)}
        item_idx = {item_id: idx for idx, item_id in enumerate(items)}

        # Initialize matrix
        matrix = np.zeros((len(users), len(items)))

        # Fill matrix
        for rating in ratings:
            u_idx = user_idx[rating['user_id']]
            i_idx = item_idx[rating['product_id']]
            matrix[u_idx, i_idx] = rating['rating']

        self.item_ids = items
        self.user_item_matrix = matrix

        logger.info(f"Built user-item matrix: {matrix.shape[0]} users x {matrix.shape[1]} items")

        return matrix

    def train(self, ratings: List[Dict]):
        """
        Train the collaborative filtering model

        Args:
            ratings: List of rating dictionaries
        """
        logger.info("Training collaborative filtering model...")

        # Build user-item matrix
        matrix = self.build_user_item_matrix(ratings)

        if matrix.size == 0:
            logger.warning("Empty rating matrix, cannot train model")
            return

        # Transpose to get item-user matrix (items x users)
        item_user_matrix = matrix.T

        # Train NearestNeighbors model on item vectors
        # Use cosine similarity (1 - cosine_distance)
        self.model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(self.item_ids)),
            metric='cosine',
            algorithm='brute'
        )
        self.model.fit(item_user_matrix)

        logger.info(f"Trained model with {len(self.item_ids)} items")

    def get_item_similarities(self, item_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """
        Find n most similar items to the given item

        Args:
            item_id: Target item ID
            n_similar: Number of similar items to return

        Returns:
            List of (item_id, similarity_score) tuples
        """
        if self.model is None or self.item_ids is None:
            logger.error("Model not trained")
            return []

        if item_id not in self.item_ids:
            logger.warning(f"Item {item_id} not in training data")
            return []

        # Get item index
        item_idx = self.item_ids.index(item_id)

        # Get item vector
        item_vector = self.user_item_matrix.T[item_idx].reshape(1, -1)

        # Find similar items
        distances, indices = self.model.kneighbors(
            item_vector,
            n_neighbors=min(n_similar + 1, len(self.item_ids))
        )

        # Convert distances to similarities (cosine similarity = 1 - cosine distance)
        similarities = 1 - distances[0]

        # Return similar items (excluding the item itself)
        similar_items = []
        for idx, sim in zip(indices[0][1:], similarities[1:]):
            similar_item_id = self.item_ids[idx]
            similar_items.append((similar_item_id, float(sim)))

        return similar_items

    def recommend(self, user_id: int, user_ratings: List[Dict], n_recommendations: int = 10, exclude_rated: bool = True) -> List[Dict]:
        """
        Generate recommendations for a user based on collaborative filtering

        Args:
            user_id: Target user ID
            user_ratings: User's rating history
            n_recommendations: Number of recommendations to generate
            exclude_rated: Whether to exclude already rated items

        Returns:
            List of recommendation dictionaries with keys: product_id, score, reasoning
        """
        if self.model is None or self.item_ids is None:
            logger.error("Model not trained, cannot generate recommendations")
            return []

        # Get user's highly rated items (rating >= min_rating)
        liked_items = [
            r['product_id'] for r in user_ratings
            if r['rating'] >= self.min_rating
        ]

        if not liked_items:
            logger.warning(f"User {user_id} has no highly rated items (>= {self.min_rating})")
            return []

        # Get rated items for exclusion
        rated_items = set(r['product_id'] for r in user_ratings) if exclude_rated else set()

        # Find similar items for each liked item
        candidate_items = {}  # {item_id: [similarities]}

        for liked_item in liked_items:
            similar_items = self.get_item_similarities(liked_item, n_similar=20)

            for item_id, similarity in similar_items:
                # Skip already rated items
                if exclude_rated and item_id in rated_items:
                    continue

                if item_id not in candidate_items:
                    candidate_items[item_id] = []

                candidate_items[item_id].append({
                    'similarity': similarity,
                    'source_item': liked_item
                })

        # Aggregate scores for candidate items
        recommendations = []

        for item_id, similarities in candidate_items.items():
            # Calculate aggregated score (average similarity)
            avg_similarity = np.mean([s['similarity'] for s in similarities])

            # Create reasoning
            top_source = max(similarities, key=lambda x: x['similarity'])

            recommendations.append({
                'product_id': item_id,
                'score': float(avg_similarity),
                'reasoning': {
                    'algorithm': 'collaborative_filtering',
                    'similar_to': [s['source_item'] for s in similarities[:3]],
                    'top_similarity': float(top_source['similarity']),
                    'num_similar_items': len(similarities),
                }
            })

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:n_recommendations]
