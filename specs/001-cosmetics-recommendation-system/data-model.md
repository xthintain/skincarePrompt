# Data Model: Cosmetics Analysis and Recommendation System

**Feature**: 001-cosmetics-recommendation-system
**Date**: 2025-11-12
**Database**: PostgreSQL 13+ with SQLAlchemy ORM
**Schema Design**: Star schema for data warehouse (per Constitution Principle I)

## Overview

This data model implements a star schema design optimized for recommendation analytics and product analysis. The model supports the 6 key entities identified in the feature specification with additional supporting entities for data warehouse functionality.

## Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   dim_date      │         │   dim_ingredient │         │    dim_user     │
│                 │         │                  │         │                 │
│ • date_id (PK)  │         │ • ingredient_id  │         │ • user_id (PK)  │
│ • date          │         │ • name           │         │ • username      │
│ • year          │         │ • function       │         │ • email         │
│ • month         │         │ • safety_rating  │         │ • password_hash │
│ • quarter       │         │ • is_allergen    │         │ • skin_type     │
└────────┬────────┘         └────────┬─────────┘         └────────┬────────┘
         │                           │                            │
         │                           │                            │
         │            ┌──────────────┴──────────────┐            │
         │            │      dim_product            │            │
         │            │                             │            │
         │            │ • product_id (PK)           │            │
         │            │ • name                      │            │
         │            │ • brand                     │            │
         │            │ • category                  │            │
         │            │ • price                     │            │
         │            │ • description               │            │
         │            │ • avg_rating                │            │
         └────────────┤                             ├────────────┘
                      └──────────────┬──────────────┘
                                     │
                                     │
                      ┌──────────────┴──────────────┐
                      │   fact_user_interaction    │  (Fact Table)
                      │                             │
                      │ • interaction_id (PK)       │
                      │ • user_id (FK)              │
                      │ • product_id (FK)           │
                      │ • date_id (FK)              │
                      │ • interaction_type          │
                      │ • rating                    │
                      │ • is_favorite               │
                      │ • timestamp                 │
                      └──────────────┬──────────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │    fact_recommendation     │  (Fact Table)
                      │                             │
                      │ • recommendation_id (PK)    │
                      │ • user_id (FK)              │
                      │ • product_id (FK)           │
                      │ • date_id (FK)              │
                      │ • relevance_score           │
                      │ • algorithm_used            │
                      │ • confidence_score          │
                      │ • reasoning                 │
                      └─────────────────────────────┘

┌─────────────────────────┐         ┌─────────────────────────┐
│ product_ingredient      │         │    user_rating         │
│ (Many-to-Many)          │         │                        │
│ • product_id (FK)       │         │ • rating_id (PK)       │
│ • ingredient_id (FK)    │         │ • user_id (FK)         │
│ • concentration         │         │ • product_id (FK)      │
└─────────────────────────┘         │ • rating               │
                                    │ • review_text          │
                                    │ • skin_type_at_review  │
                                    │ • created_at           │
                                    └─────────────────────────┘
```

## Core Entities

### 1. User Profile (dim_user)

**Purpose**: Represents system users with skin profile and preferences

**Fields**:
```python
class User(Base):
    __tablename__ = 'dim_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt

    # Profile Information
    skin_type = Column(Enum('oily', 'dry', 'combination', 'normal', 'sensitive'), nullable=True)
    age_range = Column(String(20), nullable=True)  # '18-24', '25-34', etc.
    location = Column(String(100), nullable=True)

    # Preferences
    budget_min = Column(Numeric(10, 2), nullable=True)
    budget_max = Column(Numeric(10, 2), nullable=True)
    preferred_brands = Column(ARRAY(String), nullable=True)  # PostgreSQL array

    # Concerns (many-to-many through separate table)
    # Stored as: ['acne', 'aging', 'pigmentation', 'redness']

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    ratings = relationship('UserRating', back_populates='user')
    interactions = relationship('UserInteraction', back_populates='user')
    recommendations = relationship('Recommendation', back_populates='user')
    allergies = relationship('UserAllergy', back_populates='user')
    concerns = relationship('UserConcern', back_populates='user')
