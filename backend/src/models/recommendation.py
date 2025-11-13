"""
Recommendation Model
Fact table storing recommendation results from the ML engine
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import BaseModel


class Recommendation(BaseModel):
    """
    Fact table for recommendations
    Stores recommendation results with relevance scores and reasoning
    """
    __tablename__ = 'fact_recommendation'

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=True)

    # Recommendation Metrics
    relevance_score = Column(Numeric(5, 4), nullable=False)  # 0.0000 to 1.0000
    confidence_score = Column(Numeric(5, 4), nullable=True)  # Model confidence
    rank = Column(Integer, nullable=True)  # Ranking in recommendation list

    # Algorithm Information
    algorithm_used = Column(
        String(50),
        nullable=False
    )  # 'collaborative_filtering', 'content_based', 'hybrid'
    model_version = Column(String(50), nullable=True)  # e.g., 'v1.2.3'

    # Reasoning (for explainability)
    reasoning = Column(JSON, nullable=True)  # Structured explanation
    # Example: {
    #   "factors": ["Similar to liked product X", "High rating for your skin type"],
    #   "match_score": 0.85,
    #   "ingredient_safety": "safe",
    #   "price_match": true
    # }

    # User Feedback
    feedback = Column(String(20), nullable=True)  # 'helpful', 'not_helpful', 'purchased'
    feedback_timestamp = Column(DateTime, nullable=True)

    # Timestamp
    recommended_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='recommendations')
    product = relationship('Product', back_populates='recommendations')

    def __repr__(self):
        return f"<Recommendation(id={self.recommendation_id}, user={self.user_id}, product={self.product_id}, score={self.relevance_score})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'recommendation_id': self.recommendation_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'relevance_score': float(self.relevance_score),
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'rank': self.rank,
            'algorithm_used': self.algorithm_used,
            'model_version': self.model_version,
            'reasoning': self.reasoning,
            'feedback': self.feedback,
            'recommended_at': self.recommended_at.isoformat() if self.recommended_at else None,
        }
