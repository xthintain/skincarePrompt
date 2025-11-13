"""
ProductIngredient Model
Many-to-many relationship between products and their ingredients
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class ProductIngredient(BaseModel):
    """
    Association between products and ingredients with concentration info
    """
    __tablename__ = 'product_ingredient'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('dim_product.product_id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('dim_ingredient.ingredient_id', ondelete='CASCADE'), nullable=False)

    # Ingredient details in product
    concentration = Column(Numeric(5, 2), nullable=True)  # Percentage (0.00 to 100.00)
    position = Column(Integer, nullable=True)  # Position in ingredient list (1=highest concentration)
    function_in_product = Column(String(100), nullable=True)  # Specific function in this product

    # Relationships
    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='products')

    def __repr__(self):
        return f"<ProductIngredient(product_id={self.product_id}, ingredient_id={self.ingredient_id}, position={self.position})>"

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'ingredient_id': self.ingredient_id,
            'concentration': float(self.concentration) if self.concentration else None,
            'position': self.position,
            'function_in_product': self.function_in_product,
        }
