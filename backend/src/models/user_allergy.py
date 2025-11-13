"""
UserAllergy Model
Many-to-many relationship between users and ingredients they're allergic to
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class UserAllergy(BaseModel):
    """
    User allergies to specific ingredients
    """
    __tablename__ = 'user_allergy'

    allergy_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('dim_ingredient.ingredient_id', ondelete='CASCADE'), nullable=False)

    severity = Column(String(20), nullable=True)  # 'mild', 'moderate', 'severe'
    reaction = Column(String(200), nullable=True)  # Description of allergic reaction
    verified = Column(String(20), default='self_reported')  # 'self_reported', 'doctor_confirmed'

    # Relationships
    user = relationship('User', back_populates='allergies')
    ingredient = relationship('Ingredient', back_populates='user_allergies')

    def __repr__(self):
        return f"<UserAllergy(user_id={self.user_id}, ingredient_id={self.ingredient_id}, severity='{self.severity}')>"

    def to_dict(self):
        return {
            'allergy_id': self.allergy_id,
            'user_id': self.user_id,
            'ingredient_id': self.ingredient_id,
            'severity': self.severity,
            'reaction': self.reaction,
            'verified': self.verified,
        }
