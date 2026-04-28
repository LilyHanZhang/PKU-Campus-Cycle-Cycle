#!/usr/bin/env python3
"""
完整测试：买家流程从登记到完成交易
"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def test_buyer_flow():
    print("=" * 70)
    print("完整测试：买家流程从登记到完成交易")
    print("=" * 70)
    print()
    
    # 1. 买家登录
    print("1. 买家登录...")
    buyer_email = f"buyer_{int(time.time())}@test.com"
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": buyer_email,
        "password": "password123",
        "name": "Test Buyer",
        "role": "USER"
    })
    assert response.status_code == 200, f"注册失败：{response.text}"
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": buyer_email,
        "password": "password123"
    })
    assert response.status_code == 200, f"登录失败：{response.text}"
    buyer_token = response.json()["access_token"]
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    print("   ✅ 买家登录成功")
    print()
    
    # 2. 买家登记自行车（PENDING_APPROVAL）
    print("2. 买家登记自行车（PENDING_APPROVAL）...")
    response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Test Bike",
        "condition": 8,
        "price": 300,
        "description": "买家登记的自行车"
    }, headers=buyer_headers)
    assert response.status_code == 200, f"登记失败：{response.text}"
    bike_id = response.json()["id"]
    print(f"   ✅ 自行车登记成功：{bike_id}")
    print(f"   - 状态：{response.json()['status']}")
    print()
    
    # 3. 管理员登录
    print("3. 管理员登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200, f"管理员登录失败：{response.text}"
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   ✅ 管理员登录成功")
    print()
    
    # 4. 管理员审核通过（PENDING_APPROVAL → IN_STOCK）
    print("4. 管理员审核通过（→ IN_STOCK）...")
    response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
    assert response.status_code == 200, f"审核失败：{response.text}"
    print(f"   ✅ 审核通过")
    print(f"   - 状态：{response.json()['status']}")
    print()
    
    # 5. 管理员提出时间段（IN_STOCK → LOCKED）
    print("5. 管理员提出时间段（→ LOCKED）...")
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        },
        {
            "start_time": (now + timedelta(days=2)).isoformat(),
            "end_time": (now + timedelta(days=2, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
    assert response.status_code == 200, f"提出时间段失败：{response.text}"
    print(f"   ✅ 提出时间段成功")
    # 获取最新状态
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    print(f"   - 状态：{response.json()['status']}")
    print()
    
    # 6. 买家选择时间段
    print("6. 买家选择时间段...")
    response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=buyer_headers)
    assert response.status_code == 200, f"获取时间段失败：{response.text}"
    slots = response.json()
    assert len(slots) > 0, "没有可选时间段"
    
    selected_slot = slots[0]
    response = requests.put(
        f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
        json={"time_slot_id": str(selected_slot["id"])},
        headers=buyer_headers
    )
    assert response.status_code == 200, f"选择时间段失败：{response.text}"
    print(f"   ✅ 买家选择时间段成功")
    print(f"   - 状态：LOCKED")
    print()
    
    # 7. 管理员确认预约（LOCKED → SOLD）
    print("7. 管理员确认预约（→ SOLD）...")
    
    # 获取预约
    response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
    appointments = response.json()
    bike_appointment = None
    for apt in appointments:
        if apt["bicycle_id"] == bike_id:
            bike_appointment = apt
            break
    
    assert bike_appointment, "未找到预约"
    apt_id = bike_appointment["id"]
    
    # 确认预约
    response = requests.put(
        f"{BASE_URL}/time_slots/confirm/{apt_id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200, f"确认预约失败：{response.text}"
    print(f"   ✅ 管理员确认预约成功")
    print(f"   - 状态：SOLD")
    print()
    
    # 验证最终状态
    print("8. 验证最终状态...")
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=buyer_headers)
    assert response.status_code == 200
    bike_data = response.json()
    assert bike_data["status"] == "SOLD", f"最终状态应为 SOLD，实际为 {bike_data['status']}"
    print(f"   ✅ 最终状态：{bike_data['status']}")
    print()
    
    print("=" * 70)
    print("✅ 买家流程测试通过！")
    print("=" * 70)
    print()
    print("流程总结：")
    print("1. ✅ 买家登记自行车（PENDING_APPROVAL）")
    print("2. ✅ 管理员审核通过（→ IN_STOCK）")
    print("3. ✅ 管理员提出时间段（→ LOCKED）")
    print("4. ✅ 买家选择时间段（LOCKED）")
    print("5. ✅ 管理员确认预约（→ SOLD）")
    print()

if __name__ == "__main__":
    test_buyer_flow()
