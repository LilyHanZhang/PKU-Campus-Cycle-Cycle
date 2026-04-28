# Seller flow confirmation endpoint added
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models import TimeSlot, Appointment, Bicycle, Review, AppointmentStatus, BicycleStatus
from ..schemas import TimeSlotCreate, TimeSlotResponse, ReviewCreate, ReviewResponse, TimeSlotUpdate
from ..auth import get_current_user, get_current_admin

router = APIRouter(prefix="/time_slots", tags=["时间段管理"])

class TimeSlotSelection(BaseModel):
    time_slot_id: UUID

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

@router.put("/{time_slot_id}", response_model=TimeSlotResponse)
def update_time_slot(
    time_slot_id: UUID,
    time_slot_update: TimeSlotUpdate,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员更新时间段（可以更改时间）"""
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    update_data = time_slot_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(time_slot, key, value)
    
    db.commit()
    db.refresh(time_slot)
    return time_slot

@router.delete("/{time_slot_id}")
def delete_time_slot(
    time_slot_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员删除时间段"""
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    db.delete(time_slot)
    db.commit()
    return {"message": "删除成功"}

@router.get("/bicycle/{bike_id}", response_model=List[TimeSlotResponse])
def get_bicycle_time_slots(
    bike_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取自行车的可选时间段（卖家和买家场景）"""
    from ..models import Bicycle, Appointment, TimeSlot
    
    bicycle = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bicycle:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 检查权限：自行车所有者、管理员、或有预约的用户可以查看
    from uuid import UUID
    current_user_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
    
    has_permission = (
        bicycle.owner_id == current_user_id or 
        current_user["role"] in ["ADMIN", "SUPER_ADMIN"]
    )
    
    # 检查用户是否有该自行车的待处理预约
    user_appointment = None
    if not has_permission:
        user_appointment = db.query(Appointment).filter(
            Appointment.bicycle_id == bike_id,
            Appointment.user_id == current_user_id,
            Appointment.status == "PENDING"
        ).first()
        if user_appointment:
            has_permission = True
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="无权限查看")
    
    # 查询时间段
    query = db.query(TimeSlot).filter(
        TimeSlot.bicycle_id == bike_id,
        TimeSlot.is_booked == "false"
    )
    
    # 根据用户身份和预约类型过滤时间段
    # pick-up 类型时间段：卖家流程（卖家送车），只有卖家可以查看
    # drop-off 类型时间段：买家流程（买家取车），只有买家可以查看
    if user_appointment:
        # 有预约的用户，只能查看与预约类型匹配的时间段
        if user_appointment.type == "pick-up":
            # 买家预约，只能查看 drop-off 类型（买家取车）
            query = query.filter(TimeSlot.appointment_type == "drop-off")
        elif user_appointment.type == "drop-off":
            # 卖家预约，只能查看 pick-up 类型（卖家送车）
            query = query.filter(TimeSlot.appointment_type == "pick-up")
    elif bicycle.owner_id == current_user_id:
        # 自行车所有者，查看与自行车流程匹配的时间段
        # 通过查询该自行车的预约类型来判断
        bike_appointment = db.query(Appointment).filter(
            Appointment.bicycle_id == bike_id,
            Appointment.status.in_(["PENDING", "CONFIRMED"])
        ).first()
        if bike_appointment:
            if bike_appointment.type == "pick-up":
                # 买家流程，卖家不能查看（这是买家的时间段）
                query = query.filter(TimeSlot.id == None)  # 返回空结果
            # drop-off 类型：卖家流程，卖家可以查看
        # 没有预约，返回所有时间段
    
    time_slots = query.all()
    
    return time_slots

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
    selection: TimeSlotSelection,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户选择时间段，等待管理员确认（买家场景）"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 验证是预约所有者
    if str(appointment.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限修改此预约")
    
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == selection.time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    if time_slot.is_booked == "true":
        raise HTTPException(status_code=400, detail="时间段已被预订")
    
    # 更新预约的时间段，但状态保持 PENDING，等待管理员确认
    appointment.time_slot_id = selection.time_slot_id
    # 状态改为 PENDING，等待管理员确认
    appointment.status = AppointmentStatus.PENDING.value
    db.commit()
    
    # 发送私信通知管理员确认
    from ..routers.messages import send_message_to_user
    try:
        # 获取所有管理员
        from ..models import User, Role
        admins = db.query(User).filter(User.role.in_([Role.ADMIN.value, Role.SUPER_ADMIN.value])).all()
        for admin in admins:
            send_message_to_user(
                db=db,
                sender_id=None,  # 系统消息
                receiver_id=admin.id,
                content=f"用户已选择时间段，请确认。预约 ID: {apt_id}"
            )
    except:
        pass
    
    return {"message": "时间段选择成功，等待管理员确认"}

@router.put("/select-bicycle/{bike_id}", response_model=dict)
def select_bicycle_time_slot(
    bike_id: UUID,
    selection: TimeSlotSelection,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户选择时间段，等待管理员确认（卖家和买家场景）"""
    from ..models import Appointment, TimeSlot
    from uuid import UUID
    
    bicycle = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bicycle:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 验证权限：自行车所有者或有预约的用户
    current_user_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
    
    has_permission = (bicycle.owner_id == current_user_id)
    
    # 检查用户是否有该自行车的待处理预约
    user_appointment = None
    if not has_permission:
        user_appointment = db.query(Appointment).filter(
            Appointment.bicycle_id == bike_id,
            Appointment.user_id == current_user_id,
            Appointment.status == "PENDING"
        ).first()
        if user_appointment:
            has_permission = True
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="无权限修改此自行车")
    
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == selection.time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    if time_slot.is_booked == "true":
        raise HTTPException(status_code=400, detail="时间段已被预订")
    
    # 验证时间段类型与用户身份匹配
    # pick-up 类型：卖家流程（卖家送车）
    # drop-off 类型：买家流程（买家取车）
    if user_appointment:
        # 有预约的用户，只能选择与预约类型匹配的时间段
        if user_appointment.type == "pick-up" and time_slot.appointment_type != "drop-off":
            raise HTTPException(status_code=403, detail="不能选择该类型的时间段")
        elif user_appointment.type == "drop-off" and time_slot.appointment_type != "pick-up":
            raise HTTPException(status_code=403, detail="不能选择该类型的时间段")
    elif bicycle.owner_id == current_user_id:
        # 自行车所有者，检查时间段类型
        bike_appointment = db.query(Appointment).filter(
            Appointment.bicycle_id == bike_id,
            Appointment.status.in_(["PENDING", "CONFIRMED"])
        ).first()
        if bike_appointment and bike_appointment.type == "pick-up":
            # 买家流程，卖家不能选择时间段
            raise HTTPException(status_code=403, detail="该自行车为买家流程，卖家不能选择时间段")
    
    # 标记时间段为已预订
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == selection.time_slot_id).first()
    if time_slot:
        time_slot.is_booked = "true"
    
    # 更新预约的 time_slot_id（如果有预约）
    appointment = db.query(Appointment).filter(
        Appointment.bicycle_id == bike_id,
        Appointment.status == "PENDING"
    ).first()
    if appointment:
        appointment.time_slot_id = selection.time_slot_id
    
    # 更新自行车状态为 LOCKED（已选择时间段，等待管理员确认）
    bicycle.status = BicycleStatus.LOCKED.value
    db.commit()
    
    # 发送私信通知管理员确认
    from ..routers.messages import send_message_to_user
    try:
        # 获取所有管理员
        from ..models import User, Role
        admins = db.query(User).filter(User.role.in_([Role.ADMIN.value, Role.SUPER_ADMIN.value])).all()
        for admin in admins:
            send_message_to_user(
                db=db,
                sender_id=None,  # 系统消息
                receiver_id=admin.id,
                content=f"卖家已选择时间段，请确认。自行车 ID: {bike_id}"
            )
    except:
        pass
    
    return {"message": "时间段选择成功，等待管理员确认"}

