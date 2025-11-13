# 跨平台部署指南 - 护肤品智能推荐系统

本指南帮助你在任何电脑上从零开始部署项目。

---

## 📋 目录

1. [系统要求](#系统要求)
2. [Windows部署](#windows部署)
3. [Linux部署](#linux部署)
4. [macOS部署](#macos部署)
5. [验证部署](#验证部署)
6. [常见问题](#常见问题)

---

## 系统要求

### 基本要求
- **Python**: 3.10+
- **Node.js**: 18+
- **PostgreSQL**: 13+
- **内存**: 最少4GB RAM
- **磁盘**: 最少2GB可用空间

---

## Windows部署

### 第一步：安装PostgreSQL

#### 方法1：图形化安装（推荐新手）

1. **下载PostgreSQL**
   - 访问：https://www.postgresql.org/download/windows/
   - 下载 PostgreSQL 15 或更高版本

2. **安装PostgreSQL**
   ```
   双击安装程序 → 按默认设置安装
   重要：记住你设置的postgres密码！
   ```

3. **验证安装**
   ```powershell
   # 打开PowerShell
   "C:\Program Files\PostgreSQL\15\bin\psql" --version
   ```

#### 方法2：命令行安装

```powershell
# 使用Chocolatey（需要先安装Chocolatey）
choco install postgresql
```

### 第二步：配置数据库

```powershell
# 打开PowerShell（以管理员身份）

# 1. 进入PostgreSQL bin目录
cd "C:\Program Files\PostgreSQL\15\bin"

# 2. 连接到PostgreSQL
.\psql -U postgres

# 3. 在psql提示符下执行以下命令：
```

```sql
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

### 第三步：克隆项目

```powershell
# 打开PowerShell
cd C:\Users\你的用户名\Documents

# 克隆项目
git clone https://github.com/xthintain/skincarePrompt.git
cd skincarePrompt
```

### 第四步：配置后端

```powershell
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r backend\requirements.txt

# 4. 配置环境变量
copy backend\.env.example backend\.env

# 5. 编辑.env文件（使用记事本或VSCode）
notepad backend\.env
```

**修改.env文件中的数据库连接**：
```
DATABASE_URL=postgresql://admin:password@localhost:5432/cosmetics_db
```

### 第五步：初始化数据库

```powershell
cd backend

# 1. 创建表结构
python scripts\init_database.py

# 2. 导入护肤品数据
python scripts\parse_skincare_data.py

# 3. 训练ML模型
python scripts\train_skincare_ml.py
```

### 第六步：启动后端

```powershell
# 设置PYTHONPATH
$env:PYTHONPATH="$PWD"

# 启动后端服务
python src\app.py
```

**预期输出**：
```
 * Running on http://127.0.0.1:5000
```

### 第七步：配置前端

```powershell
# 打开新的PowerShell窗口
cd C:\Users\你的用户名\Documents\skincarePrompt\frontend

# 安装依赖
npm install

# 启动前端
npm start
```

**预期输出**：
```
Compiled successfully!
Local: http://localhost:3000
```

### 第八步：访问应用

打开浏览器访问：http://localhost:3000

---

## Linux部署

### 第一步：安装依赖

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装Python、Node.js、PostgreSQL
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y nodejs npm
sudo apt install -y postgresql postgresql-contrib

# 验证安装
python3 --version
node --version
psql --version
```

#### CentOS/RHEL

```bash
# 安装Python
sudo yum install -y python310 python310-pip

# 安装Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安装PostgreSQL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup initdb
```

### 第二步：配置PostgreSQL

```bash
# 启动PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << EOF
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
EOF

# 验证连接
psql -U admin -d cosmetics_db -h localhost
# 输入密码: password
# 成功后输入 \q 退出
```

### 第三步：克隆并配置项目

```bash
# 克隆项目
cd ~
git clone https://github.com/xthintain/skincarePrompt.git
cd skincarePrompt

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装后端依赖
pip install -r backend/requirements.txt

# 配置环境变量
cp backend/.env.example backend/.env
nano backend/.env
# 修改DATABASE_URL为: postgresql://admin:password@localhost:5432/cosmetics_db
```

### 第四步：初始化数据库

```bash
cd backend

# 创建表
python scripts/init_database.py

# 导入数据
python scripts/parse_skincare_data.py

# 训练模型
python scripts/train_skincare_ml.py
```

### 第五步：启动服务

```bash
# 启动后端（在backend目录）
PYTHONPATH=$(pwd) python src/app.py &

# 安装并启动前端（打开新终端）
cd frontend
npm install
npm start
```

---

## macOS部署

### 第一步：安装Homebrew（如果还没安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 第二步：安装依赖

```bash
# 安装Python
brew install python@3.10

# 安装Node.js
brew install node

# 安装PostgreSQL
brew install postgresql@13

# 启动PostgreSQL
brew services start postgresql@13
```

### 第三步：配置数据库

```bash
# 创建数据库
createdb cosmetics_db

# 连接到PostgreSQL
psql postgres

# 在psql中执行：
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
\q
```

### 第四步：部署项目（同Linux步骤）

```bash
# 克隆项目
git clone https://github.com/xthintain/skincarePrompt.git
cd skincarePrompt

# 配置后端
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑.env文件，设置DATABASE_URL

# 初始化数据库
cd backend
python scripts/init_database.py
python scripts/parse_skincare_data.py
python scripts/train_skincare_ml.py

# 启动后端
PYTHONPATH=$(pwd) python src/app.py &

# 启动前端
cd ../frontend
npm install
npm start
```

---

## 验证部署

### 1. 检查后端API

```bash
# 测试健康检查
curl http://localhost:5000/api/v1/skincare/analytics

# 应该返回JSON格式的统计数据
```

### 2. 检查前端

打开浏览器访问：http://localhost:3000

应该看到：
- Dashboard页面显示统计数据
- Products页面显示商品列表
- Analytics页面显示算法说明

### 3. 检查数据库

```bash
# 连接到数据库
psql -U admin -d cosmetics_db -h localhost

# 检查表
\dt

# 检查数据
SELECT COUNT(*) FROM skincare_products;
# 应该显示 865

\q
```

### 4. 检查ML模型

```bash
# 检查模型文件是否存在
ls -lh backend/models/skincare_ml/

# 应该看到：
# tfidf_vectorizer.pkl
# tfidf_matrix.pkl  
# knn_model.pkl
# products_data.pkl
```

---

## 常见问题

### Q1: pip install失败

**Windows**:
```powershell
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Linux/macOS**:
```bash
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: npm install很慢

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### Q3: PostgreSQL连接被拒绝

```bash
# 检查PostgreSQL是否运行
# Windows:
services.msc  # 查找postgresql服务

# Linux:
sudo systemctl status postgresql

# macOS:
brew services list
```

### Q4: 端口被占用

**后端端口5000被占用**:
```bash
# 修改backend/src/app.py中的端口
# 将 port=5000 改为 port=5001
```

**前端端口3000被占用**:
```bash
# 设置环境变量
# Windows: $env:PORT=3001
# Linux/macOS: PORT=3001 npm start
```

### Q5: 模块导入错误

```bash
# 确保设置了PYTHONPATH
# Windows:
$env:PYTHONPATH="路径\to\backend"

# Linux/macOS:
export PYTHONPATH=/path/to/backend
```

### Q6: 数据库编码问题

```sql
-- 重新创建数据库并指定编码
DROP DATABASE cosmetics_db;
CREATE DATABASE cosmetics_db
    ENCODING 'UTF8'
    LC_COLLATE 'zh_CN.UTF-8'
    LC_CTYPE 'zh_CN.UTF-8';
```

### Q7: 虚拟环境激活失败（Windows）

```powershell
# 允许执行脚本
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 重新激活
.\.venv\Scripts\Activate.ps1
```

---

## 快速部署脚本

### Windows一键部署脚本

创建 `deploy_windows.ps1`:

```powershell
# 检查Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "请先安装Python 3.10+" -ForegroundColor Red
    exit 1
}

# 检查Node.js
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "请先安装Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host "开始部署..." -ForegroundColor Green

# 后端配置
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env

# 前端配置
cd frontend
npm install
cd ..

# 数据库初始化
cd backend
python scripts\init_database.py
python scripts\parse_skincare_data.py
python scripts\train_skincare_ml.py
cd ..

Write-Host "部署完成!" -ForegroundColor Green
Write-Host "运行以下命令启动服务:" -ForegroundColor Cyan
Write-Host "后端: cd backend && python src\app.py" -ForegroundColor Yellow
Write-Host "前端: cd frontend && npm start" -ForegroundColor Yellow
```

运行：
```powershell
.\deploy_windows.ps1
```

### Linux/macOS一键部署脚本

创建 `deploy_linux.sh`:

```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}开始部署...${NC}"

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}请先安装Python 3.10+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}请先安装Node.js 18+${NC}"
    exit 1
fi

# 后端配置
echo -e "${GREEN}配置后端...${NC}"
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

# 前端配置
echo -e "${GREEN}配置前端...${NC}"
cd frontend
npm install
cd ..

# 数据库初始化
echo -e "${GREEN}初始化数据库...${NC}"
cd backend
python scripts/init_database.py
python scripts/parse_skincare_data.py
python scripts/train_skincare_ml.py
cd ..

echo -e "${GREEN}部署完成!${NC}"
echo -e "${YELLOW}运行以下命令启动服务:${NC}"
echo -e "后端: cd backend && PYTHONPATH=\$(pwd) python src/app.py"
echo -e "前端: cd frontend && npm start"
```

运行：
```bash
chmod +x deploy_linux.sh
./deploy_linux.sh
```

---

## 生产环境部署建议

### 1. 使用环境变量

```bash
# 不要在代码中硬编码密码
# 使用环境变量：
export DATABASE_PASSWORD="your-strong-password"
export SECRET_KEY="your-secret-key"
```

### 2. 使用WSGI服务器

```bash
# 安装gunicorn
pip install gunicorn

# 运行
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 src.app:app
```

### 3. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:5000;
    }
}
```

### 4. 使用Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

---

## 支持与帮助

- **项目仓库**: https://github.com/xthintain/skincarePrompt
- **问题反馈**: 在GitHub Issues中提交
- **文档**: 查看README.md获取更多信息

---

**文档版本**: v1.0
**最后更新**: 2025-11-13
**维护者**: xthintain
