"""
Models Package
Import all models for Alembic autogenerate to detect
"""
from src.models.base import BaseModel
from src.models.user import User
from src.models.product import Product
from src.models.ingredient import Ingredient
from src.models.user_concern import UserConcern
from src.models.user_allergy import UserAllergy
from src.models.product_ingredient import ProductIngredient
from src.models.recommendation import Recommendation
from src.models.user_rating import UserRating
from src.models.user_interaction import UserInteraction

# Import DimDate from seed script
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scripts.seed_dim_date import DimDate

__all__ = [
    'BaseModel',
    'User',
    'Product',
    'Ingredient',
    'UserConcern',
    'UserAllergy',
    'ProductIngredient',
    'Recommendation',
    'UserRating',
    'UserInteraction',
    'DimDate',
]
