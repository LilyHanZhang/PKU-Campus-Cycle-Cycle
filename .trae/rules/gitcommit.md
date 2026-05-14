在推送到 github 时，不要把以下包含敏感信息的文件/目录提交到 github：

1. `website_info.md` - 包含网站配置和敏感信息
2. `frontend/.env.local` - 前端环境变量（包含 API URL 等配置）
3. `backend/app/data/*.db` - 数据库文件
4. `backend/.env` - 后端环境变量
5. `*.pem` - SSH 密钥文件
6. `node_modules/` - Node.js 依赖目录
7. `backend/venv/` - Python 虚拟环境目录
8. `frontend/.next/` - Next.js 构建输出目录
9. `__pycache__/`, `*.pyc` - Python 缓存文件
10. `*.log` - 日志文件

这些文件已添加到 `.gitignore` 中，git 会自动忽略它们。
