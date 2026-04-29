#!/usr/bin/env python3
"""
完整测试私信通知流程
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

print("=" * 60)
print("完整测试私信通知流程")
print("=" * 60)

# 1. 登录卖家
print("\n【步骤 1】卖家登录")
seller_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "seller@test.com",
    "password": "test123"
})
if seller_response.status_code != 200:
    # 创建卖家账号
    print("创建卖家账号...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "seller@test.com",
        "password": "test123",
        "role": "user"
    })
    seller_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "seller@test.com",
        "password": "test123"
    })

seller_token = seller_response.json()["access_token"]
seller_headers = {"Authorization": f"Bearer {seller_token}"}
print("✅ 卖家登录成功")

# 2. 获取卖家的自行车
print("\n【步骤 2】获取卖家的自行车")
seller_bikes_response = requests.get(f"{BASE_URL}/bicycles/my", headers=seller_headers)
if seller_bikes_response.status_code == 200:
    seller_bikes = seller_bikes_response.json()
    print(f"卖家有 {len(seller_bikes)} 辆自行车")
    for bike in seller_bikes:
        print(f"  - {bike['id']}: {bike['status']}")
else:
    print(f"❌ 获取失败：{seller_bikes_response.status_code}")
    seller_bikes = []

# 3. 找到 LOCKED 状态的自行车（已选择时间段）
print("\n【步骤 3】查找待确认的自行车")
locked_bike = None
for bike in seller_bikes:
    if bike['status'] == 'LOCKED':
        locked_bike = bike
        break

if locked_bike:
    print(f"找到待确认的自行车：{locked_bike['id']}")
    
    # 4. 管理员确认
    print("\n【步骤 4】管理员确认时间段")
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm-bicycle/{locked_bike['id']}", headers=admin_headers)
    print(f"确认响应：{confirm_response.status_code}")
    print(f"响应：{confirm_response.text}")
    
    if confirm_response.status_code == 200:
        print("✅ 管理员确认成功")
        
        # 5. 检查卖家是否收到私信
        print("\n【步骤 5】检查卖家是否收到私信")
        seller_messages_response = requests.get(f"{BASE_URL}/messages/", headers=seller_headers)
        if seller_messages_response.status_code == 200:
            messages = seller_messages_response.json()
            print(f"卖家有 {len(messages)} 条消息")
            for msg in messages[:3]:
                print(f"  - {msg['content'][:60]}... (已读：{msg['is_read']})")
        else:
            print(f"❌ 获取失败：{seller_messages_response.status_code}")
        
        # 6. 检查管理员是否收到私信
        print("\n【步骤 6】检查管理员是否收到私信")
        admin_messages_response = requests.get(f"{BASE_URL}/messages/", headers=admin_headers)
        if admin_messages_response.status_code == 200:
            messages = admin_messages_response.json()
            print(f"管理员有 {len(messages)} 条消息")
            for msg in messages[:3]:
                print(f"  - {msg['content'][:60]}... (已读：{msg['is_read']})")
        else:
            print(f"❌ 获取失败：{admin_messages_response.status_code}")
    else:
        print("❌ 管理员确认失败")
else:
    print("没有待确认的自行车")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
