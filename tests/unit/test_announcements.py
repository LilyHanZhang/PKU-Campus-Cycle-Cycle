import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database import Base
from backend.app.models import User as DBUser, Role, Announcement as DBAnnouncement
from backend.app.main import app
from backend.app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

from backend.app.database import get_db
app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

def create_test_user(db, email: str, password: str = "testpass123", role: str = Role.USER.value, name: str = "Test User"):
    user = DBUser(
        email=email,
        password_hash=get_password_hash(password),
        name=name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_access_token(email: str, password: str):
    response = client.post(
        "http://test/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.json()}")
        return None
    return response.json()["access_token"]

class TestAnnouncementModel:
    def test_create_announcement(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin@test.com", role=Role.ADMIN.value)
            
            announcement = DBAnnouncement(
                title="Test Announcement",
                content="This is a test announcement content",
                author_id=user.id,
                is_pinned=True
            )
            db.add(announcement)
            db.commit()
            db.refresh(announcement)
            
            assert announcement.id is not None
            assert announcement.title == "Test Announcement"
            assert announcement.content == "This is a test announcement content"
            assert announcement.is_pinned == True
            assert announcement.author_id == user.id
        finally:
            db.close()

class TestAnnouncementAPI:
    def test_create_announcement_unauthorized(self):
        response = client.post(
            "http://test/announcements/",
            json={
                "title": "Test Announcement",
                "content": "Test content"
            }
        )
        assert response.status_code in [401, 403]

    def test_create_announcement_no_permission(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "user@test.com", role=Role.USER.value)
            token = get_access_token("user@test.com", "testpass123")
            assert token is not None
            
            response = client.post(
                "http://test/announcements/",
                json={
                    "title": "Test Announcement",
                    "content": "Test content"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 403
            assert "只有管理员" in response.json()["detail"]
        finally:
            db.close()

    def test_create_announcement_admin(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin2@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin2@test.com", "testpass123")
            assert token is not None
            
            response = client.post(
                "http://test/announcements/",
                json={
                    "title": "Admin Announcement",
                    "content": "This is an announcement by admin",
                    "image_url": "/test/image.jpg",
                    "is_pinned": False
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Admin Announcement"
            assert data["content"] == "This is an announcement by admin"
            assert data["image_url"] == "/test/image.jpg"
            assert data["is_pinned"] == False
            assert "id" in data
            assert "author_id" in data
        finally:
            db.close()

    def test_create_announcement_super_admin(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "superadmin@test.com", role=Role.SUPER_ADMIN.value)
            token = get_access_token("superadmin@test.com", "testpass123")
            assert token is not None
            
            response = client.post(
                "http://test/announcements/",
                json={
                    "title": "Super Admin Announcement",
                    "content": "This is an announcement by super admin",
                    "is_pinned": True
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Super Admin Announcement"
            assert data["is_pinned"] == True
        finally:
            db.close()

    def test_list_announcements(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin3@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin3@test.com", "testpass123")
            assert token is not None
            
            before_count = len(client.get("http://test/announcements/").json())
            
            client.post(
                "http://test/announcements/",
                json={"title": "Announcement 1", "content": "Content 1", "is_pinned": False},
                headers={"Authorization": f"Bearer {token}"}
            )
            client.post(
                "http://test/announcements/",
                json={"title": "Announcement 2", "content": "Content 2", "is_pinned": True},
                headers={"Authorization": f"Bearer {token}"}
            )
            client.post(
                "http://test/announcements/",
                json={"title": "Announcement 3", "content": "Content 3", "is_pinned": False},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            response = client.get("http://test/announcements/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == before_count + 3
            
            pinned_announcements = [ann for ann in data if ann["is_pinned"] and ann["title"].startswith("Announcement")]
            assert len(pinned_announcements) >= 1
            assert pinned_announcements[0]["title"] == "Announcement 2"
        finally:
            db.close()

    def test_get_announcement(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin4@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin4@test.com", "testpass123")
            assert token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "Single Announcement", "content": "Single content"},
                headers={"Authorization": f"Bearer {token}"}
            )
            announcement_id = create_response.json()["id"]
            
            response = client.get(f"http://test/announcements/{announcement_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == announcement_id
            assert data["title"] == "Single Announcement"
        finally:
            db.close()

    def test_get_announcement_not_found(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin5@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin5@test.com", "testpass123")
            assert token is not None
            
            response = client.get(
                f"http://test/announcements/00000000-0000-0000-0000-000000000000",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 404
        finally:
            db.close()

    def test_update_announcement(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin6@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin6@test.com", "testpass123")
            assert token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "Original Title", "content": "Original content"},
                headers={"Authorization": f"Bearer {token}"}
            )
            announcement_id = create_response.json()["id"]
            
            update_response = client.put(
                f"http://test/announcements/{announcement_id}",
                json={"title": "Updated Title", "content": "Updated content", "is_pinned": True},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert update_response.status_code == 200
            data = update_response.json()
            assert data["title"] == "Updated Title"
            assert data["content"] == "Updated content"
            assert data["is_pinned"] == True
        finally:
            db.close()

    def test_update_announcement_no_permission(self):
        db = TestingSessionLocal()
        try:
            admin = create_test_user(db, "admin7@test.com", role=Role.ADMIN.value)
            regular_user = create_test_user(db, "user7@test.com", role=Role.USER.value)
            
            admin_token = get_access_token("admin7@test.com", "testpass123")
            assert admin_token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "Admin Announcement", "content": "Admin content"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            announcement_id = create_response.json()["id"]
            
            user_token = get_access_token("user7@test.com", "testpass123")
            assert user_token is not None
            
            update_response = client.put(
                f"http://test/announcements/{announcement_id}",
                json={"title": "Hacked Title"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert update_response.status_code == 403
        finally:
            db.close()

    def test_delete_announcement(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin8@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin8@test.com", "testpass123")
            assert token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "To Delete", "content": "Delete me"},
                headers={"Authorization": f"Bearer {token}"}
            )
            announcement_id = create_response.json()["id"]
            
            delete_response = client.delete(
                f"http://test/announcements/{announcement_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 200
            
            get_response = client.get(
                f"http://test/announcements/{announcement_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert get_response.status_code == 404
        finally:
            db.close()

    def test_pin_announcement(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin9@test.com", role=Role.ADMIN.value)
            token = get_access_token("admin9@test.com", "testpass123")
            assert token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "Pin Test", "content": "Pin me", "is_pinned": False},
                headers={"Authorization": f"Bearer {token}"}
            )
            announcement_id = create_response.json()["id"]
            
            pin_response = client.put(
                f"http://test/announcements/{announcement_id}/pin",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert pin_response.status_code == 200
            data = pin_response.json()
            assert data["is_pinned"] == True
            
            unpin_response = client.put(
                f"http://test/announcements/{announcement_id}/unpin",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert unpin_response.status_code == 200
            data = unpin_response.json()
            assert data["is_pinned"] == False
        finally:
            db.close()

    def test_announcement_author_info(self):
        db = TestingSessionLocal()
        try:
            user = create_test_user(db, "admin10@test.com", role=Role.ADMIN.value, name="Test Admin")
            token = get_access_token("admin10@test.com", "testpass123")
            assert token is not None
            
            create_response = client.post(
                "http://test/announcements/",
                json={"title": "Author Test", "content": "Test author info"},
                headers={"Authorization": f"Bearer {token}"}
            )
            data = create_response.json()
            assert data["author_name"] == "Test Admin"
            
            list_response = client.get("http://test/announcements/")
            announcements = list_response.json()
            assert len(announcements) > 0
            
            author_test_ann = [ann for ann in announcements if ann["title"] == "Author Test"]
            assert len(author_test_ann) > 0
            assert author_test_ann[0]["author_name"] == "Test Admin"
        finally:
            db.close()
