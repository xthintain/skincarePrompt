"""
Seed Data Script for User Story 1 (MVP)
Creates sample users, products, ingredients for testing the recommendation system
"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import SessionLocal
from src.models import (
    User, Product, Ingredient, UserConcern, UserAllergy,
    ProductIngredient, Recommendation, UserRating, UserInteraction
)


def create_demo_users(session):
    """Create demo users with different skin types"""
    print("Creating demo users...")

    users = [
        User(
            user_id=1,
            username="demo_oily",
            email="oily@demo.com",
            password_hash="$2b$12$demo_hash_only_for_testing",  # In production, use bcrypt
            skin_type="oily",
            age_range="25-34",
            budget_range="30-50",
            is_active=True,
        ),
        User(
            user_id=2,
            username="demo_dry",
            email="dry@demo.com",
            password_hash="$2b$12$demo_hash_only_for_testing",
            skin_type="dry",
            age_range="35-44",
            budget_range="50-100",
            is_active=True,
        ),
        User(
            user_id=3,
            username="demo_sensitive",
            email="sensitive@demo.com",
            password_hash="$2b$12$demo_hash_only_for_testing",
            skin_type="sensitive",
            age_range="18-24",
            budget_range="under-30",
            is_active=True,
        ),
    ]

    for user in users:
        session.merge(user)  # Use merge to handle existing users
    session.commit()

    print(f"✅ Created {len(users)} demo users")
    return users


def create_demo_ingredients(session):
    """Create common cosmetic ingredients"""
    print("Creating demo ingredients...")

    ingredients = [
        Ingredient(
            ingredient_id=1,
            name="Hyaluronic Acid",
            function="Moisturizer",
            description="Hydrates and plumps skin",
            safety_rating=1,
            is_common_allergen=False,
            is_comedogenic=False,
            comedogenic_rating=0,
        ),
        Ingredient(
            ingredient_id=2,
            name="Niacinamide",
            function="Antioxidant",
            description="Reduces pore appearance and evens skin tone",
            safety_rating=1,
            is_common_allergen=False,
            is_comedogenic=False,
            comedogenic_rating=0,
        ),
        Ingredient(
            ingredient_id=3,
            name="Salicylic Acid",
            function="Exfoliant",
            description="BHA for acne treatment",
            safety_rating=2,
            is_common_allergen=False,
            is_comedogenic=False,
            comedogenic_rating=0,
        ),
        Ingredient(
            ingredient_id=4,
            name="Retinol",
            function="Anti-aging",
            description="Reduces wrinkles and fine lines",
            safety_rating=3,
            is_common_allergen=False,
            is_comedogenic=False,
            comedogenic_rating=0,
        ),
        Ingredient(
            ingredient_id=5,
            name="Fragrance",
            function="Scent",
            description="Adds pleasant scent",
            safety_rating=7,
            is_common_allergen=True,
            is_comedogenic=False,
            comedogenic_rating=0,
        ),
    ]

    for ingredient in ingredients:
        session.merge(ingredient)
    session.commit()

    print(f"✅ Created {len(ingredients)} ingredients")
    return ingredients


def create_demo_products(session):
    """Create sample products"""
    print("Creating demo products...")

    products = [
        Product(
            product_id=1,
            name="Hydrating Face Cleanser",
            brand="CeraVe",
            category="cleanser",
            price=12.99,
            description="Gentle cleanser for all skin types",
            avg_rating=4.5,
            review_count=1250,
            suitable_for_skin_types=json.dumps(["dry", "normal", "sensitive"]),
            is_fragrance_free=True,
        ),
        Product(
            product_id=2,
            name="Oil Control Toner",
            brand="Paula's Choice",
            category="toner",
            price=29.99,
            description="2% BHA for oily and acne-prone skin",
            avg_rating=4.7,
            review_count=3400,
            suitable_for_skin_types=json.dumps(["oily", "combination"]),
            target_concerns=json.dumps(["acne", "pores"]),
            is_fragrance_free=True,
        ),
        Product(
            product_id=3,
            name="Niacinamide Serum 10%",
            brand="The Ordinary",
            category="serum",
            price=5.99,
            description="High-strength vitamin and mineral blemish formula",
            avg_rating=4.3,
            review_count=8900,
            suitable_for_skin_types=json.dumps(["oily", "combination", "normal"]),
            target_concerns=json.dumps(["pores", "uneven tone"]),
            is_fragrance_free=True,
        ),
        Product(
            product_id=4,
            name="Moisturizing Cream",
            brand="Neutrogena",
            category="moisturizer",
            price=15.99,
            description="Hydro Boost Water Gel",
            avg_rating=4.4,
            review_count=2100,
            suitable_for_skin_types=json.dumps(["dry", "normal"]),
            is_fragrance_free=False,
        ),
        Product(
            product_id=5,
            name="SPF 50+ Sunscreen",
            brand="La Roche-Posay",
            category="sunscreen",
            price=33.99,
            description="Anthelios Ultra-Light Fluid",
            avg_rating=4.6,
            review_count=1800,
            suitable_for_skin_types=json.dumps(["all"]),
            is_fragrance_free=True,
        ),
    ]

    for product in products:
        session.merge(product)
    session.commit()

    print(f"✅ Created {len(products)} products")
    return products


def create_product_ingredients(session):
    """Link products with ingredients"""
    print("Creating product-ingredient relationships...")

    relationships = [
        # Product 1: Hydrating Cleanser
        ProductIngredient(product_id=1, ingredient_id=1, position=3, concentration=0.5),  # Hyaluronic Acid
        ProductIngredient(product_id=1, ingredient_id=2, position=5, concentration=0.2),  # Niacinamide

        # Product 2: Oil Control Toner
        ProductIngredient(product_id=2, ingredient_id=3, position=1, concentration=2.0),  # Salicylic Acid

        # Product 3: Niacinamide Serum
        ProductIngredient(product_id=3, ingredient_id=2, position=1, concentration=10.0),  # Niacinamide

        # Product 4: Moisturizing Cream
        ProductIngredient(product_id=4, ingredient_id=1, position=2, concentration=1.0),  # Hyaluronic Acid
        ProductIngredient(product_id=4, ingredient_id=5, position=8, concentration=0.1),  # Fragrance

        # Product 5: Sunscreen
        ProductIngredient(product_id=5, ingredient_id=1, position=4, concentration=0.3),  # Hyaluronic Acid
    ]

    for rel in relationships:
        session.merge(rel)
    session.commit()

    print(f"✅ Created {len(relationships)} product-ingredient links")


def create_user_concerns(session):
    """Add user concerns"""
    print("Creating user concerns...")

    concerns = [
        UserConcern(user_id=1, concern_type="acne", severity="moderate"),
        UserConcern(user_id=1, concern_type="pores", severity="mild"),
        UserConcern(user_id=2, concern_type="wrinkles", severity="moderate"),
        UserConcern(user_id=2, concern_type="dryness", severity="severe"),
        UserConcern(user_id=3, concern_type="redness", severity="moderate"),
    ]

    for concern in concerns:
        session.add(concern)
    session.commit()

    print(f"✅ Created {len(concerns)} user concerns")


def create_sample_ratings(session):
    """Create some sample ratings"""
    print("Creating sample ratings...")

    ratings = [
        UserRating(
            user_id=1,
            product_id=2,
            rating=5.0,
            review_text="Great for oily skin! Reduced my breakouts.",
            skin_type_at_review="oily",
            reviewed_at=datetime.utcnow() - timedelta(days=30),
        ),
        UserRating(
            user_id=1,
            product_id=3,
            rating=4.5,
            review_text="Really helps with pores.",
            skin_type_at_review="oily",
            reviewed_at=datetime.utcnow() - timedelta(days=15),
        ),
        UserRating(
            user_id=2,
            product_id=1,
            rating=4.8,
            review_text="Very gentle and hydrating.",
            skin_type_at_review="dry",
            reviewed_at=datetime.utcnow() - timedelta(days=20),
        ),
    ]

    for rating in ratings:
        session.add(rating)
    session.commit()

    print(f"✅ Created {len(ratings)} sample ratings")


def seed_us1_data():
    """Main seeding function"""
    session = SessionLocal()

    try:
        print("\n🌱 Seeding User Story 1 data...\n")

        create_demo_users(session)
        create_demo_ingredients(session)
        create_demo_products(session)
        create_product_ingredients(session)
        create_user_concerns(session)
        create_sample_ratings(session)

        print("\n✅ Seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"  Users: {session.query(User).count()}")
        print(f"  Products: {session.query(Product).count()}")
        print(f"  Ingredients: {session.query(Ingredient).count()}")
        print(f"  Product-Ingredients: {session.query(ProductIngredient).count()}")
        print(f"  User Concerns: {session.query(UserConcern).count()}")
        print(f"  Ratings: {session.query(UserRating).count()}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    seed_us1_data()
