#!/usr/bin/env python3
"""
测试新的自行车状态系统

验证卖家线和买家线使用不同的状态，避免混淆
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestNewBicycleStatusSystem:
    """测试新的自行车状态系统"""
    
    def test_01_seller_flow_status_transitions(self):
        """测试 1：卖家流程状态转换"""
        print("\n" + "=" * 60)
        print("测试卖家流程状态转换")
        print("=" * 60)
        
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【步骤 1】卖家登记自行车（PENDING_APPROVAL）")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test",
            "model": "Seller Flow",
            "color": "Blue",
            "license_number": f"SELLER{datetime.now().timestamp()}",
            "description": "Seller flow test",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        assert bicycle_response.status_code == 200
        bike_id = bicycle_response.json()["id"]
        bike_status = bicycle_response.json()["status"]
        print(f"   自行车 ID: {bike_id}")
        print(f"   初始状态：{bike_status}")
        assert bike_status == "PENDING_APPROVAL"
        
        print("\n【步骤 2】管理员审核并提出时间段（→ PENDING_SELLER_SLOT_SELECTION）")
        time_slots = [
            {
                "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
            }
        ]
        propose_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
        assert propose_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   提出时间段后状态：{bike_status}")
        assert bike_status == "PENDING_SELLER_SLOT_SELECTION", f"应该是 PENDING_SELLER_SLOT_SELECTION，实际是 {bike_status}"
        
        print("\n【步骤 3】卖家选择时间段（→ PENDING_ADMIN_CONFIRMATION_SELLER）")
        # 获取时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) > 0
        
        # 选择时间段
        select_response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert select_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   选择时间段后状态：{bike_status}")
        assert bike_status == "PENDING_ADMIN_CONFIRMATION_SELLER", f"应该是 PENDING_ADMIN_CONFIRMATION_SELLER，实际是 {bike_status}"
        
        print("\n【步骤 4】管理员确认时间段（→ RESERVED）")
        confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}", json={}, headers=admin_headers)
        assert confirm_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   确认时间段后状态：{bike_status}")
        assert bike_status == "RESERVED", f"应该是 RESERVED，实际是 {bike_status}"
        
        print("\n✅ 卖家流程状态转换测试通过")
        print("   PENDING_APPROVAL → PENDING_SELLER_SLOT_SELECTION → PENDING_ADMIN_CONFIRMATION_SELLER → RESERVED")
    
    def test_02_buyer_flow_status_transitions(self):
        """测试 2：买家流程状态转换"""
        print("\n" + "=" * 60)
        print("测试买家流程状态转换")
        print("=" * 60)
        
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【步骤 1】管理员登记自行车并审核（PENDING_APPROVAL → IN_STOCK）")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test",
            "model": "Buyer Flow",
            "color": "Red",
            "license_number": f"BUYER{datetime.now().timestamp()}",
            "description": "Buyer flow test",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        assert bicycle_response.status_code == 200
        bike_id = bicycle_response.json()["id"]
        
        # 管理员审核
        approve_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/approve", json={}, headers=admin_headers)
        assert approve_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   审核后状态：{bike_status}")
        assert bike_status == "IN_STOCK"
        
        print("\n【步骤 2】买家预约自行车（→ PENDING_BUYER_SLOT_SELECTION）")
        appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
            "bicycle_id": bike_id,
            "type": "pick-up",
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "notes": "Buyer flow test"
        }, headers=admin_headers)
        assert appointment_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   预约后状态：{bike_status}")
        assert bike_status == "PENDING_BUYER_SLOT_SELECTION", f"应该是 PENDING_BUYER_SLOT_SELECTION，实际是 {bike_status}"
        
        print("\n【步骤 3】管理员提出时间段（保持 PENDING_BUYER_SLOT_SELECTION）")
        time_slots = [
            {
                "start_time": (datetime.now() + timedelta(days=2, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=2, hours=12)).isoformat()
            }
        ]
        propose_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
        assert propose_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   提出时间段后状态：{bike_status}")
        assert bike_status == "PENDING_BUYER_SLOT_SELECTION", f"应该是 PENDING_BUYER_SLOT_SELECTION，实际是 {bike_status}"
        
        print("\n【步骤 4】买家选择时间段（→ PENDING_ADMIN_CONFIRMATION_BUYER）")
        # 获取时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) > 0
        
        # 选择时间段
        select_response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert select_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   选择时间段后状态：{bike_status}")
        assert bike_status == "PENDING_ADMIN_CONFIRMATION_BUYER", f"应该是 PENDING_ADMIN_CONFIRMATION_BUYER，实际是 {bike_status}"
        
        print("\n【步骤 5】管理员确认时间段（→ SOLD）")
        confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}", json={}, headers=admin_headers)
        assert confirm_response.status_code == 200
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   确认时间段后状态：{bike_status}")
        assert bike_status == "SOLD", f"应该是 SOLD，实际是 {bike_status}"
        
        print("\n✅ 买家流程状态转换测试通过")
        print("   PENDING_APPROVAL → IN_STOCK → PENDING_BUYER_SLOT_SELECTION → PENDING_ADMIN_CONFIRMATION_BUYER → SOLD")
    
    def test_03_admin_dashboard_shows_waiting_bicycles(self):
        """测试 3：管理员仪表盘显示等待确认的自行车"""
        print("\n" + "=" * 60)
        print("测试管理员仪表盘显示等待确认的自行车")
        print("=" * 60)
        
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【步骤 1】获取管理员仪表盘数据")
        dashboard_response = requests.get(f"{BASE_URL}/bicycles/dashboard", headers=admin_headers)
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()
        
        print(f"   待审核自行车：{dashboard_data.get('pending_bicycles_count', 0)}")
        print(f"   等待确认的预约：{dashboard_data.get('waiting_appointments_count', 0)}")
        print(f"   等待确认的自行车：{len(dashboard_data.get('waiting_bicycles', []))}")
        
        # 检查 waiting_bicycles 列表
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        print(f"\n   等待确认的自行车列表:")
        for bike in waiting_bicycles:
            print(f"      - {bike['id'][:8]}... 状态：{bike['status']} 所有者：{bike.get('owner_username', '未知')}")
        
        # 验证状态
        for bike in waiting_bicycles:
            assert bike['status'] == 'PENDING_ADMIN_CONFIRMATION_SELLER', f"应该是 PENDING_ADMIN_CONFIRMATION_SELLER，实际是 {bike['status']}"
        
        print("\n✅ 管理员仪表盘显示测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
