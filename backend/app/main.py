from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .database import engine, Base
from .models import User, Role
from .auth import get_password_hash
from .routers import users, bicycles, posts

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
        Base.metadata.create_all(bind=engine)
        create_super_admin()
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

@app.get("/")
def read_root():
    return {"message": "Welcome to PKU Cycle-Recycle Hub API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
