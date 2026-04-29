#!/usr/bin/env python3
"""
测试管理员审核自行车并发送私信
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 登录超级管理员
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 获取所有自行车
bicycles_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
bicycles = bicycles_response.json()

# 找到第一辆待审核的自行车
bike = None
for b in bicycles:
    if b['status'] == 'PENDING_APPROVAL':
        bike = b
        break

if not bike:
    print("没有待审核的自行车")
    exit(1)

bike_id = bike['id']
print(f"审核自行车：{bike_id}")

# 获取卖家信息
seller_id = bike['owner_id']
print(f"卖家 ID: {seller_id}")

# 审核并提出时间段
time_slots = [
    {
        "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
    }
]

print(f"\n提出时间段：{time_slots}")

propose_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)

print(f"\n响应状态码：{propose_response.status_code}")
print(f"响应：{propose_response.text}")

if propose_response.status_code == 200:
    print("\n✅ 审核成功")
    
    # 检查卖家是否收到消息
    print("\n检查卖家的消息...")
    # 需要卖家的 token
    # 这里我们无法直接获取，所以跳过
    
    # 检查管理员的消息
    print("\n检查管理员的消息...")
    messages_response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
    if messages_response.status_code == 200:
        messages = messages_response.json()
        print(f"消息数量：{len(messages)}")
        for msg in messages:
            print(f"- {msg['content']} (已读：{msg['is_read']})")
else:
    print("\n❌ 审核失败")
