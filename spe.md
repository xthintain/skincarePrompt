# 化妆品分析和推荐系统 - 详细技术栈

## 技术栈概览

本项目采用全栈Python + React架构,结合现代数据科学工具和Web技术,构建高性能的化妆品分析和推荐系统。

## 一、数据处理技术栈

### 1.1 核心数据处理库

#### pandas (数据处理核心)
- **版本**: pandas >= 2.0.0
- **用途**:
  - 数据读取: `pd.read_csv()`, `pd.read_json()`, `pd.read_sql()`
  - 数据清洗: 缺失值处理(`fillna()`, `dropna()`), 重复值处理(`drop_duplicates()`)
  - 数据转换: 类型转换(`astype()`), 数据透视(`pivot_table()`)
  - 数据聚合: `groupby()`, `agg()`, `transform()`
  - 时间序列处理: `to_datetime()`, `resample()`
- **关键特性**:
  - DataFrame高效数据结构
  - 灵活的索引机制
  - 强大的数据对齐功能
  - 丰富的字符串处理方法

**代码示例**:
```python
import pandas as pd

# 数据读取与清洗
df = pd.read_csv('cosmetics_data.csv')
df.dropna(subset=['product_name', 'brand'], inplace=True)
df['price'] = df['price'].fillna(df['price'].median())

# 特征工程
df['price_category'] = pd.cut(df['price'], bins=[0, 50, 100, 500, float('inf')],
                               labels=['低价', '中价', '高价', '奢侈'])
```

#### numpy (数值计算基础)
- **版本**: numpy >= 1.24.0
- **用途**:
  - 数组运算: 向量化操作,矩阵运算
  - 数学函数: `np.mean()`, `np.std()`, `np.corrcoef()`
  - 随机数生成: `np.random` 模块
  - 线性代数: `np.linalg` 模块
- **性能优势**:
  - C语言实现,高效内存管理
  - 广播机制(Broadcasting)
  - 适合大规模数值计算

**代码示例**:
```python
import numpy as np

# 数据标准化
data = np.array(df['price'])
normalized_data = (data - np.mean(data)) / np.std(data)

# 相似度计算
cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

### 1.2 数据预处理扩展库

#### scikit-learn (预处理模块)
- **StandardScaler**: Z-score标准化
- **MinMaxScaler**: 最小-最大归一化
- **LabelEncoder**: 标签编码
- **OneHotEncoder**: 独热编码
- **PolynomialFeatures**: 多项式特征生成

**代码示例**:
```python
from sklearn.preprocessing import StandardScaler, LabelEncoder

# 数值特征标准化
scaler = StandardScaler()
df[['price', 'rating']] = scaler.fit_transform(df[['price', 'rating']])

# 分类特征编码
le = LabelEncoder()
df['brand_encoded'] = le.fit_transform(df['brand'])
```

## 二、数据存储技术栈

### 2.1 数据仓库

#### PostgreSQL (推荐)
- **版本**: PostgreSQL >= 13
- **选择理由**:
  - 强大的SQL标准支持
  - 支持复杂查询和分析
  - JSON/JSONB数据类型支持
  - 优秀的索引性能
  - 支持并行查询

**数据库连接**:
```python
import psycopg2
from sqlalchemy import create_engine

# 使用psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="cosmetics_db",
    user="username",
    password="password"
)

# 使用SQLAlchemy
engine = create_engine('postgresql://username:password@localhost:5432/cosmetics_db')
df.to_sql('products', engine, if_exists='replace', index=False)
```

#### MySQL (备选)
- **版本**: MySQL >= 8.0
- **适用场景**: 轻量级部署,兼容性要求高

### 2.2 数据库交互库

#### SQLAlchemy
- **版本**: SQLAlchemy >= 2.0
- **用途**: ORM映射,数据库连接池管理
- **优势**: 数据库无关性,支持多种数据库后端

#### psycopg2 / pymysql
- **psycopg2**: PostgreSQL专用驱动
- **pymysql**: MySQL纯Python驱动

### 2.3 数据仓库建模

#### 维度建模工具
- **dbt (data build tool)** (可选): SQL转换和建模
- **Python脚本**: 自定义ETL流程

**ETL流程示例**:
```python
import pandas as pd
from sqlalchemy import create_engine

def extract_data(source_path):
    """数据提取"""
    return pd.read_csv(source_path)

