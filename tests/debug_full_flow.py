#!/usr/bin/env python3
"""
完整测试买家预约流程
模拟买家创建预约 -> 管理员提出时间段
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def test_full_buyer_appointment_flow():
    print("\n" + "=" * 60)
    print("完整测试买家预约流程")
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
    
    # 2. 获取或创建自行车
    print("\n【2】准备自行车")
    bikes_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
    bikes = bikes_response.json()
    
    in_stock_bike = next((b for b in bikes if b['status'] == 'IN_STOCK'), None)
    if not in_stock_bike:
        print("   创建新的自行车...")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Full Test",
            "model": "Buyer Flow",
            "color": "Green",
            "license_number": f"FULLTEST{datetime.now().timestamp()}",
            "description": "Full flow test bike",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        bike_id = bicycle_response.json()["id"]
        requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        in_stock_bike = {"id": bike_id, "brand": "Full Test"}
    
    bike_id = in_stock_bike['id']
    print(f"   使用自行车：{bike_id} ({in_stock_bike['brand']})")
    
    # 3. 模拟买家创建预约
    print("\n【3】买家创建预约（模拟前端调用）")
    # 注意：前端调用时只传递 bicycle_id 和 type，不传递 appointment_time 和 notes
    appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
        "bicycle_id": str(bike_id),
        "type": "pick-up"
        # 不传递 appointment_time 和 notes，模拟前端行为
    }, headers=admin_headers)
    
    print(f"   响应状态码：{appointment_response.status_code}")
    if appointment_response.status_code == 200:
        apt_id = appointment_response.json()["id"]
        apt_data = appointment_response.json()
        print(f"   ✅ 预约创建成功")
        print(f"   预约 ID: {apt_id}")
        print(f"   预约数据：{apt_data}")
        
        # 4. 获取所有预约（模拟前端获取预约列表）
        print("\n【4】获取所有预约（模拟前端）")
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        all_appointments = all_appointments_response.json()
        print(f"   预约数量：{len(all_appointments)}")
        
        # 找到刚才创建的预约
        test_apt = next((a for a in all_appointments if a['id'] == apt_id), None)
        if test_apt:
            print(f"   ✅ 找到预约：{test_apt['id']}")
            print(f"   预约状态：{test_apt['status']}")
            print(f"   预约类型：{test_apt['type']}")
            
            # 5. 管理员尝试提出时间段
            print("\n【5】管理员为预约提出时间段")
            print(f"   使用的预约 ID: {apt_id}")
            print(f"   请求 URL: {BASE_URL}/appointments/{apt_id}/propose-slots")
            
            time_slots = [
                {
                    "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                    "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
                }
            ]
            
            print(f"   请求数据：{time_slots}")
            
            propose_response = requests.post(
                f"{BASE_URL}/appointments/{apt_id}/propose-slots",
                json=time_slots,
                headers=admin_headers
            )
            
            print(f"   响应状态码：{propose_response.status_code}")
            print(f"   响应内容：{propose_response.json()}")
            
            if propose_response.status_code == 200:
                print(f"   ✅ 提出时间段成功！")
            else:
                print(f"   ❌ 提出时间段失败")
                print(f"   错误详情：{propose_response.json().get('detail', 'Unknown error')}")
        else:
            print(f"   ❌ 未找到预约 {apt_id}")
            print(f"   所有预约 ID: {[a['id'] for a in all_appointments]}")
    else:
        print(f"   ❌ 创建预约失败")
        print(f"   错误信息：{appointment_response.json()}")

if __name__ == "__main__":
    test_full_buyer_appointment_flow()
