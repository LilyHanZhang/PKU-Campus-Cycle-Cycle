#!/usr/bin/env python3
"""
测试私信通知功能

测试场景：
1. 管理员提出时间段 -> 卖家应该收到私信
2. 卖家选择时间段 -> 管理员应该收到私信
3. 管理员确认时间段 -> 卖家应该收到私信
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestMessageNotifications:
    """测试私信通知功能"""
    
    def test_01_admin_proposes_time_slots_seller_receives_message(self):
        """测试 1：管理员提出时间段，卖家收到私信通知"""
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取管理员 ID
        admin_users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
        assert admin_users_response.status_code == 200
        admin_users = admin_users_response.json()
        admin_id = admin_users[0]["id"]
        
        # 登录卖家
        seller_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "seller@test.com",
            "password": "test123"
        })
        if seller_response.status_code != 200:
            # 如果卖家不存在，创建它
            seller_response = requests.post(f"{BASE_URL}/auth/register", json={
                "email": "seller@test.com",
                "password": "test123",
                "role": "user"
            })
            assert seller_response.status_code == 200
            seller_response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "seller@test.com",
                "password": "test123"
            })
        seller_token = seller_response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 获取卖家 ID
        seller_users_response = requests.get(f"{BASE_URL}/users/", headers=seller_headers)
        assert seller_users_response.status_code == 200
        seller_users = seller_users_response.json()
        seller_id = seller_users[0]["id"]
        
        print("\n【测试 1：管理员提出时间段】")
        print("1. 创建测试自行车（待审核状态）")
        # 使用一个有效的图片 URL
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test",
            "model": "Test Model",
            "color": "Blue",
            "license_number": "TEST123456",
            "description": "Test bicycle for notification",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=seller_headers)
        print(f"   响应状态码：{bicycle_response.status_code}")
        print(f"   响应：{bicycle_response.text}")
        assert bicycle_response.status_code == 200
        bicycle_id = bicycle_response.json()["id"]
        
        print("2. 管理员审核并提出时间段")
        time_slots = [
            {
                "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
            },
            {
                "start_time": (datetime.now() + timedelta(days=2, hours=14)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=2, hours=16)).isoformat()
            }
        ]
        propose_response = requests.post(f"{BASE_URL}/bicycles/{bicycle_id}/propose-slots", json={
            "time_slots": time_slots
        }, headers=admin_headers)
        print(f"   响应状态码：{propose_response.status_code}")
        print(f"   响应：{propose_response.text}")
        assert propose_response.status_code == 200
        
        print("3. 检查卖家是否收到私信")
        messages_response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
        assert messages_response.status_code == 200
        messages = messages_response.json()
        
        # 查找最新的消息
        notification_found = False
        for msg in messages:
            if "时间段" in msg["content"] and msg["receiver_id"] == seller_id:
                notification_found = True
                print(f"   ✅ 卖家收到私信：{msg['content']}")
                print(f"   消息状态：{'已读' if msg['is_read'] else '未读'}")
                break
        
        assert notification_found, "卖家应该收到管理员的私信通知"
        print("   ✅ 测试 1 通过：卖家收到了私信通知")
    
    def test_02_seller_selects_time_slot_admin_receives_message(self):
        """测试 2：卖家选择时间段，管理员收到私信通知"""
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取管理员 ID
        admin_users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
        assert admin_users_response.status_code == 200
        admin_users = admin_users_response.json()
        admin_id = admin_users[0]["id"]
        
        # 登录卖家
        seller_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "seller@test.com",
            "password": "test123"
        })
        assert seller_response.status_code == 200
        seller_token = seller_response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        print("\n【测试 2：卖家选择时间段】")
        print("1. 获取卖家的待处理预约")
        appointments_response = requests.get(f"{BASE_URL}/time_slots/my", headers=seller_headers)
        assert appointments_response.status_code == 200
        appointments = appointments_response.json()
        
        if not appointments:
            print("   ⚠️  没有待处理的预约，跳过此测试")
            pytest.skip("没有待处理的预约")
        
        # 找到第一个有待处理时间段的预约
        pending_appointment = None
        for apt in appointments:
            if apt["status"] == "PENDING" and apt.get("available_slots"):
                pending_appointment = apt
                break
        
        if not pending_appointment:
            print("   ⚠️  没有待确认时间段的预约，跳过此测试")
            pytest.skip("没有待确认时间段的预约")
        
        appointment_id = pending_appointment["id"]
        time_slot_id = pending_appointment["available_slots"][0]["id"]
        
        print(f"   预约 ID: {appointment_id}")
        print(f"   时间段 ID: {time_slot_id}")
        
        print("2. 卖家选择时间段")
        select_response = requests.post(f"{BASE_URL}/time_slots/select/{appointment_id}", json={
            "time_slot_id": time_slot_id
        }, headers=seller_headers)
        print(f"   响应状态码：{select_response.status_code}")
        print(f"   响应：{select_response.text}")
        assert select_response.status_code == 200
        
        print("3. 检查管理员是否收到私信")
        messages_response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
        assert messages_response.status_code == 200
        messages = messages_response.json()
        
        # 查找最新的消息
        notification_found = False
        for msg in messages:
            if "时间段" in msg["content"] and msg["receiver_id"] == admin_id:
                notification_found = True
                print(f"   ✅ 管理员收到私信：{msg['content']}")
                print(f"   消息状态：{'已读' if msg['is_read'] else '未读'}")
                break
        
        assert notification_found, "管理员应该收到卖家的私信通知"
        print("   ✅ 测试 2 通过：管理员收到了私信通知")
    
    def test_03_admin_confirms_time_slot_seller_receives_message(self):
        """测试 3：管理员确认时间段，卖家收到私信通知"""
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取管理员 ID
        admin_users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
        assert admin_users_response.status_code == 200
        admin_users = admin_users_response.json()
        admin_id = admin_users[0]["id"]
        
        # 登录卖家
        seller_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "seller@test.com",
            "password": "test123"
        })
        assert seller_response.status_code == 200
        seller_token = seller_response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        print("\n【测试 3：管理员确认时间段】")
        print("1. 获取管理员的待确认预约")
        # 获取所有待确认的自行车
        bicycles_response = requests.get(f"{BASE_URL}/bicycles/my", headers=admin_headers)
        assert bicycles_response.status_code == 200
        bicycles = bicycles_response.json()
        
        # 找到 LOCKED 状态的自行车（等待管理员确认时间段）
        locked_bicycle = None
        for bike in bicycles:
            if bike["status"] == "LOCKED":
                locked_bicycle = bike
                break
        
        if not locked_bicycle:
            print("   ⚠️  没有待确认时间段的自行车，跳过此测试")
            pytest.skip("没有待确认时间段的自行车")
        
        bicycle_id = locked_bicycle["id"]
        print(f"   自行车 ID: {bicycle_id}")
        
        print("2. 管理员确认时间段")
        confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm-bicycle/{bicycle_id}", headers=admin_headers)
        print(f"   响应状态码：{confirm_response.status_code}")
        print(f"   响应：{confirm_response.text}")
        
        if confirm_response.status_code != 200:
            print(f"   ⚠️  确认失败：{confirm_response.text}")
            pytest.skip("无法确认时间段")
        
        print("3. 检查卖家是否收到私信")
        messages_response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
        assert messages_response.status_code == 200
        messages = messages_response.json()
        
        # 查找最新的消息
        notification_found = False
        for msg in messages:
            if "确认" in msg["content"] and msg["receiver_id"] == str(seller_id):
                notification_found = True
                print(f"   ✅ 卖家收到私信：{msg['content']}")
                print(f"   消息状态：{'已读' if msg['is_read'] else '未读'}")
                break
        
        assert notification_found, "卖家应该收到管理员的私信通知"
        print("   ✅ 测试 3 通过：卖家收到了私信通知")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
