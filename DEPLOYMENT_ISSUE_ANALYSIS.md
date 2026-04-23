# 管理后台数据获取失败问题分析与解决

## 问题描述
管理后台在部署到 Render 后无法获取数据，所有 API 端点返回 404 或 500 错误。

## 问题原因

### 1. API URL 错误（404 错误）
**问题**：测试脚本使用了错误的 API URL
- 错误 URL：`https://pku-cycle-cycle.onrender.com`
- 正确 URL：`https://pku-campus-cycle-cycle.onrender.com`（缺少 `campus`）

**解决方案**：
- 更新所有测试脚本使用正确的 URL
- 前端应配置环境变量 `NEXT_PUBLIC_API_URL` 指向正确的生产环境地址

### 2. 数据库表结构缺失（500 错误）
**问题**：`/appointments/` 端点返回 500 错误
- 错误信息：`sqlite3.OperationalError: no such column: appointments.time_slot_id`
- 根本原因：数据库 schema 与代码模型不匹配
  - 代码中 `Appointment` 模型包含 `time_slot_id` 字段
  - 但数据库表中该字段缺失
  - Render 上的服务启动时，`Base.metadata.create_all()` 不会修改已存在的表结构

**解决方案**：
在 `backend/app/main.py` 中添加数据库迁移逻辑：

```python
def migrate_database():
    """数据库迁移：确保所有表结构正确"""
    db = SessionLocal()
    try:
        from sqlalchemy import text
        # 检查并添加缺失的字段
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            AND column_name = 'time_slot_id'
        """))
        exists = result.fetchone()
        
        if not exists:
            db.execute(text("""
                ALTER TABLE appointments 
                ADD COLUMN time_slot_id UUID
            """))
            db.commit()
            print("✓ time_slot_id 字段添加成功")
    except Exception as e:
        print(f"数据库迁移错误：{e}")
    finally:
        db.close()
```

在 `lifespan` 函数中调用迁移：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"数据库错误：{e}")
        
        try:
            migrate_database()  # 添加迁移逻辑
        except Exception as e:
            print(f"迁移错误：{e}")
        
        try:
            create_super_admin()
        except Exception as e:
            print(f"创建管理员错误：{e}")
    yield
```

## 测试验证

### 本地测试
```bash
# 运行单元测试
cd backend
python -m pytest ../tests/unit/test_new_features.py -v

# 结果：16 个测试全部通过
```

### 部署后测试
```bash
# 运行集成测试
./test_admin_full.sh

# 测试结果：
# ✓ /auth/me - 200
# ✓ /users/ - 200
# ✓ /bicycles/ - 200
# ✓ /bicycles/?status=PENDING_APPROVAL - 200
# ✓ /appointments/ - 200（关键测试）
# ✓ /time_slots/ - 200
# ✓ /messages/ - 200
```

## 经验教训

1. **数据库迁移策略**
   - 使用 Alembic 等迁移工具管理数据库 schema 变更
   - 或者在应用启动时自动执行迁移逻辑
   - 避免手动修改数据库结构

2. **环境变量配置**
   - 确保前端使用正确的 API URL
   - 生产环境应配置 `NEXT_PUBLIC_API_URL`
   - 测试脚本应使用正确的部署地址

3. **错误调试**
   - 500 错误通常表示服务器内部问题（数据库、代码逻辑等）
   - 404 错误通常表示路由或 URL 配置问题
   - 查看完整的错误信息有助于快速定位问题

## 参考文件
- 测试脚本：`test_admin_full.sh`
- 调试脚本：`test_appointments_debug.py`
- 部署配置：`render.yaml`
- 数据库迁移：`backend/app/main.py` (migrate_database 函数)

## 日期
2026-04-23
