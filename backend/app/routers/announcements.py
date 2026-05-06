from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
import os
import uuid as uuid_lib

from ..database import get_db
from ..models import Announcement, User, Role
from ..schemas import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from ..auth import get_current_user, get_current_admin

router = APIRouter(prefix="/announcements", tags=["公告管理"])

def get_announcement_with_author(db: Session, announcement: Announcement) -> dict:
    """获取公告及其作者信息"""
    author = db.query(User).filter(User.id == announcement.author_id).first()
    
    return {
        **AnnouncementResponse.model_validate(announcement).model_dump(),
        "author_name": author.name if author else None,
        "author_avatar_url": author.avatar_url if author else None
    }

@router.post("/", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建公告（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以发布公告"
        )
    
    db_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        image_url=announcement.image_url,
        attachment_url=announcement.attachment_url,
        is_pinned=announcement.is_pinned,
        author_id=UUID(current_user["user_id"])
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    
    return get_announcement_with_author(db, db_announcement)

@router.get("/", response_model=List[AnnouncementResponse])
def list_announcements(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取所有公告列表（按置顶优先，然后按时间倒序）"""
    announcements = db.query(Announcement).order_by(
        desc(Announcement.is_pinned),
        desc(Announcement.created_at)
    ).limit(limit).all()
    
    return [get_announcement_with_author(db, ann) for ann in announcements]

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(
    announcement_id: UUID,
    db: Session = Depends(get_db)
):
    """获取公告详情"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    return get_announcement_with_author(db, announcement)

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: UUID,
    announcement_update: AnnouncementUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新公告（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以编辑公告"
        )
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    update_data = announcement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    db.commit()
    db.refresh(announcement)
    
    return get_announcement_with_author(db, announcement)

@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除公告（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除公告"
        )
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    db.delete(announcement)
    db.commit()
    
    return {"message": "公告已删除"}

@router.put("/{announcement_id}/pin")
def pin_announcement(
    announcement_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """置顶公告（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以置顶公告"
        )
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    announcement.is_pinned = True
    db.commit()
    db.refresh(announcement)
    
    return get_announcement_with_author(db, announcement)

@router.put("/{announcement_id}/unpin")
def unpin_announcement(
    announcement_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消置顶公告（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以取消置顶公告"
        )
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    announcement.is_pinned = False
    db.commit()
    db.refresh(announcement)
    
    return get_announcement_with_author(db, announcement)

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传图片（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以上传图片"
        )
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的图片格式，仅支持 JPEG, PNG, GIF, WebP"
        )
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid_lib.uuid4()}.{file_extension}"
    
    upload_dir = "uploads/announcements/images"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    file_url = f"/uploads/announcements/images/{unique_filename}"
    
    return {"file_url": file_url, "filename": file.filename}

@router.post("/upload/attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传附件（管理员和主管理员权限）"""
    user = db.query(User).filter(User.id == UUID(current_user["user_id"])).first()
    if not user or user.role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以上传附件"
        )
    
    max_file_size = 10 * 1024 * 1024
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过 10MB"
        )
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_filename = f"{uuid_lib.uuid4()}.{file_extension}"
    
    upload_dir = "uploads/announcements/attachments"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    file_url = f"/uploads/announcements/attachments/{unique_filename}"
    
    return {"file_url": file_url, "filename": file.filename, "size": file_size}
