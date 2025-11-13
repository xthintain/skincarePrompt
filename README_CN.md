# 护肤品智能分析与推荐系统

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于机器学习的智能护肤品分析与推荐系统，为用户提供个性化的产品推荐和全面的数据分析。

[功能特性](#功能特性) • [技术栈](#技术栈) • [快速开始](#快速开始) • [API文档](#api文档) • [模型训练](#如何训练机器学习模型)

</div>

---

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
  - [前置要求](#前置要求)
  - [安装步骤](#安装步骤)
  - [启动服务](#启动服务)
- [项目结构](#项目结构)
- [核心功能](#核心功能)
  - [智能推荐系统](#智能推荐系统)
  - [数据分析](#数据分析)
  - [推荐报告生成](#推荐报告生成)
- [API文档](#api文档)
- [机器学习模型](#机器学习模型)
  - [为什么使用机器学习](#为什么使用机器学习)
  - [如何训练模型](#如何训练机器学习模型)
  - [模型性能](#模型性能)
- [开发指南](#开发指南)
- [部署](#部署)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 功能特性

### 🎯 核心功能

- **智能推荐引擎**
  - 基于TF-IDF和K-NN算法的相似商品推荐
  - 基于用户偏好的个性化推荐
  - 混合推荐策略（70%相似度 + 30%平台评分）

- **数据分析仪表板**
  - 商品价格分布分析
  - 平台对比分析（京东 vs 淘宝）
  - Top商品排行榜
  - 功效分类统计

- **智能报告生成**
  - 自动生成护肤品推荐报告
  - 价格区间分析（经济/中端/高端/奢华）
  - 功效分类推荐（美白/保湿/抗衰老/修护/控油）
  - 平台对比和智能建议

- **商品管理**
  - 865+护肤品数据库（385京东 + 480淘宝）
  - 实时数据导入和更新
  - 多维度搜索和筛选

### 🚀 技术亮点

- **机器学习驱动**：使用scikit-learn实现TF-IDF特征提取和K-NN相似度计算
- **高性能**：推荐API响应时间 < 150ms
- **可扩展**：模块化设计，易于添加新的推荐算法
- **跨平台**：支持Windows、macOS、Linux部署
- **容器化**：完整的Docker支持

---

## 技术栈

### 后端
- **Python 3.10+** - 主要编程语言
- **Flask 2.3+** - Web框架
- **SQLAlchemy** - ORM数据库操作
- **PostgreSQL 13+** - 主数据库
- **scikit-learn** - 机器学习库
- **pandas & numpy** - 数据处理
- **jieba** - 中文分词

### 前端
- **React 18+** - UI框架
- **Ant Design** - UI组件库
- **ECharts** - 数据可视化
- **Axios** - HTTP客户端

### 开发工具
- **Docker & Docker Compose** - 容器化部署
- **pytest** - 后端测试
- **Jest** - 前端测试
- **Git** - 版本控制

---

## 快速开始

### 前置要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- PostgreSQL 13 或更高版本
- Git

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/xthintain/skincarePrompt.git
cd skincarePrompt
```

#### 2. 配置PostgreSQL数据库

**Ubuntu/Debian:**
```bash
# 安装PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
sudo -u postgres psql
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

**macOS (使用Homebrew):**
```bash
# 安装PostgreSQL
brew install postgresql@13

# 启动服务
brew services start postgresql@13

# 创建数据库
createdb cosmetics_db
psql cosmetics_db
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

**Windows:**
1. 从 https://www.postgresql.org/download/windows/ 下载安装包
2. 运行安装程序并设置postgres用户密码
3. 使用pgAdmin或psql创建数据库：
```sql
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
```

#### 3. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑 backend/.env 文件，更新数据库连接：
# DATABASE_URL=postgresql://admin:password@localhost:5432/cosmetics_db
```

#### 4. 安装依赖

**后端依赖：**
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**前端依赖：**
```bash
cd frontend
npm install
```

#### 5. 初始化数据库

```bash
cd backend

# 初始化数据表
python scripts/init_database.py

# 导入护肤品数据
python scripts/parse_skincare_data.py

# 训练ML模型
python scripts/train_skincare_ml.py
```

### 启动服务

#### 启动后端

```bash
cd backend
PYTHONPATH=/path/to/backend python src/app.py
```

后端服务将在 http://127.0.0.1:5000 启动

#### 启动前端

```bash
cd frontend
npm start
```

前端服务将在 http://localhost:3000 启动

#### 验证安装

```bash
# 测试后端健康检查
curl http://localhost:5000/api/v1/admin/health

# 测试ML模型
curl http://localhost:5000/api/v1/skincare/ml/similar/1?n=5
```

---

## 项目结构

```
skincarePrompt/
├── backend/                    # 后端代码
│   ├── src/
│   │   ├── api/               # API端点
│   │   │   └── v1/
│   │   │       ├── admin.py          # 系统管理API
│   │   │       ├── analytics.py      # 数据分析API
│   │   │       ├── skincare.py       # 护肤品基础API
│   │   │       └── skincare_ml.py    # ML推荐API
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置文件
│   │   └── app.py             # 应用入口
│   ├── scripts/               # 脚本
│   │   ├── init_database.py          # 初始化数据库
│   │   ├── parse_skincare_data.py    # 数据导入
│   │   ├── train_skincare_ml.py      # 模型训练
│   │   ├── extract_products.py       # 商品提取
│   │   └── check_deployment.py       # 部署检查
│   ├── models/                # 训练好的ML模型
│   │   └── skincare_ml/
│   │       ├── tfidf_vectorizer.pkl  # TF-IDF向量化器
│   │       ├── tfidf_matrix.pkl      # 特征矩阵
│   │       ├── knn_model.pkl         # K-NN模型
│   │       └── products_data.pkl     # 商品数据
│   ├── data/                  # 数据文件
│   │   ├── JD/               # 京东HTML文件
│   │   └── TB/               # 淘宝HTML文件
│   ├── tests/                 # 测试文件
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/       # React组件
│   │   ├── services/         # API服务
│   │   ├── utils/            # 工具函数
│   │   └── App.js            # 应用入口
│   ├── public/               # 静态资源
│   └── package.json          # npm依赖
├── docs/                      # 文档
│   ├── DEPLOYMENT_GUIDE.md   # 部署指南
│   ├── POSTGRESQL_SETUP.md   # 数据库设置
│   └── PPT_OUTLINE.md        # 演示大纲
├── README.md                  # 英文README
├── README_CN.md              # 中文README（本文件）
└── docker-compose.yml        # Docker配置
```

---

## 核心功能

### 智能推荐系统

#### 1. 相似商品推荐（K-NN算法）

基于K近邻算法，找到与目标商品最相似的产品：

**API端点：**
```bash
GET /api/v1/skincare/ml/similar/<product_id>?n=10
```

**示例：**
```bash
curl http://localhost:5000/api/v1/skincare/ml/similar/1?n=5
```

**返回：**
```json
{
  "success": true,
  "base_product": {
    "序号": 1,
    "名称": "谷雨第三代光感水150ml",
    "价格": 169.0,
    "平台": "JD"
  },
  "recommendations": [
    {
      "rank": 1,
      "similarity": 0.7579,
      "product": {
        "序号": 21,
        "名称": "欧莱雅葡萄籽水乳套装",
        "价格": 276.0,
        "平台": "JD"
      }
    }
  ],
  "algorithm": "K-NN with cosine similarity"
}
```

#### 2. 偏好推荐（TF-IDF + 余弦相似度）

根据用户偏好关键词，推荐最匹配的商品：

**API端点：**
```bash
POST /api/v1/skincare/ml/recommend
```

**示例：**
```bash
curl -X POST http://localhost:5000/api/v1/skincare/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": "美白补水保湿 女士",
    "n": 10,
    "min_price": 50,
    "max_price": 300,
    "platform": "JD"
  }'
```

**参数说明：**
- `preferences`: 用户偏好关键词（如"美白补水保湿"）
- `n`: 返回商品数量（默认10）
- `min_price`: 最低价格（可选）
- `max_price`: 最高价格（可选）
- `platform`: 平台筛选（all/JD/TB，可选）

### 数据分析

#### 护肤品数据分析

**API端点：**
```bash
GET /api/v1/skincare/analytics
```

**功能：**
- 总体统计（总数、京东数、淘宝数）
- 价格统计（平均价、最高价、最低价）
- Top 10推荐商品
- 价格分布（6个价格区间）

### 推荐报告生成

#### 智能推荐报告

自动生成全面的护肤品推荐报告，包含多维度分析和智能建议。

**API端点：**
```bash
POST /api/v1/analytics/skincare-report
```

**示例：**
```bash
curl -X POST http://localhost:5000/api/v1/analytics/skincare-report \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": "美白补水保湿",
    "skin_concerns": ["暗沉", "干燥"],
    "budget_range": {
      "min": 100,
      "max": 500
    },
    "report_type": "comprehensive"
  }'
```

**报告内容：**

1. **报告元数据**
   - 生成时间
   - 用户偏好
   - 肤质问题
   - 预算范围

2. **数据统计摘要**
   - 分析商品总数
   - 平均价格
   - 价格范围
   - 平均推荐分数

3. **Top推荐商品**（前10名）
   - 商品详情（名称、价格、平台）
   - 相关性分数
   - 自动生成推荐理由

4. **价格区间分析**
   - 经济实惠（0-100元）
   - 中端选择（100-300元）
   - 高端产品（300-800元）
   - 奢华系列（800元以上）
   - 每个区间的商品数量、Top 3推荐、平均价格

5. **功效分类推荐**
   - 美白提亮
   - 补水保湿
   - 抗衰老
   - 修护舒缓
   - 控油清洁

6. **平台对比分析**
   - 京东 vs 淘宝商品数量
   - 平均价格对比
   - 平均推荐分数对比
   - 各平台Top 5推荐

7. **智能建议**
   - 预算建议
   - 平台选择建议
   - 功效匹配建议

**示例输出：**
```
📊 护肤品推荐报告
============================================================
生成时间: 2025-11-13T11:22:05.867331
用户偏好: 美白补水保湿
预算范围: ¥100-500

📈 统计摘要
  分析商品总数: 73
  平均价格: ¥247.57
  价格范围: ¥109.0-499.0

🏆 Top 5 推荐商品
  1. 自然堂雪润皙白晶澈淡斑精华液...
     价格: ¥120.0 | 平台: JD | 相关度: 1.1800
     推荐理由: 包含您关注的功效: 暗沉; 平台高度推荐商品

💡 智能建议
  [platform] 京东平台有更多符合您需求的商品
     → 优先查看京东商品
  [effect] 根据您的需求，我们找到49款补水保湿产品
     → 查看补水保湿分类
```

---

## API文档

### 系统管理 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/admin/health` | GET | 健康检查 |
| `/api/v1/admin/system-info` | GET | 获取系统信息 |
| `/api/v1/admin/init-database` | POST | 初始化数据库 |
| `/api/v1/admin/import-data` | POST | 导入护肤品数据 |
| `/api/v1/admin/train-model` | POST | 训练ML模型 |
| `/api/v1/admin/task-status/<task_id>` | GET | 查询任务状态 |

### 护肤品 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/skincare/products` | GET | 获取商品列表 |
| `/api/v1/skincare/products/<id>` | GET | 获取商品详情 |
| `/api/v1/skincare/search` | GET | 搜索商品 |
| `/api/v1/skincare/analytics` | GET | 数据分析 |

### ML推荐 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/skincare/ml/similar/<id>` | GET | 相似商品推荐 |
| `/api/v1/skincare/ml/recommend` | POST | 偏好推荐 |
| `/api/v1/skincare/ml/model_info` | GET | 模型信息 |

### 分析报告 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/analytics/dashboard` | GET | 仪表板数据 |
| `/api/v1/analytics/trends` | GET | 趋势分析 |
| `/api/v1/analytics/skincare-report` | POST | 生成推荐报告 |

---

## 机器学习模型

### 为什么使用机器学习

传统推荐系统的局限性：

1. **单一维度排序** - 仅按价格、评分或销量排序，无法捕捉商品之间的深层关系
2. **缺乏个性化** - 无法根据用户偏好和商品特征进行智能匹配
3. **冷启动问题** - 新商品或新用户难以获得准确推荐
4. **特征提取困难** - 无法有效从商品名称和描述中提取多维特征

机器学习模型的优势：

#### 1. 多维特征提取（TF-IDF）

- 自动从商品名称中提取品牌、功效、类型、人群等多维特征
- 支持中文分词（jieba），理解"补水保湿"、"抗皱紧致"等语义
- 生成500维特征向量，捕捉商品的细微差异

#### 2. 智能相似度计算（K-NN + 余弦相似度）

- 基于特征向量计算商品之间的真实相似度
- 实现"看了此商品的人也看了..."功能
- 相似度范围：51-76%，准确识别同类商品

#### 3. 混合推荐策略

- 结合内容特征（TF-IDF）和平台推荐度（好评率）
- 加权公式：`final_score = 0.7 × similarity + 0.3 × platform_score`
- 平衡商品质量和特征匹配度

#### 4. 高性能和可扩展性

- 训练数据：865个商品（385京东 + 480淘宝）
- 响应时间：< 150ms
- 支持实时在线推荐

### 如何训练机器学习模型

#### 训练数据来源

系统使用PostgreSQL数据库中存储的真实电商数据：

```bash
# 查看训练数据规模
cd backend
python3 -c "
from src.config import SessionLocal
from scripts.parse_skincare_data import SkincareProduct
session = SessionLocal()
print(f'总数: {session.query(SkincareProduct).count()}')
print(f'京东: {session.query(SkincareProduct).filter_by(平台=\"JD\").count()}')
print(f'淘宝: {session.query(SkincareProduct).filter_by(平台=\"TB\").count()}')
"
```

#### 训练步骤

**方法1：使用数据库数据训练（推荐）**

```bash
cd backend

# 确保PostgreSQL数据库已运行且包含数据
# 运行训练脚本
python scripts/train_skincare_ml.py
```

**训练过程：**

1. **数据加载** - 从PostgreSQL读取全部护肤品数据
2. **特征工程** - 提取品牌、功效、类型、人群等特征
3. **TF-IDF训练** - 生成500维特征矩阵（865 × 500）
4. **K-NN训练** - 使用余弦距离训练K近邻模型（k=10）
5. **模型保存** - 保存至 `backend/models/skincare_ml/`

**模型文件：**
- `tfidf_vectorizer.pkl` - TF-IDF向量化器（85KB）
- `tfidf_matrix.pkl` - 特征矩阵（169KB）
- `knn_model.pkl` - K-NN模型（169KB）
- `products_data.pkl` - 商品数据（129KB）

总模型大小：约 **552KB**

**方法2：使用JSON数据训练**

如果只想使用JSON文件训练（适用于演示或测试）：

```bash
python scripts/train_ml_from_json.py
```

#### 训练输出示例

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

保存模型到 models/skincare_ml...
✅ 模型保存成功

【测试1】相似商品推荐
基准商品: 谷雨第三代光感水150ml
  排名 1: 相似度 0.7579
  名称: 欧莱雅葡萄籽水乳套装

【测试2】基于用户偏好推荐
用户偏好: 美白补水保湿 女士
  排名 1: 加权分数 0.5421 (相似度 0.3950)
  名称: HAPN依克多因补水保湿水乳套装
============================================================
✅ 训练完成!
============================================================
```

#### 何时需要重新训练

在以下情况下应重新训练模型：

1. **数据更新** - 添加新商品到数据库后
2. **特征调整** - 修改特征提取逻辑后
3. **参数优化** - 调整TF-IDF或K-NN参数后
4. **性能下降** - 推荐准确率明显下降时

#### 模型验证

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

### 模型性能

**训练数据规模：**
- 总商品数：865个
- 京东商品：385个
- 淘宝商品：480个

**特征提取：**
- 特征总数：500维
- 特征空间：865 × 500
- Top特征：保湿(6.38%)、补水(5.72%)、套装(5.52%)

**推荐准确性：**
- K-NN相似度：51-76%（相似商品）
- TF-IDF匹配：24-40%（偏好推荐）
- 混合加权分数：44-55%（综合准确度）

**响应时间：**
- 模型加载：< 2s（懒加载）
- 相似商品API：< 100ms
- 偏好推荐API：< 150ms

### 算法详解

#### 1. TF-IDF（词频-逆文档频率）

**算法：** `sklearn.feature_extraction.text.TfidfVectorizer`

**配置：**
- `max_features=500` - 提取最重要的500个特征
- `ngram_range=(1, 2)` - 使用1-gram和2-gram特征
- 支持中文分词（jieba）

**应用：** 将商品描述转换为数值特征向量，用于相似度计算

#### 2. K近邻（K-Nearest Neighbors）

**算法：** `sklearn.neighbors.NearestNeighbors`

**配置：**
- `n_neighbors=10` - 找出10个最相似的商品
- `metric='cosine'` - 使用余弦相似度
- `algorithm='brute'` - 暴力搜索（保证准确性）

**应用：** 基于特征相似度识别相似商品，实现"看了此商品的人也看了"功能

#### 3. 余弦相似度

**算法：** `sklearn.metrics.pairwise.cosine_similarity`

**公式：**
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**应用：** 计算用户偏好与商品特征之间的相似度，范围从0（完全不同）到1（完全相同）

---

## 开发指南

### 运行测试

**后端测试：**
```bash
cd backend
pytest tests/ -v --cov=src
```

**前端测试：**
```bash
cd frontend
npm test
```

### 代码质量

**后端代码检查：**
```bash
cd backend
flake8 src/ --max-line-length=100
black src/
```

**前端代码检查：**
```bash
cd frontend
npm run lint
npm run format
```

### 数据库迁移

```bash
cd backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 部署

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend python scripts/init_database.py
docker-compose exec backend python scripts/parse_skincare_data.py
docker-compose exec backend python scripts/train_skincare_ml.py

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

参考 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 获取详细的部署指南。

**生产环境建议：**

1. 使用Gunicorn或uWSGI运行Flask应用
2. 使用Nginx作为反向代理
3. 配置SSL证书（Let's Encrypt）
4. 启用Redis缓存
5. 设置日志轮转
6. 配置监控和告警

---

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 贡献指南

- 遵循PEP 8代码规范（Python）
- 遵循Airbnb代码规范（JavaScript）
- 编写单元测试
- 更新相关文档
- 确保所有测试通过

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 致谢

### 学术引用

本系统实现的机器学习算法基于以下学术研究：

1. **Salton, G., & McGill, M. J. (1983)**. *Introduction to Modern Information Retrieval*. McGraw-Hill.
   - TF-IDF算法基础
   - 向量空间模型

2. **Fix, E., & Hodges, J. L. (1951)**. *Discriminatory Analysis. Nonparametric Discrimination*. USAF School of Aviation Medicine.
   - K近邻算法原理
   - 非参数模式识别

3. **Salton, G., Wong, A., & Yang, C. S. (1975)**. *A Vector Space Model for Automatic Indexing*. Communications of the ACM.
   - 向量空间模型
   - 余弦相似度

4. **Burke, R. (2002)**. *Hybrid Recommender Systems: Survey and Experiments*. User Modeling and User-Adapted Interaction.
   - 混合推荐策略
   - 多种推荐技术结合

---

## 联系方式

- 项目主页：https://github.com/xthintain/skincarePrompt
- Issue 跟踪：https://github.com/xthintain/skincarePrompt/issues
- 文档：查看 `docs/` 目录

---

## 更新日志

### v1.0.0 (2025-11-13)

- ✅ 初始版本发布
- ✅ 实现TF-IDF + K-NN推荐算法
- ✅ 865个护肤品数据库
- ✅ 相似商品推荐API
- ✅ 偏好推荐API
- ✅ 智能推荐报告生成
- ✅ 数据分析仪表板
- ✅ 跨平台部署支持

---

<div align="center">

**[⬆ 回到顶部](#护肤品智能分析与推荐系统)**

Made with ❤️ by LLL Development Team

</div>
