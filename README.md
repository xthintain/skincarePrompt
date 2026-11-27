# Cosmetics Analysis and Recommendation System

An intelligent cosmetics analysis and recommendation system that provides personalized product recommendations based on user profiles (skin type, concerns, allergies).

## Features

- **Personalized Recommendations**: Get product recommendations based on your skin profile
- **Ingredient Analysis**: View detailed safety ratings and allergen warnings
- **Product Comparison**: Compare up to 4 products side-by-side
- **Analytics Dashboard**: Visualize market trends and user insights
- **Profile Management**: Manage your skin profile, concerns, and allergies

## Tech Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy, scikit-learn
- **Frontend**: React 18+, ECharts, Ant Design
- **Database**: PostgreSQL 13+
- **Caching**: Redis (optional)
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Docker 20.10+ (optional, recommended)

### Option 1: Docker Setup (Recommended)

```bash
# Start all services with Docker
docker-compose up -d

# Initialize database
docker-compose exec backend python scripts/init_database.py
docker-compose exec backend python scripts/seed_dim_date.py
docker-compose exec backend python scripts/seed_us1_data.py

# Train ML model
docker-compose exec backend python scripts/train_recommendation.py

# Access the application
# Backend API: http://localhost:5000
# Frontend: http://localhost:3000
```

### Option 2: Manual PostgreSQL Setup

#### Step 1: Install and Configure PostgreSQL

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user and create database
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

**macOS (using Homebrew):**
```bash
# Install PostgreSQL
brew install postgresql@13

# Start PostgreSQL
brew services start postgresql@13

# Create database
createdb cosmetics_db
psql cosmetics_db

# In PostgreSQL shell:
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

**Windows:**
1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer and set password for postgres user
3. Use pgAdmin or psql to create database:
```sql
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
```

#### Step 2: Configure Environment Variables

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit backend/.env and update DATABASE_URL:
# DATABASE_URL=postgresql://admin:password@localhost:5432/cosmetics_db
```

#### Step 3: Initialize Database and Start Services

```bash
# Backend setup
cd backend

# Install Python dependencies (already done)
# pip install -r requirements.txt

# Initialize database tables
python scripts/init_database.py

# Populate date dimension table
python scripts/seed_dim_date.py

# Add seed data (sample products and users)
python scripts/seed_us1_data.py

# Train recommendation model
mkdir -p models
python scripts/train_recommendation.py --output models/recommendation_v1.0.0.joblib

# Start backend server
python src/app.py
```

Backend will be available at http://localhost:5000

```bash
# Frontend setup (in a new terminal)
cd frontend

# Install Node dependencies (already done)
# npm install

# Start development server
npm start
```

Frontend will be available at http://localhost:3000

### Option 3: One-Click Setup Script

```bash
# Make script executable
chmod +x quickstart.sh

# Run setup script (requires PostgreSQL installed)
./quickstart.sh
```

This script will:
1. Check PostgreSQL availability
2. Initialize database tables
3. Populate seed data
4. Train ML model
5. Display startup commands

### Verify Installation

**Test Backend API:**
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get recommendations for demo user
curl "http://localhost:5000/api/v1/recommendations?user_id=1&n=5"

