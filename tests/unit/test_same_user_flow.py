#!/usr/bin/env python3
"""
测试同一个用户的卖家和买家流程不会混淆
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestSameUserSellerAndBuyer:
    """测试同一个用户的卖家和买家流程隔离"""
    
    def test_01_same_user_seller_and_buyer_flow_isolation(self, admin_token):
        """测试 1：同一个用户的卖家和买家流程不会混淆"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 卖家流程 ==========
        print("\n【卖家流程】")
        print("1. 管理员作为卖家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        seller_bike_id = response.json()["id"]
        print(f"   卖家自行车 ID: {seller_bike_id}")
        
        print("2. 管理员提出时间段（卖家流程）")
        now = datetime.now(timezone.utc)
        seller_time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{seller_bike_id}/propose-slots",
            json=seller_time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        print("3. 管理员（作为卖家）选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{seller_bike_id}", headers=admin_headers)
        assert response.status_code == 200
        seller_slots = response.json()
        assert len(seller_slots) > 0
        print(f"   时间段类型：{seller_slots[0]['appointment_type']}")
        assert seller_slots[0]["appointment_type"] == "pick-up"  # 卖家流程应该是 pick-up
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{seller_bike_id}",
            json={"time_slot_id": str(seller_slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   选择状态码：{response.status_code}")
        
        # ========== 买家流程 ==========
        print("\n【买家流程】")
        print("4. 管理员作为买家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Buyer Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        buyer_bike_id = response.json()["id"]
        print(f"   买家自行车 ID: {buyer_bike_id}")
        
        print("5. 另一个管理员审核通过")
        admin2_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin2_token = admin2_response.json()["access_token"]
        admin2_headers = {"Authorization": f"Bearer {admin2_token}"}
        
        response = requests.put(f"{BASE_URL}/bicycles/{buyer_bike_id}/approve", headers=admin2_headers)
        assert response.status_code == 200
        print(f"   审核后状态：{response.json()['status']}")
        
        print("6. 管理员提出时间段（买家流程）")
        buyer_time_slots = [{
            "start_time": (now + timedelta(days=2)).isoformat(),
            "end_time": (now + timedelta(days=2, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{buyer_bike_id}/propose-slots",
            json=buyer_time_slots,
            headers=admin2_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        print("7. 管理员（作为买家）选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{buyer_bike_id}", headers=admin_headers)
        assert response.status_code == 200
        buyer_slots = response.json()
        assert len(buyer_slots) > 0
        print(f"   时间段类型：{buyer_slots[0]['appointment_type']}")
        assert buyer_slots[0]["appointment_type"] == "drop-off"  # 买家流程应该是 drop-off
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{buyer_bike_id}",
            json={"time_slot_id": str(buyer_slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   选择状态码：{response.status_code}")
        
        # ========== 确认时间段 ==========
        print("\n【确认时间段】")
        print("8. 确认卖家流程的时间段")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{seller_bike_id}",
            headers=admin_headers
        )
        print(f"   确认状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200
        
        # 检查卖家自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{seller_bike_id}", headers=admin_headers)
        assert response.status_code == 200
        seller_bike_status = response.json()["status"]
        print(f"   卖家自行车状态：{seller_bike_status}")
        # 卖家流程应该是 RESERVED（等待线下交易）
        assert seller_bike_status == "RESERVED", f"卖家流程自行车状态应该是 RESERVED，实际是 {seller_bike_status}"
        
        print("9. 确认买家流程的时间段")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{buyer_bike_id}",
            headers=admin_headers
        )
        print(f"   确认状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200
        
        # 检查买家自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{buyer_bike_id}", headers=admin_headers)
        assert response.status_code == 200
        buyer_bike_status = response.json()["status"]
        print(f"   买家自行车状态：{buyer_bike_status}")
        # 买家流程应该是 SOLD（交易完成）
        assert buyer_bike_status == "SOLD", f"买家流程自行车状态应该是 SOLD，实际是 {buyer_bike_status}"
        
        print("\n✅ 卖家和买家流程完全隔离，没有混淆！")
    
    def test_02_seller_flow_confirmed_bike_status(self, admin_token):
        """测试 2：卖家流程确认后自行车状态为 RESERVED"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建卖家自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Seller Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 提出时间段
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 选择时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 确认时间段
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 检查自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        assert bike_status == "RESERVED", f"卖家流程自行车状态应该是 RESERVED，实际是 {bike_status}"
    
    def test_03_buyer_flow_confirmed_bike_status(self, admin_token):
        """测试 3：买家流程确认后自行车状态为 SOLD"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建买家自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Buyer Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 审核
        admin2_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin2_token = admin2_response.json()["access_token"]
        admin2_headers = {"Authorization": f"Bearer {admin2_token}"}
        
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin2_headers)
        assert response.status_code == 200
        
        # 提出时间段
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin2_headers
        )
        assert response.status_code == 200
        
        # 选择时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 确认时间段
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 检查自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        assert bike_status == "SOLD", f"买家流程自行车状态应该是 SOLD，实际是 {bike_status}"


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
