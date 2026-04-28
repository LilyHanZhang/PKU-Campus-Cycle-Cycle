"""
卖家流程单元测试：管理员为 PENDING_APPROVAL 状态的自行车提出时间段

测试场景：
1. 卖家登记自行车（状态：PENDING_APPROVAL）
2. 管理员直接提出时间段（无需预约）
3. 验证自行车自动审核通过并变为 LOCKED 状态

正确流程：
卖家登记 → PENDING_APPROVAL
管理员提出时间段（无需预约）→ 自动审核通过 → IN_STOCK → LOCKED
卖家选择时间段 → LOCKED
管理员确认预约 → RESERVED
线下交易完成
管理员确认交易 → SOLD
"""
import pytest
import requests
from datetime import datetime, timedelta
from uuid import uuid4

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def seller_token():
    """获取卖家 token"""
    # 尝试登录
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "seller_test@example.com",
        "password": "test123"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # 注册新账号
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "seller_test@example.com",
        "password": "test123",
        "role": "SELLER"
    })
    
    if response.status_code == 200:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "seller_test@example.com",
            "password": "test123"
        })
        return response.json()["access_token"]
    
    return None


def create_test_bicycle(seller_token):
    """创建测试自行车"""
    headers = {"Authorization": f"Bearer {seller_token}"}
    response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Test Brand",
        "condition": 8,
        "price": 100.0,
        "description": "测试自行车 - 卖家流程",
        "image_url": "https://example.com/bike.jpg"
    }, headers=headers)
    
    assert response.status_code == 200
    bike = response.json()
    assert bike["status"] == "PENDING_APPROVAL"
    return bike


def test_propose_slots_for_pending_bicycle(admin_token, seller_token):
    """测试为 PENDING_APPROVAL 状态的自行车提出时间段（无需预约）"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. 创建自行车（PENDING_APPROVAL）
    bike = create_test_bicycle(seller_token)
    bike_id = bike["id"]
    
    # 2. 管理员直接提出时间段（不需要创建预约）
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
        json=time_slots,
        headers=headers
    )
    
    # 3. 验证响应
    assert response.status_code == 200, f"提出时间段失败：{response.text}"
    result = response.json()
    assert "message" in result or "slots" in result
    
    # 4. 验证自行车状态变为 LOCKED
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=headers)
    assert response.status_code == 200
    bike_data = response.json()
    assert bike_data["status"] == "LOCKED", f"自行车状态应该是 LOCKED，实际是 {bike_data['status']}"


def test_propose_slots_with_appointment(admin_token, seller_token):
    """测试有预约时提出时间段"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. 创建自行车（PENDING_APPROVAL）
    bike = create_test_bicycle(seller_token)
    bike_id = bike["id"]
    
    # 2. 先审核通过
    response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=headers)
    assert response.status_code == 200
    
    # 3. 创建预约（drop-off 类型）
    response = requests.post(f"{BASE_URL}/appointments/", json={
        "bicycle_id": bike_id,
        "type": "drop-off",
        "notes": "测试预约"
    }, headers=headers)
    
    assert response.status_code == 200
    appointment = response.json()
    assert appointment["type"] == "drop-off"
    assert appointment["status"] == "PENDING"
    
    # 4. 提出时间段
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
        json=time_slots,
        headers=headers
    )
    
    # 5. 验证响应
    assert response.status_code == 200, f"提出时间段失败：{response.text}"
    
    # 6. 验证自行车状态变为 LOCKED
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=headers)
    assert response.status_code == 200
    bike_data = response.json()
    assert bike_data["status"] == "LOCKED"


def test_propose_slots_for_in_stock_bicycle(admin_token):
    """测试 IN_STOCK 状态的自行车可以提出时间段（买家流程）"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. 创建买家用户
    buyer_email = f"buyer_test_{int(__import__('time').time())}@test.com"
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": buyer_email,
        "password": "password123",
        "name": "Test Buyer",
        "role": "USER"
    })
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": buyer_email,
        "password": "password123"
    })
    buyer_token = response.json()["access_token"]
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    
    # 2. 买家创建自行车（PENDING_APPROVAL）
    response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Test Bike",
        "condition": 8,
        "price": 300
    }, headers=buyer_headers)
    assert response.status_code == 200
    bike_id = response.json()["id"]
    
    # 2. 审核通过，变为 IN_STOCK
    response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=headers)
    assert response.status_code == 200
    
    # 3. 提出时间段（买家流程，会自动创建预约）
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
        json=time_slots,
        headers=headers
    )
    
    # 4. 验证成功
    assert response.status_code == 200
    
    # 5. 验证状态变为 LOCKED
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=headers)
    assert response.status_code == 200
    bike_data = response.json()
    assert bike_data["status"] == "LOCKED"
    
    # 6. 验证创建了 pick-up 类型的预约
    response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=headers)
    appointments = response.json()
    bike_appointment = None
    for apt in appointments:
        if apt["bicycle_id"] == bike_id:
            bike_appointment = apt
            break
    
    assert bike_appointment is not None
    assert bike_appointment["type"] == "pick-up"  # 买家流程


def test_propose_slots_creates_correct_appointment_type(admin_token, seller_token):
    """测试 PENDING_APPROVAL 状态创建 pick-up 时间段"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. 创建自行车
    bike = create_test_bicycle(seller_token)
    bike_id = bike["id"]
    
    # 2. 提出时间段
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
        json=time_slots,
        headers=headers
    )
    
    assert response.status_code == 200
    
    # 3. 验证时间段类型
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}/time-slots", headers=headers)
    if response.status_code == 200:
        slots = response.json()
        assert len(slots) > 0
        # PENDING_APPROVAL 应该创建 pick-up 时间段
        for slot in slots:
            assert slot.get("appointment_type") == "pick-up"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
