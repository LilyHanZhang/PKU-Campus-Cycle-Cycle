import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("等待部署完成并测试详细错误")
print("=" * 70)

# 等待 120 秒
print("\n等待部署完成...")
for i in range(120, 0, -10):
    print(f"剩余 {i} 秒...")
    time.sleep(10)

print("\n开始测试 API...")
print("=" * 70)

# 登录
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
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
    print(f"\n   ✓ 全局异常处理器已捕获错误！")
    print(f"   ✓ 请查看 Render 日志中的详细 traceback")
elif r.status_code == 200:
    print(f"   ✓ 成功！获取到 {len(r.json())} 条预约记录")
else:
    print(f"   响应：{r.text[:200]}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
