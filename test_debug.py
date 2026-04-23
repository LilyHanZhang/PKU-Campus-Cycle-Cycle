#!/usr/bin/env python3
"""
Debug test to check bicycle status
"""

import requests
from datetime import datetime, timedelta

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

# Get all bicycles
response = requests.get(
    f"{BASE_URL}/bicycles/",
    headers={"Authorization": f"Bearer {admin_token}"}
)

bicycles = response.json()
print(f"\nFound {len(bicycles)} bicycles:")
for bike in bicycles:
    print(f"  - {bike['brand']}: {bike['status']} (ID: {bike['id']})")
    
# Check specific bicycle
if bicycles:
    bike_id = bicycles[0]['id']
    response = requests.get(
        f"{BASE_URL}/bicycles/{bike_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    bike = response.json()
    print(f"\nBike details:")
    print(f"  Brand: {bike['brand']}")
    print(f"  Status: {bike['status']}")
    print(f"  Owner ID: {bike['owner_id']}")
    
    # Check time slots
    response = requests.get(
        f"{BASE_URL}/time_slots/bicycle/{bike_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    slots = response.json()
    print(f"\nTime slots: {len(slots)}")
    for slot in slots:
        print(f"  - ID: {slot['id']}, is_booked: {slot['is_booked']}, appointment_type: {slot.get('appointment_type', 'N/A')}")