@router.put("/confirm/{apt_id}", response_model=dict)
def confirm_time_slot(
    apt_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认用户选择的时间段"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if not appointment.time_slot_id:
        raise HTTPException(status_code=400, detail="用户还未选择时间段")
    
    # 确认时间段，标记为已预订
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment.time_slot_id).first()
    if time_slot:
        time_slot.is_booked = "true"
    
    # 更新预约状态为已确认
    appointment.status = AppointmentStatus.CONFIRMED.value
    
    # 更新自行车状态
    bicycle = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if bicycle:
        # 如果是卖家流程（type 为 drop-off），将自行车状态改为 RESERVED（等待线下交易）
        # 线下交易完成后，管理员再将自行车存入库存（IN_STOCK）或标记为已售（SOLD）
        if appointment.type == "drop-off":
            bicycle.status = BicycleStatus.RESERVED.value
        # 如果是买家流程（type 为 pick-up），将自行车状态改为 SOLD
        elif appointment.type == "pick-up":
            bicycle.status = BicycleStatus.SOLD.value
    
    db.commit()
    
    # 发送私信通知用户
    try:
        from ..routers.messages import send_message_to_user
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=appointment.user_id,
            content=f"管理员已确认时间段，请按时进行交易。预约 ID: {apt_id}"
        )
    except:
        pass
    
    return {"message": "时间段确认成功"}

