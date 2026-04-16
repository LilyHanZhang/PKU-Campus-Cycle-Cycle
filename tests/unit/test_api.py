import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.database import Base
from backend.app.models import User as DBUser, Role, Bicycle as DBBicycle, Post as DBPost, Appointment as DBAppointment
from backend.app.auth import get_password_hash

def create_test_engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

def create_test_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()

@pytest.fixture(scope="function")
def db_engine():
    engine = create_test_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    session = create_test_session(db_engine)
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_engine, db_session):
    from backend.app.main import app
    from backend.app.database import get_db

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def super_admin_token(client, db_session):
    user = DBUser(
        email="super@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Super Admin",
        role=Role.SUPER_ADMIN.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "super@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

@pytest.fixture
def admin_token(client, db_session):
    user = DBUser(
        email="admin@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Admin User",
        role=Role.ADMIN.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "admin@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

@pytest.fixture
def user_token(client, db_session):
    user = DBUser(
        email="user@pku.edu.cn",
        password_hash=get_password_hash("password123"),
        name="Normal User",
        role=Role.USER.value
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": "user@pku.edu.cn",
        "password": "password123"
    })
    return login_response.json()["access_token"]

def test_register(client):
    response = client.post("/auth/register", json={
        "email": "test@pku.edu.cn",
        "password": "testpass123",
        "name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@pku.edu.cn"
    assert data["name"] == "Test User"
    assert data["role"] == "USER"

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "email": "duplicate@pku.edu.cn",
        "password": "password123",
        "name": "User One"
    })
    response = client.post("/auth/register", json={
        "email": "duplicate@pku.edu.cn",
        "password": "password456",
        "name": "User Two"
    })
    assert response.status_code == 400
    assert "已被注册" in response.json()["detail"]

def test_login(client):
    client.post("/auth/register", json={
        "email": "login@pku.edu.cn",
        "password": "loginpass123",
        "name": "Login User"
    })
    response = client.post("/auth/login", json={
        "email": "login@pku.edu.cn",
        "password": "loginpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrongpass@pku.edu.cn",
        "password": "correctpassword",
        "name": "User"
    })
    response = client.post("/auth/login", json={
        "email": "wrongpass@pku.edu.cn",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_me(client, user_token):
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@pku.edu.cn"

def test_create_bicycle(client, user_token):
    response = client.post("/bicycles/", json={
        "brand": "Giant",
        "condition": 8,
        "price": 0,
        "description": "Almost new"
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == "Giant"
    assert data["status"] == "PENDING_APPROVAL"

def test_list_bicycles(client, user_token):
    client.post("/bicycles/", json={"brand": "Bike1", "condition": 5, "price": 100}, headers={"Authorization": f"Bearer {user_token}"})
    client.post("/bicycles/", json={"brand": "Bike2", "condition": 9, "price": 0}, headers={"Authorization": f"Bearer {user_token}"})

    response = client.get("/bicycles/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_approve_bicycle_as_admin(client, user_token, admin_token):
    bike_response = client.post("/bicycles/", json={
        "brand": "Merida",
        "condition": 7,
        "price": 50
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]

    approve_response = client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "IN_STOCK"

def test_approve_bicycle_as_user_fails(client, user_token):
    bike_response = client.post("/bicycles/", json={
        "brand": "Trek",
        "condition": 6,
        "price": 30
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]

    approve_response = client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {user_token}"})
    assert approve_response.status_code == 403

def test_create_appointment_pickup(client, user_token, admin_token):
    bike_response = client.post("/bicycles/", json={
        "brand": "Decathlon",
        "condition": 6,
        "price": 80
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]

    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})

    apt_response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})

    assert apt_response.status_code == 200
    assert apt_response.json()["status"] == "PENDING"

    bikes = client.get("/bicycles/").json()
    locked_bike = next(b for b in bikes if b["id"] == bike_id)
    assert locked_bike["status"] == "LOCKED"

def test_create_appointment_conflict(client, user_token, admin_token):
    bike_response = client.post("/bicycles/", json={
        "brand": "Specialized",
        "condition": 8,
        "price": 100
    }, headers={"Authorization": f"Bearer {user_token}"})
    bike_id = bike_response.json()["id"]
    client.put(f"/bicycles/{bike_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})

    client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})

    response = client.post("/appointments/", json={
        "bicycle_id": bike_id,
        "type": "pick-up"
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 400

def test_update_user_role_as_super_admin(client, super_admin_token):
    register_response = client.post("/auth/register", json={
        "email": "newadmin@pku.edu.cn",
        "password": "password123",
        "name": "New Admin"
    })
    user_id = register_response.json()["id"]

    update_response = client.put(
        f"/users/{user_id}/role",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "ADMIN"

def test_update_user_role_as_admin_fails(client, admin_token):
    register_response = client.post("/auth/register", json={
        "email": "someuser@pku.edu.cn",
        "password": "password123",
        "name": "Some User"
    })
    user_id = register_response.json()["id"]

    update_response = client.put(
        f"/users/{user_id}/role",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_response.status_code == 403

def test_transfer_super_admin(client, super_admin_token):
    register_response = client.post("/auth/register", json={
        "email": "newsuper@pku.edu.cn",
        "password": "password123",
        "name": "New SuperAdmin"
    })
    new_super_id = register_response.json()["id"]

    transfer_response = client.post(
        f"/users/{new_super_id}/transfer-super-admin",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert transfer_response.status_code == 200
    assert "主负责人权限已成功转让" in transfer_response.json()["message"]
    assert transfer_response.json()["new_super_admin"] == "newsuper@pku.edu.cn"

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {super_admin_token}"})
    assert me_response.json()["role"] == "USER"

def test_transfer_super_admin_requires_superadmin(client, user_token):
    register_response = client.post("/auth/register", json={
        "email": "target@pku.edu.cn",
        "password": "password123",
        "name": "Target User"
    })
    target_id = register_response.json()["id"]

    transfer_response = client.post(
        f"/users/{target_id}/transfer-super-admin",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert transfer_response.status_code == 403

def test_create_and_list_posts(client, user_token):
    response = client.post("/posts/", json={
        "title": "Test Post",
        "content": "Hello World"
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

    posts = client.get("/posts/")
    assert posts.status_code == 200
    assert len(posts.json()) >= 1

def test_like_post(client, user_token):
    post_response = client.post("/posts/", json={
        "title": "Like Test",
        "content": "Please like me"
    }, headers={"Authorization": f"Bearer {user_token}"})
    post_id = post_response.json()["id"]

    like_response = client.post(f"/posts/{post_id}/likes", headers={"Authorization": f"Bearer {user_token}"})
    assert like_response.status_code == 200
    assert like_response.json()["liked"] == True

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