```

**Validation Rules**:
- `username`: 3-50 characters, alphanumeric + underscore
- `email`: Valid email format (RFC 5322)
- `password_hash`: bcrypt with cost factor 12
- `skin_type`: Must be one of enum values
- `budget_min` < `budget_max` (if both specified)

**Indexes**:
- Primary: `user_id`
- Unique: `username`, `email`
- Non-unique: `skin_type` (for segmentation queries)

### 2. Product (dim_product)

**Purpose**: Represents cosmetics products with attributes and aggregated metrics

**Fields**:
```python
class Product(Base):
    __tablename__ = 'dim_product'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(Enum('cleanser', 'moisturizer', 'serum', 'sunscreen', 'makeup', 'other'), nullable=False)

    # Product Details
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    product_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Aggregated Metrics (denormalized for performance)
    avg_rating = Column(Numeric(3, 2), nullable=True)  # 0.00 - 5.00
    rating_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)

    # Data Quality
    is_complete = Column(Boolean, default=False)  # Has full ingredient list
    data_source = Column(String(100), nullable=True)
    last_verified = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredients = relationship('ProductIngredient', back_populates='product')
    ratings = relationship('UserRating', back_populates='product')
    interactions = relationship('UserInteraction', back_populates='product')
    recommendations = relationship('Recommendation', back_populates='product')
```

**Validation Rules**:
- `name`: 1-255 characters, not empty
- `price`: > 0, <= 10000
- `avg_rating`: 0.00 - 5.00 (if not null)
- `category`: Must be valid enum value

**Indexes**:
- Primary: `product_id`
- Non-unique: `brand`, `category`, `price` (for filtering)
- Composite: (`category`, `price`) for category-filtered searches

### 3. Ingredient (dim_ingredient)

**Purpose**: Represents cosmetic ingredients with safety and function data

**Fields**:
```python
class Ingredient(Base):
    __tablename__ = 'dim_ingredient'

    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    inci_name = Column(String(255), nullable=True)  # International Nomenclature

    # Classification
    function = Column(Enum(
        'moisturizer', 'emollient', 'humectant', 'preservative',
        'fragrance', 'surfactant', 'emulsifier', 'antioxidant',
        'uv_filter', 'colorant', 'other'
    ), nullable=False)

    # Safety Information
    safety_rating = Column(Integer, nullable=True)  # 1 (safest) - 10 (hazardous)
    is_common_allergen = Column(Boolean, default=False)
    is_pregnancy_safe = Column(Boolean, default=True)
    comedogenic_rating = Column(Integer, nullable=True)  # 0 (non) - 5 (highly)

    # Regulatory Status
    is_banned_eu = Column(Boolean, default=False)
    is_banned_us = Column(Boolean, default=False)

    # Metadata
    description = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship('ProductIngredient', back_populates='ingredient')
```

**Validation Rules**:
- `name`: Unique, non-empty
- `safety_rating`: 1-10 (if not null)
- `comedogenic_rating`: 0-5 (if not null)

**Indexes**:
- Primary: `ingredient_id`
- Unique: `name`
- Non-unique: `function`, `is_common_allergen` (for filtering)

### 4. User Rating (user_rating)

**Purpose**: User feedback on products including ratings and reviews

**Fields**:
```python
class UserRating(Base):
    __tablename__ = 'user_rating'

    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False)

    # Rating Information
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    skin_type_at_review = Column(String(20), nullable=True)  # Snapshot
    concerns_at_review = Column(ARRAY(String), nullable=True)  # Snapshot

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified_purchase = Column(Boolean, default=False)
    helpfulness_score = Column(Integer, default=0)  # Upvotes

    # Relationships
    user = relationship('User', back_populates='ratings')
    product = relationship('Product', back_populates='ratings')
