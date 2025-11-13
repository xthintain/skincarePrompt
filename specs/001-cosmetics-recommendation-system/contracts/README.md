# API Contracts

This directory contains the API contract specifications for the Cosmetics Analysis and Recommendation System.

## Files

- **api-spec.yaml**: OpenAPI 3.0.3 specification defining all REST API endpoints
- **README.md**: This file

## API Overview

### Base URL

- **Development**: `http://localhost:5000/api/v1`
- **Production**: `https://api.cosmetics-recommendation.com/api/v1`

### Authentication

All endpoints except `/auth/*` require JWT Bearer token authentication.

**Authentication Flow**:
1. Register: `POST /auth/register`
2. Login: `POST /auth/login` → Receive `access_token` (15 min) and `refresh_token` (7 days)
3. Use `access_token` in `Authorization: Bearer <token>` header
4. Refresh: `POST /auth/refresh` when access token expires

### Rate Limiting

- **Unauthenticated requests**: 100 requests/hour per IP
- **Authenticated requests**: 1000 requests/hour per user
- **High-cost operations** (search, analytics): 500 requests/hour

### Versioning

- Current version: **v1**
- Future versions will be supported alongside current for 6 months
- Version specified in URL path: `/api/v1/...`, `/api/v2/...`

## API Endpoints Summary

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Authenticate and receive tokens |
| POST | `/auth/refresh` | Refresh access token |

### Recommendations (`/recommendations`)

| Method | Endpoint | Description | Spec Reference |
|--------|----------|-------------|----------------|
| GET | `/recommendations` | Get personalized product recommendations | FR-003, FR-004, FR-005, FR-006 |
| POST | `/recommendations/feedback` | Provide feedback on recommendations | FR-013 |

**Query Parameters**:
- `limit`: Number of recommendations (1-50, default 10)
- `category`: Filter by product category (FR-005)
- `min_price`, `max_price`: Price range filtering (FR-006)

**Response Time**: <3 seconds (SC-001)

### Products (`/products`)

| Method | Endpoint | Description | Spec Reference |
|--------|----------|-------------|----------------|
| GET | `/products` | Browse and search products | FR-017 |
| GET | `/products/{id}` | Get product details | FR-007 |
| GET | `/products/{id}/ingredients` | Get ingredient analysis | FR-002, FR-008 |
| POST | `/products/compare` | Compare 2-4 products | FR-009 |

**Search Capabilities** (FR-017):
- By product name
- By brand
- By ingredient

**Allergen Detection** (FR-008):
- Automatically highlights user's allergens in ingredient list
- 100% accuracy when ingredient data complete (SC-004)

### Users (`/users`)

| Method | Endpoint | Description | Spec Reference |
|--------|----------|-------------|----------------|
| GET | `/users/profile` | Get user profile | - |
| PUT | `/users/profile` | Update user profile | FR-001 |
| POST | `/users/allergies` | Add ingredient allergy | FR-001 |
| GET | `/users/favorites` | Get favorite products | FR-012 |
| POST | `/users/favorites` | Add product to favorites | FR-012 |

**Profile Fields** (FR-001):
- `skin_type`: oily, dry, combination, normal, sensitive
- `concerns`: Array of skin concerns (acne, aging, pigmentation, etc.)
- `allergies`: Array of ingredient IDs user is allergic to
- `budget_min`, `budget_max`: Price range preferences
- `preferred_brands`: Array of preferred brand names

### Analytics (`/analytics`)

| Method | Endpoint | Description | Spec Reference |
|--------|----------|-------------|----------------|
| GET | `/analytics/dashboard` | Get dashboard overview metrics | FR-011, FR-018 |

**Metrics Provided**:
- Total users, products, recommendations
- Average user satisfaction
- Popular product categories
- Trending ingredients
- User segmentation by skin type

**Performance**: Dashboard loads in <2 seconds for 100K products (SC-006)

## Request/Response Examples

