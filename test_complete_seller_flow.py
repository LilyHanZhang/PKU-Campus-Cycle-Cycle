"""
完整测试：卖家流程从登记到入库

流程：
1. 卖家登记自行车（PENDING_APPROVAL）
2. 管理员提出时间段（自动审核通过 → LOCKED）
3. 卖家选择时间段（LOCKED）
4. 管理员确认预约（→ RESERVED）
5. 线下交易完成
6. 管理员存入库存（→ IN_STOCK）
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def login(email, password):
    """登录"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_complete_seller_flow():
    """完整测试卖家流程"""
    print("=" * 70)
    print("完整测试：卖家流程从登记到入库")
    print("=" * 70)
    print()
    
    # 1. 卖家登录
    print("1. 卖家登录...")
    seller_token = login("seller_test@example.com", "test123")
    if not seller_token:
        print("   注册新卖家...")
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "seller_test2@example.com",
            "password": "test123",
            "role": "SELLER"
        })
        seller_token = login("seller_test2@example.com", "test123")
    
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    print("   ✅ 卖家登录成功")
    print()
    
    # 2. 卖家登记自行车
    print("2. 卖家登记自行车（PENDING_APPROVAL）...")
    response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Complete Test Bike",
        "condition": 8,
        "price": 100.0,
        "description": "完整流程测试",
        "image_url": "https://example.com/bike.jpg"
    }, headers=seller_headers)
    
    assert response.status_code == 200
    bike = response.json()
    bike_id = bike["id"]
    print(f"   ✅ 自行车登记成功：{bike_id}")
    print(f"   - 状态：{bike['status']}")
    print()
    
    # 3. 管理员登录
    print("3. 管理员登录...")
    admin_token = login("2200017736@stu.pku.edu.cn", "pkucycle")
    assert admin_token, "管理员登录失败"
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   ✅ 管理员登录成功")
    print()
    
    # 4. 管理员提出时间段
    print("4. 管理员提出时间段（自动审核通过）...")
    now = datetime.utcnow()
    time_slots = [
        {
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=2)).isoformat()
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
        json=time_slots,
        headers=admin_headers
    )
    
    assert response.status_code == 200, f"提出时间段失败：{response.text}"
    print("   ✅ 提出时间段成功")
    
    # 验证状态
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_data = response.json()
    print(f"   - 状态：{bike_data['status']}")
    assert bike_data["status"] == "LOCKED"
    print()
    
    # 5. 卖家选择时间段
    print("5. 卖家选择时间段...")
    response = requests.get(f"{BASE_URL}/time_slots/bicycle/{bike_id}", headers=seller_headers)
    print(f"   获取时间段状态码：{response.status_code}")
    print(f"   响应：{response.text[:200]}")
    assert response.status_code == 200, f"获取时间段失败：{response.text}"
    slots = response.json()
    assert len(slots) > 0, "没有可选时间段"
    
    selected_slot = slots[0]
    print(f"   选择时间段 ID: {selected_slot['id']}")
    response = requests.put(
        f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
        json={"time_slot_id": str(selected_slot["id"])},
        headers=seller_headers
    )
    print(f"   选择响应状态码：{response.status_code}")
    print(f"   选择响应：{response.text[:200]}")
    
    assert response.status_code == 200, f"选择时间段失败：{response.text}"
    print("   ✅ 卖家选择时间段成功")
    
    # 验证状态
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_data = response.json()
    print(f"   - 状态：{bike_data['status']}")
    assert bike_data["status"] == "LOCKED"
    print()
    
    # 6. 管理员确认预约（卖家流程）
    print("6. 管理员确认自行车时间段（→ RESERVED）...")
    
    # 卖家流程使用 confirm-bicycle 接口
    response = requests.put(
        f"{BASE_URL}/time_slots/confirm-bicycle/{bike_id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200, f"确认时间段失败：{response.text}"
    print("   ✅ 管理员确认时间段成功")
    
    # 验证状态
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_data = response.json()
    print(f"   - 状态：{bike_data['status']}")
    assert bike_data["status"] == "RESERVED", f"状态应该是 RESERVED，实际是 {bike_data['status']}"
    print()
    
    # 7. 线下交易完成，管理员存入库存
    print("7. 线下交易完成，管理员存入库存（→ IN_STOCK）...")
    response = requests.put(
        f"{BASE_URL}/bicycles/{bike_id}/store-inventory",
        headers=admin_headers
    )
    
    assert response.status_code == 200, f"存入库存失败：{response.text}"
    print("   ✅ 存入库存成功")
    
    # 验证状态
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    bike_data = response.json()
    print(f"   - 状态：{bike_data['status']}")
    assert bike_data["status"] == "IN_STOCK", f"状态应该是 IN_STOCK，实际是 {bike_data['status']}"
    print()
    
    print("=" * 70)
    print("✅ 完整流程测试通过！")
    print("=" * 70)
    print()
    print("流程总结：")
    print("1. ✅ 卖家登记自行车（PENDING_APPROVAL）")
    print("2. ✅ 管理员提出时间段（自动审核通过 → LOCKED）")
    print("3. ✅ 卖家选择时间段（LOCKED）")
    print("4. ✅ 管理员确认预约（→ RESERVED）")
    print("5. ✅ 线下交易完成")
    print("6. ✅ 管理员存入库存（→ IN_STOCK）")
    print()
    return True

if __name__ == "__main__":
    try:
        test_complete_seller_flow()
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ 测试失败：{e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        exit(1)
