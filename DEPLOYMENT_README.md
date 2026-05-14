# cLab 部署快速指南

## 📚 文档说明

本项目包含以下部署相关文档：

### 1. [CLAB_DEPLOYMENT.md](./CLAB_DEPLOYMENT.md)
详细的 cLab 部署指南，包含：
- 部署架构说明
- 服务器配置信息
- 完整的部署流程
- 环境配置方法
- 服务管理命令
- 测试流程
- 常见问题解决方案

### 2. [CLAB_DEPLOYMENT_SUMMARY.md](./CLAB_DEPLOYMENT_SUMMARY.md)
部署总结与故障排查，包含：
- 部署概述和架构图
- 关键问题与解决方案
- 详细的测试流程
- 服务管理方法
- 性能优化建议
- 监控建议

### 3. [deploy-local.sh](./deploy-local.sh)
自动化部署脚本，一键完成：
- 本地构建前端
- 同步代码到服务器
- 安装依赖
- 初始化数据库
- 启动服务

### 4. [test_clab.sh](./test_clab.sh)
Bash 测试脚本，用于：
- 测试后端 API 连通性
- 测试管理员登录
- 验证 Token 生成
- 测试 API 端点

### 5. [test_clab_login.py](./test_clab_login.py)
Python 测试脚本，用于：
- 详细测试登录功能
- 验证 Token 有效性
- 测试用户信息获取

## 🚀 快速部署

```bash
# 1. 确保已配置 SSH 密钥
chmod 600 ~/.ssh/pku-campus-cycle.pem

# 2. 运行部署脚本
./deploy-local.sh

# 3. 等待部署完成（约 2-3 分钟）
```

## ✅ 验证部署

```bash
# 测试后端 API
curl http://10.129.245.117:8000

# 测试前端
curl http://10.129.245.117:3000

# 运行测试脚本
./test_clab.sh
```

## 🔧 服务管理

### 查看服务状态
```bash
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117 "ps aux | grep -E 'uvicorn|next'"
```

### 查看日志
```bash
# 后端日志
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117 "tail -f /home/rocky/PKU-Campus-Cycle-Cycle/backend.log"

# 前端日志
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117 "tail -f /home/rocky/PKU-Campus-Cycle-Cycle/frontend.log"
```

### 重启服务
```bash
ssh -i ~/.ssh/pku-campus-cycle.pem rocky@10.129.245.117 "
  pkill -f 'uvicorn app.main:app' || true
  pkill -f 'next start' || true
  sleep 2
  cd /home/rocky/PKU-Campus-Cycle-Cycle/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
  cd /home/rocky/PKU-Campus-Cycle-Cycle/frontend && nohup npx next start --hostname 0.0.0.0 --port 3000 > ../frontend.log 2>&1 &
"
```

## 🌐 访问地址

- **前端**: http://10.129.245.117:3000
- **后端 API**: http://10.129.245.117:8000
- **API 文档**: http://10.129.245.117:8000/docs

## 👤 管理员账号

- **邮箱**: 2200017736@stu.pku.edu.cn
- **密码**: pkucycle

⚠️ **安全提示**: 首次部署后应立即修改管理员密码！

## 📝 敏感信息管理

以下文件包含敏感信息，已添加到 `.gitignore`，**不应提交到 GitHub**：

- `website_info.md`
- `frontend/.env.local`
- `backend/app/data/*.db`
- `*.pem` (SSH 密钥)
- `backend/venv/`
- `node_modules/`
- `frontend/.next/`
- `*.log`

## 🐛 常见问题

### 1. SSH 连接超时
```bash
# 尝试重启服务器后重新连接
```

### 2. 前端缓存问题
- 清除浏览器缓存 (Ctrl+Shift+Delete)
- 使用无痕模式访问
- 强制刷新 (Ctrl+F5)

### 3. 时间解析错误
已修复，确保后端代码是最新版本。

## 📖 详细文档

请查看：
- [CLAB_DEPLOYMENT.md](./CLAB_DEPLOYMENT.md) - 完整部署指南
- [CLAB_DEPLOYMENT_SUMMARY.md](./CLAB_DEPLOYMENT_SUMMARY.md) - 部署总结

## 📞 支持

如有问题，请参考详细文档或联系项目维护者。
