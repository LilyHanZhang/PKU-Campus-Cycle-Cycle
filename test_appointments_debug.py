import requests

API_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 登录
login_response = requests.post(f"{API_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})

if login_response.status_code != 200:
    print(f"登录失败：{login_response.status_code}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=" * 70)
print("测试 /appointments/ 端点")
print("=" * 70)

# 测试 appointments
response = requests.get(f"{API_URL}/appointments/", headers=headers)
print(f"\n状态码：{response.status_code}")
print(f"响应头：{dict(response.headers)}")
print(f"响应内容：{response.text[:500]}")

if response.status_code == 500:
    print("\n❌ 服务器内部错误")
    print("可能的原因：")
    print("1. 数据库表结构不匹配")
    print("2. 序列化错误（from_attributes 问题）")
    print("3. 缺少必要字段")
elif response.status_code == 200:
    print(f"\n✓ 成功！获取到 {len(response.json())} 条预约记录")
else:
    print(f"\n✗ 失败：{response.status_code}")
