import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("等待部署完成（3 分钟）并测试")
print("=" * 70)

# 等待 180 秒（3 分钟）
print("\n等待部署完成...")
for i in range(180, 0, -15):
    print(f"剩余 {i} 秒...")
    time.sleep(15)

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

    # 测试 appointments API
    print(f"\n2. Appointments API（关键测试）：", end='')
    r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
    print(f"{r.status_code}")

    if r.status_code == 500:
        print(f"\n   错误详情：{r.text}")
        print(f"\n   现在请查看 Render Dashboard 中的 Logs")
        print(f"   应该能看到详细的错误 traceback")
    elif r.status_code == 200:
        print(f"   ✓ 成功！获取到 {len(r.json())} 条预约记录")
        print(f"   ✓ CORS 头：{r.headers.get('access-control-allow-origin', '无')}")
    else:
        print(f"   响应：{r.text[:200]}")
        
except Exception as e:
    print(f"\n   ✗ 请求失败：{e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
