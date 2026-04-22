import requests
import json

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("详细调试测试")
print("=" * 70)

# 登录
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
print("\n1. 登录...")
r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
print(f"   状态：{r.status_code}")

if r.status_code != 200:
    print(f"   ✗ 失败：{r.text}")
    exit(1)
    
token = r.json()['access_token']
print(f"   ✓ 成功")

headers = {'Authorization': f'Bearer {token}'}

# 测试 auth/me
print("\n2. 测试 /auth/me...")
r = requests.get(f'{base_url}/auth/me', headers=headers, timeout=10)
print(f"   状态：{r.status_code}")
if r.status_code == 200:
    user_info = r.json()
    print(f"   用户信息：{json.dumps(user_info, indent=2)}")
else:
    print(f"   ✗ 失败：{r.text[:200]}")

# 测试 appointments - 带详细错误处理
print("\n3. 测试 /appointments/ (详细)...")
try:
    r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
    print(f"   状态码：{r.status_code}")
    print(f"   响应头：{dict(r.headers)}")
    print(f"   响应内容：{r.text}")
    
    if r.status_code == 500:
        print("\n   ❌ 500 错误 - 可能是以下原因:")
        print("   1. 数据库查询出错")
        print("   2. 序列化失败")
        print("   3. 依赖注入问题")
        print("   4. 代码逻辑错误")
        
except Exception as e:
    print(f"   ✗ 请求失败：{e}")

# 测试一个简单的 API
print("\n4. 测试 /users/...")
r = requests.get(f'{base_url}/users/', headers=headers, timeout=10)
print(f"   状态：{r.status_code}")
if r.status_code == 200:
    print(f"   ✓ 成功：{len(r.json())} 用户")
else:
    print(f"   ✗ 失败：{r.text[:200]}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
