"""
Ingredient Model
Represents cosmetic ingredients and their properties
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Ingredient(BaseModel):
    """
    Cosmetic ingredient model with safety information
    """
    __tablename__ = 'dim_ingredient'

    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)

    # Properties
    function = Column(String(100), nullable=True)  # 'moisturizer', 'antioxidant', etc.
    description = Column(Text, nullable=True)

    # Safety Information (1-10 scale, 1=safest, 10=most dangerous)
    safety_rating = Column(Integer, nullable=True)  # Based on EWG or similar databases

    # Allergen and Sensitivity
    is_common_allergen = Column(Boolean, default=False, nullable=False)
    is_comedogenic = Column(Boolean, default=False, nullable=False)  # Blocks pores
    comedogenic_rating = Column(Integer, nullable=True)  # 0-5 scale

    # Regulatory
    is_banned_eu = Column(Boolean, default=False, nullable=False)
    is_banned_us = Column(Boolean, default=False, nullable=False)

    # Alternative Names
    synonyms = Column(Text, nullable=True)  # JSON string of alternative names
    cas_number = Column(String(50), nullable=True)  # Chemical Abstracts Service number

    # Benefits and Concerns
    benefits = Column(Text, nullable=True)  # JSON string
    concerns = Column(Text, nullable=True)  # JSON string

    # Relationships
    products = relationship('ProductIngredient', back_populates='ingredient', cascade='all, delete-orphan')
    user_allergies = relationship('UserAllergy', back_populates='ingredient', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Ingredient(ingredient_id={self.ingredient_id}, name='{self.name}', safety_rating={self.safety_rating})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ingredient_id': self.ingredient_id,
            'name': self.name,
            'function': self.function,
            'description': self.description,
            'safety_rating': self.safety_rating,
            'is_common_allergen': self.is_common_allergen,
            'is_comedogenic': self.is_comedogenic,
            'comedogenic_rating': self.comedogenic_rating,
            'is_banned_eu': self.is_banned_eu,
            'is_banned_us': self.is_banned_us,
        }
