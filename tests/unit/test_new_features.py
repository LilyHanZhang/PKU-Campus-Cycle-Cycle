import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database import Base
from backend.app.models import User as DBUser, Role, Bicycle as DBBicycle, Appointment as DBAppointment, TimeSlot as DBTimeSlot, Message as DBMessage
from backend.app.auth import get_password_hash

def create_test_engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

def create_test_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()

@pytest.fixture(scope="function")
def db_engine():
    engine = create_test_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    session = create_test_session(db_engine)
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_engine, db_session):
    from backend.app.main import app
    from backend.app.database import get_db

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def admin_token(client, db_session):
    user = DBUser(
        email="admin@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Admin User",
        role=Role.ADMIN.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "admin@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

@pytest.fixture
def user_token(client, db_session):
    user = DBUser(
        email="user@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Normal User",
        role=Role.USER.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "user@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

@pytest.fixture
def user2_token(client, db_session):
    user = DBUser(
        email="user2@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Second User",
        role=Role.USER.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "user2@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

# ==================== Time Slot Management Tests ====================

def test_create_time_slot_with_datetime(client, admin_token):
    """测试管理员创建时间段（使用 datetime-local）"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Test Bike",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert time_slot_response.status_code == 200
    data = time_slot_response.json()
    assert data["bicycle_id"] == bike_id
    assert data["appointment_type"] == "pick-up"

def test_update_time_slot(client, admin_token):
    """测试管理员更新时间段"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Test Bike",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    new_start_time = datetime.now() + timedelta(hours=3)
    new_end_time = datetime.now() + timedelta(hours=4)
    
    update_response = client.put(f"/time_slots/{time_slot_id}", json={
        "start_time": new_start_time.isoformat(),
        "end_time": new_end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert update_response.status_code == 200
    assert update_response.json()["id"] == time_slot_id

def test_delete_time_slot(client, admin_token):
    """测试管理员删除时间段"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Test Bike",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    delete_response = client.delete(f"/time_slots/{time_slot_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "删除成功"

def test_user_select_time_slot(client, user_token, admin_token):
    """测试用户选择时间段"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Test Bike",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    select_response = client.put(
        f"/time_slots/select/{apt_id}",
        json={"time_slot_id": time_slot_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert select_response.status_code == 200
    assert select_response.json()["message"] == "时间段选择成功，等待管理员确认"
    
    # 管理员确认时间段
    confirm_response = client.put(f"/time_slots/confirm/{apt_id}", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert confirm_response.status_code == 200
    assert confirm_response.json()["message"] == "时间段确认成功"

def test_get_countdown(client, user_token, admin_token):
    """测试获取交易倒计时"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Test Bike",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    client.put(f"/time_slots/select/{apt_id}?time_slot_id={time_slot_id}", 
               headers={"Authorization": f"Bearer {user_token}"})
    
    # 管理员确认时间段
    client.put(f"/time_slots/confirm/{apt_id}", 
               headers={"Authorization": f"Bearer {admin_token}"})
    
    countdown_response = client.get("/time_slots/my/countdown", 
                                    headers={"Authorization": f"Bearer {user_token}"})
    
    assert countdown_response.status_code == 200
    data = countdown_response.json()
    assert "countdowns" in data
    assert "pending_count" in data
    assert len(data["countdowns"]) == 1
    assert data["countdowns"][0]["appointment_id"] == apt_id

# ==================== Message System Tests ====================

def test_send_message(client, user_token, user2_token):
    """测试用户发送私信"""
    user2_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user2_token}"})
    user2_id = user2_id_response.json()["id"]
    
    message_response = client.post("/messages/", json={
        "receiver_id": str(user2_id),
        "content": "Hello, this is a test message!"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    assert message_response.status_code == 200
    data = message_response.json()
    assert data["content"] == "Hello, this is a test message!"
    assert data["is_read"] == False

def test_cannot_send_to_self(client, user_token):
    """测试用户不能给自己发消息"""
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    my_id = me_response.json()["id"]
    
    message_response = client.post("/messages/", json={
        "receiver_id": str(my_id),
        "content": "Message to self"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    assert message_response.status_code == 400
    assert "不能给自己" in message_response.json()["detail"]

def test_get_my_messages(client, user_token, user2_token):
    """测试获取我的私信"""
    user2_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user2_token}"})
    user2_id = user2_id_response.json()["id"]
    
    client.post("/messages/", json={
        "receiver_id": str(user2_id),
        "content": "Message 1"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    client.post("/messages/", json={
        "receiver_id": str(user2_id),
        "content": "Message 2"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    messages_response = client.get("/messages/", headers={"Authorization": f"Bearer {user_token}"})
    
    assert messages_response.status_code == 200
    assert len(messages_response.json()) == 2

def test_get_unread_count(client, user_token, user2_token):
    """测试获取未读消息数量"""
    user_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    user_id = user_id_response.json()["id"]
    
    client.post("/messages/", json={
        "receiver_id": str(user_id),
        "content": "Unread message"
    }, headers={"Authorization": f"Bearer {user2_token}"})
    
    unread_response = client.get("/messages/unread", headers={"Authorization": f"Bearer {user_token}"})
    
    assert unread_response.status_code == 200
    assert unread_response.json() == 1

def test_mark_message_as_read(client, user_token, user2_token):
    """测试标记消息为已读"""
    user_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    user_id = user_id_response.json()["id"]
    
    message_response = client.post("/messages/", json={
        "receiver_id": str(user_id),
        "content": "Test message"
    }, headers={"Authorization": f"Bearer {user2_token}"})
    message_id = message_response.json()["id"]
    
    mark_response = client.put(f"/messages/{message_id}/read", 
                               headers={"Authorization": f"Bearer {user_token}"})
    
    assert mark_response.status_code == 200
    
    unread_response = client.get("/messages/unread", headers={"Authorization": f"Bearer {user_token}"})
    assert unread_response.json() == 0

def test_admin_can_message_user(client, admin_token, user_token):
    """测试管理员可以主动联系用户"""
    user_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    user_id = user_id_response.json()["id"]
    
    message_response = client.post("/messages/", json={
        "receiver_id": str(user_id),
        "content": "Admin notification: Your appointment is confirmed"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert message_response.status_code == 200
    assert message_response.json()["content"] == "Admin notification: Your appointment is confirmed"

def test_user_can_message_admin(client, user_token, admin_token):
    """测试用户可以联系管理员"""
    admin_id_response = client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    admin_id = admin_id_response.json()["id"]
    
    message_response = client.post("/messages/", json={
        "receiver_id": str(admin_id),
        "content": "I have a question about my appointment"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    assert message_response.status_code == 200
    assert message_response.json()["content"] == "I have a question about my appointment"

# ==================== Complete Appointment Flow Tests ====================

def test_complete_seller_flow(client, user_token, admin_token):
    """测试完整的卖家流程：登记 -> 审核 -> 时间段 -> 确认 -> 评价"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Seller Bike",
        "condition": 8,
        "price": 0
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]
    
    approve_response = client.put(f"/bicycles/{bike_id}/approve", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert approve_response.json()["status"] == "IN_STOCK"
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "drop-off"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "drop-off",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    select_response = client.put(f"/time_slots/select/{apt_id}?time_slot_id={time_slot_id}", 
                                  headers={"Authorization": f"Bearer {user_token}"})
    assert select_response.status_code == 200
    
    confirm_response = client.put(f"/appointments/{apt_id}/confirm-pickup", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert confirm_response.json()["status"] == "COMPLETED"
    
    review_response = client.post("/time_slots/reviews", json={
        "appointment_id": apt_id,
        "rating": 5,
        "content": "Great service!",
        "review_type": "seller_review"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    assert review_response.status_code == 200
    assert review_response.json()["rating"] == 5

def test_complete_buyer_flow(client, user_token, admin_token):
    """测试完整的买家流程：预约 -> 时间段 -> 确认 -> 评价"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Buyer Bike",
        "condition": 7,
        "price": 100
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    time_slot_response = client.post("/time_slots/", json={
        "bicycle_id": bike_id,
        "appointment_type": "pick-up",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }, headers={"Authorization": f"Bearer {admin_token}"})
    time_slot_id = time_slot_response.json()["id"]
    
    select_response = client.put(f"/time_slots/select/{apt_id}?time_slot_id={time_slot_id}", 
                                  headers={"Authorization": f"Bearer {user_token}"})
    assert select_response.status_code == 200
    
    confirm_response = client.put(f"/appointments/{apt_id}/confirm-pickup", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert confirm_response.json()["status"] == "COMPLETED"
    
    review_response = client.post("/time_slots/reviews", json={
        "appointment_id": apt_id,
        "rating": 4,
        "content": "Good bike, smooth transaction",
        "review_type": "buyer_review"
    }, headers={"Authorization": f"Bearer {user_token}"})
    
    assert review_response.status_code == 200
    assert review_response.json()["rating"] == 4

def test_cancel_appointment(client, user_token, admin_token):
    """测试用户取消预约"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Cancel Test Bike",
        "condition": 6,
        "price": 80
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    cancel_response = client.put(f"/appointments/{apt_id}/cancel", 
                                  headers={"Authorization": f"Bearer {user_token}"})
    
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"

def test_admin_reject_appointment(client, user_token, admin_token):
    """测试管理员拒绝预约"""
    bike_response = client.post("/bicycles/", json={
        "brand": "Reject Test Bike",
        "condition": 5,
        "price": 60
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    reject_response = client.put(f"/appointments/{apt_id}/reject?reject_reason=Vehicle no longer available", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "CANCELLED"

# ==================== New Time Slot Proposal Flow Tests ====================

def test_admin_propose_time_slots_for_seller(client, user_token, admin_token):
    """测试管理员为卖家登记提出时间段（新流程）"""
    # 卖家登记自行车
    bike_response = client.post("/bicycles/", json={
        "brand": "Seller Flow Bike",
        "condition": 8,
        "price": 100
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]
    
    # 管理员提出多个时间段
    start_time1 = datetime.now() + timedelta(hours=1)
    end_time1 = datetime.now() + timedelta(hours=2)
    start_time2 = datetime.now() + timedelta(hours=3)
    end_time2 = datetime.now() + timedelta(hours=4)
    
    propose_response = client.post(
        f"/bicycles/{bike_id}/propose-slots",
        json=[
            {"start_time": start_time1.isoformat(), "end_time": end_time1.isoformat()},
            {"start_time": start_time2.isoformat(), "end_time": end_time2.isoformat()}
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert propose_response.status_code == 200
    data = propose_response.json()
    assert "slots" in data
    assert len(data["slots"]) == 2
    assert data["message"] == "已提出 2 个时间段，等待卖家选择"
    
    # 验证自行车状态变为 LOCKED
    bike_status_response = client.get(f"/bicycles/{bike_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert bike_status_response.json()["status"] == "LOCKED"

def test_admin_propose_time_slots_for_buyer(client, user_token, admin_token):
    """测试管理员为买家预约提出时间段（新流程）"""
    # 管理员创建并批准自行车
    bike_response = client.post("/bicycles/", json={
        "brand": "Buyer Flow Bike",
        "condition": 7,
        "price": 80
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    # 买家创建预约
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    # 管理员为预约提出时间段
    start_time = datetime.now() + timedelta(hours=2)
    end_time = datetime.now() + timedelta(hours=3)
    
    propose_response = client.post(
        f"/appointments/{apt_id}/propose-slots",
        json=[
            {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert propose_response.status_code == 200
    data = propose_response.json()
    assert "slots" in data
    assert len(data["slots"]) == 1
    assert data["message"] == "已提出 1 个时间段，等待买家选择"

def test_seller_select_time_slot(client, user_token, admin_token):
    """测试卖家选择时间段（新流程）"""
    # 卖家登记自行车
    bike_response = client.post("/bicycles/", json={
        "brand": "Seller Select Test Bike",
        "condition": 7,
        "price": 90
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]
    
    # 管理员提出时间段
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    
    propose_response = client.post(
        f"/bicycles/{bike_id}/propose-slots",
        json=[
            {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert propose_response.status_code == 200
    
    # 获取时间段列表
    slots_response = client.get(
        f"/time_slots/bicycle/{bike_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert slots_response.status_code == 200
    slots = slots_response.json()
    assert len(slots) > 0
    slot_id = slots[0]["id"]
    
    # 卖家选择时间段
    select_response = client.put(
        f"/time_slots/select-bicycle/{bike_id}",
        json={"time_slot_id": slot_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert select_response.status_code == 200
    data = select_response.json()
    assert data["message"] == "时间段选择成功，等待管理员确认"
    
    # 验证自行车状态保持 LOCKED
    bike_status_response = client.get(f"/bicycles/{bike_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert bike_status_response.json()["status"] == "LOCKED"

def test_buyer_select_time_slot(client, user_token, admin_token):
    """测试买家选择时间段（新流程）"""
    # 管理员创建并批准自行车
    bike_response = client.post("/bicycles/", json={
        "brand": "Buyer Select Test Bike",
        "condition": 8,
        "price": 75
    }, headers={"Authorization": f"Bearer {admin_token}"})
    bike_id = bike_response.json()["id"]
    
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    
    # 买家创建预约
    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    apt_id = apt_response.json()["id"]
    
    # 管理员提出时间段
    start_time = datetime.now() + timedelta(hours=2)
    end_time = datetime.now() + timedelta(hours=3)
    
    propose_response = client.post(
        f"/appointments/{apt_id}/propose-slots",
        json=[
            {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
        ],
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert propose_response.status_code == 200
    
    # 获取时间段列表
    slots_response = client.get(
        f"/time_slots/appointment/{apt_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert slots_response.status_code == 200
    slots = slots_response.json()
    assert len(slots) > 0
    slot_id = slots[0]["id"]
    
    # 买家选择时间段
    select_response = client.put(
        f"/time_slots/select/{apt_id}",
        json={"time_slot_id": slot_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert select_response.status_code == 200
    data = select_response.json()
    assert data["message"] == "时间段选择成功，等待管理员确认"
    
    # 验证预约状态保持 PENDING
    apt_status_response = client.get(f"/appointments/{apt_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert apt_status_response.json()["status"] == "PENDING"


