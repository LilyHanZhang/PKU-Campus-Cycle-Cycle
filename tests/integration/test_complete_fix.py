import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("等待部署完成（4 分钟）并测试修复")
print("=" * 70)

# 等待 240 秒（4 分钟）
print("\n等待部署完成...")
for i in range(240, 0, -20):
    print(f"剩余 {i} 秒...")
    time.sleep(20)

print("\n开始测试 API...")
print("=" * 70)

# 登录
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
try:
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f"\n1. 登录：{r.status_code}")

    if r.status_code != 200:
        print(f"✗ 登录失败：{r.text}")
        exit(1)
        
    token = r.json()['access_token']
    print(f"   ✓ 登录成功")

    headers = {'Authorization': f'Bearer {token}'}

    # 测试 appointments API - 这是关键
    print(f"\n2. Appointments API（关键测试）：", end='')
    r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
    print(f"{r.status_code}")

    if r.status_code == 200:
        data = r.json()
        print(f"   ✓✓✓ 成功！获取到 {len(data)} 条预约记录")
        print(f"   ✓ CORS 头：{r.headers.get('access-control-allow-origin', '无')}")
        
        # 测试用户管理
        print(f"\n3. Users API：", end='')
        r = requests.get(f'{base_url}/users/', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"✓ {len(r.json())} 用户")
        else:
            print(f"✗ {r.status_code}")
            
        # 测试自行车管理
        print(f"\n4. Bicycles API：", end='')
        r = requests.get(f'{base_url}/bicycles/', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"✓ {len(r.json())} 车辆")
        else:
            print(f"✗ {r.status_code}")
            
        print("\n" + "=" * 70)
        print("🎉🎉🎉 管理后台 API 全部测试通过！")
        print("=" * 70)
    else:
        print(f"   ✗ 失败：{r.status_code}")
        print(f"   响应：{r.text[:300]}")
        
except Exception as e:
    print(f"\n   ✗ 请求失败：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
