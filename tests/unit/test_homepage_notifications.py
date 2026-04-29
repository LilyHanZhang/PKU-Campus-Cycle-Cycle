#!/usr/bin/env python3
"""
测试主页消息通知显示功能
验证未读消息能够在主页正确显示
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestHomepageNotifications:
    """测试主页消息通知显示"""
    
    def test_01_unread_messages_count_api(self, user_token):
        """测试 1：未读消息数量 API"""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # 获取未读消息数量
        response = requests.get(f"{BASE_URL}/messages/unread", headers=headers)
        assert response.status_code == 200
        count = response.json()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_02_receive_message_increases_count(self, admin_token):
        """测试 2：收到消息后未读数量增加"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 创建用户
        user_email = f"notify_test_{int(time.time())}@test.com"
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": user_email,
            "password": "password123",
            "name": "Test User",
            "role": "USER"
        })
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": user_email,
            "password": "password123"
        })
        user_token = response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # 2. 获取初始未读消息数量
        response = requests.get(f"{BASE_URL}/messages/unread", headers=user_headers)
        assert response.status_code == 200
        initial_count = response.json()
        
        # 3. 管理员发送消息
        response = requests.post(f"{BASE_URL}/messages/", json={
            "receiver_id": user_email,  # 使用邮箱查找用户
            "content": "Test notification message"
        }, headers=admin_headers)
        
        # 注意：API 可能需要用户 ID 而不是邮箱
        # 获取用户 ID
        response = requests.get(f"{BASE_URL}/auth/me", headers=user_headers)
        user_id = response.json()["id"]
        
        response = requests.post(f"{BASE_URL}/messages/", json={
            "receiver_id": str(user_id),
            "content": "Test notification message"
        }, headers=admin_headers)
        assert response.status_code == 200
        
        # 4. 检查未读消息数量增加
        response = requests.get(f"{BASE_URL}/messages/unread", headers=user_headers)
        assert response.status_code == 200
        new_count = response.json()
        assert new_count > initial_count
    
    def test_03_admin_propose_slots_creates_notification(self, admin_token):
        """测试 3：管理员提出时间段后创建通知"""
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
        
        # 2. 获取初始未读消息数量
        response = requests.get(f"{BASE_URL}/messages/unread", headers=seller_headers)
        assert response.status_code == 200
        initial_count = response.json()
        
        # 3. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 4. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 5. 管理员提出时间段
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
        
        # 6. 检查卖家未读消息数量增加
        response = requests.get(f"{BASE_URL}/messages/unread", headers=seller_headers)
        assert response.status_code == 200
        new_count = response.json()
        assert new_count > initial_count
    
    def test_04_seller_select_slots_notifies_admin(self, admin_token):
        """测试 4：卖家选择时间段后通知管理员"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. 获取管理员初始未读消息数量
        response = requests.get(f"{BASE_URL}/messages/unread", headers=admin_headers)
        assert response.status_code == 200
        initial_count = response.json()
        
        # 2. 创建卖家用户
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
        
        # 3. 卖家登记自行车
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300
        }, headers=seller_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        # 4. 管理员审核通过
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert response.status_code == 200
        
        # 5. 管理员提出时间段
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
        
        # 6. 卖家查看时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        # 7. 卖家选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=seller_headers
        )
        assert response.status_code == 200
        
        # 8. 检查管理员未读消息数量增加
        response = requests.get(f"{BASE_URL}/messages/unread", headers=admin_headers)
        assert response.status_code == 200
        new_count = response.json()
        assert new_count > initial_count


@pytest.fixture(scope="module")
def user_token():
    """创建测试用户并返回 token"""
    user_email = f"test_user_{int(time.time())}@test.com"
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": user_email,
        "password": "password123",
        "name": "Test User",
        "role": "USER"
    })
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": user_email,
        "password": "password123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
