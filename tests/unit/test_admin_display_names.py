#!/usr/bin/env python3
"""
测试管理界面显示车辆名称和用户名的功能
"""
import pytest
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestAdminDisplayNames:
    """测试管理界面显示车辆名称和用户名"""
    
    def test_01_appointment_management_shows_bike_brand(self, admin_token):
        """测试 1：预约管理界面显示车辆名称"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试预约管理显示】")
        print("1. 创建买家流程自行车")
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test Bike Brand",
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
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        print("5. 获取所有预约，检查是否显示车辆名称")
        response = requests.get(f"{BASE_URL}/appointments/?status=PENDING", headers=admin_headers)
        assert response.status_code == 200
        appointments = response.json()
        
        # 找到刚创建的预约
        test_appointment = None
        for apt in appointments:
            if apt['bicycle_id'] == str(bike_id):
                test_appointment = apt
                break
        
        assert test_appointment is not None, "应该找到刚创建的预约"
        print(f"   预约 ID: {test_appointment['id']}")
        print(f"   车辆 ID: {test_appointment['bicycle_id']}")
        
        # 获取所有自行车，检查品牌
        response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
        assert response.status_code == 200
        bikes = response.json()
        
        bike_brand = None
        for bike in bikes:
            if bike['id'] == str(bike_id):
                bike_brand = bike['brand']
                break
        
        assert bike_brand == "Test Bike Brand", f"应该找到车辆品牌 Test Bike Brand，实际是 {bike_brand}"
        print(f"   ✅ 车辆品牌：{bike_brand}")
        print("   ✅ 预约管理界面可以显示车辆名称")
    
    def test_02_dashboard_shows_username_and_bike_brand(self, admin_token):
        """测试 2：仪表盘显示用户名和车辆名称"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试仪表盘显示】")
        print("1. 创建买家流程自行车")
        import random
        unique_brand = f"Dashboard Test Bike {random.randint(1000, 9999)}"
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": unique_brand,
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
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        print("5. 获取管理后台数据，检查 waiting_appointments")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_appointments = dashboard_data.get('waiting_appointments', [])
        
        # 找到刚创建的预约
        test_appointment = None
        for apt in waiting_appointments:
            if apt['bicycle_id'] == str(bike_id):
                test_appointment = apt
                break
        
        assert test_appointment is not None, "应该找到刚创建的预约"
        
        # 检查是否包含用户名和车辆品牌
        print(f"   预约 ID: {test_appointment['id']}")
        print(f"   用户 ID: {test_appointment['user_id']}")
        print(f"   用户名：{test_appointment.get('username', 'N/A')}")
        print(f"   车辆 ID: {test_appointment['bicycle_id']}")
        print(f"   车辆品牌：{test_appointment.get('bicycle_brand', 'N/A')}")
        
        assert 'username' in test_appointment, "waiting_appointments 应该包含 username 字段"
        assert 'bicycle_brand' in test_appointment, "waiting_appointments 应该包含 bicycle_brand 字段"
        # 用户名可能是邮箱或者 name 字段的值
        print(f"   ✅ 用户名：{test_appointment['username']}")
        assert test_appointment['bicycle_brand'] == unique_brand, f"车辆品牌应该是 {unique_brand}，实际是 {test_appointment['bicycle_brand']}"
        
        print("   ✅ 仪表盘显示用户名和车辆名称")
    
    def test_03_dashboard_shows_seller_username(self, admin_token):
        """测试 3：仪表盘显示卖家用户名"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试仪表盘显示卖家用户名】")
        print("1. 管理员作为卖家登记自行车")
        import random
        unique_brand = f"Seller Bike Test {random.randint(1000, 9999)}"
        response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": unique_brand,
            "condition": 8,
            "price": 300
        }, headers=admin_headers)
        assert response.status_code == 200
        bike_id = response.json()["id"]
        
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
        
        print("3. 管理员（作为卖家）选择时间段")
        response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert response.status_code == 200
        slots = response.json()
        
        response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(slots[0]["id"])},
            headers=admin_headers
        )
        assert response.status_code == 200
        
        print("4. 获取管理后台数据，检查 waiting_bicycles")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        waiting_bicycles = dashboard_data.get('waiting_bicycles', [])
        
        # 找到刚创建的自行车
        test_bike = None
        for bike in waiting_bicycles:
            if bike['id'] == str(bike_id):
                test_bike = bike
                break
        
        assert test_bike is not None, "应该找到刚创建的自行车"
        
        # 检查是否包含卖家用户名
        print(f"   自行车 ID: {test_bike['id']}")
        print(f"   品牌：{test_bike['brand']}")
        print(f"   卖家 ID: {test_bike['owner_id']}")
        print(f"   卖家用户名：{test_bike.get('owner_username', 'N/A')}")
        
        assert 'owner_username' in test_bike, "waiting_bicycles 应该包含 owner_username 字段"
        assert test_bike['brand'] == unique_brand, f"品牌应该是 {unique_brand}，实际是 {test_bike['brand']}"
        # 用户名可能是邮箱或者 name 字段的值
        print(f"   ✅ 卖家用户名：{test_bike['owner_username']}")
        
        print("   ✅ 仪表盘显示卖家用户名")
    
    def test_04_dashboard_data_completeness(self, admin_token):
        """测试 4：仪表盘数据完整性"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【测试仪表盘数据完整性】")
        print("1. 获取管理后台数据")
        response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard_data = response.json()
        
        print("2. 检查 waiting_appointments 字段")
        if dashboard_data.get('waiting_appointments'):
            for apt in dashboard_data['waiting_appointments']:
                print(f"   预约 ID: {apt['id']}")
                assert 'username' in apt, "每个预约都应该有 username"
                assert 'bicycle_brand' in apt, "每个预约都应该有 bicycle_brand"
                print(f"      - 用户名：{apt['username']}")
                print(f"      - 车辆品牌：{apt['bicycle_brand']}")
        
        print("3. 检查 waiting_bicycles 字段")
        if dashboard_data.get('waiting_bicycles'):
            for bike in dashboard_data['waiting_bicycles']:
                print(f"   自行车 ID: {bike['id']}")
                assert 'owner_username' in bike, "每个自行车都应该有 owner_username"
                assert 'brand' in bike, "每个自行车都应该有 brand"
                print(f"      - 卖家用户名：{bike['owner_username']}")
                print(f"      - 品牌：{bike['brand']}")
        
        print("   ✅ 仪表盘数据完整")


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
