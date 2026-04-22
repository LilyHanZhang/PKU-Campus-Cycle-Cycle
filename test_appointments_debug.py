import requests
import json

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

# 登录
login_data = {
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
}

r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
print(f"登录状态：{r.status_code}")
print(f"登录响应：{r.json()}")

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 测试 appointments API
print("\n" + "=" * 70)
print("测试 /appointments/ API")
print("=" * 70)

r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
print(f"状态码：{r.status_code}")
print(f"响应头：{dict(r.headers)}")
print(f"响应内容：{r.text[:500]}")

# 尝试获取详细错误
if r.status_code == 500:
    print("\n尝试获取错误详情...")
    try:
        error_detail = r.json()
        print(f"错误详情：{error_detail}")
    except:
        print("无法解析 JSON 错误")
