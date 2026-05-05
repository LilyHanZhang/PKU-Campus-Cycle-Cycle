from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
import uuid as uuid_lib

from ..database import get_db
from ..models import User, Role as UserRole
from ..schemas import UserCreate, UserResponse, UserUpdate, Token, RoleUpdate, PasswordUpdate
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

    # 检查邮箱是否已被其他用户使用
    if user_update.email is not None and user_update.email != user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被使用"
            )
        user.email = user_update.email

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url

    db.commit()
    db.refresh(user)
    return user

@user_router.put("/{user_id}/password")
def update_password(
    user_id: UUID,
    password_update: PasswordUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if str(current_user["user_id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="只能修改自己的密码")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证当前密码
    if not verify_password(password_update.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )

    # 更新密码
    user.password_hash = get_password_hash(password_update.new_password)
    db.commit()

    return {"message": "密码修改成功"}

@user_router.post("/{user_id}/upload-avatar")
async def upload_avatar(
    user_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传头像图片"""
    if str(current_user["user_id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="只能修改自己的头像")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{file.content_type}。只支持 JPEG, PNG, GIF, WebP"
        )

    # 验证文件大小（5MB）
    content = await file.read()
    file_size = len(content)
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过 5MB"
        )

    # 创建 uploads 目录
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # 生成唯一文件名
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid_lib.uuid4()}.{file_extension}"
    file_path = os.path.join(uploads_dir, filename)

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)

    # 生成 URL（使用 Render 的公网 URL）
    image_url = f"https://pku-campus-cycle-cycle.onrender.com/uploads/{filename}"

    # 更新用户头像
    user.avatar_url = image_url
    db.commit()
    db.refresh(user)

    return {"url": image_url, "filename": filename}

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
