#!/usr/bin/env python3
"""
测试买家流程确认时间段功能：
1. 买家选择时间段后，自行车状态应该变为 PENDING_ADMIN_CONFIRMATION_BUYER
2. 管理员点击"确认时间段"按钮后，自行车状态应该变为 PENDING_PICKUP
3. 预约状态应该变为 CONFIRMED
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


def test_buyer_slot_selection_updates_bicycle_status():
    """测试买家选择时间段后自行车状态更新"""
    print("\n" + "=" * 60)
    print("测试买家选择时间段后自行车状态更新")
    print("=" * 60)
    
    # 管理员登录
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 准备自行车
    bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Slot Selection Test",
        "model": "Buyer Flow",
        "color": "Red",
        "license_number": f"SLOT{datetime.now().timestamp()}",
        "description": "Slot selection test bike",
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
    print(f"   创建预约：{apt_id}")
    
    # 管理员提出时间段
    time_slots = [
        {
            "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
        }
    ]
    requests.post(f"{BASE_URL}/appointments/{apt_id}/propose-slots", json=time_slots, headers=admin_headers)
    
    # 检查自行车状态（应该是 PENDING_BUYER_SLOT_SELECTION）
    bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_status = bike_response.json()["status"]
    print(f"   提出时间段后自行车状态：{bike_status}")
    assert bike_status == "PENDING_BUYER_SLOT_SELECTION", f"应该是 PENDING_BUYER_SLOT_SELECTION，实际是 {bike_status}"
    print(f"   ✅ 自行车状态正确变为 PENDING_BUYER_SLOT_SELECTION")
    
    # 买家选择时间段
    slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
    slots = slots_response.json()
    select_response = requests.put(f"{BASE_URL}/time_slots/select/{apt_id}", json={"time_slot_id": str(slots[0]["id"])}, headers=admin_headers)
    assert select_response.status_code == 200
    
    # 检查自行车状态（应该是 PENDING_ADMIN_CONFIRMATION_BUYER）
    bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_status = bike_response.json()["status"]
    print(f"   买家选择时间段后自行车状态：{bike_status}")
    assert bike_status == "PENDING_ADMIN_CONFIRMATION_BUYER", f"应该是 PENDING_ADMIN_CONFIRMATION_BUYER，实际是 {bike_status}"
    print(f"   ✅ 自行车状态正确变为 PENDING_ADMIN_CONFIRMATION_BUYER（等待管理员确认）")
    
    # 检查预约状态
    all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
    appointments = all_appointments_response.json()
    test_apt = next((a for a in appointments if a['id'] == apt_id), None)
    assert test_apt is not None
    print(f"   预约状态：{test_apt['status']}")
    assert test_apt['status'] == "PENDING", f"应该是 PENDING，实际是 {test_apt['status']}"
    print(f"   ✅ 预约状态正确变为 PENDING")
    
    # 管理员确认时间段
    confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm/{apt_id}", headers=admin_headers)
    assert confirm_response.status_code == 200
    print(f"   ✅ 管理员确认时间段成功")
    
    # 检查自行车状态（应该是 PENDING_PICKUP）
    bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_status = bike_response.json()["status"]
    print(f"   确认时间段后自行车状态：{bike_status}")
    assert bike_status == "PENDING_PICKUP", f"应该是 PENDING_PICKUP，实际是 {bike_status}"
    print(f"   ✅ 自行车状态正确变为 PENDING_PICKUP（等待提车）")
    
    # 检查预约状态（应该是 CONFIRMED）
    all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
    appointments = all_appointments_response.json()
    test_apt = next((a for a in appointments if a['id'] == apt_id), None)
    assert test_apt is not None
    print(f"   预约状态：{test_apt['status']}")
    assert test_apt['status'] == "CONFIRMED", f"应该是 CONFIRMED，实际是 {test_apt['status']}"
    print(f"   ✅ 预约状态正确变为 CONFIRMED")
    
    print("\n✅ 所有测试通过！")


if __name__ == "__main__":
    test_buyer_slot_selection_updates_bicycle_status()
