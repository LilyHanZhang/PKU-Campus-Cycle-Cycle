#!/usr/bin/env python3
"""
Complete API test for PKU Campus Cycle Cycle
Tests all features from revise_detail.md
"""

import requests
from datetime import datetime, timedelta
import time

BASE_URL = "https://pku-campus-cycle-cycle.onrender.com"

# Test credentials
ADMIN_EMAIL = "2200017736@stu.pku.edu.cn"
ADMIN_PASSWORD = "pkucycle"

class APITester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_user_email = f"test_{int(time.time())}@example.com"
        self.test_user_password = "test123456"
        self.test_user_id = None
        self.bike_id = None
        self.appointment_id = None
        self.time_slot_id = None
        
    def login_admin(self):
        """Login as admin"""
        print("\n" + "="*70)
        print("📝 Logging in as admin...")
        print("="*70)
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code == 200:
            self.admin_token = response.json()["access_token"]
            print(f"✓ Admin login successful")
            return True
        else:
            print(f"✗ Admin login failed: {response.text}")
            return False
            
    def register_test_user(self):
        """Register a test user"""
        print("\n" + "="*70)
        print("📝 Registering test user...")
        print("="*70)
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": self.test_user_email,
                "password": self.test_user_password,
                "name": "Test User"
            }
        )
        
        if response.status_code == 200:
            print(f"✓ User registered: {self.test_user_email}")
            self.test_user_id = response.json()["id"]
            return True
        else:
            print(f"✗ User registration failed: {response.text}")
            return False
            
    def login_user(self):
        """Login as test user"""
        print("\n📝 Logging in as test user...")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": self.test_user_email, "password": self.test_user_password}
        )
        
        if response.status_code == 200:
            self.user_token = response.json()["access_token"]
            print(f"✓ User login successful")
            return True
        else:
            print(f"✗ User login failed: {response.text}")
            return False
            
    def test_seller_flow(self):
        """Test complete seller flow"""
        print("\n" + "="*70)
        print("🚲 TESTING SELLER FLOW")
        print("="*70)
        
        # Step 1: User registers bicycle
        print("\n1️⃣ Seller registers bicycle...")
        response = requests.post(
            f"{BASE_URL}/bicycles/",
            json={
                "brand": "Test Bike - Seller Flow",
                "condition": 8,
                "price": 200,
                "description": "Test bicycle for seller flow"
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        if response.status_code == 200:
            self.bike_id = response.json()["id"]
            print(f"✓ Bicycle registered (ID: {self.bike_id}, Status: {response.json()['status']})")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        # Step 2: Admin proposes time slots
        print("\n2️⃣ Admin proposes time slots...")
        start_time = datetime.now() + timedelta(hours=1)
        end_time = datetime.now() + timedelta(hours=2)
        
        response = requests.post(
            f"{BASE_URL}/bicycles/{self.bike_id}/propose-slots",
            json=[
                {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
            ],
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"✓ Admin proposed time slots")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        # Step 3: User selects time slot
        print("\n3️⃣ Seller selects time slot...")
        response = requests.get(
            f"{BASE_URL}/time_slots/bicycle/{self.bike_id}",
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        if response.status_code == 200 and len(response.json()) > 0:
            self.time_slot_id = response.json()[0]["id"]
            
            response = requests.put(
                f"{BASE_URL}/time_slots/select-bicycle/{self.bike_id}",
                json={"time_slot_id": self.time_slot_id},
                headers={"Authorization": f"Bearer {self.user_token}"}
            )
            
            if response.status_code == 200:
                print(f"✓ Seller selected time slot")
            else:
                print(f"✗ Failed: {response.text}")
                return False
        else:
            print(f"✗ No time slots available")
            return False
            
        # Step 4: Admin confirms time slot (CRITICAL STEP)
        print("\n4️⃣ Admin confirms time slot ⭐...")
        response = requests.post(
            f"{BASE_URL}/bicycles/{self.bike_id}/confirm",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"✓ Admin confirmed time slot")
            print(f"   Message: {response.json()['message']}")
            
            # Check bike status
            response = requests.get(
                f"{BASE_URL}/bicycles/{self.bike_id}",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            print(f"   Bike status: {response.json()['status']}")
            
            if response.json()["status"] == "RESERVED":
                print(f"✓ Status correctly changed to RESERVED")
            else:
                print(f"✗ Status should be RESERVED but is {response.json()['status']}")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        # Step 5: Admin stores bicycle in inventory
        print("\n5️⃣ Admin stores bicycle in inventory ⭐...")
        response = requests.put(
            f"{BASE_URL}/bicycles/{self.bike_id}/store-inventory",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"✓ Bicycle stored in inventory")
            print(f"   New status: {response.json()['status']}")
            
            if response.json()["status"] == "IN_STOCK":
                print(f"✓ Status correctly changed to IN_STOCK")
            else:
                print(f"✗ Status should be IN_STOCK but is {response.json()['status']}")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        print("\n✅ SELLER FLOW COMPLETED SUCCESSFULLY")
        return True
        
    def test_buyer_flow(self):
        """Test complete buyer flow"""
        print("\n" + "="*70)
        print("🛒 TESTING BUYER FLOW")
        print("="*70)
        
        # Step 1: User creates appointment
        print("\n1️⃣ Buyer creates appointment...")
        response = requests.post(
            f"{BASE_URL}/appointments/",
            json={
                "bicycle_id": self.bike_id,
                "type": "pick-up"
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        if response.status_code == 200:
            self.appointment_id = response.json()["id"]
            print(f"✓ Appointment created (ID: {self.appointment_id})")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        # Step 2: Admin proposes time slots
        print("\n2️⃣ Admin proposes time slots...")
        start_time = datetime.now() + timedelta(hours=1)
        end_time = datetime.now() + timedelta(hours=2)
        
        response = requests.post(
            f"{BASE_URL}/appointments/{self.appointment_id}/propose-slots",
            json=[
                {"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
            ],
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"✓ Admin proposed time slots")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        # Step 3: User selects time slot
        print("\n3️⃣ Buyer selects time slot...")
        response = requests.get(
            f"{BASE_URL}/time_slots/appointment/{self.appointment_id}",
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        if response.status_code == 200 and len(response.json()) > 0:
            time_slot_id = response.json()[0]["id"]
            
            response = requests.put(
                f"{BASE_URL}/time_slots/select-appointment/{self.appointment_id}",
                json={"time_slot_id": time_slot_id},
                headers={"Authorization": f"Bearer {self.user_token}"}
            )
            
            if response.status_code == 200:
                print(f"✓ Buyer selected time slot")
            else:
                print(f"✗ Failed: {response.text}")
                return False
        else:
            print(f"✗ No time slots available")
            return False
            
        # Step 4: Admin confirms time slot (CRITICAL STEP)
        print("\n4️⃣ Admin confirms time slot ⭐...")
        response = requests.put(
            f"{BASE_URL}/time_slots/confirm/{self.appointment_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            print(f"✓ Admin confirmed time slot")
            print(f"   Message: {response.json()['message']}")
            
            # Check appointment status
            response = requests.get(
                f"{BASE_URL}/appointments/{self.appointment_id}",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            print(f"   Appointment status: {response.json()['status']}")
            
            if response.json()["status"] == "CONFIRMED":
                print(f"✓ Status correctly changed to CONFIRMED")
            else:
                print(f"✗ Status should be CONFIRMED but is {response.json()['status']}")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        print("\n✅ BUYER FLOW COMPLETED SUCCESSFULLY")
        return True
        
    def test_cancel_flow(self):
        """Test cancel functionality"""
        print("\n" + "="*70)
        print("❌ TESTING CANCEL FLOW")
        print("="*70)
        
        # Create a new bicycle for cancel test
        print("\n1️⃣ Creating bicycle for cancel test...")
        response = requests.post(
            f"{BASE_URL}/bicycles/",
            json={
                "brand": "Test Bike - Cancel Test",
                "condition": 7,
                "price": 150
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        if response.status_code == 200:
            cancel_bike_id = response.json()["id"]
            print(f"✓ Bicycle created (ID: {cancel_bike_id})")
            
            # User cancels bicycle
            print("\n2️⃣ User cancels bicycle...")
            response = requests.post(
                f"{BASE_URL}/bicycles/{cancel_bike_id}/cancel",
                headers={"Authorization": f"Bearer {self.user_token}"}
            )
            
            if response.status_code == 200:
                print(f"✓ User cancelled bicycle successfully")
            else:
                print(f"✗ Failed: {response.text}")
                return False
        else:
            print(f"✗ Failed to create bicycle: {response.text}")
            return False
            
        print("\n✅ CANCEL FLOW COMPLETED SUCCESSFULLY")
        return True
        
    def test_messaging(self):
        """Test messaging system"""
        print("\n" + "="*70)
        print("💬 TESTING MESSAGING SYSTEM")
        print("="*70)
        
        # Get admin user ID
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            users = response.json()
            admin_user = next((u for u in users if u["email"] == ADMIN_EMAIL), None)
            
            if admin_user:
                admin_id = admin_user["id"]
                
                # User sends message to admin
                print("\n1️⃣ User sends message to admin...")
                response = requests.post(
                    f"{BASE_URL}/messages/",
                    json={
                        "receiver_id": admin_id,
                        "content": "Test message from user to admin"
                    },
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    print(f"✓ Message sent successfully")
                    
                    # Admin gets messages
                    print("\n2️⃣ Admin retrieves messages...")
                    response = requests.get(
                        f"{BASE_URL}/messages/",
                        headers={"Authorization": f"Bearer {self.admin_token}"}
                    )
                    
                    if response.status_code == 200:
                        messages = response.json()
                        print(f"✓ Admin has {len(messages)} messages")
                    else:
                        print(f"✗ Failed to get messages: {response.text}")
                else:
                    print(f"✗ Failed to send message: {response.text}")
                    return False
            else:
                print(f"✗ Admin user not found")
                return False
        else:
            print(f"✗ Failed to get users: {response.text}")
            return False
            
        print("\n✅ MESSAGING SYSTEM TEST COMPLETED SUCCESSFULLY")
        return True
        
    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        print("\n" + "="*70)
        print("📊 TESTING ADMIN DASHBOARD")
        print("="*70)
        
        response = requests.get(
            f"{BASE_URL}/bicycles/admin/dashboard",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Dashboard data retrieved")
            print(f"   Pending bicycles: {data.get('pending_bicycles_count', 0)}")
            print(f"   Pending appointments: {data.get('pending_appointments_count', 0)}")
            print(f"   Waiting bicycles: {len(data.get('waiting_bicycles', []))}")
            print(f"   Locked slots: {len(data.get('locked_slots_with_countdown', []))}")
            
            # Check if waiting_bicycles and waiting_appointments are available
            if 'waiting_bicycles' in data:
                print(f"✓ waiting_bicycles field available")
            if 'waiting_appointments' in data:
                print(f"✓ waiting_appointments field available")
            if 'locked_slots_with_countdown' in data:
                print(f"✓ locked_slots_with_countdown field available")
                
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
        print("\n✅ ADMIN DASHBOARD TEST COMPLETED SUCCESSFULLY")
        return True
        
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("🚀 STARTING COMPLETE API TESTS")
        print("="*70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Admin: {ADMIN_EMAIL}")
        print(f"Test User: {self.test_user_email}")
        
        all_passed = True
        
        try:
            # Login admin
            if not self.login_admin():
                all_passed = False
                return
                
            # Register and login test user
            if not self.register_test_user():
                all_passed = False
                return
                
            if not self.login_user():
                all_passed = False
                return
                
            # Run tests
            if not self.test_seller_flow():
                all_passed = False
                
            if not self.test_buyer_flow():
                all_passed = False
                
            if not self.test_cancel_flow():
                all_passed = False
                
            if not self.test_messaging():
                all_passed = False
                
            if not self.test_admin_dashboard():
                all_passed = False
                
            # Summary
            print("\n" + "="*70)
            if all_passed:
                print("✅ ALL TESTS PASSED!")
            else:
                print("❌ SOME TESTS FAILED")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