### Get Personalized Recommendations

**Request**:
```http
GET /api/v1/recommendations?category=moisturizer&min_price=20&max_price=50&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "product": {
        "product_id": 123,
        "name": "Hydrating Gel Moisturizer",
        "brand": "CeraVe",
        "category": "moisturizer",
        "price": 15.99,
        "avg_rating": 4.5,
        "image_url": "https://..."
      },
      "relevance_score": 0.92,
      "confidence_score": 0.85,
      "reasoning": {
        "factors": [
          "Matches your oily skin type",
          "Contains hyaluronic acid for hydration",
          "Similar to your previously favorited products"
        ]
      }
    }
  ],
  "metadata": {
    "total": 5,
    "algorithm": "hybrid",
    "generated_at": "2025-11-12T10:30:00Z"
  }
}
```

### Get Product Ingredient Analysis

**Request**:
```http
GET /api/v1/products/123/ingredients
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
{
  "product_id": 123,
  "product_name": "Hydrating Gel Moisturizer",
  "ingredients": [
    {
      "ingredient_id": 45,
      "name": "Hyaluronic Acid",
      "function": "humectant",
      "safety_rating": 1,
      "is_allergen": false,
      "is_user_allergen": false
    },
    {
      "ingredient_id": 89,
      "name": "Fragrance",
      "function": "fragrance",
      "safety_rating": 6,
      "is_allergen": true,
      "is_user_allergen": true
    }
  ],
  "user_allergens": [
    {
      "ingredient_name": "Fragrance",
      "severity": "moderate"
    }
  ],
  "overall_safety_score": 3.2
}
```

## Error Handling

All errors follow consistent format:

```json
{
  "error": "Error message",
  "details": {
    "field": "Specific error details"
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid token
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error (includes `trace_id` for debugging)

## Testing the API

### Using Swagger UI

```bash
# Install Swagger UI (Flask example)
pip install flask-swagger-ui

# Access at: http://localhost:5000/api/docs
```

### Using cURL

**Register User**:
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "skin_type": "oily"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Get Recommendations** (using token from login):
```bash
curl -X GET http://localhost:5000/api/v1/recommendations?limit=5 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Implementation Notes

### Backend Framework Choice

- **Flask**: Mature, well-documented, extensive ecosystem
- **FastAPI**: Modern, async support, automatic OpenAPI generation

Both comply with Constitution Principle V (API-First Design).

### OpenAPI Documentation Generation

**Flask** (using Flasgger):
```python
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app, template_file='contracts/api-spec.yaml')
```

**FastAPI** (automatic):
```python
from fastapi import FastAPI

app = FastAPI(
    title="Cosmetics Recommendation API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs"
)
```

### Security Considerations

1. **HTTPS Only**: Production must use HTTPS
2. **Token Storage**: Access tokens in memory, refresh tokens in HTTP-only cookies
3. **Password Hashing**: bcrypt with cost factor 12
4. **Input Validation**: All inputs validated against schema
5. **SQL Injection**: Use parameterized queries via SQLAlchemy
6. **XSS Prevention**: Content-Type and CORS headers properly configured

### Performance Optimization

1. **Caching**: Redis cache for frequently accessed products (optional)
2. **Pagination**: Default `per_page=20`, max 100
3. **Async Operations**: Recommendation generation can be async (FastAPI)
4. **Database Indexing**: Indexes on frequently queried fields (see data-model.md)

## Compliance

- ✅ **Constitution Principle V**: RESTful design, JWT authentication, JSON responses, API versioning
- ✅ **Functional Requirements**: Maps FR-001 through FR-020 to specific endpoints
- ✅ **Success Criteria**: Response times align with SC-001, SC-006

## Next Steps

1. Review and approve API specification
2. Implement backend endpoints following this contract
3. Generate API client SDKs (optional)
4. Set up automated contract testing
5. Deploy to development environment for integration testing

---

**Status**: API contracts complete and ready for implementation
