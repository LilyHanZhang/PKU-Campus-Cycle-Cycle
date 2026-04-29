#!/usr/bin/env python3
"""
测试买家预约时间段选择功能
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestBuyerAppointmentTimeSlot:
    """测试买家预约时间段选择"""
    
    def test_01_buyer_appointment_propose_slots(self):
        """测试 1：管理员可以为买家预约提出时间段"""
        print("\n" + "=" * 60)
        print("测试买家预约时间段选择功能")
        print("=" * 60)
        
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【步骤 1】管理员登记一辆自行车")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test",
            "model": "Buyer Appointment Test",
            "color": "Red",
            "license_number": f"TEST{datetime.now().timestamp()}",
            "description": "Test for buyer appointment",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        assert bicycle_response.status_code == 200
        bike_id = bicycle_response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        print("\n【步骤 2】管理员审核通过")
        approve_response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin_headers)
        assert approve_response.status_code == 200
        print(f"   审核响应：{approve_response.json()['message']}")
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "IN_STOCK", f"应该是 IN_STOCK，实际是 {bike_status}"
        
        print("\n【步骤 3】管理员创建买家预约（提车）")
        appointment_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/appointments", json={
            "type": "pick-up",
            "appointment_time": (datetime.now() + timedelta(days=2)).isoformat(),
            "notes": "Test appointment"
        }, headers=admin_headers)
        assert appointment_response.status_code == 200
        apt_id = appointment_response.json()["id"]
        print(f"   预约 ID: {apt_id}")
        
        # 检查预约状态
        apt_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        assert apt_response.status_code == 200
        appointments = apt_response.json()
        test_appointment = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_appointment is not None
        print(f"   预约状态：{test_appointment['status']}")
        assert test_appointment['status'] == "PENDING", f"应该是 PENDING，实际是 {test_appointment['status']}"
        
        print("\n【步骤 4】获取所有预约（模拟前端请求）")
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        assert all_appointments_response.status_code == 200
        all_appointments = all_appointments_response.json()
        print(f"   所有预约数量：{len(all_appointments)}")
        
        # 验证能找到刚才的预约
        test_apt = next((a for a in all_appointments if a['id'] == apt_id), None)
        assert test_apt is not None, f"应该能找到预约 {apt_id}"
        print(f"   ✅ 找到了测试预约：{test_apt['id']}")
        
        print("\n【步骤 5】管理员为预约提出时间段")
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
        
        # 使用正确的端点
        propose_response = requests.post(
            f"{BASE_URL}/appointments/{apt_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        
        print(f"   响应状态码：{propose_response.status_code}")
        if propose_response.status_code != 200:
            print(f"   错误信息：{propose_response.json()}")
        
        assert propose_response.status_code == 200, f"提出时间段失败：{propose_response.json()}"
        print(f"   提出响应：{propose_response.json()['message']}")
        
        # 检查预约状态
        apt_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        assert apt_response.status_code == 200
        appointments = apt_response.json()
        test_appointment = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_appointment is not None
        print(f"   预约状态：{test_appointment['status']}")
        
        print("\n【步骤 6】买家查看可选时间段")
        slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        print(f"   时间段数量：{len(slots)}")
        assert len(slots) == 2, f"应该有 2 个时间段，实际是 {len(slots)}"
        
        for i, slot in enumerate(slots):
            print(f"   时间段 {i+1}: {slot['start_time']} - {slot['end_time']}")
            assert slot['is_booked'] == 'false', f"时间段应该未被预订"
        
        print("\n✅ 测试通过：管理员可以成功为买家预约提出时间段")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
