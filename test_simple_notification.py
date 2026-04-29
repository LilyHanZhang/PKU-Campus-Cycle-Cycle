#!/usr/bin/env python3
"""
简单测试私信通知功能
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

print("=" * 60)
print("测试私信通知功能")
print("=" * 60)

# 登录超级管理员
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
assert admin_response.status_code == 200
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("\n✅ 管理员登录成功")

# 获取管理员的所有消息
print("\n1. 获取管理员的消息")
messages_response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
if messages_response.status_code == 200:
    messages = messages_response.json()
    print(f"   消息数量：{len(messages)}")
    if messages:
        print(f"   最新 3 条消息:")
        for msg in messages[:3]:
            print(f"   - {msg['content'][:50]}... (已读：{msg['is_read']})")
else:
    print(f"   ❌ 失败：{messages_response.status_code}")

# 获取未读消息数量
print("\n2. 获取未读消息数量")
unread_response = requests.get(f"{BASE_URL}/messages/unread", headers=admin_headers)
if unread_response.status_code == 200:
    print(f"   未读消息：{unread_response.json()}")
else:
    print(f"   ❌ 失败：{unread_response.status_code}")

# 获取所有自行车
print("\n3. 获取所有自行车")
bicycles_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
if bicycles_response.status_code == 200:
    bicycles = bicycles_response.json()
    print(f"   自行车数量：{len(bicycles)}")
    for bike in bicycles:
        print(f"   - ID: {bike['id']}, 状态：{bike['status']}")
else:
    print(f"   ❌ 失败：{bicycles_response.status_code}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
