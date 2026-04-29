#!/usr/bin/env python3
"""
调试：直接检查数据库中的 time_slot_id
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 管理员登录
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 准备自行车
bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
    "brand": "Debug Test",
    "model": "Buyer Flow",
    "color": "Red",
    "license_number": f"DEBUG{datetime.now().timestamp()}",
    "description": "Debug test bike",
    "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
    "condition": 3
}, headers=admin_headers)
bike_id = bicycle_response.json()["id"]
requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)

# 创建买家预约
appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
    "bicycle_id": str(bike_id),
    "type": "pick-up"
}, headers=admin_headers)
apt_id = appointment_response.json()["id"]
print(f"创建预约：{apt_id}")

# 管理员提出时间段
time_slots = [
    {
        "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
    }
]
requests.post(f"{BASE_URL}/appointments/{apt_id}/propose-slots", json=time_slots, headers=admin_headers)
print(f"管理员提出时间段")

# 检查选择前的预约
print("\n【选择前】检查预约详情：")
apt_before = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers).json()
target = next((a for a in apt_before if a['id'] == apt_id), None)
print(f"time_slot_id: {target['time_slot_id']}")
print(f"status: {target['status']}")

# 买家选择时间段
slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
slots = slots_response.json()
print(f"\n可选时间段：{len(slots)}")

select_response = requests.put(f"{BASE_URL}/time_slots/select/{apt_id}", json={"time_slot_id": str(slots[0]["id"])}, headers=admin_headers)
print(f"选择时间段响应：{select_response.status_code} - {select_response.json()}")

# 立即检查预约
print("\n【选择后】立即检查预约详情：")
apt_after = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers).json()
target = next((a for a in apt_after if a['id'] == apt_id), None)
print(f"time_slot_id: {target['time_slot_id']}")
print(f"status: {target['status']}")

# 单独获取该预约
print("\n【选择后】单独获取用户预约：")
user_id = target['user_id']
user_apts = requests.get(f"{BASE_URL}/appointments/user/{user_id}", headers=admin_headers).json()
target2 = next((a for a in user_apts if a['id'] == apt_id), None)
print(f"time_slot_id: {target2['time_slot_id']}")
print(f"status: {target2['status']}")
