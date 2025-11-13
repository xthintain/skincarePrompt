# PostgreSQL 配置指南

## 方法一：自动配置（推荐）

### 1. 安装 PostgreSQL

PostgreSQL 正在后台安装中。如果安装成功，执行：

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 如果未启动，启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. 运行配置脚本

```bash
# 执行数据库配置脚本
./setup_database.sh
```

这个脚本将：
- 创建数据库 `cosmetics_db`
- 创建用户 `admin` (密码: `password`)
- 授予所有权限

### 3. 初始化应用数据

```bash
cd backend

# 创建数据库表
python scripts/init_database.py

# 填充日期维度表
python scripts/seed_dim_date.py

# 添加示例数据
python scripts/seed_us1_data.py

# 训练ML模型
python scripts/train_recommendation.py
```

---

## 方法二：手动配置

如果自动安装失败，请手动执行以下步骤：

### 1. 安装 PostgreSQL (Ubuntu/WSL)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2. 启动PostgreSQL服务

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. 创建数据库和用户

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 PostgreSQL shell 中执行：
CREATE DATABASE cosmetics_db;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;

# 退出
\q
```

### 4. 验证连接

```bash
# 测试连接
psql -h localhost -U admin -d cosmetics_db

# 如果提示输入密码，输入: password
# 成功连接后，输入 \q 退出
```

### 5. 更新backend/.env配置

确保 `backend/.env` 文件包含正确的数据库连接字符串：

```
DATABASE_URL=postgresql://admin:password@localhost:5432/cosmetics_db
```

---

## 常见问题

### Q1: psql: command not found
**解决**: PostgreSQL 未安装或未添加到PATH
```bash
sudo apt install postgresql-client
```

### Q2: Connection refused
**解决**: PostgreSQL 服务未启动
```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### Q3: FATAL: role "admin" does not exist
**解决**: 用户未创建，重新执行步骤3

### Q4: 权限错误
**解决**: 授予权限
```bash
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE cosmetics_db TO admin;
ALTER DATABASE cosmetics_db OWNER TO admin;
```

### Q5: peer authentication failed
**解决**: 修改 pg_hba.conf
```bash
sudo vim /etc/postgresql/12/main/pg_hba.conf

# 将 peer 改为 md5:
# local   all   all   peer  →  local   all   all   md5

# 重启 PostgreSQL
sudo systemctl restart postgresql
```

---

## 快速验证

完成配置后，运行以下命令验证：

```bash
# 1. 检查PostgreSQL运行状态
sudo systemctl status postgresql

# 2. 测试数据库连接
psql -h localhost -U admin -d cosmetics_db -c "SELECT version();"

# 3. 初始化应用数据
cd backend
python scripts/init_database.py

# 4. 检查表是否创建
psql -h localhost -U admin -d cosmetics_db -c "\dt"
```

---

## 数据库信息摘要

- **数据库名**: cosmetics_db
- **用户名**: admin
- **密码**: password
- **主机**: localhost
- **端口**: 5432
- **连接字符串**: `postgresql://admin:password@localhost:5432/cosmetics_db`

---

## 下一步

数据库配置完成后：

1. **初始化数据**:
   ```bash
   cd backend
   python scripts/init_database.py
   python scripts/seed_dim_date.py
   python scripts/seed_us1_data.py
   ```

2. **训练模型**:
   ```bash
   python scripts/train_recommendation.py
   ```

3. **启动服务**:
   ```bash
   # 后端
   python src/app.py

   # 前端（新终端）
   cd ../frontend
   npm start
   ```

4. **访问应用**: http://localhost:3000

---

最后更新: 2025-11-13
