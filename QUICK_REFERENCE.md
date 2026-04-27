# 📖 快速参考指南

> 快速查找项目中的关键信息和常用命令

---

## 🎯 核心文档（最常用）

| 文档 | 用途 | 命令 |
|------|------|------|
| **测试索引** | 查找所有测试和文档 | `cat TEST_INDEX.md` |
| **测试逻辑** | 完整测试流程（买家/卖家/管理） | `cat TESTING_LOGIC_SUMMARY.md` |
| **部署问题** | 部署问题分析与解决 | `cat DEPLOYMENT_ISSUE_ANALYSIS.md` |
| **修改详情** | 功能修改详细说明 | `cat revise_detail.md` |

---

## 🧪 运行测试

### 单元测试
```bash
# 所有单元测试
pytest tests/unit/

# 单个测试文件
pytest tests/unit/test_api.py
pytest tests/unit/test_new_features.py
```

### 集成测试
```bash
# 所有集成测试
pytest tests/integration/

# 单个测试文件
pytest tests/integration/test_backend.py
pytest tests/integration/test_all_features.py
pytest tests/integration/test_admin_api.py
```

### 快速测试
```bash
# 测试后端 API
python -c "import requests; r=requests.get('https://pku-campus-cycle-cycle.onrender.com/health'); print('Backend:', r.status_code)"

# 测试前端首页
python -c "import requests; r=requests.get('https://pku-campus-cycle-cycle.vercel.app'); print('Frontend:', r.status_code)"
```

---

## 🌐 访问地址

| 环境 | URL | 说明 |
|------|-----|------|
| **前端生产** | https://pku-campus-cycle-cycle.vercel.app | Vercel 部署 |
| **后端生产** | https://pku-campus-cycle-cycle.onrender.com | Render 部署 |
| **前端本地** | http://localhost:3000 | `cd frontend && npm run dev` |
| **后端本地** | http://localhost:8000 | `cd backend && uvicorn app.main:app --reload` |

---

## 🔑 测试账号

### 管理员账号
```
Email: 2200017736@stu.pku.edu.cn
Password: pkucycle
Role: SUPER_ADMIN
```

### 普通用户（如需创建）
访问 https://pku-campus-cycle-cycle.vercel.app/register 注册

---

## 📁 项目结构

```
PKU-Campus-Cycle-Cycle/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── routers/           # API 路由
│   │   ├── models.py          # 数据库模型
│   │   └── main.py            # 应用入口
│   └── tests/                 # 后端测试
│
├── frontend/                   # Next.js 前端
│   ├── src/
│   │   ├── app/               # 页面
│   │   ├── components/        # 组件
│   │   └── contexts/          # React Context
│   └── public/                # 静态资源
│
├── tests/                      # 集成测试
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
│
├── TEST_INDEX.md              # 📖 测试和文档索引
├── TESTING_LOGIC_SUMMARY.md   # 📖 测试逻辑总结
└── README.md                  # 📖 项目说明
```

---

## 🚀 部署命令

### 前端部署（Vercel）
```bash
cd frontend
npm run build
# 推送到 GitHub 后自动部署
git push origin main
```

### 后端部署（Render）
```bash
# 推送到 GitHub 后自动部署
git push origin main
```

### 检查部署状态
```bash
# 查看 Git 状态
git status

# 查看最近提交
git log --oneline -5
```

---

## 🔧 常用 Git 命令

```bash
# 查看状态
git status

# 添加文件
git add .

# 提交
git commit -m "描述"

# 推送
git push origin main

# 拉取
git pull origin main

# 查看日志
git log --oneline

# 撤销更改
git restore <file>
```

---

## 📝 文档分类

### 核心文档 ⭐⭐⭐
- `TEST_INDEX.md` - 测试和文档索引
- `TESTING_LOGIC_SUMMARY.md` - 测试逻辑总结
- `DEPLOYMENT_ISSUE_ANALYSIS.md` - 部署问题分析
- `revise_detail.md` - 修改详情

### 实现文档 ⭐⭐
- `IMPLEMENTATION_SUMMARY.md` - 实现总结
- `FEATURES_IMPLEMENTED.md` - 功能列表
- `FIXES_SUMMARY.md` - 修复总结

### 部署文档 ⭐⭐
- `VERCEL_DEPLOYMENT_GUIDE.md` - Vercel 部署指南
- `DEPLOYMENT_TEST_REPORT.md` - 部署测试报告
- `BACKEND_DEPLOYMENT_ISSUE.md` - 后端部署问题

### 管理后台文档 ⭐⭐
- `ADMIN_ACCESS_ISSUE.md` - 管理后台访问问题
- `ADMIN_FIX_SUMMARY.md` - 管理后台修复总结
- `ADMIN_DASHBOARD_FIX.md` - 仪表盘修复

---

## 🐛 调试技巧

### 查看浏览器控制台
1. 访问 https://pku-campus-cycle-cycle.vercel.app/admin
2. 按 F12 打开开发者工具
3. 查看 Console 和 Network 标签

### 测试 API
```bash
# 使用 curl
curl https://pku-campus-cycle-cycle.onrender.com/health

# 使用 Python
python -c "import requests; print(requests.get('https://pku-campus-cycle-cycle.onrender.com/health').json())"
```

### 查看日志
```bash
# Vercel 日志（需要 Vercel CLI）
vercel logs

# Render 日志（在 Render  dashboard 查看）
```

---

## ⚠️ 注意事项

1. **敏感信息**
   - ❌ 不要提交 `website_info.md` 到 Git
   - ❌ 不要提交 `.trae/` 目录
   - ✅ 已添加到 `.gitignore`

2. **环境变量**
   - 前端使用硬编码的生产环境 API 地址
   - 本地开发时可能需要修改

3. **数据库**
   - 生产数据库连接信息在 Render dashboard
   - 不要提交数据库密码

---

## 📞 快速查找

### 我要...

#### 查看测试文件列表
```bash
find tests -name "*.py" | sort
```

#### 查看文档列表
```bash
ls *.md | grep -v README | sort
```

#### 查找特定功能测试
```bash
grep -r "def test_" tests/ | grep <功能名>
```

#### 查看最近的修改
```bash
git log --oneline -10
```

---

## 🎓 学习资源

- **Next.js 文档**: https://nextjs.org/docs
- **FastAPI 文档**: https://fastapi.tiangolo.com
- **Vercel 部署**: https://vercel.com/docs
- **Render 部署**: https://render.com/docs

---

**最后更新**: 2026-04-23  
**维护者**: AI Assistant