def transform_data(df):
    """数据转换"""
    df_clean = df.dropna()
    df_clean['created_date'] = pd.to_datetime(df_clean['created_date'])
    return df_clean

def load_data(df, table_name, engine):
    """数据加载"""
    df.to_sql(table_name, engine, if_exists='append', index=False)

# ETL执行
engine = create_engine('postgresql://user:pass@localhost/db')
raw_data = extract_data('data/raw_products.csv')
clean_data = transform_data(raw_data)
load_data(clean_data, 'dim_product', engine)
```

## 三、数据挖掘与机器学习技术栈

### 3.1 scikit-learn (核心ML库)

#### 版本
- **scikit-learn >= 1.3.0**

#### 3.1.1 推荐系统算法

**K近邻 (KNN)**
```python
from sklearn.neighbors import NearestNeighbors

# 基于物品的协同过滤
model = NearestNeighbors(n_neighbors=10, metric='cosine', algorithm='brute')
model.fit(item_features)

# 查找相似产品
distances, indices = model.kneighbors([target_product_features])
```

**余弦相似度**
```python
from sklearn.metrics.pairwise import cosine_similarity

# 计算用户-物品相似度矩阵
similarity_matrix = cosine_similarity(user_item_matrix)
```

**矩阵分解 (SVD)**
```python
from sklearn.decomposition import TruncatedSVD

# 潜在因子提取
svd = TruncatedSVD(n_components=50, random_state=42)
latent_features = svd.fit_transform(user_item_matrix)
```

**论文支撑**:
- Sarwar, B., et al. (2001). "Item-based collaborative filtering recommendation algorithms." WWW.
- Koren, Y., et al. (2009). "Matrix factorization techniques for recommender systems." Computer.

#### 3.1.2 聚类算法

**K-means聚类**
```python
from sklearn.cluster import KMeans

# 用户分群
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
user_clusters = kmeans.fit_predict(user_features)

# 评估聚类效果
from sklearn.metrics import silhouette_score
score = silhouette_score(user_features, user_clusters)
```

**DBSCAN密度聚类**
```python
from sklearn.cluster import DBSCAN

# 异常检测
dbscan = DBSCAN(eps=0.5, min_samples=5)
outliers = dbscan.fit_predict(product_features)
```

**层次聚类**
```python
from sklearn.cluster import AgglomerativeClustering

# 成分层次聚类
hierarchical = AgglomerativeClustering(n_clusters=None, distance_threshold=0.5)
ingredient_clusters = hierarchical.fit_predict(ingredient_features)
```

**论文支撑**:
- Arthur, D., & Vassilvitskii, S. (2007). "k-means++: The advantages of careful seeding." SODA.
- Ester, M., et al. (1996). "A density-based algorithm for discovering clusters." KDD.

#### 3.1.3 分类算法

**随机森林**
```python
from sklearn.ensemble import RandomForestClassifier

# 用户偏好预测
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf.fit(X_train, y_train)

# 特征重要性
feature_importance = rf.feature_importances_
```

**支持向量机 (SVM)**
```python
from sklearn.svm import SVC

# 皮肤类型分类
svm = SVC(kernel='rbf', C=1.0, gamma='scale')
svm.fit(X_train, y_train)
```

**逻辑回归**
```python
from sklearn.linear_model import LogisticRegression

# 购买意愿预测
lr = LogisticRegression(max_iter=1000, C=1.0)
lr.fit(X_train, y_train)
```

**论文支撑**:
- Breiman, L. (2001). "Random forests." Machine learning.
- Cortes, C., & Vapnik, V. (1995). "Support-vector networks." Machine learning.

#### 3.1.4 模型评估

**交叉验证**
```python
from sklearn.model_selection import cross_val_score, KFold

