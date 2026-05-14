# cLab 部署与测试总结

## 部署概述

本项目已成功部署到 cLab 服务器，采用前后端分离架构。

### 服务器配置
- **IP 地址**: 10.129.245.117
- **SSH 访问**: `ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117`
- **项目目录**: `/home/rocky/PKU-Campus-Cycle-Cycle`

### 服务架构
```
┌─────────────────┐
│   Next.js       │  Port 3000
│   Frontend      │
└─────────────────┘
         │
         │ HTTP
         ↓
┌─────────────────┐
│   FastAPI       │  Port 8000
│   Backend       │
└─────────────────┘
         │
         ↓
┌─────────────────┐
│   SQLite        │
│   Database      │
└─────────────────┘
```

## 部署流程

### 1. 自动化部署脚本

使用 `deploy-local.sh` 进行一键部署：

```bash
./deploy-local.sh
```

**部署脚本执行步骤**：
1. ✅ 在本地构建前端（使用 `npm run build`）
2. ✅ 清理旧的 `.next` 目录
3. ✅ 同步后端代码到服务器（排除 venv, *.db 等）
4. ✅ 同步前端代码到服务器（包括构建好的 .next 目录）
5. ✅ 远程安装 Python 依赖
6. ✅ 初始化数据库
7. ✅ 启动后端服务（uvicorn）
8. ✅ 启动前端服务（next start）

### 2. 环境配置

**前端环境变量** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://10.129.245.117:8000
```

**后端配置**:
- 数据库路径：`/home/rocky/PKU-Campus-Cycle-Cycle/backend/pku_cycle.db`
- 静态文件：`/home/rocky/PKU-Campus-Cycle-Cycle/backend/app/uploads/`

## 关键问题与解决方案

### 1. SSH 连接超时
**问题**: SSH 连接经常超时
**解决**: 
- 重启云主机
- 添加 SSH keepalive 选项：`-o ServerAliveInterval=30 -o ServerAliveCountMax=3`

### 2. 前端构建缓慢
**问题**: 在服务器上构建前端非常耗时
**解决**: 
- 改为在本地构建前端
- 只同步构建好的 `.next` 目录到服务器
- 部署速度提升 10 倍以上

### 3. 浏览器缓存问题
**问题**: 部署后浏览器仍显示旧版本
**解决**:
- 清除浏览器缓存 (Ctrl+Shift+Delete)
- 使用无痕模式测试
- 强制刷新 (Ctrl+F5)

### 4. 时间解析错误
**问题**: `ValueError: Invalid isoformat string: '2026-05-14T11:50:00.000Z'`
**原因**: Python 的 `datetime.fromisoformat()` 不支持带 `Z` 后缀的 ISO 时间字符串
**解决**: 在 `backend/app/routers/bicycles.py` 中添加时间字符串处理：
```python
if start_time_str.endswith('Z'):
    start_time_str = start_time_str[:-1] + '+00:00'
```

### 5. 前端硬编码 API URL
**问题**: 前端代码中硬编码了 `http://127.0.0.1:8000`
**解决**:
- 使用环境变量 `NEXT_PUBLIC_API_URL`
- 修改多个前端文件使用环境变量：
  - `AuthContext.tsx`
  - `admin/page.tsx`
  - `messages/page.tsx`

### 6. 进程管理
**问题**: 旧进程未正确停止，导致端口占用
**解决**:
- 使用 `pkill -f` 杀死旧进程
- 使用 PID 文件管理进程
- 添加延迟等待进程完全停止

## 测试流程

### 1. 后端 API 测试

**测试脚本**: `test_clab.sh`
```bash
./test_clab.sh
```

**测试内容**:
- ✅ 后端服务连通性
- ✅ 管理员登录
- ✅ Token 验证
- ✅ API 端点访问

**测试脚本**: `test_clab_login.py`
```bash
python test_clab_login.py
```

