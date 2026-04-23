#!/usr/bin/env python3
"""
使用 Selenium 测试网站（模拟真实浏览器）
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_with_selenium():
    """使用 Selenium 测试管理后台"""
    
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    print("启动浏览器...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 访问首页
        print("访问首页...")
        driver.get("https://pku-campus-cycle-cycle.vercel.app")
        time.sleep(2)
        print(f"页面标题：{driver.title}")
        
        # 访问登录页
        print("\n访问登录页...")
        driver.get("https://pku-campus-cycle-cycle.vercel.app/login")
        time.sleep(2)
        
        # 填写登录表单
        print("填写登录表单...")
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.send_keys("2200017736@stu.pku.edu.cn")
        password_input.send_keys("pkucycle")
        
        # 提交登录
        print("提交登录...")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # 等待登录完成
        time.sleep(3)
        
        # 检查是否登录成功
        current_url = driver.current_url
        print(f"登录后 URL: {current_url}")
        
        # 访问管理后台
        print("\n访问管理后台...")
        driver.get("https://pku-campus-cycle-cycle.vercel.app/admin")
        time.sleep(3)
        
        print(f"管理后台页面标题：{driver.title}")
        print(f"当前 URL: {driver.current_url}")
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 检查关键元素
        if "管理后台" in page_source:
            print("✓ 页面包含'管理后台'文字")
        else:
            print("✗ 页面不包含'管理后台'文字")
        
        if "仪表盘" in page_source:
            print("✓ 页面包含'仪表盘'文字")
        else:
            print("✗ 页面不包含'仪表盘'文字")
        
        # 检查是否有错误信息
        if "This page couldn't load" in page_source:
            print("✗ 页面显示错误：This page couldn't load")
        else:
            print("✓ 页面没有显示加载错误")
        
        # 检查控制台日志（如果可能）
        print("\n检查浏览器日志...")
        logs = driver.get_log('browser')
        for log in logs[-10:]:  # 显示最近 10 条日志
            print(f"  {log['level']}: {log['message']}")
        
        # 截图
        driver.save_screenshot("/tmp/admin_page.png")
        print("\n截图已保存到：/tmp/admin_page.png")
        
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    print("=" * 70)
    print("Selenium 浏览器测试")
    print("=" * 70)
    test_with_selenium()
    print("=" * 70)
