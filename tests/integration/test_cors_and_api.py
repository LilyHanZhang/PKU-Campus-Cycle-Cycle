import requests

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("测试 CORS 和 API 响应")
print("=" * 70)

# 测试健康检查
print("\n1. 健康检查 /health")
r = requests.get(f'{base_url}/health')
print(f"   状态码：{r.status_code}")
print(f"   响应：{r.text}")
print(f"   CORS 头：{r.headers.get('access-control-allow-origin', '无')}")

# 测试根路径
print("\n2. 根路径 /")
r = requests.get(f'{base_url}/')
print(f"   状态码：{r.status_code}")
print(f"   响应：{r.text}")
print(f"   CORS 头：{r.headers.get('access-control-allow-origin', '无')}")

# 测试登录
print("\n3. 登录 /auth/login")
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
r = requests.post(f'{base_url}/auth/login', json=login_data)
print(f"   状态码：{r.status_code}")
if r.status_code == 200:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f"   ✓ 登录成功")
    
    # 测试 appointments
    print("\n4. 测试 /appointments/")
    r = requests.get(f'{base_url}/appointments/', headers=headers)
    print(f"   状态码：{r.status_code}")
    print(f"   CORS 头：{r.headers.get('access-control-allow-origin', '无')}")
    print(f"   响应内容：{r.text[:200]}")
    
    # 测试 appointments/user
    print("\n5. 测试 /appointments/user/cfb3b525-2539-4f42-b422-55dfb54d1029")
    r = requests.get(f'{base_url}/appointments/user/cfb3b525-2539-4f42-b422-55dfb54d1029', headers=headers)
    print(f"   状态码：{r.status_code}")
    print(f"   CORS 头：{r.headers.get('access-control-allow-origin', '无')}")
    print(f"   响应内容：{r.text[:200]}")
else:
    print(f"   ✗ 登录失败：{r.text}")
