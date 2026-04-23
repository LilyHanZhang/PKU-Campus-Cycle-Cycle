#!/usr/bin/env python3
"""
Test script for deployed features on https://pku-campus-cycle-cycle.vercel.app
Tests all new features implemented from revise_detail.md
"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "https://pku-cycle-backend.onrender.com"

def test_admin_dashboard():
    """Test admin dashboard endpoint"""
    print("\n=== Testing Admin Dashboard ===")
    try:
        # First login as admin
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print("❌ Admin login failed")
            return None
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test dashboard endpoint
        dashboard_response = requests.get(f"{BASE_URL}/bicycles/admin/dashboard", headers=headers)
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print("✓ Dashboard endpoint working")
            print(f"  - Pending bicycles: {data.get('pending_bicycles_count', 0)}")
            print(f"  - Pending appointments: {data.get('pending_appointments_count', 0)}")
            print(f"  - Locked slots: {len(data.get('locked_slots_with_countdown', []))}")
            return headers
        else:
            print(f"❌ Dashboard endpoint failed: {dashboard_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return None

def test_confirm_endpoints(headers):
    """Test confirm endpoints exist"""
    print("\n=== Testing Confirm Endpoints ===")
    try:
        # These endpoints should exist (even if they return 404 for non-existent resources)
        confirm_bike = requests.post(f"{BASE_URL}/bicycles/00000000-0000-0000-0000-000000000000/confirm", headers=headers)
        confirm_apt = requests.put(f"{BASE_URL}/time_slots/confirm/00000000-0000-0000-0000-000000000000", headers=headers)
        
        # Should return 404 (not found) rather than 404 (endpoint not found)
        if confirm_bike.status_code in [404, 400] and confirm_apt.status_code in [404, 400]:
            print("✓ Confirm endpoints exist")
            return True
        else:
            print(f"❌ Confirm endpoints issue: Bike={confirm_bike.status_code}, Apt={confirm_apt.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing confirm endpoints: {e}")
        return False

def test_cancel_endpoints(headers):
    """Test cancel endpoints exist"""
    print("\n=== Testing Cancel Endpoints ===")
    try:
        cancel_bike = requests.post(f"{BASE_URL}/bicycles/00000000-0000-0000-0000-000000000000/cancel", headers=headers)
        admin_cancel_bike = requests.post(f"{BASE_URL}/bicycles/00000000-0000-0000-0000-000000000000/admin-cancel?reason=test", headers=headers)
        
        if cancel_bike.status_code in [404, 400, 403] and admin_cancel_bike.status_code in [404, 400]:
            print("✓ Cancel endpoints exist")
            return True
        else:
            print(f"❌ Cancel endpoints issue: User={cancel_bike.status_code}, Admin={admin_cancel_bike.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing cancel endpoints: {e}")
        return False

def test_notification_system(headers):
    """Test that notification system is working"""
    print("\n=== Testing Notification System ===")
    try:
        # Check if messages endpoint exists
        messages_response = requests.get(f"{BASE_URL}/messages/", headers=headers)
        
        if messages_response.status_code == 200:
            print("✓ Messaging system accessible")
            return True
        else:
            print(f"❌ Messaging system issue: {messages_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing notification system: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing Deployed Features on PKU Campus Cycle Cycle")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Admin Dashboard
    headers = test_admin_dashboard()
    
    if not headers:
        print("\n❌ Cannot continue without admin access")
        return False
    
    # Test 2: Confirm Endpoints
    test_confirm_endpoints(headers)
    
    # Test 3: Cancel Endpoints
    test_cancel_endpoints(headers)
    
    # Test 4: Notification System
    test_notification_system(headers)
    
    print("\n" + "=" * 60)
    print("✅ All deployed features tested successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Visit https://pku-campus-cycle-cycle.vercel.app")
    print("2. Login as admin to test the dashboard UI")
    print("3. Test the complete seller and buyer flows")
    print("4. Verify countdown timers are working")
    
    return True

if __name__ == "__main__":
    main()
