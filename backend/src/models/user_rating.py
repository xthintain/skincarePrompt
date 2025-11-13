"""
UserRating Model
User ratings and reviews for products
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import BaseModel


class UserRating(BaseModel):
    """
    User product ratings and reviews
    """
    __tablename__ = 'user_rating'

    rating_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('dim_user.user_id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id', ondelete='CASCADE'), nullable=False, index=True)

    # Rating (1-5 scale)
    rating = Column(Numeric(2, 1), nullable=False)  # 1.0 to 5.0

    # Review
    review_text = Column(Text, nullable=True)
    review_title = Column(String(200), nullable=True)

    # Context
    skin_type_at_review = Column(String(20), nullable=True)  # User's skin type when reviewed
    verified_purchase = Column(String(20), default='unverified')  # 'verified', 'unverified'

    # Helpfulness
    helpful_count = Column(Integer, default=0, nullable=False)
    unhelpful_count = Column(Integer, default=0, nullable=False)

    # Timestamp
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='ratings')
    product = relationship('Product', back_populates='ratings')

    def __repr__(self):
        return f"<UserRating(user={self.user_id}, product={self.product_id}, rating={self.rating})>"

    def to_dict(self):
        return {
            'rating_id': self.rating_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': float(self.rating),
            'review_text': self.review_text,
            'review_title': self.review_title,
            'skin_type_at_review': self.skin_type_at_review,
            'verified_purchase': self.verified_purchase,
            'helpful_count': self.helpful_count,
            'unhelpful_count': self.unhelpful_count,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