```

**Validation Rules**:
- `rating`: 1-5 (integer)
- Unique constraint: (`user_id`, `product_id`) - one rating per user per product

**Indexes**:
- Primary: `rating_id`
- Composite: (`user_id`, `product_id`) unique
- Non-unique: `product_id`, `created_at` (for recent reviews)

### 5. Recommendation (fact_recommendation)

**Purpose**: Generated product recommendations with reasoning (Fact Table)

**Fields**:
```python
class Recommendation(Base):
    __tablename__ = 'fact_recommendation'

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False)

    # Recommendation Details
    relevance_score = Column(Numeric(5, 4), nullable=False)  # 0.0000 - 1.0000
    confidence_score = Column(Numeric(5, 4), nullable=True)
    algorithm_used = Column(Enum(
        'collaborative_filtering', 'content_based', 'hybrid', 'popular'
    ), nullable=False)
    reasoning = Column(JSONB, nullable=True)  # {"factors": ["matches skin type", "similar to favorites"]}

    # Feedback
    was_clicked = Column(Boolean, default=False)
    was_useful = Column(Boolean, nullable=True)  # User feedback
    user_feedback = Column(String(20), nullable=True)  # 'helpful', 'not_helpful'

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship('User', back_populates='recommendations')
    product = relationship('Product', back_populates='recommendations')
    date = relationship('Date', back_populates='recommendations')
```

**Validation Rules**:
- `relevance_score`: 0.0 - 1.0
- `confidence_score`: 0.0 - 1.0 (if not null)
- `algorithm_used`: Valid enum value

**Indexes**:
- Primary: `recommendation_id`
- Composite: (`user_id`, `created_at` DESC) for user history
- Non-unique: `product_id`, `date_id` (for analytics)

### 6. User Interaction (fact_user_interaction)

**Purpose**: Tracks user engagement for analytics (Fact Table)

**Fields**:
```python
class UserInteraction(Base):
    __tablename__ = 'fact_user_interaction'

    interaction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('dim_product.product_id'), nullable=False)
    date_id = Column(Integer, ForeignKey('dim_date.date_id'), nullable=False)

    # Interaction Details
    interaction_type = Column(Enum('view', 'click', 'favorite', 'compare', 'search'), nullable=False)
    is_favorite = Column(Boolean, default=False)
    session_id = Column(String(100), nullable=True)  # For session tracking

    # Context
    source_page = Column(String(100), nullable=True)  # 'dashboard', 'search', 'recommendations'
    referrer_recommendation_id = Column(Integer, nullable=True)  # If from recommendation

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship('User', back_populates='interactions')
    product = relationship('Product', back_populates='interactions')
    date = relationship('Date', back_populates='interactions')
```

**Indexes**:
- Primary: `interaction_id`
- Composite: (`user_id`, `timestamp` DESC) for user activity
- Composite: (`product_id`, `interaction_type`) for product analytics

## Supporting Entities

### 7. Date Dimension (dim_date)

**Purpose**: Time dimension for data warehouse queries

```python
class Date(Base):
    __tablename__ = 'dim_date'

    date_id = Column(Integer, primary_key=True)  # YYYYMMDD format
    date = Column(Date, unique=True, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)  # 1-4
    month = Column(Integer, nullable=False)  # 1-12
    month_name = Column(String(10), nullable=False)
    week = Column(Integer, nullable=False)  # Week of year
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1 (Monday) - 7 (Sunday)
    day_name = Column(String(10), nullable=False)
    is_weekend = Column(Boolean, nullable=False)

    # Relationships
    interactions = relationship('UserInteraction', back_populates='date')
    recommendations = relationship('Recommendation', back_populates='date')
