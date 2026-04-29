from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models import Bicycle, BicycleStatus, Appointment, AppointmentStatus, User, TimeSlot
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

@router.put("/{bike_id}/store-inventory", response_model=BicycleResponse)
def store_bicycle_in_inventory(
    bike_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员将已完成交易的自行车存入库存（卖家流程完成后）"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    if bike.status != BicycleStatus.RESERVED.value:
        raise HTTPException(status_code=400, detail="自行车状态不是已预约，无法存入库存")
    
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
    """管理员为自行车提出时间段（支持卖家和买家场景）"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 自行车状态可以是：
    # 1. PENDING_APPROVAL - 卖家登记后，管理员直接提出时间段（无需预约）
    # 2. IN_STOCK - 已审核通过的自行车
    # 3. PENDING_SELLER_SLOT_SELECTION - 等待卖家选择时间段（卖家流程）
    # 4. PENDING_BUYER_SLOT_SELECTION - 等待买家选择时间段（买家流程）
    if bike.status not in [BicycleStatus.PENDING_APPROVAL.value, BicycleStatus.IN_STOCK.value, BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value]:
        raise HTTPException(status_code=400, detail="自行车状态不正确")
    
    from ..models import Appointment, TimeSlot
    from datetime import datetime
    
    # 检查是否有相关的预约
    appointment = db.query(Appointment).filter(
        Appointment.bicycle_id == bike_id,
        Appointment.status == "PENDING"
    ).first()
    
    # 根据自行车状态和预约类型确定 appointment_type
    # PENDING_APPROVAL: 卖家流程，审核并提出时间段
    # IN_STOCK + 有预约：根据预约类型确定
    # IN_STOCK + 无预约：买家流程
    if bike.status == BicycleStatus.PENDING_APPROVAL.value:
        # 卖家登记场景
        # 预约类型：drop-off（卖家送车到指定地点）
        # 时间段类型：pick-up（管理员从指定地点取车）
        appointment_type = "pick-up"  # 时间段类型
        # 审核通过
        bike.status = BicycleStatus.IN_STOCK.value
        # 创建预约（PENDING 状态，等待卖家选择时间段）
        appointment = Appointment(
            user_id=bike.owner_id,
            bicycle_id=bike_id,
            type="drop-off",  # 预约类型：卖家流程（卖家送车）
            status="PENDING"
        )
        db.add(appointment)
    elif appointment and bike.status == BicycleStatus.IN_STOCK.value:
        # 已有预约的场景（卖家流程已审核）
        # 根据预约类型反向设置时间段类型
        # drop-off = 卖家流程（卖家把车送来，管理员取车） -> 创建 pick-up 时间段
        # pick-up = 买家流程（买家来取车） -> 创建 drop-off 时间段
        appointment_type = "pick-up" if appointment.type == "drop-off" else "drop-off"
    elif bike.status == BicycleStatus.IN_STOCK.value:
        # 买家登记场景（无预约）
        # 预约类型：pick-up（买家来取车）
        # 时间段类型：drop-off（管理员送车/买家取车）
        appointment_type = "drop-off"  # 时间段类型
        appointment = Appointment(
            user_id=bike.owner_id,
            bicycle_id=bike_id,
            type="pick-up",  # 预约类型：买家流程（买家取车）
            status="PENDING"
        )
        db.add(appointment)
    elif bike.status in [BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value] and appointment:
        # 已有预约且已选择时间段的场景（重新提出时间段）
        # 根据预约类型反向设置时间段类型
        appointment_type = "pick-up" if appointment.type == "drop-off" else "drop-off"
    else:
        raise HTTPException(status_code=400, detail="该自行车没有待处理的预约")
    
    # 创建时间段
    created_slots = []
    for slot_data in time_slots:
        time_slot = TimeSlot(
            bicycle_id=bike_id,
            appointment_type=appointment_type,
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
    
    # 更新自行车状态为等待用户选择时间段
    # 根据预约类型确定是卖家流程还是买家流程
    if appointment and appointment.type == "drop-off":
        # 卖家流程：等待卖家选择时间段
        bike.status = BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value
    else:
        # 买家流程：等待买家选择时间段
        bike.status = BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value
    
    # 发送私信通知卖家
    try:
        from ..routers.messages import send_message_to_user
        # 使用管理员 ID 作为发送者
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        
        # 只有当卖家和管理员不是同一个人时才发送私信
        if admin_id != bike.owner_id:
            send_message_to_user(
                db=db,
                sender_id=admin_id,
                receiver_id=bike.owner_id,
                content=f"管理员已为您的自行车登记提出 {len(time_slots)} 个可选时间段，请及时登录个人中心 - 时间段选择页面进行选择。"
            )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    db.commit()
    
    return {"message": f"已提出 {len(time_slots)} 个时间段，等待卖家选择", "slots": created_slots}

@router.post("/{bike_id}/confirm", response_model=dict)
def confirm_bicycle_transaction(
    bike_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认自行车交易完成（卖家流程）"""
    from ..models import Appointment, AppointmentStatus
    
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 查询该自行车的待处理预约
    appointment = db.query(Appointment).filter(
        Appointment.bicycle_id == bike_id,
        Appointment.status == AppointmentStatus.PENDING.value
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=400, detail="该自行车没有待处理的预约")
    
    # 检查预约是否有时间段
    if not appointment.time_slot_id:
        raise HTTPException(status_code=400, detail="卖家还未选择时间段")
    
    # 根据预约类型设置自行车状态
    # drop-off = 卖家流程（卖家送车） -> RESERVED（等待线下交易）
    # pick-up = 买家流程（买家取车） -> SOLD（交易完成）
    if appointment.type == "drop-off":
        bike.status = BicycleStatus.RESERVED.value
    elif appointment.type == "pick-up":
        bike.status = BicycleStatus.SOLD.value
    
    # 更新预约状态为已确认
    appointment.status = AppointmentStatus.CONFIRMED.value
    db.commit()
    
    # 发送私信通知卖家
    try:
        from ..routers.messages import send_message_to_user
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        
        if appointment.type == "drop-off":
            content = f"管理员已确认时间段，请按时将自行车送到指定地点。自行车 ID: {bike_id}"
        else:
            content = f"管理员已确认时间段，请按时来取车。自行车 ID: {bike_id}"
        
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=appointment.user_id,
            content=content
        )
    except:
        pass
    
    return {"message": "自行车交易确认成功"}

