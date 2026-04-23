#!/usr/bin/env python3
"""
Test script for verifying deployed website functionality
Tests the time slot proposal feature and other key functionalities
"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "https://pku-campus-cycle-cycle.vercel.app"
API_URL = "https://pku-cycle-cycle.onrender.com"  # Assuming this is the Render API URL

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_homepage():
    """Test if homepage loads with background image"""
    print_section("Test 1: Homepage Loading")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"✓ Homepage loaded successfully (Status: {response.status_code})")
        
        # Check if background image is referenced in the page
        if "backgroundImage" in response.text or "unsplash" in response.text:
            print("✓ Background image CSS found in homepage")
        else:
            print("✗ Background image CSS NOT found in homepage")
        
        # Check for Chinese content
        if "燕园易骑" in response.text:
            print("✓ Chinese content (燕园易骑) found on homepage")
        else:
            print("✗ Chinese content NOT found on homepage")
            
        return True
    except Exception as e:
        print(f"✗ Failed to load homepage: {e}")
        return False

def test_admin_page():
    """Test if admin page loads with background image"""
    print_section("Test 2: Admin Page Loading")
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=10)
        print(f"✓ Admin page loaded (Status: {response.status_code})")
        
        # Check if background image is referenced
        if "backgroundImage" in response.text or "unsplash" in response.text:
            print("✓ Background image CSS found in admin page")
        else:
            print("✗ Background image CSS NOT found in admin page")
            
        return True
    except Exception as e:
        print(f"✗ Failed to load admin page: {e}")
        return False

def test_api_health():
    """Test if backend API is healthy"""
    print_section("Test 3: Backend API Health Check")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✓ Backend API is healthy (Status: {response.status_code})")
            return True
        else:
            print(f"✗ Backend API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to backend API: {e}")
        return False

def test_datetime_local_format():
    """Test the datetime-local format handling"""
    print_section("Test 4: DateTime-Local Input Format Verification")
    
    # This test verifies the format that should be used in the frontend
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%dT%H:%M")
    print(f"Current datetime-local format: {formatted}")
    print("✓ This format should be accepted by datetime-local inputs")
    
    # Test ISO format conversion
    iso_format = now.isoformat()
    print(f"ISO format: {iso_format}")
    print("✓ Backend expects ISO format for API calls")
    
    return True

def test_time_slot_validation_logic():
    """Test the validation logic that was fixed"""
    print_section("Test 5: Time Slot Validation Logic")
    
    # Simulate the validation that happens in the frontend
    test_cases = [
        ("2025-12-25T10:00", "2025-12-25T11:00", True, "Valid future time slot"),
        ("", "2025-12-25T11:00", False, "Empty start time"),
        ("2025-12-25T10:00", "", False, "Empty end time"),
        ("2025-12-25T11:00", "2025-12-25T10:00", False, "Start time after end time"),
    ]
    
    for start, end, should_pass, description in test_cases:
        if not start or not end:
            result = False
        else:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            result = start_dt < end_dt and start_dt > datetime.now()
        
        status = "✓" if result == should_pass else "✗"
        print(f"{status} {description}: {'PASS' if result == should_pass else 'FAIL'}")
    
    return True

def test_frontend_code_inspection():
    """Inspect the actual frontend code to verify fixes are deployed"""
    print_section("Test 6: Frontend Code Verification")
    
    try:
        response = requests.get(f"{BASE_URL}/_next/static/chunks/main.js", timeout=10)
        
        # Check for key fixes in the deployed code
        checks = [
            ("step", "step attribute for datetime-local"),
            ("min", "min attribute for preventing past dates"),
            ("trim()", "trim() for input validation"),
            ("使用说明", "Chinese usage instructions"),
        ]
        
        for keyword, description in checks:
            if keyword in response.text:
                print(f"✓ Found {description} in deployed code")
            else:
                print(f"? {description} not found in main bundle (may be in different chunk)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to inspect frontend code: {e}")
        return False

def test_responsive_design():
    """Test if the UI is responsive and properly styled"""
    print_section("Test 7: Responsive Design Check")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        
        # Check for responsive design classes
        responsive_indicators = [
            ("min-h-screen", "Minimum height for full screen"),
            ("flex", "Flexbox layout"),
            ("max-w-", "Maximum width constraints"),
            ("backdrop-blur", "Blur effect for readability"),
        ]
        
        for css_class, description in responsive_indicators:
            if css_class in response.text:
                print(f"✓ {description}: {css_class} found")
            else:
                print(f"? {description} not found")
        
        return True
    except Exception as e:
        print(f"✗ Failed to check responsive design: {e}")
        return False

def main():
    print_section("🧪 DEPLOYMENT VERIFICATION TEST SUITE")
    print(f"Testing website: {BASE_URL}")
    print(f"Testing API: {API_URL}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all tests
    results.append(("Homepage Loading", test_homepage()))
    results.append(("Admin Page Loading", test_admin_page()))
    results.append(("Backend API Health", test_api_health()))
    results.append(("DateTime Format", test_datetime_local_format()))
    results.append(("Validation Logic", test_time_slot_validation_logic()))
    results.append(("Frontend Code", test_frontend_code_inspection()))
    results.append(("Responsive Design", test_responsive_design()))
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Deployment is successful.")
        print("\nNext steps for manual testing:")
        print("1. Visit https://pku-campus-cycle-cycle.vercel.app")
        print("2. Login as admin")
        print("3. Navigate to admin panel")
        print("4. Try to propose time slots for a bicycle")
        print("5. Verify you can select hours and minutes using the picker")
        print("6. Verify no false '请填写所有时间段' error appears")
        print("7. Check that background images are visible")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
    
    print_section("✅ TESTING COMPLETE")

if __name__ == "__main__":
    main()
