# Quick Start: Cosmetics Analysis and Recommendation System

**Feature**: 001-cosmetics-recommendation-system
**Last Updated**: 2025-11-12

This guide helps you set up and run the cosmetics recommendation system locally in under 15 minutes.

## Prerequisites

Ensure you have the following installed:

- **Python**: 3.10+ (`python3 --version`)
- **Node.js**: 18+ (`node --version`)
- **PostgreSQL**: 13+ (`psql --version`)
- **Docker**: 20.10+ (optional, for containerized setup) (`docker --version`)
- **Git**: For version control

### Environment

- **OS**: WSL Ubuntu 20.04 (or native Linux/macOS)
- **RAM**: Minimum 4GB, recommended 8GB
- **Disk**: 2GB free space

## Quick Setup (Docker - Recommended)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd cosmetics-recommendation-system
git checkout 001-cosmetics-recommendation-system
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required environment variables**:
```bash
# Database
DATABASE_URL=postgresql://admin:password@database:5432/cosmetics_db

# JWT
JWT_SECRET_KEY=<generate-random-secret>  # openssl rand -hex 32
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days

# Flask/FastAPI
FLASK_ENV=development
DEBUG=True

# Rate Limiting
REDIS_URL=redis://redis:6379/0
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Services will be available at:
# - Backend API: http://localhost:5000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### 4. Initialize Database

```bash
# Run migrations in backend container
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python scripts/seed_data.py
```

### 5. Verify Setup

```bash
# Check backend health
curl http://localhost:5000/api/v1/health

# Expected response: {"status": "healthy"}

# Check frontend
open http://localhost:3000
```

## Manual Setup (Without Docker)

### Backend Setup

#### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies** (`requirements.txt`):
```
flask==2.3.0
flask-cors==4.0.0
flask-jwt-extended==4.5.0
flask-limiter==3.3.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.6
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
alembic==1.11.0
python-dotenv==1.0.0
```

#### 3. Setup Database

```bash
# Create database
createdb cosmetics_db

# Configure connection
export DATABASE_URL="postgresql://localhost/cosmetics_db"

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py
```

#### 4. Start Backend Server

```bash
# Development mode (Flask)
python src/app.py

# Or with FastAPI
uvicorn src.app:app --reload --port 5000
```

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

**Key dependencies** (`package.json`):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.10.0",
    "axios": "^1.3.0",
    "echarts": "^5.4.0",
    "echarts-for-react": "^3.0.0",
    "antd": "^5.4.0"
  }
}
```

#### 2. Configure API Endpoint

```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api/v1" > .env
```

#### 3. Start Development Server

```bash
npm start

# Frontend available at: http://localhost:3000
```

## First-Time Usage

### 1. Register a User

**Via cURL**:
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "SecurePass123!",
    "skin_type": "oily"
  }'
```

**Via Frontend**:
1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Fill in registration form
4. Complete skin profile questions

### 2. Login and Get Token

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "SecurePass123!"
  }'
```

**Save the `access_token` from response for subsequent requests.**

### 3. Get Recommendations

```bash
curl -X GET "http://localhost:5000/api/v1/recommendations?limit=5" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 4. Browse Products

**Via Frontend**:
- Navigate to "Products" section
- Use filters (category, price range, brand)
- Click product for detailed ingredient analysis

### 5. View Analytics Dashboard

**Via Frontend**:
- Navigate to "Analytics" section
- View trending products, user segments, ingredient popularity

## Development Workflow

### Running Tests

**Backend**:
```bash
cd backend
pytest tests/ -v --cov=src

# Specific test types
pytest tests/unit/ -v  # Unit tests
pytest tests/integration/ -v  # Integration tests
pytest tests/contract/ -v  # Contract tests
```

**Frontend**:
```bash
cd frontend
npm test

# With coverage
npm test -- --coverage
```

### Code Quality

**Backend (Python)**:
```bash
# Linting
flake8 src/ --max-line-length=100

