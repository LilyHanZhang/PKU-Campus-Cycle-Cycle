# 管理后台无法访问问题解决方案

## 问题描述
管理后台页面显示 "This page couldn't load"，无法访问。

## 问题原因

### 前端 API 地址配置错误
前端代码中硬编码的默认 API 地址是本地开发环境：
- `http://127.0.0.1:8000`
- `http://localhost:8000`

部署到 Vercel 后，前端无法访问本地地址，导致页面加载失败。

## 解决方案

### 1. 创建 Vercel 配置文件
创建 `vercel.json` 文件，配置环境变量：

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

### 2. 更新前端代码默认地址
更新所有前端文件中的默认 API 地址：
- 从 `http://127.0.0.1:8000` 改为 `https://pku-campus-cycle-cycle.onrender.com`
- 从 `http://localhost:8000` 改为 `https://pku-campus-cycle-cycle.onrender.com`

**影响文件**：
- `frontend/src/lib/api.ts`
- `frontend/src/app/admin/page.tsx`
- `frontend/src/app/login/page.tsx`
- `frontend/src/app/register/page.tsx`
- `frontend/src/app/bicycles/page.tsx`
- `frontend/src/app/bicycles/new/page.tsx`
- `frontend/src/app/profile/page.tsx`
- `frontend/src/app/forum/page.tsx`
- `frontend/src/app/my-time-slots/page.tsx`
- `frontend/src/contexts/AuthContext.tsx`

### 3. 后端 API 验证
后端 API 正常工作：
- ✅ 健康检查：`/health`
- ✅ 用户登录：`/auth/login`
- ✅ 管理后台：`/bicycles/admin/dashboard`
- ✅ 自行车列表：`/bicycles/`
- ✅ 预约列表：`/appointments/`
- ✅ 用户列表：`/users/`

## 测试验证

### 后端 API 测试
```bash
# 健康检查
curl https://pku-campus-cycle-cycle.onrender.com/health
# 返回：{"status":"healthy"}

# 管理员登录
curl -X POST https://pku-campus-cycle-cycle.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}'
# 返回：access_token

# 管理后台
curl https://pku-campus-cycle-cycle.onrender.com/bicycles/admin/dashboard \
  -H "Authorization: Bearer <token>"
# 返回：仪表盘数据
```

### Python 测试结果
```
1. Admin login...
   ✓ Login successful

2. Admin dashboard...
   Status: 200
   ✓ Dashboard data retrieved
   - Pending bicycles: 0
   - Pending appointments: 0
   - Waiting confirmation: 0

3. Bicycles list...
   Status: 200
   ✓ Bicycles retrieved: 0 items

4. Appointments list...
   Status: 200
   ✓ Appointments retrieved: 0 items

5. Users list...
   Status: 200
   ✓ Users retrieved: 1 items
```

## 部署步骤

1. **推送到 GitHub**
   ```bash
   git add vercel.json frontend/src
   git commit -m "fix: 更新前端 API 默认地址为生产环境"
   git push origin main
   ```

2. **Vercel 自动部署**
   - Vercel 检测到 Git push
   - 自动触发构建和部署
   - 使用 `vercel.json` 中的环境变量

3. **等待部署完成**
   - 通常需要 1-2 分钟
   - 访问 https://pku-campus-cycle-cycle.vercel.app 验证

## 注意事项

### 1. 环境变量优先级
Next.js 环境变量优先级：
1. `.env.local` (本地开发)
2. `.env.production` (生产构建)
3. `vercel.json` 配置
4. 代码中的默认值

### 2. 开发环境
本地开发时，建议使用 `.env.local` 文件：
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. 生产环境
生产环境使用 Vercel 环境变量或 `vercel.json` 配置：
```env
NEXT_PUBLIC_API_URL=https://pku-campus-cycle-cycle.onrender.com
```

## 相关文件

- 配置文件：`vercel.json`
- 测试脚本：`test_admin_dashboard.py`
- 部署分析：`DEPLOYMENT_ISSUE_ANALYSIS.md`
- 测试规则：`.trae/rules/test_web.md`

## 日期
2026-04-23
