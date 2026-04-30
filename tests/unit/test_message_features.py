import pytest
import requests
from typing import Dict, Any
import uuid
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
            "receiver_id": test_user2["user_id"],
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
        assert data["receiver_id"] == test_user2["user_id"]
    
    def test_get_conversations(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试获取会话列表"""
        # 先发送一条消息
        message_data = {
            "receiver_id": test_user2["user_id"],
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
        
        # 验证会话数据结构
        if len(conversations) > 0:
            conv = conversations[0]
            assert "user_id" in conv
            assert "user_name" in conv
            assert "last_message" in conv
            assert "unread_count" in conv
            assert "last_message_time" in conv
    
    def test_get_conversation_with_user(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试获取与特定用户的对话"""
        # 先发送一条消息
        message_data = {
            "receiver_id": test_user2["user_id"],
            "content": "测试对话消息"
        }
        requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        # 获取对话
        response = requests.get(
            f"{BASE_URL}/messages/conversation/{test_user2['user_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        
        # 验证消息数据结构
        if len(messages) > 0:
            msg = messages[0]
            assert "id" in msg
            assert "content" in msg
            assert "sender_id" in msg
            assert "is_read" in msg
    
    def test_get_unread_count(self, auth_headers: Dict[str, str]):
        """测试获取未读消息数量"""
        response = requests.get(
            f"{BASE_URL}/messages/unread",
            headers=auth_headers
        )
        assert response.status_code == 200
        count = response.json()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_mark_message_as_read(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试标记消息为已读"""
        # 先发送一条消息
        message_data = {
            "receiver_id": test_user2["user_id"],
            "content": "测试已读消息"
        }
        sent_response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=auth_headers
        )
        message_id = sent_response.json()["id"]
        
        # 标记为已读
        response = requests.put(
            f"{BASE_URL}/messages/{message_id}/read",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证已标记为已读
        conv_response = requests.get(
            f"{BASE_URL}/messages/conversation/{test_user2['user_id']}",
            headers=auth_headers
        )
        messages = conv_response.json()
        sent_msg = next((m for m in messages if m["id"] == message_id), None)
        assert sent_msg is not None
        assert sent_msg["is_read"] == True
    
    def test_mark_all_as_read(self, auth_headers: Dict[str, str]):
        """测试一键标记所有消息为已读"""
        response = requests.put(
            f"{BASE_URL}/messages/read-all",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证未读数量为 0
        unread_response = requests.get(
            f"{BASE_URL}/messages/unread",
            headers=auth_headers
        )
        assert unread_response.json() == 0
    
    def test_search_messages(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试搜索消息"""
        # 发送一条包含特定关键词的消息
        keyword = f"搜索测试_{time.time()}"
        message_data = {
            "receiver_id": test_user2["user_id"],
            "content": f"这是一条用于测试搜索的消息：{keyword}"
        }
        requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        # 搜索消息
        response = requests.get(
            f"{BASE_URL}/messages/search?q={keyword}",
            headers=auth_headers
        )
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        assert len(messages) > 0
        
        # 验证搜索结果包含关键词
        found = any(keyword in msg["content"] for msg in messages)
        assert found, "搜索结果应该包含关键词"
    
    def test_delete_message(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试删除单条消息"""
        # 发送一条消息
        message_data = {
            "receiver_id": test_user2["user_id"],
            "content": "测试删除的消息"
        }
        sent_response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=auth_headers
        )
        message_id = sent_response.json()["id"]
        
        # 删除消息
        response = requests.delete(
            f"{BASE_URL}/messages/{message_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证消息已被删除
        conv_response = requests.get(
            f"{BASE_URL}/messages/conversation/{test_user2['user_id']}",
            headers=auth_headers
        )
        messages = conv_response.json()
        deleted_msg = next((m for m in messages if m["id"] == message_id), None)
        assert deleted_msg is None, "消息应该已被删除"
    
    def test_delete_conversation(self, auth_headers: Dict[str, str], test_user2: Dict[str, Any]):
        """测试删除整个对话"""
        # 先发送几条消息
        for i in range(3):
            message_data = {
                "receiver_id": test_user2["user_id"],
                "content": f"测试删除对话的消息 {i}"
            }
            requests.post(f"{BASE_URL}/messages/", json=message_data, headers=auth_headers)
        
        # 删除对话
        response = requests.delete(
            f"{BASE_URL}/messages/conversation/{test_user2['user_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 验证对话已被删除
        conv_response = requests.get(
            f"{BASE_URL}/messages/conversation/{test_user2['user_id']}",
            headers=auth_headers
        )
        messages = conv_response.json()
        assert len(messages) == 0, "对话中的所有消息应该已被删除"
    
    def test_send_message_to_self(self, auth_headers: Dict[str, str]):
        """测试可以给自己发送消息（笔记功能）"""
        # 获取当前用户 ID
        user_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=auth_headers
        )
        current_user_id = user_response.json()["user_id"]
        
        # 给自己发送消息
        message_data = {
            "receiver_id": current_user_id,
            "content": "这是一条给自己的备忘录消息"
        }
        response = requests.post(
            f"{BASE_URL}/messages/",
            json=message_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["sender_id"] == current_user_id
        assert data["receiver_id"] == current_user_id
        
        # 验证可以在会话列表中看到
        conv_response = requests.get(
            f"{BASE_URL}/messages/conversations",
            headers=auth_headers
        )
        conversations = conv_response.json()
        # 应该能找到自己的会话
        self_conv = next((c for c in conversations if c["user_id"] == current_user_id), None)
        assert self_conv is not None, "应该能在会话列表中找到自己的会话"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