# Formatting
black src/

# Type checking (optional)
mypy src/
```

**Frontend (JavaScript)**:
```bash
# Linting
npm run lint

# Formatting
npm run format
```

### Database Migrations

**Create migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new field to user table"
```

**Apply migration**:
```bash
alembic upgrade head
```

**Rollback**:
```bash
alembic downgrade -1
```

## Training ML Models

### Initial Model Training

```bash
cd backend

# Train recommendation model
python scripts/train_recommendation.py \
  --config config/model_config.yaml \
  --data data/processed/user_interactions.csv \
  --output models/ \
  --seed 42 \
  --cross-validate 5

# Train classification model
python scripts/train_classification.py \
  --config config/model_config.yaml \
  --data data/processed/user_profiles.csv \
  --output models/
```

**Models will be saved to**: `backend/models/` with timestamp versions

### Using Trained Models

Models are automatically loaded by the recommendation service from `models/` directory. Latest version used by default.

## Data Management

### ETL Pipeline

```bash
cd backend

# Run ETL to process raw data
python scripts/etl/run_etl.py \
  --source data/raw/products.csv \
  --destination data/processed/ \
  --validate

# Load processed data to database
python scripts/etl/load_to_warehouse.py \
  --source data/processed/products_clean.csv
```

### Seed/Test Data

```bash
# Load sample products and ingredients
python scripts/seed_data.py --sample-size 1000

# Load test users
python scripts/seed_data.py --users-only --count 100
```

## Common Issues & Solutions

### Issue: Database connection refused

**Solution**:
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Start if not running
sudo service postgresql start

# Verify connection
psql -U postgres -c "SELECT version();"
```

### Issue: Port already in use

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python src/app.py --port 5001
```

### Issue: Module not found

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: CORS errors in frontend

**Solution**:
- Verify `REACT_APP_API_URL` in `frontend/.env`
- Check Flask-CORS configuration in `backend/src/app.py`
- Ensure backend allows frontend origin:
  ```python
  CORS(app, origins=['http://localhost:3000'])
  ```

## API Documentation

### Swagger UI

Access interactive API documentation at:
- **Local**: http://localhost:5000/api/docs
- **OpenAPI spec**: http://localhost:5000/api/v1/openapi.json

### Manual Testing

Use the Swagger UI or tools like:
- **Postman**: Import OpenAPI spec from `specs/001-cosmetics-recommendation-system/contracts/api-spec.yaml`
- **Insomnia**: Similar import process
- **cURL**: See examples in contracts/README.md

## Performance Benchmarks

Expected performance on recommended hardware:

| Operation | Target | Typical |
|-----------|--------|---------|
| User registration | <500ms | 200ms |
| Login | <300ms | 150ms |
| Get recommendations | <3s | 1.5s |
| Product search | <500ms | 250ms |
| Dashboard load (100K products) | <2s | 1.2s |
| Ingredient analysis | <200ms | 100ms |

## Next Steps

1. ✅ System running locally
2. **Explore API**: Use Swagger UI to test all endpoints
3. **Load data**: Import your cosmetics product dataset
4. **Train models**: Run ML training scripts with your data
5. **Customize**: Modify recommendation algorithms based on research.md
6. **Test**: Run full test suite before deployment
7. **Deploy**: Follow deployment guide for production setup

## Additional Resources

- **Architecture**: See `cons.md` for system architecture
- **Data Model**: See `specs/001-cosmetics-recommendation-system/data-model.md`
- **API Contracts**: See `specs/001-cosmetics-recommendation-system/contracts/`
- **Research**: See `specs/001-cosmetics-recommendation-system/research.md` for algorithm references

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review constitution.md for design principles
3. Consult research.md for algorithm implementations
4. Create new issue with detailed description

---

**Quick Start Complete!** You should now have a running cosmetics recommendation system. Proceed to implementation phase following tasks.md (generated by `/speckit.tasks`).
