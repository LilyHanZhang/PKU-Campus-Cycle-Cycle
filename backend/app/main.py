from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import os
import traceback

from .database import engine, Base
from .models import User, Role
from .auth import get_password_hash
from .routers import users, bicycles, posts, time_slots

def create_super_admin():
    from .database import SessionLocal
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database error: {e}")
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
