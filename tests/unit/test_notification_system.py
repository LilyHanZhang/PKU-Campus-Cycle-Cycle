#!/usr/bin/env python3
"""
测试通知系统
确保管理员操作后，用户能收到私信通知
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestNotificationSystem:
    """测试通知系统"""
    
    def test_01_admin_propose_slots_seller_gets_notified(self, admin_token):
        """测试 1：管理员提出时间段后，卖家收到通知"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建卖家用户
        seller_email = f"seller_notify_{int(time.time())}@test.com"
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seller_email,
            "password": "password123",
            "name": "Test Seller",
            "role": "USER"
        })
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seller_email,
            "password": "password123"
        })
        seller_token = response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 2. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 3. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 4. 管理员提出时间段
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
        
        # 5. 检查卖家是否收到消息
        response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 应该有至少一条消息
        assert len(messages) > 0
        
        # 找到关于时间段的消息
        slot_message = None
        for msg in messages:
            if "时间段" in msg["content"] and ("自行车" in msg["content"] or "预约" in msg["content"]):
                slot_message = msg
                break
        
        assert slot_message is not None, "卖家应该收到关于时间段的通知"
        assert "管理员" in slot_message["content"]
        assert slot_message["is_read"] == False
    
    def test_02_seller_select_slots_admin_gets_notified(self, admin_token):
        """测试 2：卖家选择时间段后，管理员收到通知"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建卖家用户
        seller_email = f"seller_select_{int(time.time())}@test.com"
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seller_email,
            "password": "password123",
            "name": "Test Seller",
            "role": "USER"
        })
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seller_email,
            "password": "password123"
        })
        seller_token = response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 2. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 3. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 4. 管理员提出时间段
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
        
        # 5. 卖家查看时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        # 6. 卖家选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=seller_headers
        )
        assert response.status_code == 200
        
        # 7. 检查管理员是否收到消息
        response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 应该有至少一条消息
        assert len(messages) > 0
        
        # 找到关于卖家选择时间段的消息
        select_message = None
        for msg in messages:
            if "卖家已选择时间段" in msg["content"] or ("选择时间段" in msg["content"] and "请确认" in msg["content"]):
                select_message = msg
                break
        
        assert select_message is not None, "管理员应该收到卖家选择时间段的通知"
    
    def test_03_admin_confirm_seller_gets_notified(self, admin_token):
        """测试 3：管理员确认时间段后，卖家收到通知"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建卖家用户
        seller_email = f"seller_confirm_{int(time.time())}@test.com"
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seller_email,
            "password": "password123",
            "name": "Test Seller",
            "role": "USER"
        })
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seller_email,
            "password": "password123"
        })
        seller_token = response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 2. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 3. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 4. 管理员提出时间段
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
        
        # 5. 卖家选择时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=seller_headers
        )
        assert response.status_code == 200
        
        # 6. 管理员确认时间段
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 7. 检查卖家是否收到确认消息
        response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 找到关于确认的消息
        confirm_message = None
        for msg in messages:
            if "确认" in msg["content"] and ("自行车" in msg["content"] or "预约" in msg["content"] or "按时" in msg["content"]):
                confirm_message = msg
                break
        
        assert confirm_message is not None, "卖家应该收到确认通知"
        assert "按时" in confirm_message["content"]
    
    def test_04_buyer_flow_notifications(self, admin_token):
        """测试 4：买家流程的通知"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建买家用户
        buyer_email = f"buyer_notify_{int(time.time())}@test.com"
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
        
        # 2. 买家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=buyer_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 3. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 4. 管理员提出时间段
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
        
        # 5. 检查买家是否收到消息
        response = requests.get(f"{BASE_URL}/messages/", headers=buyer_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 应该有至少一条消息
        assert len(messages) > 0
        
        # 找到关于时间段的消息
        slot_message = None
        for msg in messages:
            if "时间段" in msg["content"] and ("自行车" in msg["content"] or "预约" in msg["content"]):
                slot_message = msg
                break
        
        assert slot_message is not None, "买家应该收到关于时间段的通知"
        
        # 6. 买家查看时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=buyer_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        # 7. 买家选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=buyer_headers
        )
        assert response.status_code == 200
        
        # 8. 检查管理员是否收到买家选择的消息
        response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 找到关于买家选择时间段的消息
        select_message = None
        for msg in messages:
            if "已选择时间段" in msg["content"] and "请确认" in msg["content"]:
                select_message = msg
                break
        
        assert select_message is not None, "管理员应该收到买家选择时间段的通知"
        
        # 9. 管理员确认时间段
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 10. 检查买家是否收到确认消息
        response = requests.get(f"{BASE_URL}/messages/", headers=buyer_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 找到关于确认的消息
        confirm_message = None
        for msg in messages:
            if "确认" in msg["content"] and ("自行车" in msg["content"] or "预约" in msg["content"] or "按时" in msg["content"]):
                confirm_message = msg
                break
        
        assert confirm_message is not None, "买家应该收到确认通知"


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
