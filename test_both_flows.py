#!/usr/bin/env python3
"""
综合测试：验证卖家流程和买家流程的时间段选择
"""
import requests
from datetime import datetime, timedelta, timezone
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

print("=" * 60)
print("测试 1：卖家流程（管理员作为卖家）")
print("=" * 60)

# 创建管理员卖家
seller_email = f"seller_{int(time.time())}@test.com"
print(f"\n1. 创建管理员卖家：{seller_email}")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": seller_email,
    "password": "password123",
    "name": "Test Seller",
    "role": "USER"
})
assert response.status_code == 200

response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": seller_email,
    "password": "password123"
})
seller_token = response.json()["access_token"]
seller_headers = {"Authorization": f"Bearer {seller_token}"}

# 登记自行车
print("2. 登记自行车")
response = requests.post(f"{BASE_URL}/bicycles/", json={
    "brand": "Test Bike",
    "condition": 8,
    "price": 300
}, headers=seller_headers)
assert response.status_code == 200
bike_id = response.json()["id"]
print(f"   自行车 ID: {bike_id}, 状态：{response.json()['status']}")

# 管理员审核
print("3. 管理员审核")
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
assert response.status_code == 200
print(f"   审核后状态：{response.json()['status']}")

# 查看预约（审核后应该已经创建）
print("4. 查看预约（审核后）")
response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
appointments = response.json()
bike_appointment = None
for apt in appointments:
    if apt["bicycle_id"] == bike_id:
        bike_appointment = apt
        break

if bike_appointment:
    print(f"   ✅ 预约已创建：类型={bike_appointment['type']}")
    assert bike_appointment["type"] == "drop-off", f"❌ 预约类型错误：{bike_appointment['type']}，应该是 drop-off"
    print(f"   ✅ 预约类型正确：drop-off（卖家送车）")
else:
    print(f"   ⚠️  预约还未创建（将在提出时间段时创建）")

# 管理员提出时间段
print("5. 管理员提出时间段")
now = datetime.now(timezone.utc)
time_slots = [{
    "start_time": (now + timedelta(days=1)).isoformat(),
    "end_time": (now + timedelta(days=1, hours=2)).isoformat()
}]

response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
assert response.status_code == 200
print(f"   提出状态：{response.status_code}")

# 查看预约（提出时间段后）
print("6. 查看预约（提出时间段后）")
response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
appointments = response.json()
for apt in appointments:
    if apt["bicycle_id"] == bike_id:
        bike_appointment = apt
        break

print(f"   预约类型：{bike_appointment['type']}")
print(f"   预约状态：{bike_appointment['status']}")

# 卖家流程：预约类型应该是 drop-off
assert bike_appointment["type"] == "drop-off", f"❌ 预约类型错误：{bike_appointment['type']}，应该是 drop-off"
print(f"   ✅ 预约类型正确：drop-off（卖家送车）")

# 查看时间段
print("7. 查看时间段")
response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
assert response.status_code == 200
slots = response.json()
print(f"   时间段数量：{len(slots)}")
assert len(slots) > 0

# 卖家流程：时间段类型应该是 pick-up
print(f"   时间段类型：{slots[0]['appointment_type']}")
assert slots[0]["appointment_type"] == "pick-up", f"❌ 时间段类型错误：{slots[0]['appointment_type']}，应该是 pick-up"
print(f"   ✅ 时间段类型正确：pick-up（管理员取车）")

# 卖家选择时间段
print("8. 卖家选择时间段")
response = requests.put(
    f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
    json={"time_slot_id": str(slots[0]["id"])},
    headers=seller_headers
)
print(f"   选择状态码：{response.status_code}")
print(f"   响应：{response.text}")
assert response.status_code == 200, f"❌ 选择失败：{response.text}"
print(f"   ✅ 卖家选择成功！")

print("\n" + "=" * 60)
print("测试 2：买家流程（管理员作为买家）")
print("=" * 60)

# 创建管理员买家
buyer_email = f"buyer_{int(time.time())}@test.com"
print(f"\n1. 创建管理员买家：{buyer_email}")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": buyer_email,
    "password": "password123",
    "name": "Test Buyer",
    "role": "USER"
})
assert response.status_code == 200

response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": buyer_email,
    "password": "password123"
})
buyer_token = response.json()["access_token"]
buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

# 登记自行车
print("2. 登记自行车")
response = requests.post(f"{BASE_URL}/bicycles/", json={
    "brand": "Test Bike",
    "condition": 8,
    "price": 300
}, headers=buyer_headers)
assert response.status_code == 200
bike2_id = response.json()["id"]
print(f"   自行车 ID: {bike2_id}, 状态：{response.json()['status']}")

# 管理员审核
print("3. 管理员审核")
response = requests.put(f"{BASE_URL}/bicycles/{bike2_id}/approve", headers=admin_headers)
assert response.status_code == 200
print(f"   审核后状态：{response.json()['status']}")

# 管理员提出时间段
print("4. 管理员提出时间段")
now = datetime.now(timezone.utc)
time_slots = [{
    "start_time": (now + timedelta(days=1)).isoformat(),
    "end_time": (now + timedelta(days=1, hours=2)).isoformat()
}]

response = requests.post(f"{BASE_URL}/bicycles/{bike2_id}/propose-slots", json=time_slots, headers=admin_headers)
assert response.status_code == 200
print(f"   提出状态：{response.status_code}")

# 查看预约
print("5. 查看预约")
response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
appointments = response.json()
bike2_appointment = None
for apt in appointments:
    if apt["bicycle_id"] == bike2_id:
        bike2_appointment = apt
        break

print(f"   预约类型：{bike2_appointment['type']}")
# 买家流程：预约类型应该是 pick-up
assert bike2_appointment["type"] == "pick-up", f"❌ 预约类型错误：{bike2_appointment['type']}，应该是 pick-up"
print(f"   ✅ 预约类型正确：pick-up（买家取车）")

# 查看时间段
print("6. 查看时间段")
response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike2_id}", headers=buyer_headers)
assert response.status_code == 200
slots = response.json()
print(f"   时间段数量：{len(slots)}")
assert len(slots) > 0

# 买家流程：时间段类型应该是 drop-off
print(f"   时间段类型：{slots[0]['appointment_type']}")
assert slots[0]["appointment_type"] == "drop-off", f"❌ 时间段类型错误：{slots[0]['appointment_type']}，应该是 drop-off"
print(f"   ✅ 时间段类型正确：drop-off（管理员送车）")

# 买家选择时间段
print("7. 买家选择时间段")
response = requests.put(
    f"{BASE_URL}/time_slots/select-bicycle/{bike2_id}",
    json={"time_slot_id": str(slots[0]["id"])},
    headers=buyer_headers
)
print(f"   选择状态码：{response.status_code}")
print(f"   响应：{response.text}")
assert response.status_code == 200, f"❌ 选择失败：{response.text}"
print(f"   ✅ 买家选择成功！")

print("\n" + "=" * 60)
print("所有测试通过！✅")
print("=" * 60)
