"""
测试时间段选择后的消息功能
验证消息能正常发送和接收
"""
import pytest
import requests
from typing import Dict, Any
import time

BASE_URL = "http://127.0.0.1:8000"

class TestTimeSlotMessages:
    """测试时间段选择后的消息功能"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """创建测试用户"""
        user_data = {
            "email": f"test_msg_user_{int(time.time())}@example.com",
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
            "email": f"test_msg_admin_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试管理员"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def user_headers(self, test_user: Dict[str, Any]) -> Dict[str, str]:
        """获取用户的请求头"""
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
    
    def test_admin_sends_message_to_user(self, admin_headers: Dict[str, str], test_user: Dict[str, Any], test_admin: Dict[str, Any]):
        """测试管理员发送时间段更改通知给用户"""
        # 1. 管理员发送消息给用户
        message_data = {
            "receiver_id": test_user["id"],
            "content": f"管理员已更改时间段，请重新确认。测试时间：{time.time()}"
        }
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        sent_message = response.json()
        assert sent_message["sender_id"] == test_admin["id"]
        assert sent_message["receiver_id"] == test_user["id"]
        assert "管理员已更改时间段" in sent_message["content"]
    
    def test_user_receives_admin_message(self, user_headers: Dict[str, str], test_admin: Dict[str, Any]):
        """测试用户能看到管理员发送的消息"""
        # 用户查看消息列表
        response = requests.get(f"{BASE_URL}/messages/", headers=user_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 查找管理员发送的消息
        admin_message_found = False
        for msg in messages:
            if "管理员已更改时间段" in msg["content"]:
                admin_message_found = True
                assert msg["sender_id"] == test_admin["id"]
                break
        
        assert admin_message_found, "用户应该能看到管理员发送的消息"
    
    def test_conversation_includes_admin_message(self, user_headers: Dict[str, str], test_admin: Dict[str, Any]):
        """测试会话列表包含与管理员的会话"""
        response = requests.get(f"{BASE_URL}/messages/conversations", headers=user_headers)
        assert response.status_code == 200
        conversations = response.json()
        
        # 查找与管理员的会话
        admin_conversation_found = False
        for conv in conversations:
            if conv["user_id"] == test_admin["id"]:
                admin_conversation_found = True
                assert "last_message" in conv
                assert conv["unread_count"] >= 0
                break
        
        assert admin_conversation_found, "会话列表应该包含与管理员的会话"
    
    def test_user_replies_to_admin(self, user_headers: Dict[str, str], test_admin: Dict[str, Any], test_user: Dict[str, Any]):
        """测试用户回复管理员"""
        # 用户发送消息给管理员
        message_data = {
            "receiver_id": test_admin["id"],
            "content": f"收到，我会重新确认时间段。测试时间：{time.time()}"
        }
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=user_headers
        )
        assert response.status_code == 200
        sent_message = response.json()
        assert sent_message["sender_id"] == test_user["id"]
        assert sent_message["receiver_id"] == test_admin["id"]
    
    def test_admin_receives_user_reply(self, admin_headers: Dict[str, str], test_user: Dict[str, Any]):
        """测试管理员能看到用户回复的消息"""
        response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
        assert response.status_code == 200
        messages = response.json()
        
        # 查找用户回复的消息
        user_reply_found = False
        for msg in messages:
            if "收到，我会重新确认时间段" in msg["content"]:
                user_reply_found = True
                assert msg["sender_id"] == test_user["id"]
                break
        
        assert user_reply_found, "管理员应该能看到用户回复的消息"