@router.put("/confirm-bicycle/{bike_id}", response_model=dict)
def confirm_bicycle_time_slot(
    bike_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认用户选择的自行车时间段（卖家流程）"""
    from ..models import Appointment, AppointmentStatus
    
    bicycle = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bicycle:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 查询该自行车的已预订时间段（用户已选择）
    time_slot = db.query(TimeSlot).filter(
        TimeSlot.bicycle_id == bike_id,
        TimeSlot.is_booked == "true"
    ).first()
    
    if not time_slot:
        raise HTTPException(status_code=400, detail="用户还未选择时间段")
    
    # 创建预约记录（卖家流程）
    appointment = Appointment(
        user_id=bicycle.owner_id,
        bicycle_id=bike_id,
        type="drop-off",  # 卖家流程
        status=AppointmentStatus.CONFIRMED.value,
        time_slot_id=time_slot.id
    )
    db.add(appointment)
    
    # 更新自行车状态为 RESERVED（等待线下交易）
    bicycle.status = BicycleStatus.RESERVED.value
    db.commit()
    
    # 发送私信通知用户
    try:
        from ..routers.messages import send_message_to_user
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=bicycle.owner_id,
            content=f"管理员已确认时间段，请按时将自行车送到指定地点。自行车 ID: {bike_id}"
        )
    except:
        pass
    
    return {"message": "时间段确认成功"}

@router.put("/change/{apt_id}", response_model=dict)
def change_time_slot(
    apt_id: UUID,
    new_time_slot_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员更改时间段并通知用户"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    new_time_slot = db.query(TimeSlot).filter(TimeSlot.id == new_time_slot_id).first()
    if not new_time_slot:
        raise HTTPException(status_code=404, detail="新的时间段不存在")
    
    # 更新预约的时间段
    appointment.time_slot_id = new_time_slot_id
    # 状态改回 PENDING，等待用户确认
    appointment.status = AppointmentStatus.PENDING.value
    
    # 标记旧时间段为未预订
    if appointment.time_slot_id:
        old_time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment.time_slot_id).first()
        if old_time_slot and old_time_slot.id != new_time_slot_id:
            old_time_slot.is_booked = "false"
    
    db.commit()
    
    # 发送私信通知用户
    try:
        from ..routers.messages import send_message_to_user
        send_message_to_user(
            db=db,
            sender_id=None,  # 系统消息
            receiver_id=appointment.user_id,
            content=f"管理员已更改时间段，请重新确认。预约 ID: {apt_id}，新时间段：{new_time_slot.start_time} - {new_time_slot.end_time}"
        )
    except:
        pass
    
    return {"message": "时间段更改成功，已通知用户重新确认"}

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

@router.get("/my/countdown")
def get_my_countdown(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的交易倒计时"""
    from sqlalchemy.orm import joinedload
    
    # 查询用户已确认但未完成的预约
    appointments = db.query(Appointment).filter(
        Appointment.user_id == UUID(current_user["user_id"]),
        Appointment.status == AppointmentStatus.CONFIRMED.value,
        Appointment.time_slot_id.isnot(None)
    ).all()
    
    countdowns = []
    now = datetime.now()
    
    for apt in appointments:
        time_slot = db.query(TimeSlot).filter(TimeSlot.id == apt.time_slot_id).first()
        if time_slot:
            time_left = (time_slot.start_time - now).total_seconds()
            countdowns.append({
                "appointment_id": str(apt.id),
                "bicycle_id": str(apt.bicycle_id),
                "type": apt.type,
                "start_time": time_slot.start_time.isoformat(),
                "end_time": time_slot.end_time.isoformat(),
                "time_left_seconds": time_left,
                "status": "pending" if time_left > 0 else "overdue"
            })
    
    # 查询有待确认的预约
    pending_appointments = db.query(Appointment).filter(
        Appointment.user_id == UUID(current_user["user_id"]),
        Appointment.status == AppointmentStatus.PENDING.value
    ).all()
    
    pending_count = len(pending_appointments)
    
    return {
        "countdowns": countdowns,
        "pending_count": pending_count
    }
