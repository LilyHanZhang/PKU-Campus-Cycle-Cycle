#!/usr/bin/env python3
"""
测试管理员确认卖家时间段的功能
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestAdminConfirmSellerTimeSlot:
    """测试管理员确认卖家时间段的功能"""
    
    def test_01_admin_can_confirm_seller_time_slot(self, admin_token):
        """测试 1：管理员可以确认卖家选择的时间段"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # ========== 创建卖家流程 ==========
        print("\n【创建卖家流程】")
        print("1. 管理员作为卖家登记自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Seller Confirm Test",
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
        print("4. 获取管理后台数据，确认在 waiting_bicycles 列表中")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        seller_bike_in_list = False
        for bike in waiting_bicycles:
            if bike['id'] == str(bike_id):
                seller_bike_in_list = True
                print(f"   ✅ 自行车在 waiting_bicycles 列表中")
                break
        
        assert seller_bike_in_list, "卖家流程的自行车应该在 waiting_bicycles 列表中"
        
        # ========== 管理员确认时间段 ==========
        print("\n【管理员确认时间段】")
        print("5. 调用 /bicycles/{bike_id}/confirm 接口确认")
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/confirm",
            json={},
            headers=admin_headers
        )
        print(f"   确认状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200, f"确认失败：{response.text}"
        assert "确认成功" in response.json()["message"]
        
        # ========== 检查确认后的状态 ==========
        print("\n【检查确认后的状态】")
        print("6. 检查自行车状态")
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "RESERVED", f"卖家流程自行车状态应该是 RESERVED，实际是 {bike_status}"
        
        print("7. 检查预约状态")
        response = requests.get(f"{BASE_URL}/appointments/?status=CONFIRMED", headers=admin_headers)
        assert response.status_code == 200
        confirmed_appointments = response.json()
        
        seller_appointment = None
        for apt in confirmed_appointments:
            if apt['bicycle_id'] == str(bike_id):
                seller_appointment = apt
                break
        
        assert seller_appointment is not None, "应该找到已确认的预约"
        print(f"   预约状态：{seller_appointment['status']}")
        print(f"   预约类型：{seller_appointment['type']}")
        assert seller_appointment['status'] == 'CONFIRMED'
        assert seller_appointment['type'] == 'drop-off'
        
        print("   ✅ 确认成功，状态正确")
    
    def test_02_confirm_without_time_slot_selected(self, admin_token):
        """测试 2：卖家还未选择时间段时确认应该失败"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试未选择时间段确认】")
        print("1. 创建卖家流程自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "No Time Slot Test",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        print("2. 管理员提出时间段")
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
        
        print("3. 卖家还未选择时间段，管理员直接确认应该失败")
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/confirm",
            json={},
            headers=admin_headers
        )
        print(f"   确认状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 400, "卖家未选择时间段时确认应该失败"
        assert "待处理" in response.json()["detail"] or "时间段" in response.json()["detail"]
        print("   ✅ 正确返回错误")
    
    def test_03_buyer_flow_confirm_via_bicycles_confirm(self, admin_token):
        """测试 3：买家流程也可以通过 /bicycles/{bike_id}/confirm 确认"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试买家流程确认】")
        print("1. 创建买家流程自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Buyer Confirm Test",
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
        print("2. 另一个管理员审核通过")
        admin2_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        admin2_token = admin2_response.json()["access_token"]
        admin2_headers = {"Authorization": f"Bearer {admin2_token}"}
        
        response = requests.put(f"{BASE_URL}/bicycles/{bike_id}/approve", headers=admin2_headers)
        assert response.status_code == 200
        
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
        
        print("4. 买家选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        assert len(slots) > 0
        assert slots[0]["appointment_type"] == "drop-off"  # 买家流程应该是 drop-off
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        print("5. 管理员确认时间段（通过 /bicycles/{bike_id}/confirm）")
        response = requests.post(
            f"{BASE_URL}/bicycles/{bike_id}/confirm",
            json={},
            headers=admin_headers
        )
        print(f"   确认状态码：{response.status_code}")
        print(f"   响应：{response.text}")
        assert response.status_code == 200, f"确认失败：{response.text}"
        
        # 检查自行车状态
        response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        bike_status = response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "SOLD", f"买家流程自行车状态应该是 SOLD，实际是 {bike_status}"
        print("   ✅ 买家流程确认成功，状态正确")


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
