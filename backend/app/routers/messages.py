from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import os
import uuid as uuid_lib

from ..database import get_db
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse
from ..auth import get_current_user

router = APIRouter(prefix="/messages", tags=["私信"])

def send_message_to_user(
    db: Session,
    sender_id: Optional[UUID],
    receiver_id: UUID,
    content: str,
    message_type: str = "text"
):
    """系统或用户发送私信（内部函数）"""
    if sender_id:
        # 验证发送者存在
        sender = db.query(User).filter(User.id == sender_id).first()
        if not sender:
            raise HTTPException(status_code=404, detail="发送者不存在")
        
        # 允许给自己发送消息（用作笔记或备忘录功能）
        # if str(sender_id) == str(receiver_id):
        #     raise HTTPException(status_code=400, detail="不能给自己发送消息")
    
    db_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        message_type=message_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.post("/", response_model=MessageResponse)
def send_message(
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送私信"""
    return send_message_to_user(
        db=db,
        sender_id=UUID(current_user["user_id"]),
        receiver_id=message.receiver_id,
        content=message.content,
        message_type=message.message_type
    )

@router.get("/", response_model=List[MessageResponse])
def get_my_messages(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的私信（发送和接收的）"""
    user_id = UUID(current_user["user_id"])
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    return messages

@router.get("/unread", response_model=int)
def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取未读消息数量"""
    user_id = UUID(current_user["user_id"])
    count = db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()
    return count

@router.put("/{message_id}/read")
def mark_as_read(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    # 只能标记自己收到的消息为已读
    if str(message.receiver_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限")
    
    message.is_read = True
    db.commit()
    return {"message": "已标记为已读"}

@router.put("/read-all")
def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """一键标记所有收到的消息为已读"""
    user_id = UUID(current_user["user_id"])
    
    # 标记所有收到的未读消息为已读
    db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"message": "已标记所有消息为已读"}

@router.get("/conversations")
def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会话列表（按联系人分组，显示最后一条消息）"""
    user_id = UUID(current_user["user_id"])
    
    # 获取所有与当前用户相关的消息（发送或接收）
    messages = db.query(Message).filter(
        or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).order_by(Message.created_at.desc()).all()
    
    # 按联系人分组，每个联系人只保留最后一条消息
    conversations = {}
    for msg in messages:
        # 确定对方用户 ID
        other_user_id = msg.receiver_id if str(msg.sender_id) == str(user_id) else msg.sender_id
        
        if other_user_id not in conversations:
            conversations[other_user_id] = {
                "last_message": msg,
                "unread_count": 0
            }
        
        # 统计未读消息数量
        if msg.receiver_id == user_id and not msg.is_read:
            conversations[other_user_id]["unread_count"] += 1
    
    # 构建返回结果
    result = []
    for other_user_id, conv_data in conversations.items():
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if other_user:
            result.append({
                "user_id": str(other_user.id),
                "user_name": other_user.name or other_user.email,
                "user_avatar_url": other_user.avatar_url,
                "last_message": MessageResponse.model_validate(conv_data["last_message"]).model_dump(),
                "unread_count": conv_data["unread_count"],
                "last_message_time": conv_data["last_message"].created_at
            })
    
    # 按最后一条消息时间排序
    result.sort(key=lambda x: x["last_message_time"], reverse=True)
    
    return result

@router.get("/conversation/{user_id}")
def get_conversation_with_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取与特定用户的所有消息"""
    current_user_id = UUID(current_user["user_id"])
    
    messages = db.query(Message).filter(
        and_(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user_id)
            )
        )
    ).order_by(Message.created_at.asc()).all()
    
    # 将所有收到的消息标记为已读
    db.query(Message).filter(
        Message.sender_id == user_id,
        Message.receiver_id == current_user_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        result.append({
            **MessageResponse.model_validate(msg).model_dump(),
            "sender_name": sender.name if sender else None,
            "sender_avatar_url": sender.avatar_url if sender else None
        })
    
    return result

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传图片并返回 URL"""
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
    
    return {"url": image_url, "filename": filename}

@router.delete("/conversation/{user_id}")
def delete_conversation_with_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除与特定用户的所有消息"""
    current_user_id = UUID(current_user["user_id"])
    
    # 删除所有与指定用户的消息（发送或接收）
    db.query(Message).filter(
        and_(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user_id)
            )
        )
    ).delete()
    
    db.commit()
    return {"message": "对话已删除"}

@router.get("/search")
def search_messages(
    q: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索消息内容"""
    current_user_id = UUID(current_user["user_id"])
    
    messages = db.query(Message).filter(
        and_(
            or_(
                Message.sender_id == current_user_id,
                Message.receiver_id == current_user_id
            ),
            Message.content.contains(q)
        )
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        result.append({
            **MessageResponse.model_validate(msg).model_dump(),
            "sender_name": sender.name if sender else None,
            "sender_avatar_url": sender.avatar_url if sender else None
        })
    
    return result

@router.delete("/{message_id}")
def delete_message(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除单条消息"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    # 只能删除自己发送或接收的消息
    if str(message.sender_id) != current_user["user_id"] and str(message.receiver_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限删除此消息")
    
    db.delete(message)
    db.commit()
    return {"message": "消息已删除"}
