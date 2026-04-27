#!/usr/bin/env python3
"""
单元测试：买家流程
测试买家从登记到完成交易的完整流程
"""

import pytest
import requests
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestBuyerFlow:
    """买家流程测试类"""
    
    @pytest.fixture(scope="class")
    def buyer_token(self):
        """创建买家用户并返回 token"""
        buyer_email = f"buyer_test_{int(time.time())}@test.com"
        
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
    def buyer_bicycle(self, buyer_token):
        """买家登记自行车"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike",
            "condition": 8,
            "price": 300,
            "description": "买家登记的自行车"
        }, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]
    
    def test_01_buyer_register_bicycle(self, buyer_token, buyer_bicycle):
        """测试 1：买家登记自行车"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = requests.get(f"{BASE_URL}/bicycles/{buyer_bicycle}", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "PENDING_APPROVAL"
    
    def test_02_admin_approve(self, admin_token, buyer_bicycle):
        """测试 2：管理员审核通过"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.put(f"{BASE_URL}/bicycles/{buyer_bicycle}/approve", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "IN_STOCK"
    
    def test_03_admin_propose_time_slots(self, admin_token, buyer_bicycle):
        """测试 3：管理员提出时间段"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        now = datetime.now(timezone.utc)
        time_slots = [
            {
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=2)).isoformat()
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{buyer_bicycle}/propose-slots",
            json=time_slots,
            headers=headers
        )
        assert response.status_code == 200
        
        # 验证状态变为 LOCKED
        response = requests.get(f"{BASE_URL}/bicycles/{buyer_bicycle}", headers=headers)
        assert response.json()["status"] == "LOCKED"
    
    def test_04_buyer_select_time_slot(self, buyer_token, buyer_bicycle):
        """测试 4：买家选择时间段"""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        
        # 获取时间段
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{buyer_bicycle}", headers=headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        
        # 选择时间段
        selected_slot = slots[0]
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{buyer_bicycle}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=headers
        )
        assert response.status_code == 200
        
        # 验证状态保持 LOCKED
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{BASE_URL}/bicycles/{buyer_bicycle}", headers=admin_headers)
        assert response.json()["status"] == "LOCKED"
    
    def test_05_admin_confirm_appointment(self, admin_token, buyer_bicycle):
        """测试 5：管理员确认预约"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取预约
        response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=headers)
        appointments = response.json()
        bike_appointment = None
        for apt in appointments:
            if apt["bicycle_id"] == buyer_bicycle:
                bike_appointment = apt
                break
        
        assert bike_appointment is not None
        
        # 确认预约
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm/{bike_appointment['id']}",
            headers=headers
        )
        assert response.status_code == 200
        
        # 验证状态变为 SOLD
        response = requests.get(f"{BASE_URL}/bicycles/{buyer_bicycle}", headers=headers)
        assert response.json()["status"] == "SOLD"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
