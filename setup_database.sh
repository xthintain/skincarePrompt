#!/bin/bash
#
# PostgreSQL Database Setup Script
# 配置数据库、创建用户和数据库
#

set -e

echo "========================================="
echo "PostgreSQL 数据库配置"
echo "========================================="

# 数据库配置
DB_NAME="cosmetics_db"
DB_USER="admin"
DB_PASSWORD="password"

echo "创建数据库和用户..."

# 使用 postgres 用户执行 SQL
sudo -u postgres psql <<EOF
-- 创建数据库
CREATE DATABASE ${DB_NAME};

-- 创建用户
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- 显示结果
\l ${DB_NAME}
EOF

echo ""
echo "✅ 数据库配置完成!"
echo ""
echo "数据库信息:"
echo "  数据库名: ${DB_NAME}"
echo "  用户名: ${DB_USER}"
echo "  密码: ${DB_PASSWORD}"
echo "  连接字符串: postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
echo ""
