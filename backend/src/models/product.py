"""
Product Model
Represents cosmetic products in the system
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Product(BaseModel):
    """
    Cosmetic product model
    """
    __tablename__ = 'dim_product'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)

    # Product Information
    category = Column(
        Enum('cleanser', 'moisturizer', 'serum', 'sunscreen', 'makeup', 'treatment', 'toner',
             name='product_category_enum'),
        nullable=False,
        index=True
    )
    subcategory = Column(String(100), nullable=True)

    # Pricing
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default='USD', nullable=False)

    # Details
    description = Column(Text, nullable=True)
    size = Column(String(50), nullable=True)  # '50ml', '30g', etc.

    # Ratings and Reviews
    avg_rating = Column(Numeric(3, 2), nullable=True)  # 0.00 to 5.00
    review_count = Column(Integer, default=0, nullable=False)

    # Attributes
    is_organic = Column(Boolean, default=False, nullable=False)
    is_cruelty_free = Column(Boolean, default=False, nullable=False)
    is_vegan = Column(Boolean, default=False, nullable=False)
    is_fragrance_free = Column(Boolean, default=False, nullable=False)

    # Suitability
    suitable_for_skin_types = Column(Text, nullable=True)  # JSON string: ['oily', 'combination']
    target_concerns = Column(Text, nullable=True)  # JSON string: ['acne', 'wrinkles']

    # Availability
    is_available = Column(Boolean, default=True, nullable=False)
    external_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Relationships
    ingredients = relationship('ProductIngredient', back_populates='product', cascade='all, delete-orphan')
    ratings = relationship('UserRating', back_populates='product', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='product')
    interactions = relationship('UserInteraction', back_populates='product')

    def __repr__(self):
        return f"<Product(product_id={self.product_id}, name='{self.name}', brand='{self.brand}', category='{self.category}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'description': self.description,
            'size': self.size,
            'avg_rating': float(self.avg_rating) if self.avg_rating else None,
            'review_count': self.review_count,
            'is_organic': self.is_organic,
            'is_cruelty_free': self.is_cruelty_free,
            'is_vegan': self.is_vegan,
            'is_fragrance_free': self.is_fragrance_free,
            'is_available': self.is_available,
            'image_url': self.image_url,
        }
