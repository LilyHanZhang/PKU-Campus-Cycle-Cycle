# 网站 404 错误修复

## 问题描述
访问网站时显示 404 NOT_FOUND 错误。

## 问题原因

### 错误的 vercel.json 配置
我创建了一个新的 `frontend/vercel.json` 文件，只包含环境变量配置：
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

**问题**：缺少关键的构建配置
- `buildCommand`: 告诉 Vercel 如何构建项目
- `outputDirectory`: 指定构建输出目录
- `framework`: 指定使用的框架

### Vercel 无法构建项目
没有这些配置，Vercel 不知道：
1. 如何构建 Next.js 项目
2. 构建产物在哪里
3. 使用什么框架

导致部署失败，显示 404 错误。

## 解决方案

### 恢复正确的 vercel.json 配置
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
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

**关键配置说明**：
- `buildCommand: "npm run build"` - 执行 `npm run build` 构建项目
- `outputDirectory: ".next"` - Next.js 的构建输出目录
- `framework: "nextjs"` - 使用 Next.js 框架
- `env` - 环境变量配置

## 部署状态

### Git 提交
- Commit: `8368b50`
- Message: "fix: 恢复 vercel.json 的构建配置，同时添加环境变量"
- 状态：已推送到 GitHub

### Vercel 部署
- 状态：自动部署中
- 预计时间：1-2 分钟
- 生产 URL: https://pku-campus-cycle-cycle.vercel.app

## 验证步骤

1. **等待 Vercel 部署完成**
   - 访问 https://vercel.com/dashboard
   - 查看部署状态

2. **测试网站**
   - 主页：https://pku-campus-cycle-cycle.vercel.app
   - 管理后台：https://pku-campus-cycle-cycle.vercel.app/admin

3. **检查 API 连接**
   - 打开浏览器开发者工具（F12）
   - 查看 Network 标签
   - API 请求应该指向 `https://pku-campus-cycle-cycle.onrender.com`

## 经验教训

### Vercel 配置文件的完整性
`vercel.json` 必须包含所有必要的配置项：
1. 构建命令（buildCommand）
2. 输出目录（outputDirectory）
3. 框架类型（framework）
4. 环境变量（env）

### 不要破坏原有配置
修改配置文件时：
1. 先备份原始配置
2. 理解每个配置项的作用
3. 只添加必要的内容
4. 测试后再提交

## 相关文件

- 前端配置：`frontend/vercel.json`
- 部署指南：`VERCEL_DEPLOYMENT_GUIDE.md`
- 修复文档：`ADMIN_DASHBOARD_FIX.md`

## 日期
2026-04-23
