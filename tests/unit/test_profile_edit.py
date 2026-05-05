"""
单元测试：测试用户个人信息修改功能

测试用例：
1. 测试更新用户信息（用户名、邮箱、头像）API 端点存在
2. 测试更新密码 API 端点存在
3. 测试上传头像 API 端点存在
4. 测试权限验证
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.main import app

client = TestClient(app)


def get_auth_token(username: str = "testuser", password: str = "Test1234!"):
    """获取认证 token"""
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


class TestUserProfileUpdate:
    """测试用户信息更新"""
    
    @pytest.mark.skip(reason="需要数据库初始化和真实用户")
    def test_update_user_name(self):
        """测试更新用户名"""
        token = get_auth_token()
        if not token:
            pytest.skip("需要测试用户")
        
        headers = {"Authorization": f"Bearer {token}"}
        # 需要先获取用户 ID
        user_response = client.get("/users/me", headers=headers)
        if user_response.status_code != 200:
            pytest.skip("无法获取用户信息")
        
        user_id = user_response.json()["id"]
        
        response = client.put(
            f"/users/{user_id}",
            json={"name": "Updated Name"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    @pytest.mark.skip(reason="需要数据库初始化和真实用户")
    def test_update_user_email(self):
        """测试更新邮箱"""
        token = get_auth_token()
        if not token:
            pytest.skip("需要测试用户")
        
        headers = {"Authorization": f"Bearer {token}"}
        user_response = client.get("/users/me", headers=headers)
        if user_response.status_code != 200:
            pytest.skip("无法获取用户信息")
        
        user_id = user_response.json()["id"]
        
        response = client.put(
            f"/users/{user_id}",
            json={"email": "new_email@example.com"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new_email@example.com"
    
    def test_update_user_api_exists(self):
        """测试更新用户 API 端点存在"""
        response = client.put("/users/test-id", json={})
        # 应该返回 401 或 403（未授权），而不是 404
        assert response.status_code in [401, 403, 422]
    
    def test_update_password_api_exists(self):
        """测试更新密码 API 端点存在"""
        response = client.put("/users/test-id/password", json={})
        # 应该返回 401 或 403（未授权），而不是 404
        assert response.status_code in [401, 403, 422]
    
    def test_upload_avatar_api_exists(self):
        """测试上传头像 API 端点存在"""
        response = client.post("/users/test-id/upload-avatar", files={})
        # 应该返回 401 或 403（未授权），而不是 404
        assert response.status_code in [401, 403, 422]


class TestPasswordUpdate:
    """测试密码修改"""
    
    @pytest.mark.skip(reason="需要数据库初始化和真实用户")
    def test_update_password_success(self):
        """测试成功修改密码"""
        token = get_auth_token()
        if not token:
            pytest.skip("需要测试用户")
        
        headers = {"Authorization": f"Bearer {token}"}
        user_response = client.get("/users/me", headers=headers)
        if user_response.status_code != 200:
            pytest.skip("无法获取用户信息")
        
        user_id = user_response.json()["id"]
        
        response = client.put(
            f"/users/{user_id}/password",
            json={
                "current_password": "Test1234!",
                "new_password": "NewPass123!"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "密码修改成功"
    
    def test_password_update_requires_auth(self):
        """测试密码修改需要认证"""
        response = client.put("/users/test-id/password", json={})
        assert response.status_code in [401, 403, 422]


class TestAvatarUpload:
    """测试头像上传"""
    
    @pytest.mark.skip(reason="需要数据库初始化和真实用户")
    def test_upload_avatar_success(self):
        """测试成功上传头像"""
        token = get_auth_token()
        if not token:
            pytest.skip("需要测试用户")
        
        headers = {"Authorization": f"Bearer {token}"}
        user_response = client.get("/users/me", headers=headers)
        if user_response.status_code != 200:
            pytest.skip("无法获取用户信息")
        
        user_id = user_response.json()["id"]
        
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        files = {"file": ("test_avatar.png", img_byte_arr, "image/png")}
        
        response = client.post(
            f"/users/{user_id}/upload-avatar",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "filename" in data
    
    def test_upload_avatar_requires_auth(self):
        """测试上传头像需要认证"""
        response = client.post("/users/test-id/upload-avatar", files={})
        assert response.status_code in [401, 403, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