# 5折交叉验证
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=kfold, scoring='accuracy')
print(f"平均准确率: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

**评估指标**
```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, mean_squared_error)

# 分类评估
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='weighted')
recall = recall_score(y_true, y_pred, average='weighted')
f1 = f1_score(y_true, y_pred, average='weighted')

# 推荐系统评估
from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(true_ratings, predicted_ratings)
rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))
```

**论文支撑**:
- Powers, D. M. (2011). "Evaluation: from precision, recall and F-measure to ROC." Journal of Machine Learning Technologies.

#### 3.1.5 文本特征提取

**TF-IDF**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

# 产品描述/成分文本向量化
tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
text_features = tfidf.fit_transform(product_descriptions)
```

**CountVectorizer**
```python
from sklearn.feature_extraction.text import CountVectorizer

# 词频统计
vectorizer = CountVectorizer(max_features=500)
ingredient_vectors = vectorizer.fit_transform(ingredient_lists)
```

#### 3.1.6 降维算法

**PCA (主成分分析)**
```python
from sklearn.decomposition import PCA

# 特征降维
pca = PCA(n_components=0.95)  # 保留95%方差
reduced_features = pca.fit_transform(high_dim_features)
```

**t-SNE (可视化降维)**
```python
from sklearn.manifold import TSNE

# 2D可视化
tsne = TSNE(n_components=2, random_state=42)
embedded_features = tsne.fit_transform(features)
```

### 3.2 模型持久化

**joblib / pickle**
```python
import joblib

# 保存模型
joblib.dump(trained_model, 'models/recommendation_model.pkl')

# 加载模型
loaded_model = joblib.load('models/recommendation_model.pkl')
```

## 四、数据分析与可视化技术栈

### 4.1 Python可视化库

#### matplotlib
- **版本**: matplotlib >= 3.7.0
- **用途**: 基础静态图表

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.title('趋势图')
plt.savefig('output/trend.png', dpi=300)
```

#### seaborn
- **版本**: seaborn >= 0.12.0
- **用途**: 统计可视化

```python
import seaborn as sns

# 相关性热力图
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('特征相关性矩阵')

# 分布图
sns.histplot(data=df, x='price', hue='category', kde=True)
```

#### plotly
- **版本**: plotly >= 5.14.0
- **用途**: 交互式可视化

```python
import plotly.express as px

# 交互式散点图
fig = px.scatter(df, x='price', y='rating', color='brand',
                 size='popularity', hover_data=['product_name'])
fig.show()

# 3D可视化
fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster')
```

### 4.2 交互式BI工具

#### 选项1: Tableau (商业工具)
- **优势**: 强大的拖拽式分析,丰富的图表类型
- **集成**: Tableau Server / Tableau Embedded API

#### 选项2: Apache Superset (开源)
- **版本**: Apache Superset >= 2.0
- **优势**: 开源免费,Python生态集成良好
- **安装**:
```bash
pip install apache-superset
superset db upgrade
superset fab create-admin
superset init
superset run -p 8088
```

#### 选项3: Metabase (开源)
- **优势**: 简单易用,快速部署
- **特点**: SQL友好,适合非技术人员

## 五、前端技术栈

### 5.1 React核心生态

#### React
- **版本**: React >= 18.2.0
- **核心特性**:
  - Hooks: useState, useEffect, useMemo, useCallback
  - Context API: 全局状态管理
  - Concurrent Features: 并发渲染

**项目初始化**:
```bash
npx create-react-app cosmetics-dashboard --template typescript
cd cosmetics-dashboard
```

#### React Router
- **版本**: react-router-dom >= 6.10.0
- **用途**: 单页应用路由管理

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 5.2 状态管理

#### Zustand (推荐 - 轻量级)
- **版本**: zustand >= 4.3.0

```javascript
import create from 'zustand';

const useStore = create((set) => ({
  filters: {},
  setFilters: (filters) => set({ filters }),
  products: [],
  fetchProducts: async () => {
    const response = await fetch('/api/products');
    const products = await response.json();
    set({ products });
  }
}));
```

#### Redux Toolkit (备选 - 复杂应用)
- **版本**: @reduxjs/toolkit >= 1.9.0

### 5.3 数据可视化库

#### ECharts for React
- **版本**: echarts-for-react >= 3.0.0
- **特点**: 丰富的图表类型,性能优秀

```jsx
import ReactECharts from 'echarts-for-react';

function SalesChart() {
  const option = {
    title: { text: '销售趋势' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月'] },
    yAxis: { type: 'value' },
    series: [{ data: [120, 200, 150], type: 'line' }]
  };

  return <ReactECharts option={option} />;
}
```

#### Recharts (备选)
- **版本**: recharts >= 2.5.0
- **特点**: React原生组件,API友好

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function TrendChart({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

#### D3.js (高级定制)
- **版本**: d3 >= 7.8.0
- **用途**: 复杂的自定义可视化

### 5.4 UI组件库

#### Ant Design (推荐)
- **版本**: antd >= 5.4.0
- **特点**: 企业级设计,组件丰富

```jsx
import { Table, Card, Button, Select } from 'antd';

function ProductTable({ products }) {
  const columns = [
    { title: '产品名称', dataIndex: 'name', key: 'name' },
    { title: '品牌', dataIndex: 'brand', key: 'brand' },
    { title: '价格', dataIndex: 'price', key: 'price' }
  ];

  return <Table columns={columns} dataSource={products} />;
}
```

#### Material-UI (备选)
- **版本**: @mui/material >= 5.11.0

### 5.5 HTTP客户端

#### Axios
- **版本**: axios >= 1.3.0

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000
});

// 获取推荐结果
const fetchRecommendations = async (userId) => {
  const response = await api.get(`/recommendations/${userId}`);
  return response.data;
};
```

### 5.6 构建工具

#### Vite (推荐 - 快速开发)
- **版本**: vite >= 4.2.0

```bash
npm create vite@latest cosmetics-dashboard -- --template react-ts
```

#### Webpack (传统方案)
- **版本**: webpack >= 5.80.0

## 六、后端API技术栈

### 6.1 Web框架

#### Flask (推荐 - 轻量级)
- **版本**: Flask >= 2.3.0

```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 处理跨域

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    # 调用推荐模型
    recommendations = recommendation_engine.predict(user_id)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**扩展库**:
- **Flask-CORS**: 跨域处理
- **Flask-SQLAlchemy**: 数据库ORM
- **Flask-Caching**: 缓存支持
- **Flask-JWT-Extended**: JWT认证

#### FastAPI (备选 - 现代异步框架)
- **版本**: fastapi >= 0.95.0

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: int):
    recommendations = await recommendation_engine.predict(user_id)
    return recommendations
