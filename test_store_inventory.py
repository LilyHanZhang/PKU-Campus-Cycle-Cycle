#!/usr/bin/env python3
"""
Test store-inventory endpoint
"""

import requests

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"
ADMIN_EMAIL = "2200017736@stu.pku.edu.cn"
ADMIN_PASSWORD = "pkucycle"

# Login as admin
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
)
admin_token = response.json()["access_token"]
print(f"✓ Admin logged in")

# Get bicycles with RESERVED status
response = requests.get(
    f"{BASE_URL}/bicycles/",
    headers={"Authorization": f"Bearer {admin_token}"}
)

bicycles = response.json()
print(f"\nFound {len(bicycles)} bicycles:")

for bike in bicycles:
    print(f"  - {bike['brand']}: {bike['status']} (ID: {bike['id']})")
    
    # Try to store in inventory if RESERVED
    if bike['status'] == 'RESERVED':
        print(f"    → Attempting to store in inventory...")
        response = requests.put(
            f"{BASE_URL}/bicycles/{bike['id']}/store-inventory",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"    Response: {response.status_code}")
        if response.status_code == 200:
            print(f"    ✓ Success! New status: {response.json()['status']}")
        else:
            print(f"    ✗ Failed: {response.text}")
