#!/usr/bin/env python3
"""
模拟浏览器测试管理后台页面
"""
import requests
import json

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"
FRONTEND_URL = "https://pku-campus-cycle-cycle.vercel.app"

def test_frontend_homepage():
    """测试前端首页是否能访问"""
    print("1. 测试前端首页...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"   状态码：{response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ 首页可以访问")
            # 检查页面是否包含关键内容
            if "燕园易骑" in response.text or "login" in response.text.lower():
                print(f"   ✓ 页面内容正常")
            return True
        else:
            print(f"   ✗ 首页访问失败")
            return False
    except Exception as e:
        print(f"   ✗ 错误：{e}")
        return False

def test_frontend_admin_page():
    """测试前端管理后台页面是否能访问"""
    print("2. 测试前端管理后台页面...")
    try:
        response = requests.get(f"{FRONTEND_URL}/admin", timeout=10)
        print(f"   状态码：{response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ 管理后台页面可以访问")
            # 检查页面是否包含关键内容
            if "管理后台" in response.text or "admin" in response.text.lower():
                print(f"   ✓ 页面内容正常")
            else:
                print(f"   ⚠ 页面内容可能有问题")
            return True
        else:
            print(f"   ✗ 管理后台页面访问失败")
            return False
    except Exception as e:
        print(f"   ✗ 错误：{e}")
        return False

def test_backend_api():
    """测试后端 API"""
    print("3. 测试后端 API...")
    try:
        # 测试健康检查
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✓ 后端服务正常")
            return True
        else:
            print(f"   ✗ 后端服务异常")
            return False
    except Exception as e:
        print(f"   ✗ 错误：{e}")
        return False

def test_admin_login_and_access():
    """测试管理员登录并访问管理后台 API"""
    print("4. 测试管理员登录和 API 访问...")
    
    # 登录
    print("   正在登录...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    }, timeout=10)
    
    if login_response.status_code != 200:
        print(f"   ✗ 登录失败：{login_response.status_code}")
        return False
    
    token = login_response.json().get("access_token")
    print(f"   ✓ 登录成功，获取到 token")
    
    # 测试 /auth/me
    print("   测试 /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
    
    if me_response.status_code != 200:
        print(f"   ✗ /auth/me 失败：{me_response.status_code}")
        print(f"   响应：{me_response.text}")
        return False
    
    user_info = me_response.json()
    print(f"   ✓ 获取用户信息成功")
    print(f"   - 角色：{user_info.get('role')}")
    print(f"   - 邮箱：{user_info.get('email')}")
    
    # 测试管理后台仪表盘
    print("   测试管理后台仪表盘 API...")
    dashboard_response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=headers, timeout=10)
    
    if dashboard_response.status_code != 200:
        print(f"   ✗ 仪表盘 API 失败：{dashboard_response.status_code}")
        print(f"   响应：{dashboard_response.text}")
        return False
    
    print(f"   ✓ 仪表盘 API 正常")
    print(f"   - 待审核：{dashboard_response.json().get('pending_bicycles_count', 0)}")
    
    return True

def check_cors():
    """检查 CORS 配置"""
    print("5. 检查 CORS 配置...")
    try:
        # 发送 OPTIONS 请求
        response = requests.options(f"{BASE_URL}/auth/login", 
                                  headers={
                                      "Origin": "https://pku-campus-cycle-cycle.vercel.app",
                                      "Access-Control-Request-Method": "POST"
                                  },
                                  timeout=10)
        
        print(f"   OPTIONS 状态码：{response.status_code}")
        print(f"   CORS 头：{response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        
        if response.headers.get('Access-Control-Allow-Origin'):
            print(f"   ✓ CORS 配置正确")
            return True
        else:
            print(f"   ⚠ CORS 头未设置")
            return False
    except Exception as e:
        print(f"   ✗ 错误：{e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("管理后台访问问题诊断测试")
    print("=" * 70)
    print()
    
    tests = [
        ("前端首页", test_frontend_homepage),
        ("前端管理后台页面", test_frontend_admin_page),
        ("后端 API 健康", test_backend_api),
        ("管理员登录和 API", test_admin_login_and_access),
        ("CORS 配置", check_cors),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ✗ 测试异常：{e}")
            results.append((name, False))
        print()
    
    print("=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print()
    if all(r for _, r in results):
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请查看上面的详细信息")
    print("=" * 70)
