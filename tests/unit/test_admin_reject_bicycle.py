"""
测试管理员拒绝卖家登记自行车的功能
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.unit.test_announcements import create_test_user, get_access_token, client, TestingSessionLocal
from backend.app.models import Role, Bicycle, BicycleStatus
from uuid import UUID

class TestAdminRejectBicycle:
    """测试管理员拒绝自行车登记功能"""
    
    def test_admin_reject_bicycle(self):
        """测试管理员拒绝自行车登记"""
        db = TestingSessionLocal()
        try:
            # 创建测试用户（卖家）
            seller = create_test_user(db, "seller_reject@test.com", role=Role.USER.value, name="Seller User")
            
            # 创建测试管理员
            admin = create_test_user(db, "admin_reject@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_reject@test.com", "testpass123")
            assert admin_token is not None
            
            # 卖家登记自行车
            bike_response = client.post(
                "/bicycles/",
                json={
                    "brand": "Reject Test Bike",
                    "condition": 7,
                    "price": 400,
                    "description": "This bike should be rejected"
                },
                headers={"Authorization": f"Bearer {admin_token}"}  # 使用 admin_token 因为需要审核
            )
            assert bike_response.status_code == 200
            bike_id = bike_response.json()["id"]
            
            # 管理员审核通过（先 approve）
            approve_response = client.put(
                f"/bicycles/{bike_id}/approve",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert approve_response.status_code == 200
            
            # 管理员拒绝自行车登记
            reject_response = client.put(
                f"/bicycles/{bike_id}/reject?reason=Vehicle does not meet requirements",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert reject_response.status_code == 200
            assert reject_response.json()["message"] == "已拒绝并删除"
            
            # 验证自行车已被删除
            get_bike_response = client.get(
                f"/bicycles/{bike_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert get_bike_response.status_code == 404
            
        finally:
            db.close()
    
    def test_admin_reject_nonexistent_bicycle(self):
        """测试管理员拒绝不存在的自行车"""
        db = TestingSessionLocal()
        try:
            # 创建测试管理员
            admin = create_test_user(db, "admin_reject_nonexist@test.com", role=Role.ADMIN.value, name="Admin User")
            admin_token = get_access_token("admin_reject_nonexist@test.com", "testpass123")
            assert admin_token is not None
            
            # 尝试拒绝不存在的自行车
            fake_id = "00000000-0000-0000-0000-000000000000"
            reject_response = client.put(
                f"/bicycles/{fake_id}/reject?reason=Test",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert reject_response.status_code == 404
            assert "自行车不存在" in reject_response.json()["detail"]
            
        finally:
            db.close()
    
    def test_unauthorized_reject(self):
        """测试普通用户不能拒绝自行车"""
        db = TestingSessionLocal()
        try:
            # 创建测试用户（普通用户）
            user = create_test_user(db, "user_reject@test.com", role=Role.USER.value, name="Normal User")
            user_token = get_access_token("user_reject@test.com", "testpass123")
            assert user_token is not None
            
            # 尝试拒绝自行车（应该失败）
            fake_id = "00000000-0000-0000-0000-000000000000"
            reject_response = client.put(
                f"/bicycles/{fake_id}/reject?reason=Test",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            # 应该返回 401 或 403
            assert reject_response.status_code in [401, 403]
            
        finally:
            db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
