#!/usr/bin/env python3
"""
测试管理后台页面修复
"""
import requests
import json

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

def test_admin_login():
    """测试管理员登录"""
    print("1. 测试管理员登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"   ✓ 登录成功")
        return token
    else:
        print(f"   ✗ 登录失败：{response.status_code}")
        print(f"   {response.text}")
        return None

def test_auth_me(token):
    """测试 /auth/me 端点"""
    print("2. 测试 /auth/me 端点...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 获取用户信息成功")
        print(f"   - 角色：{data.get('role')}")
        print(f"   - 邮箱：{data.get('email')}")
        return True
    else:
        print(f"   ✗ 获取用户信息失败：{response.status_code}")
        return False

def test_admin_dashboard(token):
    """测试管理后台仪表盘"""
    print("3. 测试管理后台仪表盘...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 仪表盘数据获取成功")
        print(f"   - 待审核自行车：{data.get('pending_bicycles_count', 0)}")
        print(f"   - 待处理预约：{data.get('pending_appointments_count', 0)}")
        print(f"   - 待确认交易：{data.get('waiting_confirmation_count', 0)}")
        return True
    else:
        print(f"   ✗ 仪表盘数据获取失败：{response.status_code}")
        print(f"   {response.text}")
        return False

def test_bicycles(token):
    """测试自行车列表"""
    print("4. 测试自行车列表...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/bicycles/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 自行车列表获取成功")
        print(f"   - 自行车数量：{len(data)}")
        return True
    else:
        print(f"   ✗ 自行车列表获取失败：{response.status_code}")
        return False

def test_appointments(token):
    """测试预约列表"""
    print("5. 测试预约列表...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/appointments/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 预约列表获取成功")
        print(f"   - 预约数量：{len(data)}")
        return True
    else:
        print(f"   ✗ 预约列表获取失败：{response.status_code}")
        return False

def test_users(token):
    """测试用户列表"""
    print("6. 测试用户列表...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ 用户列表获取成功")
        print(f"   - 用户数量：{len(data)}")
        return True
    else:
        print(f"   ✗ 用户列表获取失败：{response.status_code}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("管理后台 API 测试")
    print("=" * 60)
    print()
    
    # 测试登录
    token = test_admin_login()
    if not token:
        print("\n❌ 测试失败：无法登录")
        exit(1)
    
    print()
    
    # 测试各个端点
    tests = [
        test_auth_me,
        test_admin_dashboard,
        test_bicycles,
        test_appointments,
        test_users
    ]
    
    all_passed = True
    for test in tests:
        if not test(token):
            all_passed = False
        print()
    
    print("=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
