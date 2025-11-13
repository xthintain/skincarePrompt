#!/bin/bash
#
# 化妆品推荐系统 - 快速启动脚本
# Quick Start Script for Cosmetics Recommendation System
#

set -e  # Exit on error

echo "========================================="
echo "化妆品推荐系统 - 快速启动"
echo "Cosmetics Recommendation System - Quick Start"
echo "========================================="
echo ""

# 检查 Python
echo "检查 Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装"
    exit 1
fi
echo "✅ Python 已安装: $(python --version)"

# 检查 PostgreSQL
echo "检查 PostgreSQL..."
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL 未运行，尝试使用 Docker..."

    if command -v docker-compose &> /dev/null; then
        echo "启动 Docker 服务..."
        docker-compose up -d database
        sleep 5
    else
        echo "❌ PostgreSQL 和 Docker 都不可用"
        echo "请先安装 PostgreSQL 或 Docker"
        exit 1
    fi
fi
echo "✅ PostgreSQL 可用"

# 初始化数据库
echo ""
echo "========================================="
echo "步骤 1: 初始化数据库"
echo "========================================="
cd backend

echo "创建数据库表..."
python scripts/init_database.py

echo "填充日期维度表..."
python scripts/seed_dim_date.py

echo "填充种子数据..."
python scripts/seed_us1_data.py

# 训练模型
echo ""
echo "========================================="
echo "步骤 2: 训练推荐模型"
echo "========================================="
echo "训练 ML 模型 (这可能需要几分钟)..."
mkdir -p models
python scripts/train_recommendation.py --output models/recommendation_v1.0.0.joblib

echo ""
echo "========================================="
echo "✅ 初始化完成！"
echo "========================================="
echo ""
echo "启动命令:"
echo ""
echo "后端 (终端 1):"
echo "  cd backend && python src/app.py"
echo ""
echo "前端 (终端 2):"
echo "  cd frontend && npm start"
echo ""
echo "访问: http://localhost:3000"
echo ""
echo "========================================="
