"""
Content-Based Filtering Recommendation Engine
Uses TF-IDF and cosine similarity to recommend products based on content features

References:
- Pazzani, M. J., & Billsus, D. (2007).
  "Content-based recommendation systems."
  The adaptive web (pp. 325-341). Springer.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class ContentBasedFiltering:
    """
    Content-Based Filtering Engine

    Algorithm:
    1. Extract product features (category, ingredients, concerns, attributes)
    2. Build TF-IDF feature vectors
    3. Calculate content similarity using cosine similarity
    4. Match user profile to product features

    Reference: Pazzani & Billsus (2007)
    """

    def __init__(self, feature_weights=None):
        """
        Initialize content-based filtering engine

        Args:
            feature_weights: Dict of weights for different features
                            e.g., {'category': 1.0, 'ingredients': 2.0, 'concerns': 1.5}
        """
        self.feature_weights = feature_weights or {
            'category': 1.0,
            'ingredients': 2.0,
            'concerns': 1.5,
            'attributes': 0.5,
        }
        self.tfidf_vectorizer = None
        self.product_vectors = None
        self.product_ids = None
        self.product_features = None

    def extract_product_features(self, products: List[Dict]) -> List[str]:
        """
        Extract and concatenate product features into text representations

        Args:
            products: List of product dictionaries

        Returns:
            List of feature strings for each product
        """
        feature_strings = []

        for product in products:
            features = []

            # Category (weighted)
            category = product.get('category', '')
            features.extend([category] * int(self.feature_weights.get('category', 1) * 3))

            # Ingredients (weighted)
            ingredients = product.get('ingredients', [])
            if isinstance(ingredients, str):
                try:
                    ingredients = json.loads(ingredients)
                except:
                    ingredients = []
            ingredient_text = ' '.join(ing.get('name', '') for ing in ingredients if isinstance(ing, dict))
            features.extend([ingredient_text] * int(self.feature_weights.get('ingredients', 1)))

            # Target concerns (weighted)
            concerns = product.get('target_concerns', [])
            if isinstance(concerns, str):
                try:
                    concerns = json.loads(concerns)
                except:
                    concerns = []
            concerns_text = ' '.join(concerns) if concerns else ''
            features.extend([concerns_text] * int(self.feature_weights.get('concerns', 1) * 2))

            # Attributes (weighted)
            attributes = []
            if product.get('is_organic'):
                attributes.append('organic')
            if product.get('is_cruelty_free'):
                attributes.append('cruelty_free')
            if product.get('is_vegan'):
                attributes.append('vegan')
            if product.get('is_fragrance_free'):
                attributes.append('fragrance_free')

            attributes_text = ' '.join(attributes)
            features.extend([attributes_text] * int(self.feature_weights.get('attributes', 1)))

            # Suitable skin types
            skin_types = product.get('suitable_for_skin_types', [])
            if isinstance(skin_types, str):
                try:
                    skin_types = json.loads(skin_types)
                except:
                    skin_types = []
            skin_types_text = ' '.join(skin_types) if skin_types else ''
            features.append(skin_types_text)

            # Brand
            brand = product.get('brand', '')
            features.append(brand)

            # Combine all features
            feature_string = ' '.join(filter(None, features))
            feature_strings.append(feature_string)

        return feature_strings

    def train(self, products: List[Dict]):
        """
        Train the content-based model by building TF-IDF vectors

        Args:
            products: List of product dictionaries
        """
        logger.info("Training content-based filtering model...")

        if not products:
            logger.warning("No products provided for training")
            return

        self.product_ids = [p['product_id'] for p in products]
        self.product_features = products

        # Extract product features
        feature_strings = self.extract_product_features(products)

        # Build TF-IDF vectors
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8,
        )

        self.product_vectors = self.tfidf_vectorizer.fit_transform(feature_strings)

        logger.info(f"Trained content model with {len(products)} products, "
                   f"vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}")

    def build_user_profile_vector(self, user_profile: Dict) -> np.ndarray:
        """
        Build feature vector from user profile

        Args:
            user_profile: User profile dictionary with skin_type, concerns, etc.

        Returns:
            TF-IDF vector representing user preferences
        """
        profile_features = []

        # Skin type (most important)
        skin_type = user_profile.get('skin_type', '')
        profile_features.extend([skin_type] * 5)

        # Concerns
        concerns = user_profile.get('concerns', [])
        concerns_text = ' '.join(c.get('concern_type', '') for c in concerns if isinstance(c, dict))
        profile_features.extend([concerns_text] * 3)

        # Preferences
        if user_profile.get('prefer_organic'):
            profile_features.extend(['organic'] * 2)
        if user_profile.get('prefer_cruelty_free'):
            profile_features.extend(['cruelty_free'] * 2)
        if user_profile.get('prefer_fragrance_free'):
            profile_features.extend(['fragrance_free'] * 2)

        # Combine
        profile_string = ' '.join(filter(None, profile_features))

        # Transform using TF-IDF
        if self.tfidf_vectorizer is None:
            logger.error("Model not trained, cannot build user profile vector")
            return np.array([])

        profile_vector = self.tfidf_vectorizer.transform([profile_string])

        return profile_vector

    def recommend(self, user_profile: Dict, n_recommendations: int = 10, exclude_products: List[int] = None) -> List[Dict]:
        """
        Generate content-based recommendations for a user

        Args:
            user_profile: User profile dictionary
            n_recommendations: Number of recommendations to generate
            exclude_products: List of product IDs to exclude

        Returns:
            List of recommendation dictionaries
        """
        if self.tfidf_vectorizer is None or self.product_vectors is None:
            logger.error("Model not trained, cannot generate recommendations")
            return []

        exclude_products = exclude_products or []

        # Build user profile vector
        user_vector = self.build_user_profile_vector(user_profile)

        if user_vector.size == 0:
            logger.warning("Empty user profile vector")
            return []

        # Calculate similarity between user profile and all products
        similarities = cosine_similarity(user_vector, self.product_vectors)[0]

        # Create recommendations
        recommendations = []

        for idx, similarity in enumerate(similarities):
            product_id = self.product_ids[idx]

            # Skip excluded products
            if product_id in exclude_products:
                continue

            # Get product info
            product = self.product_features[idx]

            # Create reasoning
            reasoning = {
                'algorithm': 'content_based',
                'similarity_score': float(similarity),
                'matched_features': {
                    'skin_type_match': user_profile.get('skin_type') in str(product.get('suitable_for_skin_types', [])),
                    'category': product.get('category'),
                },
            }

            # Check concern matches
            user_concerns = set(c.get('concern_type', '') for c in user_profile.get('concerns', []))
            product_concerns = product.get('target_concerns', [])
            if isinstance(product_concerns, str):
                try:
                    product_concerns = json.loads(product_concerns)
                except:
                    product_concerns = []

            concern_matches = list(user_concerns.intersection(set(product_concerns)))
            if concern_matches:
                reasoning['matched_features']['concerns'] = concern_matches

            recommendations.append({
                'product_id': product_id,
                'score': float(similarity),
                'reasoning': reasoning,
            })

        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:n_recommendations]
