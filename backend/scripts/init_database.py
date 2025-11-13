"""
Database Initialization Script
Creates all tables using SQLAlchemy create_all()
Run this instead of Alembic migrations for initial setup
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import engine, Base
from src.models import (
    User, Product, Ingredient, UserConcern, UserAllergy,
    ProductIngredient, Recommendation, UserRating, UserInteraction, DimDate
)


def init_database():
    """Create all tables in the database"""
    print("Creating all tables...")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")

        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📋 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


if __name__ == '__main__':
    init_database()
