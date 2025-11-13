"""
Products API Endpoints
Handles product listing, details, and ingredient analysis
"""
from flask import Blueprint, request, jsonify
from src.api.middleware.rate_limiter import rate_limit
from src.config import SessionLocal
from src.models import Product, ProductIngredient, Ingredient
from src.utils.errors import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['GET'])
@rate_limit(limit=200)
def list_products():
    """
    List products with pagination and filtering

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)
        category (str): Filter by category
        brand (str): Filter by brand
        min_price (float): Minimum price
        max_price (float): Maximum price
        search (str): Search in product name
        skin_type (str): Filter by suitable skin type

    Returns:
        JSON response with products list
    """
    try:
        # Pagination parameters
        page = max(request.args.get('page', 1, type=int), 1)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Filter parameters
        category = request.args.get('category')
        brand = request.args.get('brand')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        skin_type = request.args.get('skin_type')

        session = SessionLocal()

        try:
            # Build query
            query = session.query(Product).filter(Product.is_available == True)

            # Apply filters
            if category:
                query = query.filter(Product.category == category)
            if brand:
                query = query.filter(Product.brand == brand)
            if min_price is not None:
                query = query.filter(Product.price >= min_price)
            if max_price is not None:
                query = query.filter(Product.price <= max_price)
            if search:
                query = query.filter(Product.name.ilike(f'%{search}%'))
            if skin_type:
                query = query.filter(Product.suitable_for_skin_types.contains(skin_type))

            # Get total count
            total = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            products = query.offset(offset).limit(per_page).all()

            # Convert to dict
            products_list = [p.to_dict() for p in products]

            return jsonify({
                'success': True,
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'products': products_list,
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error listing products: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<int:product_id>', methods=['GET'])
@rate_limit(limit=200)
def get_product_details(product_id):
    """
    Get detailed information about a product

    Returns:
        JSON response with product details
    """
    try:
        session = SessionLocal()

        try:
            product = session.query(Product).filter(Product.product_id == product_id).first()

            if not product:
                raise NotFoundError(f"Product {product_id} not found")

            product_dict = product.to_dict()

            # Get ingredient count
            ingredient_count = session.query(ProductIngredient).filter(
                ProductIngredient.product_id == product_id
            ).count()

            product_dict['ingredient_count'] = ingredient_count

            return jsonify({
                'success': True,
                'product': product_dict,
            }), 200

        finally:
            session.close()

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting product details: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<int:product_id>/ingredients', methods=['GET'])
@rate_limit(limit=200)
def get_product_ingredients(product_id):
    """
    Get ingredient analysis for a product

    Returns:
        JSON response with ingredients and safety analysis
    """
    try:
        session = SessionLocal()

        try:
            # Check product exists
            product = session.query(Product).filter(Product.product_id == product_id).first()
            if not product:
                raise NotFoundError(f"Product {product_id} not found")

            # Get product ingredients
            product_ingredients = session.query(ProductIngredient, Ingredient).join(
                Ingredient, ProductIngredient.ingredient_id == Ingredient.ingredient_id
            ).filter(
                ProductIngredient.product_id == product_id
            ).order_by(ProductIngredient.position).all()

            # Build ingredients list
            ingredients_list = []
            total_safety_score = 0
            allergen_count = 0

            for pi, ingredient in product_ingredients:
                ingredient_dict = ingredient.to_dict()
                ingredient_dict['position'] = pi.position
                ingredient_dict['concentration'] = float(pi.concentration) if pi.concentration else None

                ingredients_list.append(ingredient_dict)

                if ingredient.safety_rating:
                    total_safety_score += ingredient.safety_rating
                if ingredient.is_common_allergen:
                    allergen_count += 1

            # Calculate overall safety
            avg_safety_rating = total_safety_score / len(ingredients_list) if ingredients_list else 0

            # Safety assessment
            if avg_safety_rating <= 3:
                safety_level = "safe"
            elif avg_safety_rating <= 5:
                safety_level = "moderate"
            else:
                safety_level = "concerning"

            return jsonify({
                'success': True,
                'product_id': product_id,
                'product_name': product.name,
                'ingredient_count': len(ingredients_list),
                'ingredients': ingredients_list,
                'safety_analysis': {
                    'average_safety_rating': round(avg_safety_rating, 2),
                    'safety_level': safety_level,
                    'allergen_count': allergen_count,
                    'has_allergens': allergen_count > 0,
                }
            }), 200

        finally:
            session.close()

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting product ingredients: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
