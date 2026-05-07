"""
测试管理员直接操作自行车状态的功能
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.unit.test_announcements import create_test_user, get_access_token, client, TestingSessionLocal
from backend.app.models import Role, Bicycle, BicycleStatus
from uuid import UUID

class TestAdminBicycleOperations:
    """测试管理员直接操作自行车功能"""
    
    def test_admin_update_bicycle_status(self):
        """测试管理员修改自行车状态"""
        db = TestingSessionLocal()
        try:
            # 创建测试管理员
            admin = create_test_user(db, "admin_status@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_status@test.com", "testpass123")
            assert admin_token is not None
            
            # 创建测试自行车
            bike_response = client.post(
                "/bicycles/",
                json={
                    "brand": "Status Test Bike",
                    "condition": 8,
                    "price": 500
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert bike_response.status_code == 200
            bike_id = bike_response.json()["id"]
            
            # 测试修改状态为 IN_STOCK
            status_response = client.put(
                f"/bicycles/{bike_id}/status?new_status=IN_STOCK",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert status_response.status_code == 200
            assert status_response.json()["status"] == "IN_STOCK"
            
            # 测试修改状态为 RESERVED
            status_response = client.put(
                f"/bicycles/{bike_id}/status?new_status=RESERVED",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert status_response.status_code == 200
            assert status_response.json()["status"] == "RESERVED"
            
            # 测试修改状态为 SOLD
            status_response = client.put(
                f"/bicycles/{bike_id}/status?new_status=SOLD",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert status_response.status_code == 200
            assert status_response.json()["status"] == "SOLD"
            
        finally:
            db.close()
    
    def test_admin_update_status_invalid_value(self):
        """测试管理员修改自行车状态为无效值"""
        db = TestingSessionLocal()
        try:
            # 创建测试管理员
            admin = create_test_user(db, "admin_invalid@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_invalid@test.com", "testpass123")
            assert admin_token is not None
            
            # 创建测试自行车
            bike_response = client.post(
                "/bicycles/",
                json={
                    "brand": "Invalid Status Bike",
                    "condition": 7,
                    "price": 400
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert bike_response.status_code == 200
            bike_id = bike_response.json()["id"]
            
            # 尝试修改为无效状态
            status_response = client.put(
                f"/bicycles/{bike_id}/status?new_status=INVALID_STATUS",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert status_response.status_code == 400
            assert "无效的状态值" in status_response.json()["detail"]
            
        finally:
            db.close()
    
    def test_admin_delete_bicycle_with_reason(self):
        """测试管理员删除自行车（带理由）"""
        db = TestingSessionLocal()
        try:
            # 创建测试用户（卖家）
            seller = create_test_user(db, "seller_delete@test.com", role=Role.USER.value, name="Seller User")
            
            # 创建测试管理员
            admin = create_test_user(db, "admin_delete@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_delete@test.com", "testpass123")
            assert admin_token is not None
            
            # 创建测试自行车
            bike_response = client.post(
                "/bicycles/",
                json={
                    "brand": "Delete Test Bike",
                    "condition": 6,
                    "price": 300
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert bike_response.status_code == 200
            bike_id = bike_response.json()["id"]
            
            # 管理员删除自行车
            delete_response = client.post(
                f"/bicycles/{bike_id}/admin-delete?reason=Vehicle does not meet requirements",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert delete_response.status_code == 200
            assert delete_response.json()["message"] == "自行车已被管理员删除"
            
            # 验证自行车已被删除
            get_bike_response = client.get(
                f"/bicycles/{bike_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert get_bike_response.status_code == 404
            
        finally:
            db.close()
    
    def test_admin_delete_bicycle_without_reason(self):
        """测试管理员删除自行车（不带理由）"""
        db = TestingSessionLocal()
        try:
            # 创建测试管理员
            admin = create_test_user(db, "admin_delete_noreason@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_delete_noreason@test.com", "testpass123")
            assert admin_token is not None
            
            # 创建测试自行车
            bike_response = client.post(
                "/bicycles/",
                json={
                    "brand": "No Reason Delete Bike",
                    "condition": 7,
                    "price": 400
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert bike_response.status_code == 200
            bike_id = bike_response.json()["id"]
            
            # 管理员删除自行车（不带理由）
            delete_response = client.post(
                f"/bicycles/{bike_id}/admin-delete",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert delete_response.status_code == 200
            assert delete_response.json()["message"] == "自行车已被管理员删除"
            
        finally:
            db.close()
    
    def test_unauthorized_status_update(self):
        """测试普通用户不能修改自行车状态"""
        db = TestingSessionLocal()
        try:
            # 创建测试用户（普通用户）
            user = create_test_user(db, "user_status@test.com", role=Role.USER.value, name="Normal User")
            user_token = get_access_token("user_status@test.com", "testpass123")
            assert user_token is not None
            
            # 尝试修改状态（应该失败）
            fake_id = "00000000-0000-0000-0000-000000000000"
            status_response = client.put(
                f"/bicycles/{fake_id}/status?new_status=IN_STOCK",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # 应该返回 401 或 403
            assert status_response.status_code in [401, 403]
            
        finally:
            db.close()
    
    def test_unauthorized_admin_delete(self):
        """测试普通用户不能执行管理员删除"""
        db = TestingSessionLocal()
        try:
            # 创建测试用户（普通用户）
            user = create_test_user(db, "user_admin_delete@test.com", role=Role.USER.value, name="Normal User")
            user_token = get_access_token("user_admin_delete@test.com", "testpass123")
            assert user_token is not None
            
            # 尝试删除（应该失败）
            fake_id = "00000000-0000-0000-0000-000000000000"
            delete_response = client.post(
                f"/bicycles/{fake_id}/admin-delete",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # 应该返回 401 或 403
            assert delete_response.status_code in [401, 403]
            
        finally:
            db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
