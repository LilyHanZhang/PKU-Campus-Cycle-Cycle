#!/usr/bin/env python3
"""
测试卖家和管理员是同一人的情况
验证时间段选择和查看功能正常工作
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestSellerIsAdmin:
    """测试卖家和管理员是同一人的场景"""
    
    def test_01_admin_as_seller_can_select_time_slots(self, admin_token):
        """测试 1：管理员作为卖家登记自行车后可以选择时间段"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 管理员作为卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        # 2. 另一个管理员审核通过
        # 获取第二个管理员的 token
        admin2_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin2_token = admin2_response.json()["access_token"]
        admin2_headers = {"Authorization": f"Bearer {admin2_token}"}
        
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin2_headers)
        assert response.status_code == 200
        print(f"   审核后状态：{response.json()['status']}")
        
        # 3. 第三个管理员提出时间段
        admin3_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin3_token = admin3_response.json()["access_token"]
        admin3_headers = {"Authorization": f"Bearer {admin3_token}"}
        
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin3_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        # 4. 查看预约类型
        response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
        appointments = response.json()
        bike_appointment = None
        for apt in appointments:
            if apt["bicycle_id"] == bike_id:
                bike_appointment = apt
                break
        
        assert bike_appointment is not None
        print(f"   预约类型：{bike_appointment['type']}")
        # 卖家流程，预约类型应该是 drop-off
        assert bike_appointment["type"] == "drop-off"
        
        # 5. 管理员（作为卖家）查看时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        print(f"   时间段数量：{len(slots)}")
        assert len(slots) > 0
        
        # 卖家流程，时间段类型应该是 pick-up
        print(f"   时间段类型：{slots[0]['appointment_type']}")
        assert slots[0]["appointment_type"] == "pick-up"
        
        # 6. 管理员（作为卖家）选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=admin_headers
        )
        print(f"   选择状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200, f"选择失败：{response.text}"
        assert "时间段选择成功" in response.json()["message"]
    
    def test_02_seller_can_select_time_slots_after_admin_proposes(self, admin_token):
        """测试 2：管理员提出时间段后卖家可以选择"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建卖家用户
        seller_email = f"seller2_{int(time.time())}@test.com"
        seller_response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seller_email,
            "password": "password123",
            "name": "Test Seller 2",
            "role": "USER"
        })
        assert seller_response.status_code == 200
        
        seller_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seller_email,
            "password": "password123"
        })
        seller_token = seller_login.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 2. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        # 3. 管理员审核并提出时间段
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        # 直接提出时间段（从 PENDING_APPROVAL 状态）
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        # 4. 卖家查看时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert response.status_code == 200
        slots = response.json()
        print(f"   时间段数量：{len(slots)}")
        assert len(slots) > 0
        
        # 5. 卖家选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=seller_headers
        )
        print(f"   选择状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200, f"选择失败：{response.text}"
        assert "时间段选择成功" in response.json()["message"]


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
