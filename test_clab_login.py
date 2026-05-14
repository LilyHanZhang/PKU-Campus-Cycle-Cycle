import requests
import json

BASE_URL = "http://10.129.245.117:8000"

print("=" * 60)
print("测试 cLab 管理员登录")
print("=" * 60)
print()

# 测试登录
login_data = {
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
}

print("1. 尝试登录...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
    print(f"   状态码：{response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 登录成功！")
        print(f"   Token: {data['access_token'][:50]}...")
        print(f"   Token 类型：{data['token_type']}")
        
        # 测试获取用户信息
        print("\n2. 获取用户信息...")
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✓ 获取成功！")
            print(f"   邮箱：{user_data['email']}")
            print(f"   姓名：{user_data['name']}")
            print(f"   角色：{user_data['role']}")
            print(f"   ID: {user_data['id']}")
            
            # 测试管理后台 API
            print("\n3. 测试管理后台 API...")
            admin_response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=headers, timeout=10)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                print(f"   ✓ 管理后台 API 正常！")
                print(f"   待审核自行车：{admin_data.get('pending_bicycles_count', 0)}")
                print(f"   待处理预约：{admin_data.get('pending_appointments_count', 0)}")
            else:
                print(f"   ✗ 管理后台 API 失败：{admin_response.status_code}")
        else:
            print(f"   ✗ 获取用户信息失败：{user_response.status_code}")
            print(f"   错误：{user_response.text}")
    else:
        print(f"   ✗ 登录失败！")
        print(f"   错误：{response.text}")
        
except Exception as e:
    print(f"   ✗ 发生错误：{e}")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
