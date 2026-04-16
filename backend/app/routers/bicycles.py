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
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")

    bike.status = BicycleStatus.IN_STOCK.value
    db.commit()
    db.refresh(bike)
    return bike

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

@appointment_router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)
    if current_user["role"] == "USER":
        query = query.filter(Appointment.user_id == UUID(current_user["user_id"]))
    if status:
        query = query.filter(Appointment.status == status)

    appointments = query.all()
    return appointments

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