```

**优势**:
- 自动生成OpenAPI文档
- 类型检查和数据验证(Pydantic)
- 异步性能优秀

### 6.2 API文档

#### Swagger/OpenAPI
- **Flask**: Flask-RESTX / Flasgger
- **FastAPI**: 内置支持

```python
# FastAPI自动生成文档
# 访问: http://localhost:8000/docs
```

## 七、开发与部署工具

### 7.1 Python环境管理

#### virtualenv / venv
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # WSL/Linux

# 安装依赖
pip install -r requirements.txt
```

#### Conda (备选)
```bash
conda create -n cosmetics python=3.10
conda activate cosmetics
```

### 7.2 依赖管理

**requirements.txt**:
```
# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# 机器学习
scikit-learn>=1.3.0

# 数据库
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.6

# Web框架
flask>=2.3.0
flask-cors>=4.0.0

# 可视化
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0

# 工具库
joblib>=1.2.0
requests>=2.28.0
```

### 7.3 容器化部署

#### Docker
- **版本**: Docker >= 20.10

**Dockerfile (Backend)**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**Dockerfile (Frontend)**:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  database:
    image: postgres:13
    environment:
      POSTGRES_DB: cosmetics_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - database
    environment:
      DATABASE_URL: postgresql://admin:password@database:5432/cosmetics_db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 7.4 版本控制

#### Git
```bash
git init
git add .
git commit -m "Initial commit"
```

**.gitignore**:
```
# Python
__pycache__/
*.py[cod]
venv/
*.pkl

# Node
node_modules/
build/
.env

# IDEs
.vscode/
.idea/
```

### 7.5 测试框架

#### pytest (Python)
- **版本**: pytest >= 7.3.0

```python
# tests/test_recommendation.py
import pytest
from models.recommendation import RecommendationEngine

def test_recommendation_output_format():
    engine = RecommendationEngine()
    results = engine.predict(user_id=1)
    assert isinstance(results, list)
    assert len(results) > 0
```

#### Jest (JavaScript)
- **版本**: jest >= 29.5.0

```javascript
// __tests__/ProductCard.test.js
import { render, screen } from '@testing-library/react';
import ProductCard from '../components/ProductCard';

test('renders product name', () => {
  render(<ProductCard name="Test Product" />);
  const linkElement = screen.getByText(/Test Product/i);
  expect(linkElement).toBeInTheDocument();
});
```

## 八、性能优化工具

### 8.1 缓存

#### Redis (可选)
- **版本**: Redis >= 7.0
- **Python客户端**: redis-py

