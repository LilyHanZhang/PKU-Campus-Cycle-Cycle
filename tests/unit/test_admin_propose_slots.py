"""
单元测试：管理后台提出时间段功能
验证管理员在审核通过前后都能提出时间段
"""
import pytest
import requests
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"


class TestAdminProposeTimeSlots:
    """测试管理后台提出时间段功能"""
    
    @pytest.fixture(scope="class")
    def admin_user(self):
        """创建管理员用户"""
        user_data = {
            "email": f"test_admin_propose_{int(time.time())}@example.com",
            "password": "admin123456",
            "name": "测试管理员"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        
        # 设置为管理员（需要现有管理员权限）
        # 这里假设用户已经是管理员
        return user_data
    
    @pytest.fixture(scope="class")
    def seller_user(self):
        """创建卖家用户"""
        user_data = {
            "email": f"test_seller_propose_{int(time.time())}@example.com",
            "password": "seller123456",
            "name": "测试卖家"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_user):
        """获取管理员认证头"""
        login_data = {
            "email": admin_user["email"],
            "password": "admin123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def seller_headers(self, seller_user):
        """获取卖家认证头"""
        login_data = {
            "email": seller_user["email"],
            "password": "seller123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_01_register_bicycle_as_seller(self, seller_headers):
        """测试 1：卖家登记自行车"""
        bicycle_data = {
            "brand": "测试自行车",
            "color": "蓝色",
            "description": "用于测试提出时间段功能",
            "purchase_price": 500,
            "purchase_year": 2023
        }
        response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "测试自行车"
        assert data["status"] == "PENDING_APPROVAL"
        print(f"\n✅ 卖家登记自行车成功，ID: {data['id']}")
        return data["id"]
    
    def test_02_admin_propose_slots_before_approval(self, admin_headers, seller_headers):
        """测试 2：管理员在审核时直接提出时间段（卖家流程）"""
        # 1. 卖家登记自行车
        bicycle_data = {
            "brand": "永久",
            "color": "黑色",
            "description": "管理员直接提出时间段测试",
            "purchase_price": 600,
            "purchase_year": 2022
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bike_id = bike_response.json()["id"]
        
        # 2. 管理员直接提出时间段（会自动审核通过）
        now = datetime.now(timezone.utc)
        time_slots = [
            {
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=2)).isoformat()
            },
            {
                "start_time": (now + timedelta(days=2)).isoformat(),
                "end_time": (now + timedelta(days=2, hours=2)).isoformat()
            }
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        
        assert propose_response.status_code == 200
        data = propose_response.json()
        assert "slots" in data
        assert len(data["slots"]) == 2
        print(f"\n✅ 管理员直接提出时间段成功，状态码：{propose_response.status_code}")
        
        # 3. 验证自行车状态变为 IN_STOCK
        bike_status_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_status_response.json()["status"] == "IN_STOCK"
        print(f"✅ 自行车状态已更新为 IN_STOCK")
        
        # 4. 验证卖家可以看到时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) == 2
        print(f"✅ 卖家可以看到 {len(slots)} 个时间段")
        
        return bike_id
    
    def test_03_admin_approve_then_propose_slots(self, admin_headers):
        """测试 3：管理员先审核通过，然后再提出时间段"""
        # 1. 创建测试用户
        user_data = {
            "email": f"test_user_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户"
        }
        user_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        user_id = user_response.json()["id"]
        
        # 2. 用户登录
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": user_data["email"],
            "password": "test123456"
        })
        user_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # 3. 用户登记自行车
        bicycle_data = {
            "brand": "凤凰",
            "color": "红色",
            "description": "先审核后提出时间段测试",
            "purchase_price": 700,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=user_headers)
        bike_id = bike_response.json()["id"]
        
        # 4. 管理员审核通过
        approve_response = requests.put(
            f"{BASE_URL}/bicycles/{bike_id}/approve",
            headers=admin_headers
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "IN_STOCK"
        print(f"\n✅ 管理员审核通过，状态码：{approve_response.status_code}")
        
        # 5. 管理员提出时间段
        now = datetime.now(timezone.utc)
        time_slots = [
            {
                "start_time": (now + timedelta(days=3)).isoformat(),
                "end_time": (now + timedelta(days=3, hours=1)).isoformat()
            }
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        
        assert propose_response.status_code == 200
        data = propose_response.json()
        assert len(data["slots"]) == 1
        print(f"✅ 管理员在审核后提出时间段成功，状态码：{propose_response.status_code}")
        
        return bike_id
    
    def test_04_seller_select_time_slot(self, seller_headers):
        """测试 4：卖家选择时间段"""
        # 1. 登记自行车
        bicycle_data = {
            "brand": "捷安特",
            "color": "黄色",
            "description": "卖家选择时间段测试",
            "purchase_price": 800,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bike_id = bike_response.json()["id"]
        
        # 2. 获取管理员 token
        admin_data = {
            "email": f"test_admin2_{int(time.time())}@example.com",
            "password": "admin123456",
            "name": "测试管理员 2"
        }
        admin_response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        
        admin_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_data["email"],
            "password": "admin123456"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        
        # 3. 管理员提出时间段
        now = datetime.now(timezone.utc)
        time_slots = [
            {
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=2)).isoformat()
            }
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert propose_response.status_code == 200
        print(f"\n✅ 管理员提出时间段成功")
        
        # 4. 卖家查看时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) > 0
        print(f"✅ 卖家查看到 {len(slots)} 个时间段")
        
        # 5. 卖家选择时间段
        selected_slot = slots[0]
        select_response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=seller_headers
        )
        
        assert select_response.status_code == 200
        print(f"✅ 卖家选择时间段成功，状态码：{select_response.status_code}")
        
        # 6. 验证自行车状态
        bike_status_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        bike_status = bike_status_response.json()["status"]
        assert bike_status == "PENDING_SELLER_SLOT_SELECTION" or bike_status == "LOCKED"
        print(f"✅ 自行车状态更新为：{bike_status}")
    
    def test_05_propose_multiple_slots(self, admin_headers, seller_headers):
        """测试 5：提出多个时间段"""
        # 1. 登记自行车
        bicycle_data = {
            "brand": "美利达",
            "color": "绿色",
            "description": "多个时间段测试",
            "purchase_price": 900,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bike_id = bike_response.json()["id"]
        
        # 2. 提出多个时间段
        now = datetime.now(timezone.utc)
        time_slots = [
            {"start_time": (now + timedelta(days=i, hours=10)).isoformat(), 
             "end_time": (now + timedelta(days=i, hours=12)).isoformat()}
            for i in range(1, 6)  # 5 个时间段
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        
        assert propose_response.status_code == 200
        data = propose_response.json()
        assert len(data["slots"]) == 5
        print(f"\n✅ 成功提出 5 个时间段")
        
        # 3. 验证时间段都可以被选择
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) == 5
        print(f"✅ 卖家可以看到所有 5 个时间段")
    
    def test_06_propose_slots_validation(self, admin_headers, seller_headers):
        """测试 6：时间段验证"""
        # 1. 登记自行车
        bicycle_data = {
            "brand": "测试验证",
            "color": "白色",
            "description": "时间段验证测试",
            "purchase_price": 400,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bike_id = bike_response.json()["id"]
        
        # 2. 测试无效时间段（结束时间早于开始时间）
        now = datetime.now(timezone.utc)
        invalid_slots = [
            {
                "start_time": (now + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=8)).isoformat()  # 结束时间早于开始时间
            }
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=invalid_slots,
            headers=admin_headers
        )
        
        # 应该返回错误
        assert propose_response.status_code == 400 or propose_response.status_code == 422
        print(f"\n✅ 时间段验证正确，拒绝了无效的时间段")
    
    def test_07_frontend_button_display(self):
        """测试 7：前端按钮显示验证"""
        # 验证前端代码中包含提出时间段按钮
        import os
        admin_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "frontend", "src", "app", "admin", "page.tsx"
        )
        
        with open(admin_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证有待审核列表中的提出时间段按钮
        assert 'handleProposeTimeSlots' in content
        assert '提出时间段' in content
        print("\n✅ 前端代码包含提出时间段功能")
        
        # 验证按钮使用了 Calendar 图标
        assert '<Calendar size={16}' in content or 'Calendar size={16}' in content
        print("✅ 提出时间段按钮使用 Calendar 图标")


class TestAdminProposeSlotsEdgeCases:
    """测试边界情况"""
    
    @pytest.fixture(scope="class")
    def admin_headers(self):
        """获取管理员认证头"""
        admin_data = {
            "email": f"test_admin_edge_{int(time.time())}@example.com",
            "password": "admin123456",
            "name": "测试管理员"
        }
        admin_response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        
        admin_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_data["email"],
            "password": "admin123456"
        })
        token = admin_login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_propose_slots_for_sold_bike(self, admin_headers):
        """测试为已售自行车提出时间段应该失败"""
        # 这个测试需要一辆已售的自行车，暂时跳过
        pytest.skip("需要先创建已售状态的自行车")
    
    def test_propose_slots_empty_list(self, admin_headers, seller_headers):
        """测试提出空时间段列表"""
        # 1. 登记自行车
        bicycle_data = {
            "brand": "测试空列表",
            "color": "紫色",
            "description": "空列表测试",
            "purchase_price": 300,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bike_id = bike_response.json()["id"]
        
        # 2. 提出空时间段列表
        propose_response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=[],
            headers=admin_headers
        )
        
        # 应该返回错误
        assert propose_response.status_code == 400 or propose_response.status_code == 422
        print("\n✅ 正确拒绝了空时间段列表")
