#!/usr/bin/env python3
import requests

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 登录
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 获取仪表盘
response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
