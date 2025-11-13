"""
UserConcern Model
Many-to-many relationship between users and their skin concerns
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class UserConcern(BaseModel):
    """
    User skin concerns (acne, wrinkles, dark spots, etc.)
    """
    __tablename__ = 'user_concern'

    concern_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id', ondelete='CASCADE'), nullable=False)
    concern_type = Column(String(100), nullable=False)  # 'acne', 'wrinkles', 'dark_spots', etc.
    severity = Column(String(20), nullable=True)  # 'mild', 'moderate', 'severe'
    notes = Column(String(500), nullable=True)

    # Relationships
    user = relationship('User', back_populates='concerns')

    def __repr__(self):
        return f"<UserConcern(user_id={self.user_id}, concern='{self.concern_type}', severity='{self.severity}')>"

    def to_dict(self):
        return {
            'concern_id': self.concern_id,
            'user_id': self.user_id,
            'concern_type': self.concern_type,
            'severity': self.severity,
            'notes': self.notes,
        }
