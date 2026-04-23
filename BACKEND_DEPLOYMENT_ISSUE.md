# 后端部署问题诊断报告

## 问题描述

后端服务 `https://pku-cycle-backend.onrender.com` 返回 404 错误，所有 API 端点都无法访问。

## 诊断结果

### 1. 测试结果

```bash
# 测试健康检查端点
curl https://pku-cycle-backend.onrender.com/health
# 结果：404 Not Found

# 测试登录端点
curl -X POST https://pku-cycle-backend.onrender.com/auth/login
# 结果：404 Not Found

# 测试 API 文档
curl https://pku-cycle-backend.onrender.com/docs
# 结果：404 Not Found
# 响应头：x-render-routing: no-server
```

### 2. 问题分析

**关键发现**: `x-render-routing: no-server` 响应头表明 Render 上没有运行的服务实例。

**可能原因**:

1. **Render 服务进入睡眠状态** - Render 免费套餐的服务在 15 分钟无活动后会进入睡眠
2. **Render 部署失败** - 最新代码部署时出错
3. **Render 服务被停止** - 服务可能因错误而崩溃
4. **端口配置问题** - uvicorn 可能没有正确绑定到 Render 分配的端口

### 3. 代码检查结果

✅ **路由配置正确**:
- `/auth/login` 路由在 `backend/app/routers/users.py` 中正确定义
- `APIRouter(prefix="/auth")` 配置正确
- 主应用正确包含了所有路由器

✅ **启动配置正确**:
- `render.yaml` 中命令：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 使用环境变量 `$PORT` 正确

✅ **代码已推送**:
- Git 日志显示最新提交已推送到 origin/main
- 所有新功能代码都已提交

## 解决方案

### 方案 1: 等待 Render 唤醒服务（推荐）

Render 免费服务在收到请求时会唤醒，但第一次请求会超时。

**操作步骤**:
```bash
# 发送请求唤醒服务
curl https://pku-cycle-backend.onrender.com/health

# 等待 30-60 秒

# 再次测试
curl https://pku-cycle-backend.onrender.com/health
```

**预期结果**: 第一次请求可能失败，但后续请求应该成功（返回 200）

### 方案 2: 检查 Render 部署日志

1. 登录 Render 控制台：https://dashboard.render.com
2. 找到 `pku-cycle-backend` 服务
3. 查看 "Logs" 标签页
4. 检查是否有启动错误或运行时错误

**可能的错误**:
- 数据库连接失败
- 依赖安装失败
- 端口绑定失败
- 代码语法错误

### 方案 3: 手动触发重新部署

如果服务部署失败，可以手动触发重新部署：

1. 登录 Render 控制台
2. 进入 `pku-cycle-backend` 服务
3. 点击 "Manual Deploy"
4. 选择 "Clear build cache & deploy"

### 方案 4: 检查环境变量

确保 Render 中配置了正确的环境变量：

1. `DATABASE_URL` - 已在 render.yaml 中配置
2. `SECRET_KEY` - 需要在 Render 控制台手动添加
3. `ACCESS_TOKEN_EXPIRE_MINUTES` - 可选

**添加 SECRET_KEY**:
```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 在 Render 控制台添加环境变量
# Key: SECRET_KEY
# Value: [生成的密钥]
```

### 方案 5: 本地测试后端

在本地启动后端，确认代码没有问题：

```bash
cd backend

# 设置环境变量
export DATABASE_URL="postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a.oregon-postgres.render.com/pku_cycle_db_qre8"
export SECRET_KEY="test-secret-key-for-local-testing"

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 测试
curl http://localhost:8000/health
```

## 测试脚本

创建了以下测试脚本用于验证后端功能：

### 1. test_api_simple.py
```bash
python test_api_simple.py
```

测试基本 API 端点：
- 健康检查
- 用户登录
- 获取自行车列表
- 管理员仪表盘

### 2. manual_test_guide.py
```bash
python manual_test_guide.py
```

提供详细的手动测试步骤指南。

## 下一步行动

1. **等待 Render 服务唤醒**（5-10 分钟）
2. **运行测试脚本**验证后端是否可用
3. **如果仍然失败**，检查 Render 控制台日志
4. **修复发现的任何问题**
5. **重新推送代码**触发自动部署
6. **再次测试**

## 联系信息

如果问题持续，需要：
1. 查看 Render 控制台的详细日志
2. 检查数据库连接状态
3. 验证 Render 服务配置
4. 考虑升级到 Render 付费套餐（避免睡眠）

## 附录：完整的 API 端点列表

后端应该提供以下端点：

### 认证
- POST /auth/register
- POST /auth/login

### 用户管理
- GET /users/me
- GET /users/
- PUT /users/{user_id}/role

### 自行车管理
- GET /bicycles/
- POST /bicycles/
- GET /bicycles/{bike_id}
- PUT /bicycles/{bike_id}
- DELETE /bicycles/{bike_id}
- POST /bicycles/{bike_id}/propose-slots
- POST /bicycles/{bike_id}/confirm
- PUT /bicycles/{bike_id}/store-inventory
- GET /bicycles/admin/dashboard

### 时间段管理
- GET /time_slots/
- POST /time_slots/
- PUT /time_slots/{slot_id}
- DELETE /time_slots/{slot_id}
- PUT /time_slots/select-bicycle/{bike_id}
- PUT /time_slots/select-appointment/{apt_id}
- PUT /time_slots/confirm/{apt_id}

### 消息管理
- GET /messages/
- POST /messages/
- PUT /messages/{message_id}/read

### 预约管理
- GET /appointments/
- POST /appointments/
- PUT /appointments/{apt_id}/cancel
