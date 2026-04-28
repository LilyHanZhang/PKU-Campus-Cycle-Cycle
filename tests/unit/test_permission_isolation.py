#!/usr/bin/env python3
"""
单元测试：买家和卖家流程权限隔离测试
验证买家和卖家不能互相查看或选择对方的时间段
"""

import pytest
import requests
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestBuyerSellerPermissionIsolation:
    """买家和卖家流程权限隔离测试类"""
    
    @pytest.fixture(scope="class")
    def seller_token(self):
        """创建卖家用户并返回 token"""
        seller_email = f"seller_perm_{int(time.time())}@test.com"
        
        # 注册
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": seller_email,
            "password": "password123",
            "name": "Test Seller",
            "role": "USER"
        })
        assert response.status_code == 200
        
        # 登录
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": seller_email,
            "password": "password123"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def buyer_token(self):
        """创建买家用户并返回 token"""
        buyer_email = f"buyer_perm_{int(time.time())}@test.com"
        
        # 注册
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": buyer_email,
            "password": "password123",
            "name": "Test Buyer",
            "role": "USER"
        })
        assert response.status_code == 200
        
        # 登录
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": buyer_email,
            "password": "password123"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """管理员登录并返回 token"""
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def seller_bicycle(self, seller_token):
        """卖家登记自行车（卖家流程）"""
        headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Bike",
            "condition": 8,
            "price": 300,
            "description": "卖家登记的自行车"
        }, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def buyer_bicycle(self, buyer_token):
        """买家登记自行车（买家流程）"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Buyer Bike",
            "condition": 8,
            "price": 300,
            "description": "买家登记的自行车"
        }, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    
    def test_01_seller_flow_seller_can_view_slots(self, seller_token, seller_bicycle, admin_token):
        """测试 1：卖家流程中，卖家可以查看自己的时间段"""
        # 管理员提出时间段（卖家流程，pick-up 类型）
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{seller_bicycle}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 卖家查看时间段
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{seller_bicycle}",
            headers=seller_headers
        )
        assert response.status_code == 200
        slots = response.json()
        # 卖家流程，卖家可以看到时间段（pick-up 类型）
        assert len(slots) > 0
        assert slots[0]["appointment_type"] == "pick-up"
    
    def test_02_buyer_cannot_view_seller_slots(self, buyer_token, seller_bicycle):
        """测试 2：买家不能查看卖家流程的时间段"""
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
        
        # 买家查看卖家自行车的时间段
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{seller_bicycle}",
            headers=buyer_headers
        )
        
        # 买家没有权限，应该返回 403
        assert response.status_code == 403
    
    def test_03_buyer_flow_buyer_can_view_slots(self, buyer_token, buyer_bicycle, admin_token):
        """测试 3：买家流程中，买家可以查看自己的时间段"""
        # 管理员审核通过
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.put(
            f"{BASE_URL}/bicycles/{buyer_bicycle}/approve",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 管理员提出时间段（买家流程，pick-up 类型预约，drop-off 类型时间段）
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{buyer_bicycle}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 买家查看时间段
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{buyer_bicycle}",
            headers=buyer_headers
        )
        assert response.status_code == 200
        slots = response.json()
        # 买家流程，买家可以看到时间段（drop-off 类型）
        assert len(slots) > 0
        assert slots[0]["appointment_type"] == "drop-off"
    
    def test_04_seller_cannot_view_buyer_slots(self, seller_token, buyer_bicycle):
        """测试 4：卖家不能查看买家流程的时间段"""
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 卖家查看买家自行车的时间段
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{buyer_bicycle}",
            headers=seller_headers
        )
        
        # 卖家不是所有者，没有预约，应该返回 403
        assert response.status_code == 403
    
    def test_05_seller_cannot_select_buyer_slots(self, seller_token, buyer_bicycle, admin_token):
        """测试 5：卖家不能选择买家流程的时间段"""
        # 先获取时间段
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{buyer_bicycle}",
            headers=admin_headers
        )
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        # 卖家尝试选择时间段
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{buyer_bicycle}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=seller_headers
        )
        
        # 卖家不是所有者，应该返回 403
        assert response.status_code == 403
    
    def test_06_buyer_cannot_select_seller_slots(self, buyer_token, seller_bicycle, admin_token):
        """测试 6：买家不能选择卖家流程的时间段"""
        # 先获取时间段（管理员查看）
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{seller_bicycle}",
            headers=admin_headers
        )
        assert response.status_code == 200
        slots = response.json()
        
        if len(slots) > 0:
            # 买家尝试选择时间段
            buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
            response = requests.put(
                f"{BASE_URL}/time_slots/select-bicycle/{seller_bicycle}",
                json={"time_slot_id": str(slots[0]["id"])},
                headers=buyer_headers
            )
            
            # 买家没有权限，应该返回 403
            assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
