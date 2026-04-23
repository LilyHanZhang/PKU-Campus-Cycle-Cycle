#!/usr/bin/env python3
"""
Simple API test for PKU Cycle Backend
"""
import requests
import json

BASE_URL = "https://pku-cycle-backend.onrender.com"

def test_login():
    print("Testing login endpoint...")
    
    # Test admin login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "2200017736@stu.pku.edu.cn",
            "password": "pkucycle"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        return data.get('access_token')
    else:
        print(f"✗ Login failed")
        return None

def test_health():
    print("\nTesting health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def test_get_bicycles(token):
    print("\nTesting get bicycles endpoint...")
    response = requests.get(
        f"{BASE_URL}/bicycles/",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        bikes = response.json()
        print(f"✓ Found {len(bikes)} bicycles")
    else:
        print(f"✗ Failed: {response.text}")

def test_admin_dashboard(token):
    print("\nTesting admin dashboard endpoint...")
    response = requests.get(
        f"{BASE_URL}/bicycles/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Dashboard data:")
        print(f"  - Pending bicycles: {data.get('pending_bicycles_count', 0)}")
        print(f"  - Pending appointments: {data.get('pending_appointments_count', 0)}")
        print(f"  - Waiting bicycles: {len(data.get('waiting_bicycles', []))}")
        print(f"  - Locked slots: {len(data.get('locked_slots_with_countdown', []))}")
    else:
        print(f"✗ Failed: {response.text}")

if __name__ == "__main__":
    print("="*70)
    print("PKU Cycle Backend API Test")
    print("="*70)
    
    # Test health
    test_health()
    
    # Test login
    token = test_login()
    
    if token:
        # Test other endpoints
        test_get_bicycles(token)
        test_admin_dashboard(token)
        
        print("\n" + "="*70)
        print("✓ All API tests completed!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("✗ Cannot proceed without valid token")
        print("="*70)
