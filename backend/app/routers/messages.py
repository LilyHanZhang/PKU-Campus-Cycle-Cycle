from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse
from ..auth import get_current_user

router = APIRouter(prefix="/messages", tags=["私信"])

@router.post("/", response_model=MessageResponse)
def send_message(
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送私信"""
    # 验证接收者存在
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="接收者不存在")
    
    # 不能给自己发消息
    if str(current_user["user_id"]) == str(message.receiver_id):
        raise HTTPException(status_code=400, detail="不能给自己发送消息")
    
    db_message = Message(
        sender_id=UUID(current_user["user_id"]),
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

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
