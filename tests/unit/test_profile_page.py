"""
单元测试：个人中心页面功能
- 用户信息展示
- 车辆管理
- 预约管理
- 收藏功能
- 消息通知
"""
import pytest
import requests
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"


class TestProfilePage:
    """测试个人中心页面功能"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """创建测试用户"""
        user_data = {
            "email": f"test_profile_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def admin_user(self):
        """创建管理员用户"""
        user_data = {
            "email": f"test_admin_{int(time.time())}@example.com",
            "password": "admin123456",
            "name": "测试管理员",
            "role": "ADMIN"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def auth_headers(self, test_user):
        """获取认证头"""
        login_data = {
            "email": test_user["email"],
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_user):
        """获取管理员认证头"""
        login_data = {
            "email": admin_user["email"],
            "password": "admin123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_user_profile(self, auth_headers):
        """测试获取用户个人信息"""
        response = requests.get(f"{BASE_URL}/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert "role" in data
    
    def test_update_user_profile(self, auth_headers):
        """测试更新用户个人信息"""
        update_data = {
            "name": "新昵称",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        response = requests.put(f"{BASE_URL}/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新昵称"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"
    
    def test_register_bicycle(self, auth_headers):
        """测试在个人中心登记车辆"""
        bicycle_data = {
            "brand": "永久",
            "color": "蓝色",
            "description": "测试车辆",
            "purchase_price": 500,
            "purchase_year": 2023
        }
        response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "永久"
        assert data["color"] == "蓝色"
        assert data["owner_id"] is not None
        return data["id"]
    
    def test_get_my_bicycles(self, auth_headers, test_user):
        """测试获取我的车辆列表"""
        # 先登记一辆车
        bicycle_data = {
            "brand": "凤凰",
            "color": "红色",
            "description": "测试车辆 2",
            "purchase_price": 600,
            "purchase_year": 2022
        }
        requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=auth_headers)
        
        # 获取车辆列表
        response = requests.get(f"{BASE_URL}/bicycles/", headers=auth_headers)
        assert response.status_code == 200
        bicycles = response.json()
        
        # 验证包含自己的车辆
        my_bicycles = [b for b in bicycles if b["owner_id"] == test_user["id"]]
        assert len(my_bicycles) > 0
    
    def test_get_my_appointments_empty(self, auth_headers):
        """测试获取空预约列表"""
        response = requests.get(f"{BASE_URL}/appointments/user/me", headers=auth_headers)
        assert response.status_code == 200
        appointments = response.json()
        assert isinstance(appointments, list)
    
    def test_create_appointment(self, auth_headers, admin_headers):
        """测试创建预约"""
        # 管理员先登记一辆车
        bicycle_data = {
            "brand": "捷安特",
            "color": "黑色",
            "description": "管理员车辆",
            "purchase_price": 1000,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=admin_headers)
        bicycle_id = bike_response.json()["id"]
        
        # 管理员审核通过
        requests.put(f"{BASE_URL}/bicycles/{bicycle_id}/approve", headers=admin_headers)
        
        # 用户创建预约
        appointment_data = {
            "bicycle_id": bicycle_id,
            "type": "pick-up",
            "notes": "测试预约"
        }
        response = requests.post(f"{BASE_URL}/appointments/", json=appointment_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["bicycle_id"] == bicycle_id
        assert data["type"] == "pick-up"
        assert data["status"] == "PENDING"
    
    def test_get_my_appointments(self, auth_headers):
        """测试获取我的预约列表"""
        response = requests.get(f"{BASE_URL}/appointments/user/me", headers=auth_headers)
        assert response.status_code == 200
        appointments = response.json()
        assert isinstance(appointments, list)
    
    def test_bookmark_post(self, auth_headers):
        """测试收藏帖子功能"""
        # 先创建一个帖子
        post_data = {
            "title": "测试收藏功能的帖子",
            "content": "这是一个用于测试收藏功能的帖子 #测试"
        }
        create_response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=auth_headers)
        assert create_response.status_code == 200
        post_id = create_response.json()["id"]
        
        # 测试收藏
        bookmark_response = requests.post(f"{BASE_URL}/posts/{post_id}/bookmarks", headers=auth_headers)
        assert bookmark_response.status_code == 200
        assert bookmark_response.json()["post_id"] == post_id
        
        # 验证帖子详情中显示已收藏
        post_response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=auth_headers)
        assert post_response.status_code == 200
        assert post_response.json()["is_bookmarked"] == True
        assert post_response.json()["bookmark_count"] >= 1
    
    def test_get_my_bookmarks(self, auth_headers):
        """测试获取我的收藏列表"""
        # 先创建一个帖子并收藏
        post_data = {
            "title": "被收藏的测试帖子",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=auth_headers)
        post_id = create_response.json()["id"]
        
        # 收藏
        requests.post(f"{BASE_URL}/posts/{post_id}/bookmarks", headers=auth_headers)
        
        # 获取收藏列表
        bookmarks_response = requests.get(f"{BASE_URL}/posts/bookmarks/my", headers=auth_headers)
        assert bookmarks_response.status_code == 200
        bookmarks = bookmarks_response.json()
        assert isinstance(bookmarks, list)
        assert len(bookmarks) > 0
        assert any(post["id"] == post_id for post in bookmarks)
        
        # 验证返回的数据包含作者信息
        bookmarked_post = next(post for post in bookmarks if post["id"] == post_id)
        assert "author_name" in bookmarked_post
        assert "author_avatar_url" in bookmarked_post
        assert "hashtags" in bookmarked_post
    
    def test_toggle_bookmark(self, auth_headers):
        """测试取消收藏功能"""
        # 创建并收藏一个帖子
        post_data = {
            "title": "测试取消收藏",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=auth_headers)
        post_id = create_response.json()["id"]
        
        # 收藏
        bookmark_response1 = requests.post(f"{BASE_URL}/posts/{post_id}/bookmarks", headers=auth_headers)
        assert bookmark_response1.status_code == 200
        
        # 取消收藏
        bookmark_response2 = requests.post(f"{BASE_URL}/posts/{post_id}/bookmarks", headers=auth_headers)
        assert bookmark_response2.status_code == 200
        
        # 验证已取消收藏
        post_response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=auth_headers)
        assert post_response.status_code == 200
        assert post_response.json()["is_bookmarked"] == False
        assert post_response.json()["bookmark_count"] == 0
    
    def test_get_unread_messages(self, auth_headers):
        """测试获取未读消息数量"""
        response = requests.get(f"{BASE_URL}/messages/unread", headers=auth_headers)
        assert response.status_code == 200
        unread_count = response.json()
        assert isinstance(unread_count, int)
        assert unread_count >= 0
    
    def test_profile_page_forum_link(self):
        """测试个人中心收藏页面的论坛链接正确性"""
        # 这是一个前端测试，验证链接指向 /forum 而不是 /posts
        # 通过检查前端文件来验证
        import os
        profile_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "frontend", "src", "app", "profile", "page.tsx"
        )
        
        with open(profile_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证链接指向 /forum
        assert 'href="/forum"' in content
        # 验证没有错误的 /posts 链接（在收藏空状态中）
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '浏览帖子' in line and 'Link' in line:
                # 检查下一行是否包含正确的链接
                if i + 1 < len(lines):
                    assert 'href="/forum"' in lines[i+1] or 'href="/forum"' in line


class TestProfilePageIntegration:
    """个人中心页面集成测试"""
    
    @pytest.fixture(scope="class")
    def seller_user(self):
        """创建卖家用户"""
        user_data = {
            "email": f"test_seller_{int(time.time())}@example.com",
            "password": "seller123456",
            "name": "测试卖家"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def buyer_user(self):
        """创建买家用户"""
        user_data = {
            "email": f"test_buyer_{int(time.time())}@example.com",
            "password": "buyer123456",
            "name": "测试买家"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def seller_headers(self, seller_user):
        """获取卖家认证头"""
        login_data = {
            "email": seller_user["email"],
            "password": "seller123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def buyer_headers(self, buyer_user):
        """获取买家认证头"""
        login_data = {
            "email": buyer_user["email"],
            "password": "buyer123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_complete_seller_flow(self, seller_headers, buyer_headers):
        """测试卖家完整流程"""
        # 1. 登记车辆
        bicycle_data = {
            "brand": "美利达",
            "color": "黄色",
            "description": "卖家测试车辆",
            "purchase_price": 800,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        assert bike_response.status_code == 200
        bicycle_id = bike_response.json()["id"]
        
        # 2. 查看我的车辆（应该在待审核状态）
        bikes_response = requests.get(f"{BASE_URL}/bicycles/", headers=seller_headers)
        assert bikes_response.status_code == 200
        my_bikes = [b for b in bikes_response.json() if b["owner_id"] == seller_headers.get("owner_id")]
        assert len(my_bikes) > 0
        
        # 3. 管理员审核通过
        admin_data = {
            "email": f"test_admin2_{int(time.time())}@example.com",
            "password": "admin123456",
            "name": "测试管理员 2"
        }
        admin_response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        admin_id = admin_response.json()["id"]
        
        # 设置管理员角色（需要数据库权限，这里跳过）
        # 直接测试后续流程
        
        # 4. 买家创建预约
        appointment_data = {
            "bicycle_id": bicycle_id,
            "type": "pick-up",
            "notes": "买家测试预约"
        }
        apt_response = requests.post(f"{BASE_URL}/appointments/", json=appointment_data, headers=buyer_headers)
        assert apt_response.status_code == 200
        
        # 5. 卖家查看预约
        appointments_response = requests.get(f"{BASE_URL}/appointments/bicycle/{bicycle_id}", headers=seller_headers)
        assert appointments_response.status_code == 200
        appointments = appointments_response.json()
        assert len(appointments) > 0
    
    def test_complete_buyer_flow(self, seller_headers, buyer_headers):
        """测试买家完整流程"""
        # 1. 管理员先登记并审核车辆
        bicycle_data = {
            "brand": "崔克",
            "color": "绿色",
            "description": "买家测试用车辆",
            "purchase_price": 1200,
            "purchase_year": 2023
        }
        bike_response = requests.post(f"{BASE_URL}/bicycles/", json=bicycle_data, headers=seller_headers)
        bicycle_id = bike_response.json()["id"]
        
        # 2. 买家浏览车辆
        all_bikes_response = requests.get(f"{BASE_URL}/bicycles/")
        assert all_bikes_response.status_code == 200
        
        # 3. 买家创建预约
        appointment_data = {
            "bicycle_id": bicycle_id,
            "type": "delivery",
            "notes": "需要送货"
        }
        apt_response = requests.post(f"{BASE_URL}/appointments/", json=appointment_data, headers=buyer_headers)
        assert apt_response.status_code == 200
        
        # 4. 买家查看我的预约
        my_apts_response = requests.get(f"{BASE_URL}/appointments/user/me", headers=buyer_headers)
        assert my_apts_response.status_code == 200
        my_apts = my_apts_response.json()
        assert len(my_apts) > 0
        
        # 5. 买家收藏帖子
        post_data = {
            "title": "买家指南",
            "content": "这是买家使用指南 #买家 #指南"
        }
        post_response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=buyer_headers)
        post_id = post_response.json()["id"]
        
        # 收藏
        bookmark_response = requests.post(f"{BASE_URL}/posts/{post_id}/bookmarks", headers=buyer_headers)
        assert bookmark_response.status_code == 200
        
        # 6. 买家查看我的收藏
        bookmarks_response = requests.get(f"{BASE_URL}/posts/bookmarks/my", headers=buyer_headers)
        assert bookmarks_response.status_code == 200
        bookmarks = bookmarks_response.json()
        assert len(bookmarks) > 0
        assert any(post["id"] == post_id for post in bookmarks)
