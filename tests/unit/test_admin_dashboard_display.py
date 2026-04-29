#!/usr/bin/env python3
"""
测试管理后台显示逻辑，确保卖家流程不会出现在等待确认列表中
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestAdminDashboardDisplay:
    """测试管理后台显示逻辑"""
    
    def test_01_seller_flow_not_in_waiting_appointments(self, admin_token):
        """测试 1：卖家流程确认后不出现在等待确认列表中"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 创建卖家流程 ==========
        print("\n【创建卖家流程】")
        print("1. 管理员作为卖家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Flow Test Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        print("2. 管理员提出时间段（卖家流程）")
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        print("3. 管理员（作为卖家）选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        print(f"   时间段类型：{slots[0]['appointment_type']}")
        assert slots[0]["appointment_type"] == "pick-up"  # 卖家流程应该是 pick-up
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   选择状态码：{response.status_code}")
        
        print("4. 管理员确认时间段")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   确认状态码：{response.status_code}")
        
        # ========== 检查管理后台显示 ==========
        print("\n【检查管理后台显示】")
        print("5. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        print(f"   待处理自行车登记：{dashboard_data['pending_bicycles_count']}")
        print(f"   待处理预约：{dashboard_data['pending_appointments_count']}")
        print(f"   等待确认总数：{dashboard_data['waiting_confirmation_count']}")
        
        # 检查等待确认的预约
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        print(f"   等待确认的预约列表：{len(waiting_appointments)} 个")
        
        # 验证卖家流程的预约不在等待确认列表中
        seller_appointment_in_waiting = False
        for apt in waiting_appointments:
            print(f"      - 预约 ID: {apt['id']}, 类型：{apt['type']}, 自行车 ID: {apt['bicycle_id']}")
            if apt['bicycle_id'] == str(bike_id):
                seller_appointment_in_waiting = True
                print(f"      ❌ 错误：卖家流程的预约出现在等待确认列表中！")
        
        assert not seller_appointment_in_waiting, "卖家流程的预约不应该出现在等待确认列表中"
        print("   ✅ 卖家流程的预约不在等待确认列表中")
        
        # 验证等待确认的预约都是买家流程（pick-up）
        for apt in waiting_appointments:
            assert apt['type'] == 'pick-up', f"等待确认的预约应该是买家流程（pick-up），实际是 {apt['type']}"
        
        print("   ✅ 所有等待确认的预约都是买家流程（pick-up）")
        
        # ========== 检查预约管理显示 ==========
        print("\n【检查预约管理显示】")
        print("6. 获取所有预约")
        response = requests.get(f"{BASE_URL}/appointments/", headers=admin_headers)
        assert response.status_code == 200
        all_appointments = response.json()
        
        # 找到卖家流程的预约
        seller_appointment = None
        for apt in all_appointments:
            if apt['bicycle_id'] == str(bike_id):
                seller_appointment = apt
                break
        
        assert seller_appointment is not None, "卖家流程的预约应该存在"
        print(f"   卖家流程预约 ID: {seller_appointment['id']}")
        print(f"   卖家流程预约类型：{seller_appointment['type']}")
        print(f"   卖家流程预约状态：{seller_appointment['status']}")
        
        # 验证卖家流程预约的状态
        assert seller_appointment['type'] == 'drop-off', "卖家流程的预约类型应该是 drop-off"
        assert seller_appointment['status'] == 'CONFIRMED', "卖家流程的预约状态应该是 CONFIRMED"
        print("   ✅ 卖家流程预约状态正确（CONFIRMED, drop-off）")
    
    def test_02_buyer_flow_in_waiting_appointments(self, admin_token):
        """测试 2：买家流程确认后出现在等待确认列表中"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 创建买家流程 ==========
        print("\n【创建买家流程】")
        print("1. 管理员作为买家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Buyer Flow Test Bike",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        print("2. 另一个管理员审核通过")
        admin2_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin2_token = admin2_response.json()["access_token"]
        admin2_headers = {"Authorization": f"Bearer {admin2_token}"}
        
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin2_headers)
        assert response.status_code == 200
        print(f"   审核后状态：{response.json()['status']}")
        
        print("3. 管理员提出时间段（买家流程）")
        now = datetime.now(timezone.utc)
        time_slots = [{
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }]
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
            json=time_slots,
            headers=admin2_headers
        )
        assert response.status_code == 200
        print(f"   提出时间段状态：{response.status_code}")
        
        print("4. 管理员（作为买家）选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        print(f"   时间段类型：{slots[0]['appointment_type']}")
        assert slots[0]["appointment_type"] == "drop-off"  # 买家流程应该是 drop-off
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   选择状态码：{response.status_code}")
        
        # ========== 检查管理后台显示 ==========
        print("\n【检查管理后台显示】")
        print("5. 获取管理后台数据（买家流程应该出现在等待确认列表中）")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        # 检查等待确认的预约
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        print(f"   等待确认的预约列表：{len(waiting_appointments)} 个")
        
        # 验证买家流程的预约在等待确认列表中
        buyer_appointment_in_waiting = False
        for apt in waiting_appointments:
            print(f"      - 预约 ID: {apt['id']}, 类型：{apt['type']}, 自行车 ID: {apt['bicycle_id']}")
            if apt['bicycle_id'] == str(bike_id):
                buyer_appointment_in_waiting = True
                print(f"      ✅ 买家流程的预约出现在等待确认列表中")
                assert apt['type'] == 'pick-up', "买家流程的预约类型应该是 pick-up"
        
        assert buyer_appointment_in_waiting, "买家流程的预约应该出现在等待确认列表中"
        print("   ✅ 买家流程的预约在等待确认列表中")
    
    def test_03_dashboard_waiting_appointments_type_filter(self, admin_token):
        """测试 3：等待确认列表只包含 pick-up 类型的预约"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试等待确认列表类型过滤】")
        print("1. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        print(f"   等待确认的预约数量：{len(waiting_appointments)}")
        
        # 验证所有等待确认的预约都是 pick-up 类型
        for apt in waiting_appointments:
            print(f"      - 预约 ID: {apt['id']}, 类型：{apt['type']}")
            assert apt['type'] == 'pick-up', f"等待确认的预约应该是 pick-up 类型，实际是 {apt['type']}"
        
        print("   ✅ 所有等待确认的预约都是 pick-up 类型（买家流程）")


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
