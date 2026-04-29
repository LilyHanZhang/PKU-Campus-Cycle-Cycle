#!/usr/bin/env python3
"""
测试卖家和买家流程显示在正确的列表中
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestSellerBuyerDisplayLists:
    """测试卖家和买家流程显示在正确的列表中"""
    
    def test_01_seller_flow_shows_in_waiting_bicycles(self, admin_token):
        """测试 1：卖家选择时间段后出现在 waiting_bicycles 列表中"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 创建卖家流程 ==========
        print("\n【卖家流程】")
        print("1. 管理员作为卖家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Flow Test",
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
        
        # ========== 检查管理后台显示 ==========
        print("\n【检查管理后台显示】")
        print("4. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        
        print(f"   waiting_bicycles（卖家已选）：{len(waiting_bicycles)} 个")
        print(f"   waiting_appointments（买家已选）：{len(waiting_appointments)} 个")
        
        # 验证卖家流程的自行车在 waiting_bicycles 中
        seller_bike_in_waiting_bicycles = False
        for bike in waiting_bicycles:
            print(f"      - 自行车 ID: {bike['id']}, 品牌：{bike['brand']}")
            if bike['id'] == str(bike_id):
                seller_bike_in_waiting_bicycles = True
                print(f"      ✅ 卖家流程的自行车在 waiting_bicycles 中")
        
        assert seller_bike_in_waiting_bicycles, "卖家流程的自行车应该在 waiting_bicycles 中"
        
        # 验证卖家流程的自行车不在 waiting_appointments 中
        seller_bike_in_waiting_appointments = False
        for apt in waiting_appointments:
            if apt['bicycle_id'] == str(bike_id):
                seller_bike_in_waiting_appointments = True
                print(f"      ❌ 错误：卖家流程的自行车出现在 waiting_appointments 中！")
        
        assert not seller_bike_in_waiting_appointments, "卖家流程的自行车不应该在 waiting_appointments 中"
        
        print("   ✅ 卖家流程的自行车在正确的列表中（waiting_bicycles）")
        
        # ========== 确认时间段 ==========
        print("\n【确认时间段】")
        print("5. 管理员确认时间段")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   确认状态码：{response.status_code}")
        
        # 检查自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "RESERVED", f"卖家流程自行车状态应该是 RESERVED，实际是 {bike_status}"
        print("   ✅ 卖家流程确认后状态正确（RESERVED）")
    
    def test_02_buyer_flow_shows_in_waiting_appointments(self, admin_token):
        """测试 2：买家选择时间段后出现在 waiting_appointments 列表中"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 创建买家流程 ==========
        print("\n【买家流程】")
        print("1. 管理员作为买家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Buyer Flow Test",
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
        print("5. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        
        print(f"   waiting_bicycles（卖家已选）：{len(waiting_bicycles)} 个")
        print(f"   waiting_appointments（买家已选）：{len(waiting_appointments)} 个")
        
        # 验证买家流程的预约在 waiting_appointments 中
        buyer_appointment_in_waiting = False
        for apt in waiting_appointments:
            print(f"      - 预约 ID: {apt['id']}, 类型：{apt['type']}, 自行车 ID: {apt['bicycle_id']}")
            if apt['bicycle_id'] == str(bike_id):
                buyer_appointment_in_waiting = True
                print(f"      ✅ 买家流程的预约在 waiting_appointments 中")
                assert apt['type'] == 'pick-up', "买家流程的预约类型应该是 pick-up"
        
        assert buyer_appointment_in_waiting, "买家流程的预约应该在 waiting_appointments 中"
        
        # 验证买家流程的自行车不在 waiting_bicycles 中
        buyer_bike_in_waiting_bicycles = False
        for bike in waiting_bicycles:
            if bike['id'] == str(bike_id):
                buyer_bike_in_waiting_bicycles = True
                print(f"      ❌ 错误：买家流程的自行车出现在 waiting_bicycles 中！")
        
        assert not buyer_bike_in_waiting_bicycles, "买家流程的自行车不应该在 waiting_bicycles 中"
        
        print("   ✅ 买家流程的预约在正确的列表中（waiting_appointments）")
        
        # ========== 确认时间段 ==========
        print("\n【确认时间段】")
        print("6. 管理员确认时间段")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        print(f"   确认状态码：{response.status_code}")
        
        # 检查自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "SOLD", f"买家流程自行车状态应该是 SOLD，实际是 {bike_status}"
        print("   ✅ 买家流程确认后状态正确（SOLD）")
    
    def test_03_dashboard_lists_separation(self, admin_token):
        """测试 3：管理后台两个列表完全分离"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试列表分离】")
        print("1. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        
        print(f"   waiting_bicycles 数量：{len(waiting_bicycles)}")
        print(f"   waiting_appointments 数量：{len(waiting_appointments)}")
        
        # 验证 waiting_bicycles 中的自行车都是 LOCKED 状态
        for bike in waiting_bicycles:
            print(f"      - 自行车 ID: {bike['id']}, 状态：{bike['status']}")
            # 注意：这里无法直接获取状态，需要通过 API 查询
            # 但我们可以验证所有 waiting_bicycles 都不在 waiting_appointments 中
            for apt in waiting_appointments:
                assert bike['id'] != apt['bicycle_id'], "同一辆自行车不应该同时出现在两个列表中"
        
        # 验证 waiting_appointments 中的预约都是 pick-up 类型
        for apt in waiting_appointments:
            print(f"      - 预约 ID: {apt['id']}, 类型：{apt['type']}")
            assert apt['type'] == 'pick-up', f"waiting_appointments 中的预约应该是 pick-up 类型，实际是 {apt['type']}"
        
        print("   ✅ 两个列表完全分离，没有重叠")


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
