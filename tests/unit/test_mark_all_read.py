#!/usr/bin/env python3
"""
测试一键标记所有私信为已读的功能
"""
import pytest
import requests

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestMarkAllMessagesAsRead:
    """测试一键标记所有私信为已读的功能"""
    
    def test_01_mark_all_as_read(self):
        """测试 1：一键标记所有消息为已读"""
        # 登录获取 token
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n【测试一键已读】")
        print("1. 获取未读消息数量")
        response = requests.get(f"{BASE_URL}/messages/unread", headers=headers)
        assert response.status_code == 200
        unread_count_before = response.json()
        print(f"   未读消息数量：{unread_count_before}")
        
        print("2. 调用一键已读接口")
        response = requests.put(f"{BASE_URL}/messages/read-all", json={}, headers=headers)
        print(f"   响应状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200
        assert "已标记所有消息为已读" in response.json()["message"]
        
        print("3. 再次获取未读消息数量，应该为 0")
        response = requests.get(f"{BASE_URL}/messages/unread", headers=headers)
        assert response.status_code == 200
        unread_count_after = response.json()
        print(f"   未读消息数量：{unread_count_after}")
        assert unread_count_after == 0, f"未读消息数量应该为 0，实际是 {unread_count_after}"
        
        print("   ✅ 一键已读功能正常")
    
    def test_02_mark_all_as_read_no_messages(self):
        """测试 2：没有未读消息时调用一键已读"""
        # 登录获取 token
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n【测试没有未读消息时一键已读】")
        print("1. 调用一键已读接口")
        response = requests.put(f"{BASE_URL}/messages/read-all", json={}, headers=headers)
        print(f"   响应状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200
        assert "已标记所有消息为已读" in response.json()["message"]
        print("   ✅ 没有未读消息时也能正常调用")
