from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import User, Role as UserRole
from ..schemas import UserCreate, UserResponse, UserUpdate, Token, RoleUpdate
from ..auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_super_admin
)

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    db_user = User(
        email=user.email,
        password_hash=get_password_hash(user.password),
        name=user.name,
        role=UserRole.USER.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    access_token = create_access_token(
        data={"sub": str(db_user.id), "role": db_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

user_router = APIRouter(prefix="/users", tags=["用户管理"])

@user_router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if str(current_user["user_id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="只能修改自己的信息")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url

    db.commit()
    db.refresh(user)
    return user

@user_router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: UUID,
    role_update: RoleUpdate,
    current_user: dict = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user

@user_router.get("/{user_id}/role-check")
def check_user_role(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user_id": str(user.id), "role": user.role}

@user_router.post("/{user_id}/transfer-super-admin")
def transfer_super_admin(
    user_id: UUID,
    current_user: dict = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    if current_user["role"] != UserRole.SUPER_ADMIN.value:
        raise HTTPException(status_code=403, detail="只有主负责人可以执行此操作")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    current_super_admin = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if current_super_admin:
        current_super_admin.role = UserRole.USER.value

    target_user.role = UserRole.SUPER_ADMIN.value

    db.commit()

    return {"message": "主负责人权限已成功转让", "new_super_admin": target_user.email}
