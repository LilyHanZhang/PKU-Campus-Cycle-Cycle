from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import TimeSlot, Appointment, Bicycle, Review, AppointmentStatus
from ..schemas import TimeSlotCreate, TimeSlotResponse, ReviewCreate, ReviewResponse
from ..auth import get_current_user, get_current_admin

router = APIRouter(prefix="/time_slots", tags=["时间段管理"])

@router.get("/", response_model=List[TimeSlotResponse])
def list_time_slots(
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员查看所有时间段"""
    time_slots = db.query(TimeSlot).all()
    return time_slots

@router.post("/", response_model=TimeSlotResponse)
def create_time_slot(
    time_slot: TimeSlotCreate,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员为预约创建可选时间段"""
    # 验证自行车存在
    bicycle = db.query(Bicycle).filter(Bicycle.id == time_slot.bicycle_id).first()
    if not bicycle:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    db_time_slot = TimeSlot(**time_slot.model_dump())
    db.add(db_time_slot)
    db.commit()
    db.refresh(db_time_slot)
    return db_time_slot

@router.get("/appointment/{apt_id}", response_model=List[TimeSlotResponse])
def get_available_time_slots(
    apt_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预约的可选时间段"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 只有预约所有者或管理员可以查看
    if str(appointment.user_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限查看")
    
    time_slots = db.query(TimeSlot).filter(
        TimeSlot.bicycle_id == appointment.bicycle_id,
        TimeSlot.appointment_type == appointment.type,
        TimeSlot.is_booked == "false"
    ).all()
    
    return time_slots

@router.put("/select/{apt_id}", response_model=dict)
def select_time_slot(
    apt_id: UUID,
    time_slot_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户选择时间段"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 验证是预约所有者
    if str(appointment.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限修改此预约")
    
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    if time_slot.is_booked == "true":
        raise HTTPException(status_code=400, detail="时间段已被预订")
    
    # 更新预约的时间段
    appointment.time_slot_id = time_slot_id
    appointment.status = AppointmentStatus.CONFIRMED.value
    db.commit()
    
    return {"message": "时间段选择成功"}

@router.post("/reviews", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建评价"""
    appointment = db.query(Appointment).filter(Appointment.id == review.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 验证预约已完成
    if appointment.status != AppointmentStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="预约未完成，无法评价")
    
    # 验证评价者身份
    if str(appointment.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限评价此预约")
    
    # 检查是否已经评价过
    existing_review = db.query(Review).filter(
        Review.appointment_id == review.appointment_id,
        Review.reviewer_id == UUID(current_user["user_id"])
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="已经评价过此预约")
    
    db_review = Review(
        **review.model_dump(),
        reviewer_id=UUID(current_user["user_id"])
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review
