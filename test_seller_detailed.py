#!/usr/bin/env python3
"""
Detailed test of seller flow
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

# Register a new user
test_email = f"test_seller_{int(datetime.now().timestamp())}@example.com"
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"email": test_email, "password": "test123", "name": "Test Seller"}
)
user_token = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": test_email, "password": "test123"}
).json()["access_token"]
print(f"✓ Test user created and logged in")

# Step 1: User registers bicycle
print("\n" + "="*60)
print("Step 1: User registers bicycle")
print("="*60)
response = requests.post(
    f"{BASE_URL}/bicycles/",
    json={"brand": "Test Bike", "condition": 8, "price": 200},
    headers={"Authorization": f"Bearer {user_token}"}
)
print(f"Status: {response.status_code}")
bike = response.json()
bike_id = bike["id"]
print(f"Bike ID: {bike_id}")
print(f"Bike Status: {bike['status']}")

# Step 2: Admin proposes time slots
print("\n" + "="*60)
print("Step 2: Admin proposes time slots")
print("="*60)
start_time = datetime.now() + timedelta(hours=1)
end_time = datetime.now() + timedelta(hours=2)
response = requests.post(
    f"{BASE_URL}/bicycles/{bike_id}/propose-slots",
    json=[{"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}],
    headers={"Authorization": f"Bearer {admin_token}"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Check bike status
response = requests.get(
    f"{BASE_URL}/bicycles/{bike_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
print(f"Bike Status after propose: {response.json()['status']}")

# Step 3: User selects time slot
print("\n" + "="*60)
print("Step 3: User selects time slot")
print("="*60)
response = requests.get(
    f"{BASE_URL}/time_slots/bicycle/{bike_id}",
    headers={"Authorization": f"Bearer {user_token}"}
)
slots = response.json()
print(f"Available slots: {len(slots)}")
if slots:
    slot_id = slots[0]["id"]
    print(f"Slot ID: {slot_id}")
    print(f"Appointment Type: {slots[0].get('appointment_type', 'N/A')}")
    
    response = requests.put(
        f"{BASE_URL}/time_slots/select-bicycle/{bike_id}",
        json={"time_slot_id": slot_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    print(f"Select Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check bike status
    response = requests.get(
        f"{BASE_URL}/bicycles/{bike_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"Bike Status after select: {response.json()['status']}")

# Step 4: Admin confirms time slot
print("\n" + "="*60)
print("Step 4: Admin confirms time slot")
print("="*60)
response = requests.post(
    f"{BASE_URL}/bicycles/{bike_id}/confirm",
    headers={"Authorization": f"Bearer {admin_token}"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Check bike status IMMEDIATELY
response = requests.get(
    f"{BASE_URL}/bicycles/{bike_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
print(f"Bike Status after confirm: {response.json()['status']}")

# Check time slot
response = requests.get(
    f"{BASE_URL}/time_slots/bicycle/{bike_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
slots = response.json()
if slots:
    print(f"Slot is_booked: {slots[0]['is_booked']}")
    print(f"Slot appointment_type: {slots[0].get('appointment_type', 'N/A')}")
