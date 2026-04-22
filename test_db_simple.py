"""
最简单的数据库连接测试
"""
import os
from sqlalchemy import create_engine, text

# 使用正确的数据库 URL
DATABASE_URL = "postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a.oregon-postgres.render.com/pku_cycle_db_qre8"

print("=" * 70)
print("测试数据库连接")
print("=" * 70)

try:
    print(f"\n尝试连接：{DATABASE_URL[:50]}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        print(f"✓ 数据库连接成功！测试值：{test_value}")
        
        # 检查 appointments 表
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM appointments"))
            count = result.scalar()
            print(f"✓ Appointments 表存在，数据量：{count}")
        except Exception as e:
            print(f"✗ 查询 appointments 表失败：{e}")
            
        # 检查 users 表
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✓ Users 表存在，数据量：{count}")
        except Exception as e:
            print(f"✗ 查询 users 表失败：{e}")
    
    print("\n" + "=" * 70)
    print("数据库测试完成")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 数据库连接失败：{e}")
    import traceback
    traceback.print_exc()
