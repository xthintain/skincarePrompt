"""
UserInteraction Model
Fact table tracking user interactions with products for analytics
"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import BaseModel


class UserInteraction(BaseModel):
    """
    User interaction events (view, click, favorite, compare)
    Used for analytics and improving recommendations
    """
    __tablename__ = 'fact_user_interaction'

    interaction_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=True)

    # Interaction Type
    interaction_type = Column(
        String(50),
        nullable=False,
        index=True
    )  # 'view', 'click', 'favorite', 'unfavorite', 'compare', 'cart_add'

    # Context
    source = Column(String(100), nullable=True)  # 'recommendation', 'search', 'category_browse'
    session_id = Column(String(100), nullable=True, index=True)

    # Flags
    is_favorite = Column(Boolean, default=False, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='interactions')
    product = relationship('Product', back_populates='interactions')

    def __repr__(self):
        return f"<UserInteraction(user={self.user_id}, product={self.product_id}, type='{self.interaction_type}')>"

    def to_dict(self):
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'interaction_type': self.interaction_type,
            'source': self.source,
            'is_favorite': self.is_favorite,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