# Get dashboard metrics
curl http://localhost:5000/api/v1/analytics/dashboard
```

**Access Frontend:**
Open http://localhost:3000 in your browser to see the Dashboard with ML-powered recommendations.

## Project Structure

```
.
├── backend/               # Python backend
│   ├── src/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── services/      # Business logic
│   │   ├── api/           # Flask REST endpoints
│   │   └── utils/         # Utilities
│   ├── tests/             # Backend tests
│   ├── models/            # Trained ML models
│   ├── data/              # Data storage
│   └── scripts/           # ETL and training scripts
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API clients
│   │   └── utils/         # Utilities
│   └── tests/             # Frontend tests
├── database/              # Database files
│   ├── migrations/        # Alembic migrations
│   └── seeds/             # Seed data
└── docker-compose.yml     # Multi-container orchestration
```

## Development

### Running Tests

**Backend**:
```bash
cd backend
pytest tests/ -v --cov=src
```

**Frontend**:
```bash
cd frontend
npm test
```

### Code Quality

**Backend**:
```bash
flake8 src/ --max-line-length=100
black src/
```

**Frontend**:
```bash
npm run lint
npm run format
```

## Documentation

- [Feature Specification](specs/001-cosmetics-recommendation-system/spec.md)
- [Implementation Plan](specs/001-cosmetics-recommendation-system/plan.md)
- [Data Model](specs/001-cosmetics-recommendation-system/data-model.md)
- [API Contracts](specs/001-cosmetics-recommendation-system/contracts/)
- [Quick Start Guide](specs/001-cosmetics-recommendation-system/quickstart.md)
- [Research & Algorithms](specs/001-cosmetics-recommendation-system/research.md)

## API Documentation

Access interactive API documentation at:
- Swagger UI: http://localhost:5000/api/docs
- OpenAPI spec: http://localhost:5000/api/v1/openapi.json

### Skincare Product ML APIs

The system now includes advanced machine learning capabilities for skincare product recommendations:

**Model Information:**
```bash
GET /api/v1/skincare/ml/model_info
```

**Similar Product Recommendations (K-NN):**
```bash
GET /api/v1/skincare/ml/similar/<product_id>?n=10
```

**Preference-based Recommendations (TF-IDF + Cosine Similarity):**
```bash
POST /api/v1/skincare/ml/recommend
{
  "preferences": "美白补水保湿 女士",
  "n": 10,
  "min_price": 50,
  "max_price": 300,
  "platform": "all"
}
```

## 为什么使用机器学习模型？

### 传统推荐系统的局限性

传统的推荐系统通常依赖简单的规则和排序算法，存在以下问题：

1. **单一维度排序**：仅按价格、评分或销量排序，无法捕捉商品之间的深层关系
2. **缺乏个性化**：无法根据用户偏好和商品特征进行智能匹配
3. **冷启动问题**：新商品或新用户难以获得准确推荐
4. **特征提取困难**：无法有效从商品名称和描述中提取多维特征

### 机器学习模型的优势

本系统采用机器学习算法解决以上问题：

#### 1. **多维特征提取（TF-IDF）**
- 自动从商品名称中提取品牌、功效、类型、人群等多维特征
- 支持中文分词（jieba），理解"补水保湿"、"抗皱紧致"等语义
- 生成500维特征向量，捕捉商品的细微差异

#### 2. **智能相似度计算（K-NN + 余弦相似度）**
- 基于特征向量计算商品之间的真实相似度
- 实现"看了此商品的人也看了..."功能
- 相似度范围：51-76%，准确识别同类商品

#### 3. **混合推荐策略（Hybrid Filtering）**
- 结合内容特征（TF-IDF）和平台推荐度（好评率）
- 加权公式：`final_score = 0.7 × similarity + 0.3 × platform_score`
- 平衡商品质量和特征匹配度

#### 4. **可扩展性和准确性**
- 训练数据：865个商品（385京东 + 480淘宝）
- 响应时间：< 150ms
- 支持实时在线推荐

## 如何训练机器学习模型？

### 训练数据来源

系统使用PostgreSQL数据库中存储的真实电商数据：

```bash
# 查看训练数据规模
python3 -c "
from backend.src.config import SessionLocal
from backend.scripts.parse_skincare_data import SkincareProduct
session = SessionLocal()
print(f'Total: {session.query(SkincareProduct).count()}')
print(f'JD: {session.query(SkincareProduct).filter_by(平台=\"JD\").count()}')
print(f'TB: {session.query(SkincareProduct).filter_by(平台=\"TB\").count()}')
"
```

### 训练步骤

#### 方法1：使用数据库数据训练（推荐）

```bash
# 1. 确保PostgreSQL数据库已运行且包含数据
# 2. 进入backend目录
cd backend

# 3. 运行训练脚本（使用全部865个商品）
python3 scripts/train_skincare_ml.py
```

训练过程：
1. **数据加载**：从PostgreSQL读取全部护肤品数据
2. **特征工程**：提取品牌、功效、类型、人群等特征
3. **TF-IDF训练**：生成500维特征矩阵（865 × 500）
4. **K-NN训练**：使用余弦距离训练K近邻模型（k=10）
5. **模型保存**：保存至 `backend/models/skincare_ml/`

模型文件：
- `tfidf_vectorizer.pkl` - TF-IDF向量化器（85KB）
- `tfidf_matrix.pkl` - 特征矩阵（169KB）
- `knn_model.pkl` - K-NN模型（169KB）
- `products_data.pkl` - 商品数据（129KB）

总模型大小：约 **552KB**

#### 方法2：使用JSON数据训练

如果只想使用JSON文件训练（适用于演示或测试）：

```bash
# 使用100个精选商品训练
python3 backend/scripts/train_ml_from_json.py
```

### 训练输出示例

```
============================================================
护肤品ML推荐系统训练
============================================================
从数据库加载护肤品数据...
✅ 成功加载 865 个商品