@router.post("/{bike_id}/cancel", response_model=dict)
def cancel_bicycle(
    bike_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """卖家取消自行车登记"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 验证是自行车所有者
    if str(bike.owner_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限取消此自行车")
    
    # 删除相关的时间段
    from ..models import TimeSlot
    db.query(TimeSlot).filter(TimeSlot.bicycle_id == bike_id).delete()
    
    # 删除自行车
    db.delete(bike)
    db.commit()
    
    return {"message": "自行车登记已取消"}

@router.post("/{bike_id}/admin-cancel", response_model=dict)
def admin_cancel_bicycle(
    bike_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员取消自行车登记"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 删除相关的时间段
    from ..models import TimeSlot
    db.query(TimeSlot).filter(TimeSlot.bicycle_id == bike_id).delete()
    
    # 删除自行车
    db.delete(bike)
    db.commit()
    
    # 发送私信通知卖家
    try:
        from ..routers.messages import send_message_to_user
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=bike.owner_id,
            content=f"管理员已取消您的自行车登记。原因：{reason}。自行车 ID: {bike_id}"
        )
    except:
        pass
    
    return {"message": "自行车登记已被管理员取消"}

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
        # 买家流程：预约后进入等待买家选择时间段状态
        bike.status = BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value

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
            # 取消预约后，恢复自行车到库存状态
            if bike and bike.status in [BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value, BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_SELLER.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_BUYER.value]:
                bike.status = BicycleStatus.IN_STOCK.value

    if apt_update.appointment_time:
        appointment.appointment_time = apt_update.appointment_time
    if apt_update.notes is not None:
        appointment.notes = apt_update.notes

    db.commit()
    db.refresh(appointment)
    return appointment

@appointment_router.put("/{apt_id}/confirm-pickup")
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
    
    return {
        "message": "买家取车确认成功，交易完成",
        "appointment_id": str(appointment.id),
        "status": appointment.status
    }

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
    # 取消预约后，恢复自行车到库存状态
    if bike and bike.status in [BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value, BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_SELLER.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_BUYER.value]:
        bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    db.refresh(appointment)
    return appointment

@appointment_router.post("/{apt_id}/admin-cancel", response_model=dict)
def admin_cancel_appointment(
    apt_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员取消预约"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 删除相关的时间段
    from ..models import TimeSlot
    db.query(TimeSlot).filter(TimeSlot.appointment_id == apt_id).delete()
    
    appointment.status = AppointmentStatus.CANCELLED.value
    # 释放自行车
    bike = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    # 取消预约后，恢复自行车到库存状态
    if bike and bike.status in [BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value, BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_SELLER.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_BUYER.value]:
        bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    
    # 发送私信通知买家
    try:
        from ..routers.messages import send_message_to_user
        from uuid import UUID
        admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=appointment.user_id,
            content=f"管理员已取消您的预约。原因：{reason}。预约 ID: {apt_id}"
        )
    except:
        pass
    
    return {"message": "预约已被管理员取消"}

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
    # 取消预约后，恢复自行车到库存状态
    if bike and bike.status in [BicycleStatus.PENDING_BUYER_SLOT_SELECTION.value, BicycleStatus.PENDING_SELLER_SLOT_SELECTION.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_SELLER.value, BicycleStatus.PENDING_ADMIN_CONFIRMATION_BUYER.value]:
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

@router.get("/admin/dashboard")
def get_admin_dashboard(
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员仪表盘 - 显示待处理交易及倒计时"""
    from datetime import timedelta
    from sqlalchemy.orm import joinedload
    
    # 获取待处理的自行车登记
    pending_bicycles = db.query(Bicycle).filter(
        Bicycle.status == BicycleStatus.PENDING_APPROVAL.value
    ).all()
    
    # 获取待处理的预约（用户已选择时间段，等待管理员确认）
    # 只查询买家流程的预约（pick-up = 买家取车，需要管理员确认）
    # 卖家流程（drop-off）不需要出现在这里，因为卖家确认后直接完成
    waiting_appointments = db.query(Appointment).options(
        joinedload(Appointment.user),
        joinedload(Appointment.bicycle)
    ).filter(
        Appointment.status == AppointmentStatus.PENDING.value,
        Appointment.time_slot_id != None,
        Appointment.type == "pick-up"  # 只查询买家流程
    ).all()
    
    # 获取已锁定但未完成的时间段（带倒计时）
    locked_slots = db.query(TimeSlot).filter(
        TimeSlot.is_booked == "false"
    ).all()
    
    now = datetime.utcnow()
    slots_with_countdown = []
    for slot in locked_slots:
        time_remaining = (slot.start_time - now).total_seconds()
        if time_remaining > 0:
            slots_with_countdown.append({
                "id": str(slot.id),
                "bicycle_id": str(slot.bicycle_id),
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "countdown_seconds": int(time_remaining),
                "appointment_type": slot.appointment_type
            })
    
    # 获取等待管理员确认的自行车（卖家已选择时间段）
    # 查询 PENDING_ADMIN_CONFIRMATION_SELLER 状态且有已预订时间段的自行车
    # 并且时间段类型是 pick-up（卖家流程的时间段类型）
    locked_bike_ids = db.query(TimeSlot.bicycle_id).filter(
        TimeSlot.is_booked == "true",
        TimeSlot.appointment_type == "pick-up"  # 只查询卖家流程的时间段
    ).distinct()
    waiting_bicycles = db.query(Bicycle).options(
        joinedload(Bicycle.owner)
    ).filter(
        Bicycle.status == BicycleStatus.PENDING_ADMIN_CONFIRMATION_SELLER.value,
        Bicycle.id.in_(locked_bike_ids)
    ).all()
    
    return {
        "pending_bicycles_count": len(pending_bicycles),
        "pending_appointments_count": len(waiting_appointments),
        "waiting_confirmation_count": len(waiting_bicycles) + len(waiting_appointments),
        "pending_bicycles": [
            {
                "id": str(bike.id),
                "brand": bike.brand,
                "owner_id": str(bike.owner_id),
                "status": bike.status,
                "created_at": bike.created_at.isoformat() if bike.created_at else None
            } for bike in pending_bicycles
        ],
        "waiting_appointments": [
            {
                "id": str(apt.id),
                "user_id": str(apt.user_id),
                "username": getattr(getattr(apt, 'user', None), 'name', None) or "未知",
                "bicycle_id": str(apt.bicycle_id),
                "bicycle_brand": getattr(getattr(apt, 'bicycle', None), 'brand', None) or "未知",
                "type": apt.type,
                "status": apt.status,
                "time_slot_id": str(apt.time_slot_id) if apt.time_slot_id else None,
                "created_at": apt.created_at.isoformat() if apt.created_at else None
            } for apt in waiting_appointments
        ],
        "waiting_bicycles": [
            {
                "id": str(bike.id),
                "brand": bike.brand,
                "owner_id": str(bike.owner_id),
                "owner_username": getattr(getattr(bike, 'owner', None), 'name', None) or "未知",
                "status": bike.status,
                "time_slot_id": str(getattr(db.query(TimeSlot).filter(TimeSlot.bicycle_id == bike.id, TimeSlot.is_booked == "true").first(), 'id', None)) if db.query(TimeSlot).filter(TimeSlot.bicycle_id == bike.id, TimeSlot.is_booked == "true").first() else None,
                "created_at": bike.created_at.isoformat() if bike.created_at else None
            } for bike in waiting_bicycles
        ],
        "locked_slots_with_countdown": slots_with_countdown
    }
