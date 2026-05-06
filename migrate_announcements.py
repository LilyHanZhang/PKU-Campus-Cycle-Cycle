"""
数据库迁移脚本：添加公告表（announcements）
运行此脚本将在数据库中创建 announcements 表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import engine, SessionLocal
from backend.app.models import Announcement
from sqlalchemy import text

def create_announcements_table():
    """创建 announcements 表"""
    print("开始创建 announcements 表...")
    
    try:
        db = SessionLocal()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS announcements (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(200) NOT NULL,
            TEXT NOT NULL,
            image_url TEXT,
            attachment_url TEXT,
            is_pinned BOOLEAN DEFAULT FALSE,
            author_id UUID REFERENCES users(id),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        db.execute(text(create_table_sql))
        db.commit()
        
        print("✓ announcements 表创建成功！")
        
    except Exception as e:
        print(f"✗ 创建表失败：{e}")
        raise
    finally:
        db.close()

def check_table_exists():
    """检查 announcements 表是否存在"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'announcements'
            );
        """))
        exists = result.fetchone()[0]
        return exists
    finally:
        db.close()

if __name__ == "__main__":
    if check_table_exists():
        print("announcements 表已存在，无需创建")
    else:
        create_announcements_table()
        print("\n数据库迁移完成！")
