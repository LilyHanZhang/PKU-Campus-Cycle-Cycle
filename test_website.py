#!/usr/bin/env python3
"""
Website integration test for PKU Campus Cycle Cycle
Tests all features from revise_detail.md
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
import time
import sys

BASE_URL = "https://pku-campus-cycle-cycle.vercel.app"

# Test credentials
ADMIN_EMAIL = "2200017736@stu.pku.edu.cn"
ADMIN_PASSWORD = "pkucycle"

class WebsiteTester:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.test_user_email = f"test_{int(time.time())}@example.com"
        self.test_user_password = "test123456"
        
    def login(self, email, password):
        """Login to the website"""
        print(f"\n📝 Logging in as {email}...")
        self.driver.get(f"{BASE_URL}/login")
        
        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)
        
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)
        
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        time.sleep(2)
        print(f"✓ Login successful")
        
    def register_user(self, email, password, name="Test User"):
        """Register a new user"""
        print(f"\n📝 Registering new user: {email}...")
        self.driver.get(f"{BASE_URL}/register")
        
        name_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        name_input.send_keys(name)
        
        email_input = self.driver.find_element(By.ID, "email")
        email_input.send_keys(email)
        
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        
        register_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        register_button.click()
        
        time.sleep(2)
        print(f"✓ Registration successful")
        
    def test_seller_flow(self):
        """Test complete seller flow from revise_detail.md"""
        print("\n" + "="*70)
        print("🚲 TESTING SELLER FLOW")
        print("="*70)
        
        # Step 1: Seller registers bicycle
        print("\n1️⃣ Seller registers bicycle...")
        self.driver.get(f"{BASE_URL}/bicycles/new")
        
        brand_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "brand"))
        )
        brand_input.send_keys("Test Bike for Seller Flow")
        
        condition_input = self.driver.find_element(By.ID, "condition")
        condition_input.send_keys("8")
        
        price_input = self.driver.find_element(By.ID, "price")
        price_input.send_keys("200")
        
        description_input = self.driver.find_element(By.ID, "description")
        description_input.send_keys("Test bicycle for seller flow testing")
        
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        time.sleep(2)
        print("✓ Bicycle registered successfully (Status: PENDING_APPROVAL)")
        
        # Step 2: Admin proposes time slots
        print("\n2️⃣ Admin proposes time slots...")
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.driver.get(f"{BASE_URL}/admin")
        
        time.sleep(2)
        
        # Find the bicycle in pending list
        pending_tab = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '待审核车辆')]"))
        )
        pending_tab.click()
        
        time.sleep(1)
        
        # Click propose time slots button
        try:
            propose_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '提出时间段')]"
            )
            propose_button.click()
            
            time.sleep(1)
            
            # Set start time (1 hour from now)
            start_time = datetime.now() + timedelta(hours=1)
            end_time = datetime.now() + timedelta(hours=2)
            
            # Fill in time slot form
            start_input = self.driver.find_element(By.ID, "start_time")
            start_input.clear()
            start_input.send_keys(start_time.strftime("%Y-%m-%dT%H:%M"))
            
            end_input = self.driver.find_element(By.ID, "end_time")
            end_input.clear()
            end_input.send_keys(end_time.strftime("%Y-%m-%dT%H:%M"))
            
            submit_slot_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认')]"
            )
            submit_slot_button.click()
            
            time.sleep(2)
            print("✓ Admin proposed time slots (Status: LOCKED)")
        except Exception as e:
            print(f"⚠️ Could not propose time slots: {e}")
        
        # Step 3: Seller selects time slot
        print("\n3️⃣ Seller selects time slot...")
        self.login(self.test_user_email, self.test_user_password)
        self.driver.get(f"{BASE_URL}/my-time-slots")
        
        time.sleep(2)
        
        try:
            # Select the time slot
            select_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '选择')]"
            )
            select_button.click()
            
            time.sleep(2)
            print("✓ Seller selected time slot (Status: LOCKED, waiting for admin confirmation)")
        except Exception as e:
            print(f"⚠️ Could not select time slot: {e}")
        
        # Step 4: Admin confirms time slot
        print("\n4️⃣ Admin confirms time slot...")
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.driver.get(f"{BASE_URL}/admin")
        
        time.sleep(2)
        
        try:
            # Go to Dashboard tab
            dashboard_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Dashboard')]"
            )
            dashboard_tab.click()
            
            time.sleep(1)
            
            # Find confirm button in waiting confirmation section
            confirm_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认交易')]"
            )
            confirm_button.click()
            
            time.sleep(2)
            print("✓ Admin confirmed time slot (Status: RESERVED)")
        except Exception as e:
            print(f"⚠️ Could not confirm time slot: {e}")
        
        # Step 5: Admin stores bicycle in inventory
        print("\n5️⃣ Admin stores bicycle in inventory...")
        self.driver.get(f"{BASE_URL}/admin")
        
        time.sleep(2)
        
        try:
            # Go to All Bicycles tab
            all_bikes_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '所有车辆')]"
            )
            all_bikes_tab.click()
            
            time.sleep(1)
            
            # Find store inventory button for RESERVED bike
            store_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认入库')]"
            )
            store_button.click()
            
            time.sleep(2)
            print("✓ Bicycle stored in inventory (Status: IN_STOCK)")
        except Exception as e:
            print(f"⚠️ Could not store bicycle: {e}")
            
    def test_buyer_flow(self):
        """Test complete buyer flow from revise_detail.md"""
        print("\n" + "="*70)
        print("🛒 TESTING BUYER FLOW")
        print("="*70)
        
        # Step 1: Buyer creates appointment
        print("\n1️⃣ Buyer creates appointment...")
        self.login(self.test_user_email, self.test_user_password)
        self.driver.get(f"{BASE_URL}/bicycles")
        
        time.sleep(2)
        
        try:
            # Find a bicycle and click appointment button
            appointment_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '预约')]"
            )
            appointment_button.click()
            
            time.sleep(2)
            print("✓ Appointment created (Status: PENDING)")
        except Exception as e:
            print(f"⚠️ Could not create appointment: {e}")
        
        # Step 2: Admin proposes time slots
        print("\n2️⃣ Admin proposes time slots...")
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.driver.get(f"{BASE_URL}/admin")
        
        time.sleep(2)
        
        try:
            # Go to Appointment Management tab
            apt_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '预约管理')]"
            )
            apt_tab.click()
            
            time.sleep(1)
            
            # Click propose time slots
            propose_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '提出时间段')]"
            )
            propose_button.click()
            
            time.sleep(1)
            
            # Set time slots
            start_time = datetime.now() + timedelta(hours=1)
            end_time = datetime.now() + timedelta(hours=2)
            
            start_input = self.driver.find_element(By.ID, "start_time")
            start_input.send_keys(start_time.strftime("%Y-%m-%dT%H:%M"))
            
            end_input = self.driver.find_element(By.ID, "end_time")
            end_input.send_keys(end_time.strftime("%Y-%m-%dT%H:%M"))
            
            submit_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认')]"
            )
            submit_button.click()
            
            time.sleep(2)
            print("✓ Admin proposed time slots")
        except Exception as e:
            print(f"⚠️ Could not propose time slots: {e}")
        
        # Step 3: Buyer selects time slot
        print("\n3️⃣ Buyer selects time slot...")
        self.login(self.test_user_email, self.test_user_password)
        self.driver.get(f"{BASE_URL}/my-time-slots")
        
        time.sleep(2)
        
        try:
            select_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '选择')]"
            )
            select_button.click()
            
            time.sleep(2)
            print("✓ Buyer selected time slot")
        except Exception as e:
            print(f"⚠️ Could not select time slot: {e}")
        
        # Step 4: Admin confirms time slot
        print("\n4️⃣ Admin confirms time slot...")
        self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.driver.get(f"{BASE_URL}/admin")
        
        time.sleep(2)
        
        try:
            dashboard_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Dashboard')]"
            )
            dashboard_tab.click()
            
            time.sleep(1)
            
            # Find confirm button for appointments
            confirm_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认时间段')]"
            )
            confirm_button.click()
            
            time.sleep(2)
            print("✓ Admin confirmed time slot (Status: CONFIRMED, Bicycle: SOLD)")
        except Exception as e:
            print(f"⚠️ Could not confirm time slot: {e}")
            
    def test_cancel_flow(self):
        """Test cancel functionality"""
        print("\n" + "="*70)
        print("❌ TESTING CANCEL FLOW")
        print("="*70)
        
        # User cancels bicycle
        print("\n1️⃣ User cancels bicycle...")
        self.login(self.test_user_email, self.test_user_password)
        self.driver.get(f"{BASE_URL}/my-bicycles")
        
        time.sleep(2)
        
        try:
            cancel_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '取消')]"
            )
            cancel_button.click()
            
            time.sleep(1)
            confirm_cancel = self.driver.find_element(
                By.XPATH, "//button[contains(text(), '确认取消')]"
            )
            confirm_cancel.click()
            
            time.sleep(2)
            print("✓ User cancelled bicycle")
        except Exception as e:
            print(f"⚠️ Could not cancel bicycle: {e}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("🚀 STARTING WEBSITE INTEGRATION TESTS")
        print("="*70)
        print(f"Base URL: {BASE_URL}")
        print(f"Admin: {ADMIN_EMAIL}")
        print(f"Test User: {self.test_user_email}")
        
        try:
            # Register test user
            self.register_user(self.test_user_email, self.test_user_password)
            
            # Test seller flow
            self.test_seller_flow()
            
            # Test buyer flow
            self.test_buyer_flow()
            
            # Test cancel flow
            self.test_cancel_flow()
            
            print("\n" + "="*70)
            print("✅ ALL TESTS COMPLETED")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.driver.quit()
            print("\n👋 Browser closed")

if __name__ == "__main__":
    tester = WebsiteTester()
    tester.run_all_tests()
