#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

API_URL = "https://pku-campus-cycle-cycle.onrender.com"

print("=" * 50)
print("测试部署环境的时间线新功能")
print("=" * 50)
print()

# 登录
print("1. 登录...")
admin_login = requests.post(f"{API_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_login.json()["access_token"]
print(f"   ✓ 管理员登录成功")

# 使用管理员作为测试用户（简化测试）
user_token = admin_token
print(f"   ✓ 使用管理员 token 作为用户 token")
print()

# 测试 1: 卖家场景
print("2. 测试卖家场景：管理员为自行车提出时间段")
headers = {"Authorization": f"Bearer {admin_token}"}
bike = requests.post(f"{API_URL}/bicycles/", json={
    "brand": "Seller Test",
    "condition": 8,
    "price": 100
}, headers={"Authorization": f"Bearer {user_token}"})
bike_id = bike.json()["id"]
print(f"   创建自行车：{bike_id}")

start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
end_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()

propose = requests.post(
    f"{API_URL}/bicycles/{bike_id}/propose-slots",
    json=[{"start_time": start_time, "end_time": end_time}],
    headers=headers
)
message = propose.json().get("message", "")
print(f"   响应：{message}")

if "已提出" in message:
    print("   ✓ 卖家场景测试通过")
else:
    print("   ✗ 卖家场景测试失败")
print()

# 测试 2: 买家场景
print("3. 测试买家场景：管理员为预约提出时间段")
bike2 = requests.post(f"{API_URL}/bicycles/", json={
    "brand": "Buyer Test",
    "condition": 7,
    "price": 80
}, headers=headers)
bike2_id = bike2.json()["id"]
print(f"   创建自行车：{bike2_id}")

# 批准
requests.put(f"{API_URL}/bicycles/{bike2_id}/approve", headers=headers)

# 创建预约
apt = requests.post(f"{API_URL}/appointments/", json={
    "bicycle_id": bike2_id,
    "type": "pick-up"
}, headers={"Authorization": f"Bearer {user_token}"})
apt_id = apt.json()["id"]
print(f"   创建预约：{apt_id}")

start_time2 = (datetime.utcnow() + timedelta(hours=3)).isoformat()
end_time2 = (datetime.utcnow() + timedelta(hours=4)).isoformat()

propose2 = requests.post(
    f"{API_URL}/appointments/{apt_id}/propose-slots",
    json=[{"start_time": start_time2, "end_time": end_time2}],
    headers=headers
)
message2 = propose2.json().get("message", "")
print(f"   响应：{message2}")

if "已提出" in message2:
    print("   ✓ 买家场景测试通过")
else:
    print("   ✗ 买家场景测试失败")
print()

print("=" * 50)
print("部署测试完成")
print("=" * 50)
