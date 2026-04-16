import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User, Role
from app.auth import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "2200017736@stu.pku.edu.cn").first()
        if not existing:
            super_admin = User(
                email="2200017736@stu.pku.edu.cn",
                password_hash=get_password_hash("pkucycle"),
                name="SuperAdmin",
                role=Role.SUPER_ADMIN.value
            )
            db.add(super_admin)
            db.commit()
            print("SuperAdmin account created: 2200017736@stu.pku.edu.cn / pkucycle")
        else:
            print("SuperAdmin account already exists")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
