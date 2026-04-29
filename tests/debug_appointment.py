#!/usr/bin/env python3
"""
调试买家预约时间段选择问题
模拟前端完整流程
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def debug_buyer_appointment_flow():
    print("\n" + "=" * 60)
    print("调试买家预约时间段选择问题")
    print("=" * 60)
    
    # 登录超级管理员
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    print("\n【步骤 1】获取所有自行车")
    bikes_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
    bikes = bikes_response.json()
    print(f"   自行车数量：{len(bikes)}")
    
    # 找到一个 IN_STOCK 状态的自行车
    in_stock_bike = next((b for b in bikes if b['status'] == 'IN_STOCK'), None)
    
    if not in_stock_bike:
        print("   没有在库自行车，创建一辆...")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Debug",
            "model": "Test Bike",
            "color": "Blue",
            "license_number": f"DEBUG{datetime.now().timestamp()}",
            "description": "Debug bike",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        bike_id = bicycle_response.json()["id"]
        
        # 审核通过
        requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        in_stock_bike = {"id": bike_id, "brand": "Debug", "status": "IN_STOCK"}
    
    print(f"   使用自行车：{in_stock_bike['id']} ({in_stock_bike['brand']})")
    bike_id = in_stock_bike['id']
    
    print("\n【步骤 2】创建买家预约")
    appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
        "bicycle_id": str(bike_id),
        "type": "pick-up",
        "appointment_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "notes": "Debug appointment"
    }, headers=admin_headers)
    
    if appointment_response.status_code == 200:
        apt_id = appointment_response.json()["id"]
        print(f"   ✅ 预约创建成功：{apt_id}")
        print(f"   预约数据类型：{type(apt_id)}")
        print(f"   预约 ID 长度：{len(apt_id)}")
        
        print("\n【步骤 3】获取所有预约（模拟前端）")
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        all_appointments = all_appointments_response.json()
        print(f"   预约数量：{len(all_appointments)}")
        
        # 找到刚才创建的预约
        test_apt = next((a for a in all_appointments if a['id'] == apt_id), None)
        if test_apt:
            print(f"   ✅ 找到预约：{test_apt['id']}")
            print(f"   预约状态：{test_apt['status']}")
            print(f"   预约 ID 类型：{type(test_apt['id'])}")
            
            print("\n【步骤 4】尝试为预约提出时间段")
            print(f"   使用的预约 ID: {apt_id}")
            print(f"   URL: {BASE_URL}/appointments/{apt_id}/propose-slots")
            
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
            
            print(f"   响应状态码：{propose_response.status_code}")
            print(f"   响应内容：{propose_response.json()}")
            
            if propose_response.status_code == 200:
                print(f"   ✅ 提出时间段成功！")
            else:
                print(f"   ❌ 提出时间段失败：{propose_response.json().get('detail', 'Unknown error')}")
        else:
            print(f"   ❌ 未找到预约 {apt_id}")
    else:
        print(f"   ❌ 创建预约失败：{appointment_response.status_code}")
        print(f"   错误信息：{appointment_response.json()}")

if __name__ == "__main__":
    debug_buyer_appointment_flow()
