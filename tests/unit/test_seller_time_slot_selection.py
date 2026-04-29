#!/usr/bin/env python3
"""
测试卖家可以在"我的时间段选择"模块中看到管理员提出的时间段
"""
import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"


class TestSellerCanSeeTimeSlots:
    """测试卖家可以看到并选择时间段"""
    
    def test_01_seller_can_see_bicycles_for_time_slot_selection(self):
        """测试 1：卖家可以在'我的时间段选择'模块中看到自行车"""
        print("\n" + "=" * 60)
        print("测试卖家可以看到并选择时间段")
        print("=" * 60)
        
        # 登录超级管理员
        admin_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        })
        assert admin_response.status_code == 200
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        print("\n【步骤 1】管理员给自己登记自行车")
        bicycle_response = requests.post(f"{BASE_URL}/bicycles/", json={
            "brand": "Test",
            "model": "Seller Selection Test",
            "color": "Blue",
            "license_number": f"TEST{datetime.now().timestamp()}",
            "description": "Test for seller time slot selection",
            "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?q=80&w=2070&auto=format&fit=crop",
            "condition": 3
        }, headers=admin_headers)
        assert bicycle_response.status_code == 200
        bike_id = bicycle_response.json()["id"]
        print(f"   自行车 ID: {bike_id}")
        
        print("\n【步骤 2】管理员审核并提出时间段")
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
        propose_response = requests.post(f"{BASE_URL}/bicycles/{bike_id}/propose-slots", json=time_slots, headers=admin_headers)
        assert propose_response.status_code == 200
        print(f"   提出时间段响应：{propose_response.json()['message']}")
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   自行车状态：{bike_status}")
        assert bike_status == "PENDING_SELLER_SLOT_SELECTION", f"应该是 PENDING_SELLER_SLOT_SELECTION，实际是 {bike_status}"
        
        print("\n【步骤 3】获取所有自行车（模拟前端请求）")
        all_bikes_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
        assert all_bikes_response.status_code == 200
        all_bikes = all_bikes_response.json()
        
        # 模拟前端过滤逻辑
        pending_bikes = [b for b in all_bikes if b['status'] == 'PENDING_SELLER_SLOT_SELECTION']
        print(f"   所有自行车数量：{len(all_bikes)}")
        print(f"   PENDING_SELLER_SLOT_SELECTION 状态的自行车：{len(pending_bikes)}")
        
        # 验证能找到刚才的自行车
        test_bike = next((b for b in pending_bikes if b['id'] == bike_id), None)
        assert test_bike is not None, f"应该能找到自行车 {bike_id}"
        print(f"   ✅ 找到了测试自行车：{test_bike['id']}")
        
        print("\n【步骤 4】获取自行车的时间段")
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        print(f"   时间段数量：{len(slots)}")
        assert len(slots) == 2, f"应该有 2 个时间段，实际是 {len(slots)}"
        
        for i, slot in enumerate(slots):
            print(f"   时间段 {i+1}: {slot['start_time']} - {slot['end_time']}")
            assert slot['is_booked'] == 'false', f"时间段应该未被预订"
        
        print("\n【步骤 5】卖家选择时间段")
        selected_slot = slots[0]
        select_response = requests.put(
            f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
            json={"time_slot_id": str(selected_slot["id"])},
            headers=admin_headers
        )
        assert select_response.status_code == 200
        print(f"   选择响应：{select_response.json()['message']}")
        
        # 检查自行车状态
        bike_response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
        assert bike_response.status_code == 200
        bike_status = bike_response.json()["status"]
        print(f"   选择后状态：{bike_status}")
        assert bike_status == "PENDING_ADMIN_CONFIRMATION_SELLER", f"应该是 PENDING_ADMIN_CONFIRMATION_SELLER，实际是 {bike_status}"
        
        # 检查时间段是否被标记为已预订
        slots_response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=admin_headers)
        assert slots_response.status_code == 200
        slots = slots_response.json()
        selected_slot_data = next((s for s in slots if s['id'] == selected_slot['id']), None)
        assert selected_slot_data is not None
        print(f"   选中时间段的 is_booked: {selected_slot_data['is_booked']}")
        assert selected_slot_data['is_booked'] == 'true', "时间段应该被标记为已预订"
        
        print("\n✅ 测试通过：卖家可以成功看到并选择时间段")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
