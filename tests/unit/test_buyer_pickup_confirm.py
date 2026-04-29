#!/usr/bin/env python3
"""
测试买家流程确认提车后自行车状态变化
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def test_buyer_pickup_confirmation():
    print("\n" + "=" * 60)
    print("测试买家流程确认提车后自行车状态变化")
    print("=" * 60)
    
    # 1. 管理员登录
    print("\n【1】管理员登录")
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"   ✅ 管理员登录成功")
    
    # 2. 准备自行车
    print("\n【2】准备自行车")
    bikes_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
    bikes = bikes_response.json()
    
    in_stock_bike = next((b for b in bikes if b['status'] == 'IN_STOCK'), None)
    if not in_stock_bike:
        print("   创建新的自行车...")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Pickup Test",
            "model": "Buyer Flow",
            "color": "Yellow",
            "license_number": f"PICKUP{datetime.now().timestamp()}",
            "description": "Pickup test bike",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        bike_id = bicycle_response.json()["id"]
        requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        in_stock_bike = {"id": bike_id, "brand": "Pickup Test"}
    
    bike_id = in_stock_bike['id']
    print(f"   使用自行车：{bike_id} ({in_stock_bike['brand']})")
    
    # 3. 创建买家预约
    print("\n【3】创建买家预约（pick-up）")
    appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
        "bicycle_id": str(bike_id),
        "type": "pick-up"
    }, headers=admin_headers)
    
    if appointment_response.status_code == 200:
        apt_id = appointment_response.json()["id"]
        print(f"   ✅ 预约创建成功：{apt_id}")
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        bike_status = bike_response.json()["status"]
        print(f"   预约后自行车状态：{bike_status}")
        
        # 4. 管理员提出时间段
        print("\n【4】管理员提出时间段")
        time_slots = [
            {
                "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
            }
        ]
        
        propose_response = requests.post(
            f"{BASE_URL}/appointments/{apt_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        
        if propose_response.status_code == 200:
            print(f"   ✅ 提出时间段成功")
            
            # 5. 买家选择时间段
            print("\n【5】买家选择时间段")
            # 获取时间段
            slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
            slots = slots_response.json()
            
            if len(slots) > 0:
                selected_slot = slots[0]
                select_response = requests.put(
                    f"{BASE_URL}/time_slots/select/{apt_id}",
                    json={"time_slot_id": str(selected_slot["id"])},
                    headers=admin_headers
                )
                
                if select_response.status_code == 200:
                    print(f"   ✅ 选择时间段成功")
                    
                    # 6. 管理员确认时间段（确认提车）
                    print("\n【6】管理员确认时间段（确认提车）")
                    confirm_response = requests.put(
                        f"{BASE_URL}/time_slots/confirm/{apt_id}",
                        headers=admin_headers
                    )
                    
                    if confirm_response.status_code == 200:
                        print(f"   ✅ 确认成功：{confirm_response.json()['message']}")
                        
                        # 7. 检查自行车状态
                        print("\n【7】检查自行车状态")
                        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
                        bike_status = bike_response.json()["status"]
                        print(f"   确认提车后自行车状态：{bike_status}")
                        
                        if bike_status == "SOLD":
                            print(f"   ✅ 自行车状态正确变为 SOLD（已售出）")
                        else:
                            print(f"   ❌ 自行车状态应该是 SOLD，实际是 {bike_status}")
                        
                        # 8. 检查预约状态
                        print("\n【8】检查预约状态")
                        apt_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
                        appointments = apt_response.json()
                        test_apt = next((a for a in appointments if a['id'] == apt_id), None)
                        
                        if test_apt:
                            print(f"   预约状态：{test_apt['status']}")
                            if test_apt['status'] == "CONFIRMED":
                                print(f"   ✅ 预约状态正确变为 CONFIRMED")
                            else:
                                print(f"   ❌ 预约状态应该是 CONFIRMED，实际是 {test_apt['status']}")
                    else:
                        print(f"   ❌ 确认失败：{confirm_response.json()}")
                else:
                    print(f"   ❌ 选择时间段失败：{select_response.json()}")
            else:
                print(f"   ❌ 没有可用时间段")
        else:
            print(f"   ❌ 提出时间段失败：{propose_response.json()}")
    else:
        print(f"   ❌ 创建预约失败：{appointment_response.json()}")

if __name__ == "__main__":
    test_buyer_pickup_confirmation()
