# 管理后台无法访问问题分析

## 问题症状
访问管理后台页面时显示 "This page couldn't load" 错误。

## 后端 API 状态
✅ 所有后端 API 正常工作：
- `/auth/login` - 登录成功
- `/bicycles/admin/dashboard` - 返回 200
- `/bicycles/` - 返回 200
- `/appointments/` - 返回 200
- `/users/` - 返回 200

## 问题排查

### 1. 前端代码状态
前端代码已恢复到原始状态：
- API 默认地址：`http://127.0.0.1:8000`
- 通过 `process.env.NEXT_PUBLIC_API_URL` 环境变量配置生产地址

### 2. Vercel 配置
`frontend/vercel.json` 配置：
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://pku-campus-cycle-cycle.onrender.com"
  }
}
```

### 3. Git 提交状态
- 最新提交：`804d854` - "revert: 恢复前端代码到修改前的状态"
- 已推送到 GitHub

## 可能的原因

### 原因 1: Vercel 环境变量未生效
**问题**：Vercel 可能没有正确读取 `vercel.json` 中的环境变量配置

**解决方案**：
1. 访问 https://vercel.com/dashboard
2. 选择 `pku-campus-cycle-cycle` 项目
3. 进入 **Settings** → **Environment Variables**
4. 手动添加环境变量：
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://pku-campus-cycle-cycle.onrender.com`
   - Environment: 勾选 Production, Preview, Development
5. 保存后重新部署

### 原因 2: Vercel 部署失败
**问题**：构建过程可能失败

**解决方案**：
1. 访问 Vercel Dashboard
2. 查看最新部署的日志
3. 检查是否有构建错误
4. 如果有错误，根据错误信息修复

### 原因 3: 缓存问题
**问题**：Vercel 或浏览器缓存了旧版本

**解决方案**：
1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 使用无痕模式访问
3. 或者访问新的部署预览 URL

### 原因 4: Root Directory 配置错误
**问题**：Vercel 项目可能没有正确配置 Root Directory

**解决方案**：
1. 访问 Vercel Dashboard
2. 进入 **Settings** → **General**
3. 检查 **Root Directory** 是否为 `frontend`
4. 如果不是，设置为 `frontend` 并重新部署

## 调试步骤

### 步骤 1: 检查 Vercel 部署状态
```bash
# 访问 Vercel Dashboard
https://vercel.com/dashboard
```

查看：
- 最新部署状态（应该是 "Ready"）
- 部署日志（查看是否有错误）
- 部署预览 URL

### 步骤 2: 测试部署预览 URL
访问部署预览 URL（例如：`https://pku-campus-cycle-[hash].vercel.app`）

### 步骤 3: 检查浏览器控制台
1. 按 F12 打开开发者工具
2. 查看 Console 标签的错误信息
3. 查看 Network 标签的 API 请求
   - 请求的 URL 是什么
   - 是否返回错误

### 步骤 4: 手动设置环境变量测试
如果 Vercel 环境变量配置有问题，可以：
1. 在 Vercel Dashboard 手动添加环境变量
2. 重新部署

## 快速解决方案

### 方案 A: 在 Vercel 控制台配置环境变量（推荐）
1. 访问 https://vercel.com/dashboard
2. 选择项目
3. Settings → Environment Variables
4. 添加 `NEXT_PUBLIC_API_URL=https://pku-campus-cycle-cycle.onrender.com`
5. Redeploy

### 方案 B: 强制 Vercel 重新构建
1. 访问 Vercel Dashboard
2. 选择最新部署
3. 点击 ⋮ → Redeploy
4. 或者推送一个新的 commit

### 方案 C: 检查 Root Directory
1. Vercel Dashboard → Settings → General
2. 确认 Root Directory 设置为 `frontend`
3. 如果没有，设置并重新部署

## 验证修复

修复后，访问管理后台应该：
1. ✅ 页面正常加载
2. ✅ 显示管理后台仪表盘
3. ✅ 能看到待审核自行车、预约等数据
4. ✅ API 请求指向 `https://pku-campus-cycle-cycle.onrender.com`

## 相关文件

- 前端配置：`frontend/vercel.json`
- 管理后台页面：`frontend/src/app/admin/page.tsx`
- API 配置：`frontend/src/lib/api.ts`

## 日期
2026-04-23
