#!/usr/bin/env python3
"""
检查卖家的消息
"""
import requests

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 登录卖家
seller_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "seller@test.com",
    "password": "test123"
})
seller_token = seller_response.json()["access_token"]
seller_headers = {"Authorization": f"Bearer {seller_token}"}

print("卖家的消息:")
messages_response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
if messages_response.status_code == 200:
    messages = messages_response.json()
    print(f"消息数量：{len(messages)}")
    for msg in messages:
        print(f"- {msg['content']}")
        print(f"  已读：{msg['is_read']}, 发送者：{msg['sender_id']}")
        print()
else:
    print(f"失败：{messages_response.status_code}")
    print(messages_response.text)