```

### 8. Product-Ingredient Mapping (product_ingredient)

**Purpose**: Many-to-many relationship with concentration data

```python
class ProductIngredient(Base):
    __tablename__ = 'product_ingredient'

    product_id = Column(Integer, ForeignKey('dim_product.product_id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('dim_ingredient.ingredient_id'), primary_key=True)

    # Additional Data
    concentration = Column(String(50), nullable=True)  # '5%', '< 1%', 'trace'
    position_in_list = Column(Integer, nullable=True)  # Order in ingredient list (1-based)

    # Relationships
    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='products')
```

### 9. User Allergy Mapping (user_allergy)

**Purpose**: Tracks user-specified ingredient allergies

```python
class UserAllergy(Base):
    __tablename__ = 'user_allergy'

    user_id = Column(Integer, ForeignKey('dim_user.user_id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('dim_ingredient.ingredient_id'), primary_key=True)

    severity = Column(Enum('mild', 'moderate', 'severe'), default='moderate')
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='allergies')
    ingredient = relationship('Ingredient')
```

### 10. User Concern Mapping (user_concern)

**Purpose**: User-specified skin concerns

```python
class UserConcern(Base):
    __tablename__ = 'user_concern'

    user_concern_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_user.user_id'), nullable=False)
    concern = Column(Enum(
        'acne', 'aging', 'pigmentation', 'redness', 'dryness',
        'oiliness', 'sensitivity', 'dark_circles', 'pores', 'other'
    ), nullable=False)
    severity = Column(Integer, nullable=True)  # 1 (mild) - 5 (severe)
    priority = Column(Integer, nullable=True)  # 1 (highest) - N

    # Relationships
    user = relationship('User', back_populates='concerns')
```

## Data Validation Rules

### Global Constraints

1. **Referential Integrity**: All foreign keys must reference existing records
2. **Cascade Deletes**: User deletion cascades to interactions/ratings/recommendations
3. **Soft Deletes**: Products marked as inactive rather than deleted
4. **Audit Trail**: All tables have `created_at` and `updated_at` timestamps

### Business Rules

1. **Allergen Detection** (FR-004): 100% accuracy requirement
   - Query: `SELECT i.* FROM user_allergy ua JOIN product_ingredient pi ON ua.ingredient_id = pi.ingredient_id WHERE ua.user_id = ? AND pi.product_id = ?`

2. **Rating Aggregation**: `avg_rating` updated via trigger on `user_rating` insert/update

3. **Data Completeness**: Products with `is_complete = FALSE` excluded from safety analysis (FR-002)

## State Transitions

### User Profile States

```
NEW → ACTIVE → INACTIVE (no transitions to DELETED for compliance)
       ↓
   SUSPENDED (admin action)
       ↓
   ACTIVE (appeal)
```

### Product Data Quality States

```
INCOMPLETE (is_complete=FALSE) → VERIFIED (is_complete=TRUE, last_verified set)
                                     ↓
                                 STALE (last_verified > 6 months ago)
                                     ↓
                                 RE-VERIFIED
```

## Performance Optimization

### Denormalization Strategy

1. **Product aggregates**: `avg_rating`, `rating_count`, `view_count` stored in `dim_product`
2. **Snapshot data**: `skin_type_at_review` in `user_rating` for historical accuracy

### Indexing Strategy

**Critical Queries**:
1. User profile lookup: Index on `username`, `email`
2. Product search by category/price: Composite index (`category`, `price`)
3. Ingredient safety check: Index on `is_common_allergen`
4. User interaction history: Composite index (`user_id`, `timestamp DESC`)
5. Recommendation retrieval: Composite index (`user_id`, `created_at DESC`)

### Partitioning (Future)

For scale >1M records:
- `fact_user_interaction`: Partition by `timestamp` (monthly)
- `fact_recommendation`: Partition by `date_id` (quarterly)

## Migration Strategy

**Initial Schema**: Alembic migrations for reproducible setup

```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

**Seed Data**: Populate `dim_date` for 10 years (past 5 + future 5)

## Compliance with Constitution

- ✅ **Principle I (Data-Driven Architecture)**: Star schema with clear fact/dimension separation
- ✅ **Principle II (Layered System Design)**: Models in Data Layer, no business logic in ORM
- ✅ **Principle IV (Model Reproducibility)**: All transformations reversible via timestamps
- ✅ **Quality Assurance**: Data quality flags (`is_complete`, `last_verified`)

---

**Status**: Data model complete and ready for API contract design
