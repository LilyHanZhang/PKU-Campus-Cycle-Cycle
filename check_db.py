import psycopg2
from psycopg2.extras import RealDictCursor

# 使用 Render 提供的数据库连接信息
DATABASE_URL = "postgresql://pku_cycle_cycle_db_user:dK9vR2mP4nL7wQ3xT8yB1cF5gH6jM0sA/pku_cycle_cycle_db@pku-cycle-cycle-db.o1.ril._render.com:5432/pku_cycle_cycle_db"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 70)
    print("数据库表结构检查")
    print("=" * 70)
    
    # 检查 appointments 表
    cur.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        ORDER BY ordinal_position;
    """)
    columns = cur.fetchall()
    
    print("\nAppointments 表结构:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 检查是否有 time_slot_id 列
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            AND column_name = 'time_slot_id'
        );
    """)
    has_time_slot = cur.fetchone()
    print(f"\n是否有 time_slot_id 列：{has_time_slot['exists']}")
    
    # 检查 appointments 数据
    cur.execute("SELECT COUNT(*) as count FROM appointments")
    count = cur.fetchone()
    print(f"\nAppointments 表数据量：{count['count']}")
    
    # 如果有数据，查看一条记录
    if count['count'] > 0:
        cur.execute("SELECT * FROM appointments LIMIT 1")
        sample = cur.fetchone()
        print(f"\n示例数据：{sample}")
    
    # 检查所有表
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print("\n所有表:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
