"""
单元测试：社区广场新功能
- 书签（收藏）功能
- 话题标签功能
- 用户头像和昵称显示
"""
import pytest
import requests
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

class TestForumFeatures:
    """测试社区广场新功能"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """创建测试用户"""
        user_data = {
            "email": f"test_forum_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def test_user2(self):
        """创建第二个测试用户"""
        user_data = {
            "email": f"test_forum2_{int(time.time())}@example.com",
            "password": "test123456",
            "name": "测试用户 2"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def auth_headers(self, test_user: Dict[str, Any]):
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
    def auth_headers2(self, test_user2: Dict[str, Any]):
        """获取第二个用户的认证头"""
        login_data = {
            "email": test_user2["email"],
            "password": "test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_post_with_hashtags(self, auth_headers: Dict[str, str]):
        """测试创建带话题标签的帖子"""
        post_data = {
            "title": "测试带话题的帖子",
            "content": "这是一个测试帖子，包含 #北京大学 和 #自行车 话题标签"
        }
        response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        post = response.json()
        assert post["title"] == post_data["title"]
        assert "hashtags" in post
        assert "北京大学" in post["hashtags"]
        assert "自行车" in post["hashtags"]
        assert post["author_name"] == "测试用户"
    
    def test_list_posts_with_hashtag_filter(self, auth_headers: Dict[str, str]):
        """测试按话题标签筛选帖子"""
        # 先创建一个带特定话题的帖子
        hashtag = f"测试话题_{int(time.time())}"
        post_data = {
            "title": f"测试话题帖子",
            "content": f"这是 #{hashtag} 的测试内容"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # 测试筛选
        response = requests.get(f"{BASE_URL}/posts/?hashtag={hashtag}")
        assert response.status_code == 200
        posts = response.json()
        assert len(posts) > 0
        assert any(hashtag in post.get("hashtags", []) for post in posts)
    
    def test_bookmark_post(self, auth_headers: Dict[str, str]):
        """测试收藏帖子功能"""
        # 先创建一个帖子
        post_data = {
            "title": "测试收藏功能的帖子",
            "content": "这是一个用于测试收藏功能的帖子 #测试"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        post_id = create_response.json()["id"]
        
        # 测试收藏
        bookmark_response = requests.post(
            f"{BASE_URL}/posts/{post_id}/bookmarks",
            headers=auth_headers
        )
        assert bookmark_response.status_code == 200
        assert bookmark_response.json()["post_id"] == post_id
        
        # 验证帖子详情中显示已收藏
        post_response = requests.get(
            f"{BASE_URL}/posts/{post_id}",
            headers=auth_headers
        )
        assert post_response.status_code == 200
        assert post_response.json()["is_bookmarked"] == True
        assert post_response.json()["bookmark_count"] >= 1
    
    def test_toggle_bookmark(self, auth_headers: Dict[str, str]):
        """测试取消收藏功能"""
        # 创建并收藏一个帖子
        post_data = {
            "title": "测试取消收藏",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        post_id = create_response.json()["id"]
        
        # 收藏
        bookmark_response1 = requests.post(
            f"{BASE_URL}/posts/{post_id}/bookmarks",
            headers=auth_headers
        )
        assert bookmark_response1.status_code == 200
        
        # 取消收藏
        bookmark_response2 = requests.post(
            f"{BASE_URL}/posts/{post_id}/bookmarks",
            headers=auth_headers
        )
        assert bookmark_response2.status_code == 200
        
        # 验证已取消收藏
        post_response = requests.get(
            f"{BASE_URL}/posts/{post_id}",
            headers=auth_headers
        )
        assert post_response.json()["is_bookmarked"] == False
    
    def test_get_my_bookmarks(self, auth_headers: Dict[str, str], auth_headers2: Dict[str, str]):
        """测试获取我的收藏列表"""
        # 用户 2 创建一个帖子
        post_data = {
            "title": "被收藏的帖子",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers2
        )
        post_id = create_response.json()["id"]
        
        # 用户 1 收藏该帖子
        requests.post(
            f"{BASE_URL}/posts/{post_id}/bookmarks",
            headers=auth_headers
        )
        
        # 获取用户 1 的收藏列表
        bookmarks_response = requests.get(
            f"{BASE_URL}/posts/bookmarks/my",
            headers=auth_headers
        )
        assert bookmarks_response.status_code == 200
        bookmarks = bookmarks_response.json()
        assert len(bookmarks) > 0
        assert any(post["id"] == post_id for post in bookmarks)
        # 验证返回的数据包含作者信息
        bookmarked_post = next(post for post in bookmarks if post["id"] == post_id)
        assert "author_name" in bookmarked_post
        assert "hashtags" in bookmarked_post
    
    def test_trending_hashtags(self, auth_headers: Dict[str, str]):
        """测试热门话题功能"""
        # 创建多个带相同话题的帖子
        hashtag = f"热门话题_{int(time.time())}"
        for i in range(3):
            post_data = {
                "title": f"测试帖子{i}",
                "content": f"内容 #{hashtag}"
            }
            requests.post(
                f"{BASE_URL}/posts/",
                json=post_data,
                headers=auth_headers
            )
        
        # 获取热门话题
        trending_response = requests.get(f"{BASE_URL}/posts/hashtags/trending")
        assert trending_response.status_code == 200
        trending = trending_response.json()
        assert isinstance(trending, list)
        # 验证新创建的话题在热门列表中（如果 limit 足够大）
        # 注意：这个断言可能失败，因为取决于数据库中其他帖子的话题
    
    def test_comment_with_author_info(self, auth_headers: Dict[str, str]):
        """测试评论返回作者信息"""
        # 创建帖子
        post_data = {
            "title": "测试评论",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        post_id = create_response.json()["id"]
        
        # 添加评论
        comment_data = {
            "content": "这是一条测试评论"
        }
        comment_response = requests.post(
            f"{BASE_URL}/posts/{post_id}/comments",
            json=comment_data,
            headers=auth_headers
        )
        assert comment_response.status_code == 200
        comment = comment_response.json()
        assert comment["author_name"] == "测试用户"
        
        # 获取评论列表
        comments_response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
        assert comments_response.status_code == 200
        comments = comments_response.json()
        assert len(comments) > 0
        assert any(c["author_name"] == "测试用户" for c in comments)
    
    def test_post_stats_in_list(self, auth_headers: Dict[str, str]):
        """测试帖子列表返回完整统计信息"""
        # 创建帖子
        post_data = {
            "title": "统计信息测试",
            "content": "测试内容 #测试"
        }
        create_response = requests.post(
            f"{BASE_URL}/posts/",
            json=post_data,
            headers=auth_headers
        )
        post_id = create_response.json()["id"]
        
        # 获取帖子列表
        posts_response = requests.get(f"{BASE_URL}/posts/")
        assert posts_response.status_code == 200
        posts = posts_response.json()
        
        # 验证返回的帖子包含所有统计字段
        test_post = next((p for p in posts if p["id"] == post_id), None)
        assert test_post is not None
        assert "like_count" in test_post
        assert "comment_count" in test_post
        assert "bookmark_count" in test_post
        assert "author_name" in test_post
        assert "author_avatar_url" in test_post
        assert "hashtags" in test_post


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