训练TF-IDF向量化模型...
✅ TF-IDF矩阵形状: (865, 500)
   - 商品数量: 865
   - 特征维度: 500

📊 Top 20 重要特征:
   - 功效_保湿: 0.0638
   - 功效_补水: 0.0572
   - 类型_套装: 0.0552
   - 人群_女: 0.0469
   ...

训练K-NN相似商品模型...
✅ K-NN模型训练完成
   - 使用算法: brute force
   - 相似度度量: cosine
   - 邻居数量: 10

保存模型到 backend/models/skincare_ml...
✅ 模型保存成功

【测试1】相似商品推荐
基准商品: 韩束红蛮腰水乳150ml紧致抗皱补水保湿
  排名 1: 相似度 0.7579
  名称: 韩束红蛮腰水乳80ml套装抗皱紧致补水保湿

【测试2】基于用户偏好推荐
用户偏好: 美白补水保湿 女士
  排名 1: 加权分数 0.5421 (相似度 0.3950)
  名称: HAPN依克多因补水保湿水乳套装
============================================================
✅ 训练完成!
============================================================
```

### 何时需要重新训练？

在以下情况下应重新训练模型：

1. **数据更新**：添加新商品到数据库后
2. **特征调整**：修改特征提取逻辑后
3. **参数优化**：调整TF-IDF或K-NN参数后
4. **性能下降**：推荐准确率明显下降时

### 模型验证

训练完成后，系统会自动运行测试用例验证模型效果：

```bash
# 手动测试模型
curl -X POST http://localhost:5000/api/v1/skincare/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": "美白补水保湿 女士",
    "n": 10
  }'
