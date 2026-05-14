# cLab 部署指南

## 部署架构

- **前端**: Next.js 运行在 cLab 服务器 (http://10.129.245.117:3000)
- **后端**: FastAPI 运行在 cLab 服务器 (http://10.129.245.117:8000)
- **数据库**: SQLite (本地文件存储)

## 服务器信息

- **SSH 登录**: `ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117`
- **项目目录**: `/home/rocky/PKU-Campus-Cycle-Cycle`
- **前端端口**: 3000
- **后端端口**: 8000

## 部署流程

### 1. 本地构建前端

```bash
cd frontend
npm install
npm run build
```

### 2. 同步代码到服务器

```bash
# 同步后端代码
rsync -avz --exclude 'venv' --exclude '*.db' --exclude '__pycache__' --exclude '*.pyc' \
  -e "ssh -i ~/.ssh/pku-campus-cycle.pem" \
  backend/ \
  rocky@10.129.245.117:/home/rocky/PKU-Campus-Cycle-Cycle/backend/

# 同步前端代码（包括构建好的 .next 目录）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  -e "ssh -i ~/.ssh/pku-campus-cycle.pem" \
  frontend/ \
  rocky@10.129.245.117:/home/rocky/PKU-Campus-Cycle-Cycle/frontend/
```

### 3. 远程服务器操作

```bash
# SSH 登录
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117

# 安装 Python 依赖
cd /home/rocky/PKU-Campus-Cycle-Cycle/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端服务
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &

# 启动前端服务
cd /home/rocky/PKU-Campus-Cycle-Cycle/frontend
nohup npx next start --hostname 0.0.0.0 --port 3000 > ../frontend.log 2>&1 &
```

## 自动化部署脚本

使用 `deploy-local.sh` 脚本进行一键部署：

```bash
./deploy-local.sh
```

该脚本会：
1. 在本地构建前端
2. 同步代码到远程服务器
3. 安装依赖
4. 初始化数据库
5. 启动服务

## 环境配置

### 前端环境变量 (.env.local)

```env
NEXT_PUBLIC_API_URL=http://10.129.245.117:8000
```

### 后端环境变量

后端使用硬编码的配置，数据库文件位于 `/home/rocky/PKU-Campus-Cycle-Cycle/backend/app/data/campus_cycle.db`

## 服务管理

### 查看服务状态

```bash
# 查看进程
ps aux | grep -E "uvicorn|next"

# 查看日志
tail -f /home/rocky/PKU-Campus-Cycle-Cycle/backend.log
tail -f /home/rocky/PKU-Campus-Cycle-Cycle/frontend.log
```

### 停止服务

```bash
kill $(cat /home/rocky/PKU-Campus-Cycle-Cycle/backend.pid) 2>/dev/null || true
kill $(cat /home/rocky/PKU-Campus-Cycle-Cycle/frontend.pid) 2>/dev/null || true
```

### 重启服务

```bash
# 停止旧进程
pkill -f "uvicorn app.main:app" || true
pkill -f "next start" || true

# 启动新进程
cd /home/rocky/PKU-Campus-Cycle-Cycle/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &

cd /home/rocky/PKU-Campus-Cycle-Cycle/frontend
nohup npx next start --hostname 0.0.0.0 --port 3000 > ../frontend.log 2>&1 &
```

## 测试流程

### 1. 后端 API 测试

```bash
# 测试管理员登录
curl -X POST "http://10.129.245.117:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}'

# 提取 token 并测试其他 API
```

### 2. 前端功能测试

访问 http://10.129.245.117:3000 并测试：
- 用户登录/注册
- 管理员后台功能
- 时间段管理
- 公告板功能
- 自行车预约流程

### 3. 使用测试脚本

```bash
# 运行 cLab 测试脚本
./test_clab.sh
```

## 常见问题

### 1. SSH 连接超时

如果遇到 SSH 连接超时，可能需要重启服务器：
```bash
# 联系 cLab 管理员重启服务器
```

### 2. 端口被占用

```bash
# 查找占用端口的进程
lsof -i :3000
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 3. 前端缓存问题

如果前端更新后仍然显示旧版本：
1. 清除浏览器缓存 (Ctrl+Shift+Delete)
2. 使用无痕模式访问
3. 强制刷新 (Ctrl+F5)

### 4. 时间解析错误

如果遇到 `ValueError: Invalid isoformat string: '2026-05-14T11:50:00.000Z'`：
- 确保后端代码已更新到最新版本
- 后端已修复处理带 Z 后缀的 ISO 时间字符串

## 敏感信息管理

以下文件包含敏感信息，不应提交到 GitHub：

- `.env.local` - 前端环境变量
- `backend/app/data/*.db` - 数据库文件
- `backend/.env` - 后端环境变量（如果有）
- `*.pem` - SSH 密钥文件
- `website_info.md` - 包含敏感信息的网站信息

这些文件已添加到 `.gitignore` 中。

## 部署日志

- **后端日志**: `/home/rocky/PKU-Campus-Cycle-Cycle/backend.log`
- **前端日志**: `/home/rocky/PKU-Campus-Cycle-Cycle/frontend.log`
- **部署日志**: `deploy-local.log` (本地)

## 访问地址

- **前端**: http://10.129.245.117:3000
- **后端 API**: http://10.129.245.117:8000
- **API 文档**: http://10.129.245.117:8000/docs

## 管理员账号

- **邮箱**: 2200017736@stu.pku.edu.cn
- **密码**: pkucycle

⚠️ **注意**: 管理员账号信息仅用于测试，生产环境应修改密码！