```python
import redis

# 连接Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 缓存推荐结果
r.setex(f'recommendations:{user_id}', 3600, json.dumps(recommendations))

# 获取缓存
cached = r.get(f'recommendations:{user_id}')
```

### 8.2 异步任务

#### Celery
- **版本**: celery >= 5.2.0
- **消息队列**: Redis / RabbitMQ

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def train_model():
    # 后台模型训练任务
    model.fit(X_train, y_train)
    joblib.dump(model, 'models/latest_model.pkl')
```

## 九、监控与日志

### 9.1 日志

#### Python logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info('推荐系统启动成功')
```

### 9.2 性能监控

#### Python性能分析
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 运行代码
recommendation_engine.predict(user_id=1)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 十、开发环境配置 (WSL Ubuntu 20.04)

### 10.1 系统依赖安装

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python开发工具
sudo apt install python3.10 python3-pip python3-venv -y

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Docker
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
```

### 10.2 项目结构

```
cosmetics-analysis-system/
├── backend/
│   ├── app.py                 # Flask应用入口
│   ├── models/                # 机器学习模型
│   │   ├── recommendation.py
│   │   ├── clustering.py
│   │   └── classification.py
│   ├── api/                   # API路由
│   │   ├── recommendations.py
│   │   └── analytics.py
│   ├── data/                  # 数据处理
│   │   ├── etl.py
│   │   └── preprocessing.py
│   ├── utils/                 # 工具函数
│   ├── tests/                 # 测试文件
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── Dashboard/
│   │   │   ├── Recommendations/
│   │   │   └── Analytics/
│   │   ├── services/          # API服务
│   │   ├── utils/             # 工具函数
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/                      # 原始数据 (用户编写)
│   ├── raw/
│   └── processed/
│
├── notebooks/                 # Jupyter笔记本
│   ├── EDA.ipynb
│   └── model_training.ipynb
│
├── models/                    # 训练好的模型文件
│   └── recommendation_model.pkl
│
├── docs/                      # 文档
│   ├── plan.md
│   ├── cons.md
│   └── spe.md
│
├── docker-compose.yml
└── README.md
```

## 技术栈总结表

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **数据处理** | pandas | >= 2.0.0 | 数据清洗、转换、分析 |
| | numpy | >= 1.24.0 | 数值计算 |
| **数据存储** | PostgreSQL | >= 13 | 关系型数据仓库 |
| | SQLAlchemy | >= 2.0.0 | ORM |
| **机器学习** | scikit-learn | >= 1.3.0 | 推荐、聚类、分类 |
| **Python可视化** | matplotlib | >= 3.7.0 | 静态图表 |
| | seaborn | >= 0.12.0 | 统计可视化 |
| | plotly | >= 5.14.0 | 交互式图表 |
| **BI工具** | Apache Superset | >= 2.0 | 交互式BI |
| **后端框架** | Flask | >= 2.3.0 | Web API |
| **前端框架** | React | >= 18.2.0 | 用户界面 |
| **前端可视化** | ECharts | >= 5.4.0 | 图表库 |
| **UI组件** | Ant Design | >= 5.4.0 | UI组件库 |
| **HTTP客户端** | Axios | >= 1.3.0 | API请求 |
| **容器化** | Docker | >= 20.10 | 应用部署 |
| **测试** | pytest | >= 7.3.0 | Python测试 |
| | Jest | >= 29.5.0 | JavaScript测试 |

## 学术论文要求

### 推荐系统论文引用
1. Sarwar et al. (2001) - 协同过滤基础理论
2. Koren et al. (2009) - 矩阵分解技术
3. He et al. (2017) - 神经协同过滤(未来优化方向)

### 评估方法论文
1. Herlocker et al. (2004) - 推荐系统评估框架
2. Shani & Gunawardana (2011) - 推荐系统评估综述

### 实验验证要求
- 至少3种算法对比实验
- 使用标准评估指标(RMSE, MAE, Precision@K, Recall@K)
- 5折交叉验证
- 统计显著性检验

## 下一步行动

1. **数据获取**: 由用户编写数据采集脚本
2. **环境搭建**: 安装所有依赖库
3. **数据预处理**: 使用pandas/numpy清洗数据
4. **模型开发**: 基于scikit-learn实现推荐算法
5. **API开发**: Flask构建RESTful API
6. **前端开发**: React + ECharts可视化大屏
7. **系统集成**: Docker部署完整系统
8. **论文撰写**: 整理实验结果和文献综述
