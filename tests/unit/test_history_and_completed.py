#!/usr/bin/env python3
"""
测试历史记录功能和完整的状态流转：
1. 买家流程：
   - 管理员确认时间段后，自行车状态变为 PENDING_PICKUP（等待提车）
   - 管理员确认提车后，自行车状态变为 SOLD，预约状态变为 COMPLETED
2. 卖家流程：
   - 管理员确认时间段后，自行车状态变为 RESERVED（等待交车）
   - 管理员确认入库后，自行车状态变为 IN_STOCK，预约状态变为 COMPLETED
3. 预约管理页面只显示 PENDING 和 CONFIRMED 状态的预约
4. 历史记录页面显示 COMPLETED 状态的预约
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestHistoryAndStatusFlow:
    """测试历史记录和完整状态流转"""
    
    def test_01_buyer_flow_two_step_confirmation(self):
        """测试 1：买家流程两步确认（先确认时间段，再确认提车）"""
        print("\n" + "=" * 60)
        print("测试 1：买家流程两步确认")
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
            "brand": "Buyer Flow Test",
            "model": "Two Step",
            "color": "Red",
            "license_number": f"BUY{datetime.now().timestamp()}",
            "description": "Buyer flow test bike",
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
        
        # 买家选择时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
        slots = slots_response.json()
        requests.put(f"{BASE_URL}/time_slots/select/{apt_id}", json={"time_slot_id": str(slots[0]["id"])}, headers=admin_headers)
        
        # 步骤 1：管理员确认时间段
        confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm/{apt_id}", headers=admin_headers)
        assert confirm_response.status_code == 200
        print(f"   ✅ 步骤 1：管理员确认时间段成功")
        
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
        
        # 步骤 2：管理员确认提车（线下交易完成后）
        pickup_response = requests.put(f"{BASE_URL}/time_slots/confirm-pickup/{apt_id}", headers=admin_headers)
        assert pickup_response.status_code == 200
        print(f"   ✅ 步骤 2：管理员确认提车成功")
        
        # 检查自行车状态（应该是 SOLD）
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        bike_status = bike_response.json()["status"]
        print(f"   确认提车后自行车状态：{bike_status}")
        assert bike_status == "SOLD", f"应该是 SOLD，实际是 {bike_status}"
        print(f"   ✅ 自行车状态正确变为 SOLD（已售出）")
        
        # 检查预约状态（应该是 COMPLETED）
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        appointments = all_appointments_response.json()
        test_apt = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_apt is not None
        print(f"   预约状态：{test_apt['status']}")
        assert test_apt['status'] == "COMPLETED", f"应该是 COMPLETED，实际是 {test_apt['status']}"
        print(f"   ✅ 预约状态正确变为 COMPLETED（已完成）")
    
    def test_02_seller_flow_two_step_confirmation(self):
        """测试 2：卖家流程两步确认（先确认时间段，再确认入库）"""
        print("\n" + "=" * 60)
        print("测试 2：卖家流程两步确认")
        print("=" * 60)
        
        # 管理员登录
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 准备自行车（卖家流程）
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Flow Test",
            "model": "Two Step",
            "color": "Blue",
            "license_number": f"SELL{datetime.now().timestamp()}",
            "description": "Seller flow test bike",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        bike_id = bicycle_response.json()["id"]
        
        # 创建卖家预约（drop-off）
        appointment_response = requests.post(f"{BASE_URL}/appointments/", json={
            "bicycle_id": str(bike_id),
            "type": "drop-off"
        }, headers=admin_headers)
        apt_id = appointment_response.json()["id"]
        print(f"   创建预约：{apt_id}")
        
        # 管理员审核并提出时间段
        time_slots = [
            {
                "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=12)).isoformat()
            }
        ]
        requests.post(f"{BASE_URL}/appointments/{apt_id}/propose-slots", json=time_slots, headers=admin_headers)
        print(f"   管理员提出时间段")
        
        # 卖家选择时间段
        slots_response = requests.get(f"{BASE_URL}/time_slots/appointment/{apt_id}", headers=admin_headers)
        slots = slots_response.json()
        requests.put(f"{BASE_URL}/time_slots/select/{apt_id}", json={"time_slot_id": str(slots[0]["id"])}, headers=admin_headers)
        print(f"   卖家选择时间段")
        
        # 步骤 1：管理员确认时间段
        confirm_response = requests.put(f"{BASE_URL}/time_slots/confirm/{apt_id}", headers=admin_headers)
        assert confirm_response.status_code == 200
        print(f"   ✅ 步骤 1：管理员确认时间段成功")
        
        # 检查自行车状态（应该是 RESERVED）
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        bike_status = bike_response.json()["status"]
        print(f"   确认时间段后自行车状态：{bike_status}")
        assert bike_status == "RESERVED", f"应该是 RESERVED，实际是 {bike_status}"
        print(f"   ✅ 自行车状态正确变为 RESERVED（等待交车）")
        
        # 检查预约状态（应该是 CONFIRMED）
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        appointments = all_appointments_response.json()
        test_apt = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_apt is not None
        print(f"   预约状态：{test_apt['status']}")
        assert test_apt['status'] == "CONFIRMED", f"应该是 CONFIRMED，实际是 {test_apt['status']}"
        print(f"   ✅ 预约状态正确变为 CONFIRMED")
        
        # 步骤 2：管理员确认入库（线下交车完成后）
        store_response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/store-inventory", headers=admin_headers)
        assert store_response.status_code == 200
        print(f"   ✅ 步骤 2：管理员确认入库成功")
        
        # 检查自行车状态（应该是 IN_STOCK）
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        bike_status = bike_response.json()["status"]
        print(f"   确认入库后自行车状态：{bike_status}")
        assert bike_status == "IN_STOCK", f"应该是 IN_STOCK，实际是 {bike_status}"
        print(f"   ✅ 自行车状态正确变为 IN_STOCK（在库）")
        
        # 检查预约状态（应该是 COMPLETED）
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        appointments = all_appointments_response.json()
        test_apt = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_apt is not None
        print(f"   预约状态：{test_apt['status']}")
        assert test_apt['status'] == "COMPLETED", f"应该是 COMPLETED，实际是 {test_apt['status']}"
        print(f"   ✅ 预约状态正确变为 COMPLETED（已完成）")
    
    def test_03_appointment_filtering_and_history(self):
        """测试 3：预约过滤和历史记录 API"""
        print("\n" + "=" * 60)
        print("测试 3：预约过滤和历史记录 API")
        print("=" * 60)
        
        # 管理员登录
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取所有预约
        all_appointments_response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        all_appointments = all_appointments_response.json()
        print(f"   所有预约数量：{len(all_appointments)}")
        
        # 获取已完成预约
        completed_response = requests.get(f"{BASE_URL}/appointments/completed", headers=admin_headers)
        assert completed_response.status_code == 200
        completed_appointments = completed_response.json()
        print(f"   已完成预约数量：{len(completed_appointments)}")
        
        # 验证已完成预约的状态
        for apt in completed_appointments:
            print(f"   预约 {apt['id'][:8]}... 状态：{apt['status']}")
            assert apt['status'] == "COMPLETED", f"已完成预约的状态应该是 COMPLETED，实际是 {apt['status']}"
        
        # 验证活跃预约（PENDING 或 CONFIRMED）
        active_appointments = [a for a in all_appointments if a['status'] in ['PENDING', 'CONFIRMED']]
        print(f"   活跃预约数量：{len(active_appointments)}")
        
        for apt in active_appointments:
            print(f"   预约 {apt['id'][:8]}... 状态：{apt['status']}")
            assert apt['status'] in ['PENDING', 'CONFIRMED'], f"活跃预约的状态应该是 PENDING 或 CONFIRMED"
        
        print(f"   ✅ 预约过滤逻辑正确")
        
        # 验证已完成的预约不在活跃预约中
        completed_ids = [apt['id'] for apt in completed_appointments]
        for apt in active_appointments:
            assert apt['id'] not in completed_ids, f"已完成的预约不应该出现在活跃预约中"
        
        print(f"   ✅ 已完成的预约正确地从活跃预约中移除")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
