#!/usr/bin/env python3
"""
Test the deployed website using Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Test credentials
ADMIN_EMAIL = "2200017736@stu.pku.edu.cn"
ADMIN_PASSWORD = "pkucycle"

def setup_driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_frontend_backend_connection():
    """Test if frontend can connect to backend"""
    print("="*70)
    print("Testing Frontend-Backend Connection")
    print("="*70)
    
    driver = setup_driver()
    
    try:
        # Open the website
        print("\n1. Opening website...")
        driver.get("https://pku-campus-cycle-cycle.vercel.app")
        time.sleep(3)
        
        # Check if page loaded
        print(f"   Page title: {driver.title}")
        print(f"   Current URL: {driver.current_url}")
        
        # Try to login
        print("\n2. Testing login...")
        driver.get("https://pku-campus-cycle-cycle.vercel.app/login")
        time.sleep(2)
        
        # Find email input
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            print("   ✓ Email input found")
            
            # Enter credentials
            email_input.send_keys(ADMIN_EMAIL)
            
            password_input = driver.find_element(By.ID, "password")
            password_input.send_keys(ADMIN_PASSWORD)
            
            # Find and click login button
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            print(f"   Login button text: {login_button.text}")
            login_button.click()
            
            time.sleep(3)
            
            # Check if login was successful
            current_url = driver.current_url
            print(f"   Current URL after login: {current_url}")
            
            if "/login" in current_url:
                print("   ✗ Still on login page - login failed")
                
                # Check for error message
                try:
                    error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'alert') or contains(@class, 'error')]")
                    print(f"   Error message: {error_msg.text}")
                except:
                    print("   No error message found")
            else:
                print("   ✓ Login successful - redirected to:", current_url)
                
        except Exception as e:
            print(f"   ✗ Error during login: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        driver.quit()
        print("\n✓ Test completed")

if __name__ == "__main__":
    test_frontend_backend_connection()