**详细测试**:
- 登录 API 响应
- Token 生成
- 用户信息获取

### 2. 前端功能测试

**访问地址**: http://10.129.245.117:3000

**测试项目**:
- ✅ 用户注册/登录
- ✅ 管理员后台访问
- ✅ 仪表盘功能
- ✅ 时间段管理（卖家线/买家线）
- ✅ 公告板功能
- ✅ 自行车预约流程
- ✅ 消息通知

### 3. 单元测试

**位置**: `tests/unit/`

**运行方式**:
```bash
cd tests
pytest unit/test_admin_dashboard_layout.py -v
```

## 服务管理

### 查看服务状态
```bash
# SSH 登录
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117

# 查看进程
ps aux | grep -E "uvicorn|next"

# 查看日志
tail -f /home/rocky/PKU-Campus-Cycle-Cycle/backend.log
tail -f /home/rocky/PKU-Campus-Cycle-Cycle/frontend.log
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

## 敏感信息管理

以下文件包含敏感信息，已添加到 `.gitignore`：

1. `website_info.md` - 网站配置信息
2. `frontend/.env.local` - 前端环境变量
3. `backend/app/data/*.db` - 数据库文件
4. `*.pem` - SSH 密钥文件
5. `backend/venv/` - Python 虚拟环境
6. `node_modules/` - Node.js 依赖
7. `frontend/.next/` - Next.js 构建输出
8. `*.log` - 日志文件

## 访问信息

### 生产环境
- **前端**: http://10.129.245.117:3000
- **后端 API**: http://10.129.245.117:8000
- **API 文档**: http://10.129.245.117:8000/docs

### 管理员账号
- **邮箱**: 2200017736@stu.pku.edu.cn
- **密码**: pkucycle

⚠️ **安全提示**: 生产环境应修改默认密码！

## 部署日志

### 成功部署的标志
1. ✅ 后端服务运行在 8000 端口
2. ✅ 前端服务运行在 3000 端口
3. ✅ 管理员可以成功登录
4. ✅ API 调用返回正确数据
5. ✅ 前端页面正常显示
6. ✅ 时间段管理功能正常（卖家线/买家线）

### 常见错误排查

**错误**: Connection timed out
- 检查 SSH 连接
- 检查服务器是否运行
- 可能需要重启服务器

**错误**: 500 Internal Server Error
- 查看后端日志：`tail -f backend.log`
- 检查数据库连接
- 检查 Python 依赖

**错误**: Failed to load resource
- 检查前端是否正确构建
- 清除浏览器缓存
- 检查 API URL 配置

## 性能优化建议

1. **前端构建优化**
   - 本地构建后同步，减少服务器负载
   - 使用 Next.js 增量静态生成

2. **后端优化**
   - 使用 Gunicorn + Uvicorn workers
   - 启用数据库连接池

3. **缓存策略**
   - 使用 CDN 加速静态资源
   - 启用浏览器缓存
   - 实施 API 响应缓存

## 监控建议

1. **服务监控**
   - 监控 CPU 和内存使用率
   - 监控磁盘空间
   - 设置服务自动重启

2. **日志监控**
   - 定期查看错误日志
   - 设置日志轮转
   - 关键错误告警

3. **数据库备份**
   - 定期备份 SQLite 数据库
   - 实施增量备份策略

## 未来改进

1. **容器化部署**
   - 使用 Docker 容器
   - 简化部署流程
   - 提高环境一致性

2. **CI/CD 集成**
   - GitHub Actions 自动部署
   - 自动化测试
   - 自动回滚机制

3. **高可用架构**
   - 负载均衡
   - 数据库主从复制
   - 故障自动转移

## 参考文档

- `/CLAB_DEPLOYMENT.md` - 详细部署指南
- `/deploy-local.sh` - 部署脚本
- `/test_clab.sh` - 测试脚本
- `/test_clab_login.py` - 登录测试脚本
- `/.trae/rules/test_web.md` - 测试规则
