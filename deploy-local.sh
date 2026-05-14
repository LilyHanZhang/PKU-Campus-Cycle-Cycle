#!/bin/bash

# PKU Campus Cycle Cycle 部署脚本
# 从本地部署到 cLab 云主机（本地构建版本）

set -e

# 配置
REMOTE_USER="rocky"
REMOTE_HOST="10.129.245.117"
REMOTE_KEY="/Users/zhanghong/.ssh/pku-campus-cycle.pem"
REMOTE_DIR="/home/rocky/PKU-Campus-Cycle-Cycle"
BACKEND_PORT=8000
FRONTEND_PORT=3000
LOCAL_PROJECT_DIR="/Users/zhanghong/Documents/Curriculum/Computer Science/Vibe Coding/PKU-Campus-Cycle-Cycle"

echo "🚀 开始部署 PKU Campus Cycle Cycle 到 cLab 云主机..."

# 1. 确保 SSH 密钥权限正确
echo "📋 设置 SSH 密钥权限..."
chmod 600 "$REMOTE_KEY"

# 2. 测试 SSH 连接
echo "🔌 测试 SSH 连接..."
ssh -i "$REMOTE_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH 连接成功!'"

# 3. 在本地构建前端
echo "📦 在本地构建前端..."
cd "$LOCAL_PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "📥 安装 Node.js 依赖..."
    npm install
fi
echo "🔨 构建前端..."
npm run build

# 4. 创建远程目录
echo "📁 创建远程目录..."
ssh -i "$REMOTE_KEY" "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

# 5. 在本地清理旧的构建
echo "🧹 清理本地 .next 目录..."
rm -rf "$LOCAL_PROJECT_DIR/frontend/.next"

# 6. 重新在本地构建前端
echo "🔨 重新构建前端（确保使用最新环境变量）..."
cd "$LOCAL_PROJECT_DIR/frontend"
npm run build

# 7. 同步代码（排除不需要上传的文件）
echo "📤 同步代码到远程服务器..."

# 同步后端代码
rsync -avz --exclude 'venv' --exclude '*.db' --exclude '__pycache__' --exclude '*.pyc' \
  -e "ssh -i $REMOTE_KEY -o StrictHostKeyChecking=no" \
  "$LOCAL_PROJECT_DIR/backend/" \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/backend/"

# 同步前端代码（包括构建好的 .next 目录）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  -e "ssh -i $REMOTE_KEY -o StrictHostKeyChecking=no" \
  "$LOCAL_PROJECT_DIR/frontend/" \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/frontend/"

# 6. 在远程服务器上安装依赖和启动服务
echo "🚀 在远程服务器上安装依赖并启动服务..."
ssh -i "$REMOTE_KEY" "$REMOTE_USER@$REMOTE_HOST" "bash -s" << 'EOFREMOTE'
#!/bin/bash
set -e

PROJECT_DIR="/home/rocky/PKU-Campus-Cycle-Cycle"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo '🎯 安装依赖并启动服务...'
cd $PROJECT_DIR

# 安装 Python 依赖
echo '🐍 安装 Python 依赖...'
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo '📂 创建必要目录...'
mkdir -p $PROJECT_DIR/backend/app/uploads/announcements/images
mkdir -p $PROJECT_DIR/backend/app/uploads/announcements/attachments

# 初始化数据库
echo '💾 初始化数据库...'
cd $PROJECT_DIR/backend
source venv/bin/activate
python init_db.py || true

# 停止旧进程
echo '🛑 停止旧进程...'
pkill -f "uvicorn app.main:app" || true
pkill -f "next start" || true
sleep 2

# 启动后端
echo '🚀 启动后端服务...'
cd $PROJECT_DIR/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > ../backend.log 2>&1 &
echo $! > ../backend.pid
cd ..

# 等待后端启动
echo '⏳ 等待后端启动...'
sleep 5

# 启动前端（使用已构建好的 .next 目录）
echo '🚀 启动前端服务...'
cd $PROJECT_DIR/frontend
nohup npx next start --hostname 0.0.0.0 --port $FRONTEND_PORT > ../frontend.log 2>&1 &
echo $! > ../frontend.pid
cd ..

echo ''
echo '✅ 部署完成!'
echo ''
echo '📊 服务信息:'
echo "  后端：http://10.129.245.117:$BACKEND_PORT"
echo "  前端：http://10.129.245.117:$FRONTEND_PORT"
echo ''
echo '📝 日志文件:'
echo "  后端日志：$PROJECT_DIR/backend.log"
echo "  前端日志：$PROJECT_DIR/frontend.log"
echo ''
echo '🔄 查看进程:'
echo '  ps aux | grep -E "uvicorn|next"'
echo ''
echo '🛑 停止服务:'
echo '  kill $(cat backend.pid) 2>/dev/null || true'
echo '  kill $(cat frontend.pid) 2>/dev/null || true'

EOFREMOTE

echo ""
echo "✅ 部署完成！"
echo ""
echo " 访问地址:"
echo "  前端：http://$REMOTE_HOST:$FRONTEND_PORT"
echo "  后端 API: http://$REMOTE_HOST:$BACKEND_PORT/docs"
echo ""
echo "📝 查看日志:"
echo "  ssh -i $REMOTE_KEY $REMOTE_USER@$REMOTE_HOST 'tail -f $REMOTE_DIR/backend.log'"
echo "  ssh -i $REMOTE_KEY $REMOTE_USER@$REMOTE_HOST 'tail -f $REMOTE_DIR/frontend.log'"
