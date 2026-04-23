from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..models import Bicycle, BicycleStatus, Appointment, AppointmentStatus, User
from ..schemas import (
    BicycleCreate, BicycleUpdate, BicycleResponse,
    AppointmentCreate, AppointmentUpdate, AppointmentResponse
)
from ..auth import get_current_user, get_current_admin

router = APIRouter(prefix="/bicycles", tags=["自行车管理"])

@router.post("/", response_model=BicycleResponse)
def create_bicycle(
    bike: BicycleCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_bike = Bicycle(
        owner_id=UUID(current_user["user_id"]),
        brand=bike.brand,
        condition=bike.condition,
        price=bike.price,
        description=bike.description,
        image_url=bike.image_url,
        status=BicycleStatus.PENDING_APPROVAL.value
    )
    db.add(db_bike)
    db.commit()
    db.refresh(db_bike)
    return db_bike

@router.get("/", response_model=List[BicycleResponse])
def list_bicycles(
    status: Optional[str] = None,
    min_condition: Optional[int] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Bicycle)
    if status:
        query = query.filter(Bicycle.status == status)
    if min_condition:
        query = query.filter(Bicycle.condition >= min_condition)
    if max_price is not None:
        query = query.filter(Bicycle.price <= max_price)

    bikes = query.offset(skip).limit(limit).all()
    return bikes

@router.get("/{bike_id}", response_model=BicycleResponse)
def get_bicycle(bike_id: UUID, db: Session = Depends(get_db)):
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    return bike

@router.put("/{bike_id}", response_model=BicycleResponse)
def update_bicycle(
    bike_id: UUID,
    bike_update: BicycleUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    if str(bike.owner_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限修改")

    update_data = bike_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bike, key, value)

    db.commit()
    db.refresh(bike)
    return bike

@router.put("/{bike_id}/approve", response_model=BicycleResponse)
def approve_bicycle(
    bike_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员批准自行车（仅用于买家预约的场景）"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    db.refresh(bike)
    return bike

@router.post("/{bike_id}/propose-slots", response_model=dict)
def propose_time_slots(
    bike_id: UUID,
    time_slots: List[dict],
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员为卖家登记的自行车提出时间段（卖家场景）"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    if bike.status != BicycleStatus.PENDING_APPROVAL.value:
        raise HTTPException(status_code=400, detail="自行车状态不正确")
    
    from ..models import TimeSlot
    from datetime import datetime
    
    # 创建时间段
    created_slots = []
    for slot_data in time_slots:
        time_slot = TimeSlot(
            bicycle_id=bike_id,
            appointment_type="pick-up",  # 卖家取车
            start_time=datetime.fromisoformat(slot_data["start_time"]),
            end_time=datetime.fromisoformat(slot_data["end_time"]),
            is_booked="false"
        )
        db.add(time_slot)
        created_slots.append({
            "id": str(time_slot.id),
            "start_time": slot_data["start_time"],
            "end_time": slot_data["end_time"]
        })
    
    # 更新自行车状态为待处理（等待卖家选择时间段）
    bike.status = BicycleStatus.LOCKED.value
    db.commit()
    
    # 发送私信通知卖家
    try:
        from ..routers.messages import send_message_to_user
        # 使用管理员 ID 作为发送者
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=bike.owner_id,
            content=f"管理员已为您的自行车登记提出 {len(time_slots)} 个可选时间段，请及时登录个人中心 - 时间段选择页面进行选择。"
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return {"message": f"已提出 {len(time_slots)} 个时间段，等待卖家选择", "slots": created_slots}

@router.put("/{bike_id}/reject", response_model=BicycleResponse)
def reject_bicycle(
    bike_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    bike.status = BicycleStatus.SOLD.value
    db.delete(bike)
    db.commit()
    return {"message": "已拒绝并删除"}

@router.delete("/{bike_id}")
def delete_bicycle(
    bike_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    if str(bike.owner_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限删除")

    db.delete(bike)
    db.commit()
    return {"message": "删除成功"}

appointment_router = APIRouter(prefix="/appointments", tags=["预约管理"])

@appointment_router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    if appointment.type == "pick-up":
        if bike.status != BicycleStatus.IN_STOCK.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该自行车当前不可预约"
            )
        bike.status = BicycleStatus.LOCKED.value

    db_appointment = Appointment(
        user_id=UUID(current_user["user_id"]),
        bicycle_id=appointment.bicycle_id,
        type=appointment.type,
        appointment_time=appointment.appointment_time,
        notes=appointment.notes,
        status=AppointmentStatus.PENDING.value
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@appointment_router.post("/{apt_id}/propose-slots", response_model=dict)
def propose_appointment_slots(
    apt_id: UUID,
    time_slots: List[dict],
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员为买家预约提出时间段（买家场景）"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if appointment.status != AppointmentStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="预约状态不正确")
    
    from ..models import TimeSlot
    from datetime import datetime
    
    # 创建时间段
    created_slots = []
    for slot_data in time_slots:
        time_slot = TimeSlot(
            bicycle_id=appointment.bicycle_id,
            appointment_type=appointment.type,  # 买家取车
            start_time=datetime.fromisoformat(slot_data["start_time"]),
            end_time=datetime.fromisoformat(slot_data["end_time"]),
            is_booked="false"
        )
        db.add(time_slot)
        created_slots.append({
            "id": str(time_slot.id),
            "start_time": slot_data["start_time"],
            "end_time": slot_data["end_time"]
        })
    
    db.commit()
    
    # 发送私信通知买家
    try:
        from ..routers.messages import send_message_to_user
        # 使用管理员 ID 作为发送者
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=appointment.user_id,
            content=f"管理员已为您的预约提出 {len(time_slots)} 个可选时间段，请及时登录个人中心 - 时间段选择页面进行选择。"
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return {"message": f"已提出 {len(time_slots)} 个时间段，等待买家选择", "slots": created_slots}

@appointment_router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"✓ current_user: {current_user}")
    print(f"✓ role: {current_user.get('role')}")
    try:
        query = db.query(Appointment)
        if current_user["role"] == "USER":
            print(f"   过滤用户预约：{current_user['user_id']}")
            query = query.filter(Appointment.user_id == UUID(current_user["user_id"]))
        if status:
            print(f"   过滤状态：{status}")
            query = query.filter(Appointment.status == status)

        appointments = query.all()
        print(f"✓ Successfully fetched {len(appointments)} appointments")
        # 手动转换，避免 from_attributes 问题
        return [AppointmentResponse(
            id=apt.id,
            user_id=apt.user_id,
            bicycle_id=apt.bicycle_id,
            type=apt.type,
            appointment_time=apt.appointment_time,
            notes=apt.notes,
            status=apt.status,
            created_at=apt.created_at
        ) for apt in appointments]
    except Exception as e:
        print(f"❌ Error in list_appointments: {e}")
        import traceback
        traceback.print_exc()
        raise

@appointment_router.get("/user/{user_id}", response_model=List[AppointmentResponse])
def get_user_appointments(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if str(user_id) != current_user["user_id"] and current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="无权限查看")

    appointments = db.query(Appointment).filter(Appointment.user_id == user_id).all()
    return appointments

@appointment_router.put("/{apt_id}", response_model=AppointmentResponse)
def update_appointment(
    apt_id: UUID,
    apt_update: AppointmentUpdate,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    if apt_update.status:
        appointment.status = apt_update.status
        if apt_update.status == AppointmentStatus.COMPLETED.value:
            bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
            if bike:
                bike.status = BicycleStatus.SOLD.value
        elif apt_update.status == AppointmentStatus.CANCELLED.value:
            bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
            if bike and bike.status == BicycleStatus.LOCKED.value:
                bike.status = BicycleStatus.IN_STOCK.value

    if apt_update.appointment_time:
        appointment.appointment_time = apt_update.appointment_time
    if apt_update.notes is not None:
        appointment.notes = apt_update.notes

    db.commit()
    db.refresh(appointment)
    return appointment

@appointment_router.put("/{apt_id}/confirm-pickup", response_model=AppointmentResponse)
def confirm_pickup(
    apt_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认提车完成"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    appointment.status = AppointmentStatus.COMPLETED.value
    bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if bike:
        bike.status = BicycleStatus.SOLD.value
    db.commit()
    db.refresh(appointment)
    return appointment

@appointment_router.put("/{apt_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    apt_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户取消预约"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 验证是预约所有者
    if str(appointment.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限取消此预约")
    
    # 只有 PENDING 或 CONFIRMED 状态可以取消
    if appointment.status not in [AppointmentStatus.PENDING.value, AppointmentStatus.CONFIRMED.value]:
        raise HTTPException(status_code=400, detail="当前状态无法取消")
    
    appointment.status = AppointmentStatus.CANCELLED.value
    # 释放自行车
    bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if bike and bike.status == BicycleStatus.LOCKED.value:
        bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    db.refresh(appointment)
    return appointment

@appointment_router.put("/{apt_id}/reject", response_model=AppointmentResponse)
def reject_appointment(
    apt_id: UUID,
    reject_reason: str,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员拒绝预约并给出理由"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    appointment.status = AppointmentStatus.CANCELLED.value
    # 释放自行车
    bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if bike and bike.status == BicycleStatus.LOCKED.value:
        bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    db.refresh(appointment)
    # TODO: 发送通知给用户（可以通过私信系统）
    return appointment

@router.get("/stats/summary")
def get_statistics(db: Session = Depends(get_db)):
    """获取平台统计数据"""
    total_bicycles = db.query(Bicycle).count()
    sold_bicycles = db.query(Bicycle).filter(Bicycle.status == BicycleStatus.SOLD.value).count()
    in_stock_bicycles = db.query(Bicycle).filter(Bicycle.status == BicycleStatus.IN_STOCK.value).count()
    total_users = db.query(User).count()
    
    return {
        "total_bicycles": total_bicycles,
        "sold_bicycles": sold_bicycles,
        "in_stock_bicycles": in_stock_bicycles,
        "total_users": total_users
    }
