"""
数据库迁移脚本：为 appointments 表添加 time_slot_id 字段
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import engine, SessionLocal
from sqlalchemy import text

def migrate_appointments_table():
    """为 appointments 表添加 time_slot_id 字段（如果不存在）"""
    db = SessionLocal()
    try:
        # 检查字段是否已经存在
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            AND column_name = 'time_slot_id'
        """))
        exists = result.fetchone()
        
        if exists:
            print("✓ time_slot_id 字段已存在")
        else:
            print("添加 time_slot_id 字段到 appointments 表...")
            db.execute(text("""
                ALTER TABLE appointments 
                ADD COLUMN time_slot_id UUID
            """))
            db.commit()
            print("✓ time_slot_id 字段添加成功")
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_appointments_table()
