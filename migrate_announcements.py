"""
数据库迁移脚本：添加公告表（announcements）
运行此脚本将在数据库中创建 announcements 表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.database import engine, Base
from backend.app.models import Announcement

def create_announcements_table():
    """创建 announcements 表"""
    print("开始创建 announcements 表...")
    
    try:
        # 使用 SQLAlchemy 创建所有表（包括 announcements）
        Base.metadata.create_all(bind=engine)
        print("✓ announcements 表创建成功！")
        
    except Exception as e:
        print(f"✗ 创建表失败：{e}")
        raise

if __name__ == "__main__":
    print("检查并创建 announcements 表...")
    create_announcements_table()
    print("\n✓ 数据库迁移完成！")
