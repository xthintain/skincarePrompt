"""
Base SQLAlchemy Model
Provides common fields and methods for all models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from src.config import Base


class BaseModel(Base):
    """
    Base model with common fields
    All models should inherit from this class
    """
    __abstract__ = True

    # Note: Primary key should be defined in each subclass
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        """String representation of model"""
        # Get the primary key column name dynamically
        pk_cols = [col.name for col in self.__table__.primary_key.columns]
        pk_val = getattr(self, pk_cols[0]) if pk_cols else 'N/A'
        return f"<{self.__class__.__name__}({pk_cols[0] if pk_cols else 'pk'}={pk_val})>"
