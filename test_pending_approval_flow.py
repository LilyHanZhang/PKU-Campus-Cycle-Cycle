"""
测试卖家流程：管理员无需预约即可提出时间段
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def test_propose_slots_without_appointment():
    """测试 PENDING_APPROVAL 状态下无需预约即可提出时间段"""
    print("=" * 70)
    print("测试：卖家登记后管理员直接提出时间段（无需预约）")
    print("=" * 70)
    print()
    
    # 1. 卖家登录
    print("1. 卖家登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "seller_test@example.com",
        "password": "test123"
    })
    
    if response.status_code != 200:
        # 注册卖家
        print("   注册新卖家账号...")
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "seller_test@example.com",
            "password": "test123",
            "role": "SELLER"
        })
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "seller_test@example.com",
            "password": "test123"
        })
    
    seller_token = response.json()["access_token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    print("   ✅ 卖家登录成功")
    print()
    
    # 2. 卖家登记自行车
    print("2. 卖家登记自行车（PENDING_APPROVAL）...")
    response = requests.post(f"{BASE_URL}/bicycles/", json={
        "brand": "Test Bike",
        "condition": 8,
        "price": 100.0,
        "description": "测试 - 无需预约直接提出时间段",
        "image_url": "https://example.com/bike.jpg"
    }, headers=seller_headers)
    
    assert response.status_code == 200, f"登记失败：{response.text}"
    bike = response.json()
    bike_id = bike["id"]
    print(f"   ✅ 自行车登记成功：{bike_id}")
    print(f"   - 状态：{bike['status']}")
    print()
    
    # 3. 管理员登录
    print("3. 管理员登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    assert response.status_code == 200
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   ✅ 管理员登录成功")
    print()
    
    # 4. 管理员直接提出时间段（不创建预约）
    print("4. 管理员直接提出时间段（无预约）...")
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
    
    print(f"   响应状态码：{response.status_code}")
    print(f"   响应内容：{response.text[:300]}")
    
    # 5. 验证结果
    assert response.status_code == 200, f"提出时间段失败：{response.text}"
    print("   ✅ 成功！无需预约即可提出时间段")
    print()
    
    # 6. 验证自行车状态
    print("6. 验证自行车状态...")
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}", headers=admin_headers)
    assert response.status_code == 200
    bike_data = response.json()
    print(f"   自行车状态：{bike_data['status']}")
    
    assert bike_data["status"] == "LOCKED", f"状态应该是 LOCKED，实际是 {bike_data['status']}"
    print("   ✅ 自行车状态已正确更新为 LOCKED")
    print()
    
    # 7. 验证时间段类型
    print("7. 验证时间段类型...")
    response = requests.get(f"{BASE_URL}/bicycles/{bike_id}/time-slots", headers=admin_headers)
    if response.status_code == 200:
        slots = response.json()
        print(f"   创建了 {len(slots)} 个时间段")
        for slot in slots:
            print(f"   - 类型：{slot.get('appointment_type')}, 时间：{slot.get('start_time')} ~ {slot.get('end_time')}")
            assert slot.get("appointment_type") == "pick-up", "时间段类型应该是 pick-up"
        print("   ✅ 时间段类型正确（pick-up）")
    print()
    
    print("=" * 70)
    print("✅ 测试通过！")
    print("=" * 70)
    print()
    print("流程总结：")
    print("1. ✅ 卖家登记自行车（PENDING_APPROVAL）")
    print("2. ✅ 管理员无需预约直接提出时间段")
    print("3. ✅ 自动审核通过并创建 pick-up 时间段")
    print("4. ✅ 自行车状态变为 LOCKED")
    return True

if __name__ == "__main__":
    try:
        test_propose_slots_without_appointment()
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ 测试失败：{e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        exit(1)
