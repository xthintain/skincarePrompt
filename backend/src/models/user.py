"""
User Model
Represents users in the cosmetics recommendation system
"""
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class User(BaseModel):
    """
    User profile model with skin information and preferences
    """
    __tablename__ = 'dim_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Skin Profile
    skin_type = Column(
        Enum('oily', 'dry', 'combination', 'normal', 'sensitive', name='skin_type_enum'),
        nullable=True
    )
    age_range = Column(String(20), nullable=True)  # '18-24', '25-34', etc.
    location = Column(String(100), nullable=True)

    # Preferences
    budget_range = Column(String(50), nullable=True)  # 'under_30', '30_50', etc.
    preferred_brands = Column(Text, nullable=True)  # JSON string of brand list
    avoid_ingredients = Column(Text, nullable=True)  # JSON string of ingredient list

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    concerns = relationship('UserConcern', back_populates='user', cascade='all, delete-orphan')
    allergies = relationship('UserAllergy', back_populates='user', cascade='all, delete-orphan')
    ratings = relationship('UserRating', back_populates='user', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='user')
    interactions = relationship('UserInteraction', back_populates='user')

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', skin_type='{self.skin_type}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'skin_type': self.skin_type,
            'age_range': self.age_range,
            'location': self.location,
            'budget_range': self.budget_range,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
