import pytest
import requests
from typing import Dict, Any
import time

BASE_URL = "http://127.0.0.1:8000"

class TestMessageFeatures:
    """测试私信功能"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """创建测试用户"""
        user_data = {
            "email": f"test_msg_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def auth_headers(self, test_user: Dict[str, Any]) -> Dict[str, str]:
        """获取认证用户的请求头"""
        login_data = {
            "email": test_user["email"],
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def test_user2(self):
        """创建第二个测试用户"""
        user_data = {
            "email": f"test_msg2_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户 2"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    def test_send_message(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试发送消息"""
        message_data = {
            "receiver_id": test_user2["id"],
            "content": f"测试消息 - {time.time()}"
        }
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["receiver_id"] == test_user2["id"]
    
    def test_get_conversations(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试获取会话列表"""
        message_data = {
            "receiver_id": test_user2["id"],
            "content": "测试会话"
        }
        requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        response = requests.get(
            f"{BASE_URL}/messages/conversations",
            headers=auth_headers
        )
        assert response.status_code == 200
        conversations = response.json()
        assert isinstance(conversations, list)
        
        if len(conversations) > 0:
            conv = conversations[0]
            assert "user_id" in conv
            assert "user_name" in conv
            assert "last_message" in conv
            assert "unread_count" in conv
            assert "last_message_time" in conv
    
    def test_get_conversation_with_user(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试获取与特定用户的对话"""
        message_data = {
            "receiver_id": test_user2["id"],
            "content": "测试对话消息"
        }
        requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        response = requests.get(
            f"{BASE_URL}/messages/conversation/{test_user2['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        assert len(messages) > 0
        
        msg = messages[-1]
        assert "id" in msg
        assert "sender_id" in msg
        assert "receiver_id" in msg
        assert "content" in msg
        assert "is_read" in msg
        assert "created_at" in msg
    
    def test_send_message_to_self(self, auth_headers: Dict[str, str], test_user: Dict[str, Any]):
        """测试给自己发送消息（笔记功能）"""
        message_data = {
            "receiver_id": test_user["id"],
            "content": f"给自己的备忘录 - {time.time()}"
        }
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sender_id"] == test_user["id"]
        assert data["receiver_id"] == test_user["id"]
    
    def test_list_all_users(self, auth_headers: Dict[str, str], test_user: Dict[str, Any], test_user2: Dict[str, Any]):
        """测试获取所有用户列表（包括自己）"""
        response = requests.get(
            f"{BASE_URL}/users/",
            headers=auth_headers
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2
        
        user_ids = [u["id"] for u in users]
        assert test_user["id"] in user_ids
        assert test_user2["id"] in user_ids
        
        user = users[0]
        assert "id" in user
        assert "email" in user
        assert "name" in user
    
    def test_delete_conversation(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试删除对话"""
        message_data = {
            "receiver_id": test_user2["id"],
            "content": "测试删除对话"
        }
        requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        response = requests.delete(
            f"{BASE_URL}/messages/conversation/{test_user2['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        response = requests.get(
            f"{BASE_URL}/messages/conversations",
            headers=auth_headers
        )
        conversations = response.json()
        user_ids = [c["user_id"] for c in conversations]
        assert test_user2["id"] not in user_ids
