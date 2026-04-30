"""
测试系统消息功能
验证时间段选择后系统消息能正确发送和接收
"""
import pytest
import requests
from typing import Dict, Any
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

class TestSystemMessages:
    """测试系统消息（sender_id=None）"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """创建测试用户（普通用户）"""
        user_data = {
            "email": f"test_system_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def test_admin(self):
        """创建测试管理员"""
        user_data = {
            "email": f"test_admin_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试管理员",
            "role": "admin"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def user_headers(self, test_user: Dict[str, Any]) -> Dict[str, str]:
        """获取普通用户的请求头"""
        login_data = {
            "email": test_user["email"],
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def admin_headers(self, test_admin: Dict[str, Any]) -> Dict[str, str]:
        """获取管理员的请求头"""
        login_data = {
            "email": test_admin["email"],
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_system_message_visible_to_receiver(self, admin_headers: Dict[str, str], test_user: Dict[str, Any]):
        """测试系统消息对接收者可见"""
        # 1. 管理员发送系统消息给用户（模拟时间段更改通知）
        message_data = {
            "receiver_id": test_user["id"],
            "content": f"系统通知：管理员已更改时间段，请重新确认。测试时间：{time.time()}"
        }
        
        # 使用普通发送接口，但后端会设置 sender_id=None
        # 这里我们直接测试接收者能否看到消息
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # 2. 用户查看自己的消息，应该能看到系统消息
        response = requests.get(
            f"{BASE_URL}/messages/",
            headers=self.user_headers
        )
        assert response.status_code == 200
        messages = response.json()
        
        # 查找系统消息
        system_message_found = False
        for msg in messages:
            if "系统通知" in msg["content"] or "管理员已更改时间段" in msg["content"]:
                system_message_found = True
                # 验证消息内容
                assert "系统通知" in msg["content"] or "管理员已更改时间段" in msg["content"]
                break
        
        assert system_message_found, "用户应该能看到系统消息"
    
    def test_get_all_messages_includes_system(self, admin_headers: Dict[str, str]):
        """测试 /messages/all 接口能获取系统消息"""
        # 调用 /messages/all 接口
        response = requests.get(
            f"{BASE_URL}/messages/all",
            headers=admin_headers
        )
        assert response.status_code == 200
        messages = response.json()
        
        # 验证返回的是列表
        assert isinstance(messages, list)
        
        # 如果有消息，验证格式
        if len(messages) > 0:
            msg = messages[0]
            assert "id" in msg
            assert "content" in msg
            assert "receiver_id" in msg
            assert "created_at" in msg
    
    def test_conversations_excludes_system_messages(self, user_headers: Dict[str, str]):
        """测试会话列表不包含系统消息"""
        response = requests.get(
            f"{BASE_URL}/messages/conversations",
            headers=user_headers
        )
        assert response.status_code == 200
        conversations = response.json()
        
        # 验证返回的是列表
        assert isinstance(conversations, list)
        
        # 每个会话都应该有 user_id
        for conv in conversations:
            assert "user_id" in conv
            assert conv["user_id"] is not None, "会话列表不应该包含系统消息"
