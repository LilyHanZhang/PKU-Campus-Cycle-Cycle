# Vercel 部署配置指南

## 问题描述
管理后台页面显示 "This page couldn't load"，前端无法连接到后端 API。

## 根本原因

### 1. 项目结构问题
```
PKU-Campus-Cycle-Cycle/
├── frontend/          # Next.js 前端项目
├── backend/           # FastAPI 后端项目
├── vercel.json        # 根目录 Vercel 配置
└── ...
```

Vercel 部署的是 `frontend` 子目录，而不是根目录。因此：
- 根目录的 `vercel.json` 不会被 Vercel 使用
- 必须在 `frontend/` 目录内配置 Vercel 设置

### 2. 环境变量配置
前端代码使用：
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pku-campus-cycle-cycle.onrender.com";
```

如果 `NEXT_PUBLIC_API_URL` 环境变量未设置，会使用默认值。但在 Vercel 构建时，需要确保这个环境变量被正确配置。

## 解决方案

### 方案 1：在 frontend 目录添加 vercel.json（已实施）

创建 `frontend/vercel.json`：
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://pku-campus-cycle-cycle.onrender.com"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://pku-campus-cycle-cycle.onrender.com"
    }
  }
}
```

**优点**：
- 版本控制中的配置
- 自动应用于所有部署

**缺点**：
- 敏感信息可能暴露（但此 URL 是公开的，没问题）

### 方案 2：在 Vercel 控制台配置环境变量（推荐）

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目 `pku-campus-cycle-cycle`
3. 进入 **Settings** → **Environment Variables**
4. 添加环境变量：
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://pku-campus-cycle-cycle.onrender.com`
   - Environment: 勾选 **Production**, **Preview**, **Development**
5. 点击 **Save**
6. 重新部署项目（Redeploy）

**优点**：
- 更安全，配置不在代码库中
- 可以为不同环境设置不同值

**缺点**：
- 需要手动配置

### 方案 3：配置 Vercel 项目的 Root Directory

如果 Vercel 项目配置不正确，可能需要设置 Root Directory：

1. 访问 Vercel Dashboard
2. 选择项目
3. 进入 **Settings** → **General** → **Root Directory**
4. 设置为 `frontend`
5. 保存并重新部署

## 验证部署

### 1. 检查 Vercel 部署状态
访问：https://vercel.com/dashboard
查看部署日志，确保：
- ✅ Build 成功
- ✅ 环境变量已加载

### 2. 测试前端 API 连接
打开浏览器开发者工具（F12），检查：
- Network 标签中的 API 请求
- 请求 URL 应该是 `https://pku-campus-cycle-cycle.onrender.com/...`
- 不应该出现 `http://127.0.0.1:8000` 或 `http://localhost:8000`

### 3. 测试管理后台
访问：https://pku-campus-cycle-cycle.vercel.app/admin
- 应该能正常加载登录页面
- 使用管理员账号登录：
  - Email: `2200017736@stu.pku.edu.cn`
  - Password: `pkucycle`
- 登录后应该能看到管理后台仪表盘

## 常见问题

### Q1: 部署后仍然是旧版本？
**A**: Vercel 有缓存机制，需要：
1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 或者使用无痕模式访问
3. 或者访问新的部署预览 URL

### Q2: 如何查看当前部署的 URL？
**A**: 
- 生产环境：https://pku-campus-cycle-cycle.vercel.app
- 预览环境：https://pku-campus-cycle-[commit-hash].vercel.app
- 在 Vercel Dashboard 查看所有部署

### Q3: API 请求失败，CORS 错误？
**A**: 需要在后端配置 CORS：
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pku-campus-cycle-cycle.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q4: 如何强制 Vercel 重新构建？
**A**: 
1. 访问 Vercel Dashboard
2. 选择项目
3. 进入 **Deployments**
4. 找到最新部署，点击 **⋮** → **Redeploy**
5. 或者推送新的 commit 触发自动部署

## 当前状态

### Git 提交
- Commit: `edb7728`
- Message: "fix: 在前端目录添加 vercel.json 配置环境变量"
- 状态：已推送到 GitHub

### Vercel 部署
- 状态：等待自动部署（1-2 分钟）
- 生产 URL: https://pku-campus-cycle-cycle.vercel.app

### 后端 API
- URL: https://pku-campus-cycle-cycle.onrender.com
- 状态：✅ 正常运行

## 下一步

1. **等待 Vercel 部署完成**
   - 访问 https://vercel.com/dashboard 查看进度
   - 通常需要 1-2 分钟

2. **测试管理后台**
   - 访问 https://pku-campus-cycle-cycle.vercel.app/admin
   - 使用管理员账号登录

3. **如果仍然失败**
   - 检查浏览器控制台的错误信息
   - 查看 Vercel 的部署日志
   - 确认环境变量配置正确

## 相关文件

- 前端配置：`frontend/vercel.json`
- 根目录配置：`vercel.json`
- 测试脚本：`test_admin_dashboard.py`
- 修复文档：`ADMIN_DASHBOARD_FIX.md`

## 日期
2026-04-23
