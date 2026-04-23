from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import os
import traceback

from .database import engine, Base, SessionLocal
from .models import User, Role
from .auth import get_password_hash
from .routers import users, bicycles, posts, time_slots, messages

def create_super_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "2200017736@stu.pku.edu.cn").first()
        if not existing:
            super_admin = User(
                email="2200017736@stu.pku.edu.cn",
                password_hash=get_password_hash("pkucycle"),
                name="Super Admin",
                role=Role.SUPER_ADMIN.value
            )
            db.add(super_admin)
            db.commit()
            print("Super Admin created: 2200017736@stu.pku.edu.cn")
        else:
            print("Super Admin already exists")
    finally:
        db.close()

def migrate_database():
    """数据库迁移：确保所有表结构正确"""
    db = SessionLocal()
    try:
        # 检查 appointments 表是否有 time_slot_id 字段
        from sqlalchemy import text
        try:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'appointments' 
                AND column_name = 'time_slot_id'
            """))
            exists = result.fetchone()
            
            if not exists:
                print("添加 time_slot_id 字段到 appointments 表...")
                db.execute(text("""
                    ALTER TABLE appointments 
                    ADD COLUMN time_slot_id UUID
                """))
                db.commit()
                print("✓ time_slot_id 字段添加成功")
            else:
                print("✓ time_slot_id 字段已存在")
        except Exception as e:
            # SQLite 不支持 information_schema，直接尝试添加字段
            print(f"检查字段失败（可能是 SQLite）: {e}")
            print("尝试直接添加 time_slot_id 字段...")
            try:
                db.execute(text("""
                    ALTER TABLE appointments 
                    ADD COLUMN time_slot_id UUID
                """))
                db.commit()
                print("✓ time_slot_id 字段添加成功")
            except Exception as e2:
                print(f"字段可能已存在或添加失败：{e2}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        try:
            migrate_database()
        except Exception as e:
            print(f"❌ Database migration error: {e}")
        
        try:
            create_super_admin()
        except Exception as e:
            print(f"❌ Create super admin error: {e}")
    yield

app = FastAPI(
    title="PKU Cycle-Recycle Hub API",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(users.user_router)
app.include_router(bicycles.router)
app.include_router(bicycles.appointment_router)
app.include_router(posts.router)
app.include_router(time_slots.router)
app.include_router(messages.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PKU Cycle-Recycle Hub API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"\n{'='*70}")
    print(f"❌ GLOBAL EXCEPTION CAUGHT!")
    print(f"Path: {request.url.path}")
    print(f"Method: {request.method}")
    print(f"Exception type: {type(exc).__name__}")
    print(f"Exception: {exc}")
    print(f"\nTraceback:")
    traceback.print_exc()
    print(f"{'='*70}\n")
    
    return PlainTextResponse(
        content=f"Internal Server Error: {str(exc)}",
        status_code=500,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
