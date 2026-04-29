#!/usr/bin/env python3
"""
测试买家选择时间段后从列表中隐藏：
1. 买家选择时间段前，预约显示在时间段选择列表中
2. 买家选择时间段后，预约不再显示在时间段选择列表中
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


def test_buyer_appointment_disappears_after_selection():
    """测试买家选择时间段后预约从列表中消失"""
    print("\n" + "=" * 60)
    print("测试买家选择时间段后预约从列表中消失")
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
        "brand": "Disappear Test",
        "model": "Buyer Flow",
        "color": "Red",
        "license_number": f"DIS{datetime.now().timestamp()}",
        "description": "Disappear test bike",
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
        },
        {
            "start_time": (datetime.now() + timedelta(days=1, hours=14)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=16)).isoformat()
        }
    ]
    requests.post(f"{BASE_URL}/appointments/{apt_id}/propose-slots", json=time_slots, headers=admin_headers)
    print(f"   管理员提出 {len(time_slots)} 个时间段")
    
    # 步骤 1：检查选择时间段前，预约是否显示在列表中
    print(f"\n   【步骤 1】检查选择时间段前的列表")
    all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
    all_appointments = all_appointments_response.json()
    
    # 查找该预约
    target_apt = next((a for a in all_appointments if a['id'] == apt_id), None)
    assert target_apt is not None, "预约不存在"
    print(f"   预约状态：{target_apt['status']}")
    print(f"   时间段 ID: {target_apt['time_slot_id']}")
    
    # 此时 time_slot_id 应该为 None
    assert target_apt['time_slot_id'] is None, f"选择前 time_slot_id 应该为 None，实际是 {target_apt['time_slot_id']}"
    print(f"   ✅ 选择前 time_slot_id 为 None，预约应该显示在列表中")
    
    # 步骤 2：买家选择时间段
    print(f"\n   【步骤 2】买家选择时间段")
    slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
    slots = slots_response.json()
    print(f"   可选时间段数量：{len(slots)}")
    
    # 选择第一个时间段
    select_response = requests.put(f"{BASE_URL}/time_slots/select/{apt_id}", json={"time_slot_id": str(slots[0]["id"])}, headers=admin_headers)
    assert select_response.status_code == 200
    print(f"   ✅ 时间段选择成功")
    
    # 步骤 3：检查选择时间段后，预约是否从列表中消失
    print(f"\n   【步骤 3】检查选择时间段后的列表")
    all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
    all_appointments = all_appointments_response.json()
    
    # 查找该预约
    target_apt = next((a for a in all_appointments if a['id'] == apt_id), None)
    assert target_apt is not None, "预约不存在"
    print(f"   预约状态：{target_apt['status']}")
    print(f"   时间段 ID: {target_apt['time_slot_id']}")
    
    # 此时 time_slot_id 应该不为 None
    assert target_apt['time_slot_id'] is not None, f"选择后 time_slot_id 应该不为 None，实际是 {target_apt['time_slot_id']}"
    print(f"   ✅ 选择后 time_slot_id 不为 None")
    
    # 验证：过滤掉已选择时间段的预约后，该预约不应该出现在列表中
    pending_appointments = [a for a in all_appointments if a['status'] == 'PENDING' and not a['time_slot_id']]
    target_in_list = next((a for a in pending_appointments if a['id'] == apt_id), None)
    
    assert target_in_list is None, f"选择时间段后，预约不应该出现在待选择列表中"
    print(f"   ✅ 预约已从待选择时间段列表中消失")
    
    print(f"\n✅ 所有测试通过！")


if __name__ == "__main__":
    test_buyer_appointment_disappears_after_selection()
