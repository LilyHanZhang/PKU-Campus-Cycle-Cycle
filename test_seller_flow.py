#!/usr/bin/env python3
"""直接测试卖家流程"""
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 创建卖家
seller_email = f"test_seller_{int(time.time())}@test.com"
print(f"1. 创建卖家：{seller_email}")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": seller_email,
    "password": "password123",
    "name": "Test Seller",
    "role": "USER"
})

response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": seller_email,
    "password": "password123"
})
seller_token = response.json()["access_token"]
seller_headers = {"Authorization": f"Bearer {seller_token}"}

# 卖家登记自行车
print("2. 卖家登记自行车")
response = requests.post(f"{BASE_URL}/bicycles/", json={
    "brand": "Test Bike",
    "condition": 8,
    "price": 300
}, headers=seller_headers)
bike_id = response.json()["id"]
print(f"   自行车 ID: {bike_id}")
print(f"   自行车状态：{response.json()['status']}")

# 管理员审核
print("3. 管理员审核（创建卖家流程预约）")
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
print(f"   审核后状态：{response.json()['status']}")

# 查看预约
print("4. 查看预约（审核后）")
response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
appointments = response.json()
for apt in appointments:
    if apt["bicycle_id"] == bike_id:
        print(f"   预约 ID: {apt['id']}")
        print(f"   预约类型：{apt['type']}")
        print(f"   预约状态：{apt['status']}")

# 管理员提出时间段
print("5. 管理员提出时间段")
now = datetime.now(timezone.utc)
time_slots = [{
    "start_time": (now + timedelta(days=1)).isoformat(),
    "end_time": (now + timedelta(days=1, hours=2)).isoformat()
}]

response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
print(f"   提出状态：{response.status_code}")
print(f"   响应：{response.text}")

# 再次查看预约
print("6. 查看预约（提出时间段后）")
response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
appointments = response.json()
for apt in appointments:
    if apt["bicycle_id"] == bike_id:
        print(f"   预约 ID: {apt['id']}")
        print(f"   预约类型：{apt['type']}")
        print(f"   预约状态：{apt['status']}")

# 查看时间段
print("7. 查看时间段")
response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
print(f"   状态码：{response.status_code}")
slots = response.json()
print(f"   时间段数量：{len(slots)}")
if slots:
    print(f"   时间段 ID: {slots[0]['id']}")
    print(f"   时间段类型：{slots[0]['appointment_type']}")

# 卖家选择时间段
print("8. 卖家选择时间段")
if slots:
    response = requests.put(
        f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
        json={"time_slot_id": str(slots[0]["id"])},
        headers=seller_headers
    )
    print(f"   选择状态码：{response.status_code}")
    print(f"   响应：{response.text}")
