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

# 测试一键已读
response = requests.put(f"{BASE_URL}/messages/read-all", json={}, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
