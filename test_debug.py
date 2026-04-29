#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# 登录
admin_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
})
admin_token = admin_response.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 获取所有自行车
bicycles_response = requests.get(f"{BASE_URL}/bicycles/", headers=admin_headers)
print(f"Bicycles status: {bicycles_response.status_code}")
if bicycles_response.status_code == 200:
    bicycles = bicycles_response.json()
    print(f"Total bicycles: {len(bicycles)}")
    for bike in bicycles[:3]:
        print(f"  - {bike['id']}: {bike['brand']} {bike['model']} ({bike['status']})")
else:
    print(bicycles_response.text[:500])