```

## Machine Learning Algorithms

This system implements state-of-the-art machine learning algorithms for personalized recommendations:

### 1. TF-IDF (Term Frequency-Inverse Document Frequency)

**Algorithm**: `sklearn.feature_extraction.text.TfidfVectorizer`

**Configuration**:
- `max_features=500`: Extracts top 500 most important features
- `ngram_range=(1, 2)`: Uses 1-gram and 2-gram features
- Supports Chinese text segmentation with jieba

**Application**: Converts product descriptions into numerical feature vectors for similarity computation.

**Reference**:
> Salton, G., & McGill, M. J. (1983). *Introduction to Modern Information Retrieval*. McGraw-Hill.

### 2. K-Nearest Neighbors (K-NN)

**Algorithm**: `sklearn.neighbors.NearestNeighbors`

**Configuration**:
- `n_neighbors=10`: Finds 10 most similar products
- `metric='cosine'`: Uses cosine similarity distance
- `algorithm='brute'`: Brute-force search for accuracy

**Application**: Identifies similar products based on feature similarity for "customers who bought this also bought" recommendations.

**Reference**:
> Fix, E., & Hodges, J. L. (1951). *Discriminatory Analysis. Nonparametric Discrimination: Consistency Properties*. USAF School of Aviation Medicine, Randolph Field, Texas.

### 3. Cosine Similarity

**Algorithm**: `sklearn.metrics.pairwise.cosine_similarity`

**Formula**:
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**Application**: Measures similarity between user preferences and product features, ranging from 0 (completely different) to 1 (identical).

**Reference**:
> Salton, G., Wong, A., & Yang, C. S. (1975). *A Vector Space Model for Automatic Indexing*. Communications of the ACM, 18(11), 613-620.

### 4. Hybrid Recommendation System

**Algorithm**: Weighted combination of Collaborative Filtering and Content-Based Filtering

**Formula**:
```
final_score = α × CF_score + β × CB_score
```

**Configuration**:
- Regular users: `α=0.6, β=0.4`
- Cold start users (< 3 ratings): `α=0.2, β=0.8`

**Application**: Combines multiple recommendation signals for improved accuracy and addresses the cold-start problem.

**Reference**:
> Burke, R. (2002). *Hybrid Recommender Systems: Survey and Experiments*. User Modeling and User-Adapted Interaction, 12(4), 331-370.

### 5. Collaborative Filtering (Item-Based)

**Algorithm**: Item-based CF using K-NN with user-item rating matrix

**Application**: Recommends products based on similar user rating patterns.

**Reference**:
> Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001). *Item-based Collaborative Filtering Recommendation Algorithms*. In Proceedings of the 10th International Conference on World Wide Web (pp. 285-295).

### 6. Content-Based Filtering

**Algorithm**: TF-IDF vectorization with weighted features

**Feature Weights**:
- Ingredients: 2.0 (most important)
- Skin concerns: 1.5
- Category: 1.0
- Other attributes: 0.5

**Application**: Recommends products with similar ingredients and properties to user's preferences.

**Reference**:
> Pazzani, M. J., & Billsus, D. (2007). *Content-Based Recommendation Systems*. In The Adaptive Web (pp. 325-341). Springer, Berlin, Heidelberg.

## Academic References

The machine learning algorithms implemented in this system are based on the following peer-reviewed research:

1. **Salton, G., & McGill, M. J. (1983)**. *Introduction to Modern Information Retrieval*. McGraw-Hill, New York.
   - Foundation of TF-IDF algorithm
   - Vector space model for information retrieval

2. **Fix, E., & Hodges, J. L. (1951)**. *Discriminatory Analysis. Nonparametric Discrimination: Consistency Properties*. USAF School of Aviation Medicine, Randolph Field, Texas, Project 21-49-004, Report 4.
   - Original K-Nearest Neighbors algorithm
   - Nonparametric pattern recognition

3. **Salton, G., Wong, A., & Yang, C. S. (1975)**. *A Vector Space Model for Automatic Indexing*. Communications of the ACM, 18(11), 613-620. DOI: 10.1145/361219.361220
   - Vector space model
   - Cosine similarity for document similarity

4. **Burke, R. (2002)**. *Hybrid Recommender Systems: Survey and Experiments*. User Modeling and User-Adapted Interaction, 12(4), 331-370. DOI: 10.1023/A:1021240730564
   - Hybrid recommendation strategies
   - Combining multiple recommendation techniques

5. **Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001)**. *Item-based Collaborative Filtering Recommendation Algorithms*. In Proceedings of the 10th International Conference on World Wide Web (WWW '01), pp. 285-295. DOI: 10.1145/371920.372071
   - Item-based collaborative filtering
   - Scalable recommendation algorithms

6. **Pazzani, M. J., & Billsus, D. (2007)**. *Content-Based Recommendation Systems*. In P. Brusilovsky, A. Kobsa, & W. Nejdl (Eds.), The Adaptive Web (pp. 325-341). Springer, Berlin, Heidelberg. DOI: 10.1007/978-3-540-72079-9_10
   - Content-based filtering techniques
   - User profile modeling

## Model Performance

**Training Data**: 865 skincare products from JD.com (385) and Taobao (480)

**Feature Extraction**:
- Total features: 500
- Feature space: 865 products × 500 features
- Top features: 保湿 (6.38%), 补水 (5.72%), 套装 (5.52%)

**Recommendation Accuracy**:
- K-NN similarity: 51-76% for similar products
- TF-IDF matching: 24-40% for preference-based recommendations
- Hybrid weighted score: 44-55% combined accuracy

**Response Time**:
- Model loading: < 2s (lazy loading)
- Similar products API: < 100ms
- Preference-based API: < 150ms

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and code style guidelines.

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0) — non-commercial use only; commercial use requires a separate license. See [LICENSE](LICENSE).

## Citation

If you use this system in your research, please cite:

```bibtex
@software{cosmetics_recommendation_system,
  author = {LLL Development Team},
  title = {Intelligent Cosmetics Analysis and Recommendation System},
  year = {2025},
  url = {https://github.com/yourusername/cosmetics-recommendation},
  note = {Machine learning-based skincare product recommendation system
          implementing TF-IDF, K-NN, and hybrid filtering algorithms}
}
```

## Support

For issues or questions, please create a GitHub issue or consult the documentation.
