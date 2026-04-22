"""
检查并修复数据库表结构
"""
from sqlalchemy import create_engine, inspect, text

# Render 数据库连接字符串
DATABASE_URL = "postgresql://pku_cycle_cycle_db_user:dK9vR2mP4nL7wQ3xT8yB1cF5gH6jM0sA@pku-cycle-cycle-db.o1.ril.render.com:5432/pku_cycle_cycle_db"

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    print("=" * 70)
    print("数据库表检查")
    print("=" * 70)
    
    # 获取所有表
    tables = inspector.get_table_names()
    print(f"\n现有表：{tables}")
    
    # 检查 appointments 表结构
    if 'appointments' in tables:
        print("\nAppointments 表结构:")
        columns = inspector.get_columns('appointments')
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
    else:
        print("\n⚠️ appointments 表不存在！")
    
    # 检查 users 表
    if 'users' in tables:
        print("\nUsers 表结构:")
        columns = inspector.get_columns('users')
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
    
    # 尝试查询 appointments 数据
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM appointments"))
            count = result.scalar()
            print(f"\nAppointments 表数据量：{count}")
        except Exception as e:
            print(f"\n❌ 查询 appointments 失败：{e}")
            
        # 查询 users
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"Users 表数据量：{count}")
        except Exception as e:
            print(f"❌ 查询 users 失败：{e}")
    
    print("\n" + "=" * 70)
    print("✓ 数据库检查完成")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
