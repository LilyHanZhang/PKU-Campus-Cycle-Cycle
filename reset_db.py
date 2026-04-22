import psycopg2

conn = psycopg2.connect('postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a.oregon-postgres.render.com/pku_cycle_db_qre8')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS reviews CASCADE')
cur.execute('DROP TABLE IF EXISTS likes CASCADE')
cur.execute('DROP TABLE IF EXISTS comments CASCADE')
cur.execute('DROP TABLE IF EXISTS time_slots CASCADE')
cur.execute('DROP TABLE IF EXISTS appointments CASCADE')
cur.execute('DROP TABLE IF EXISTS posts CASCADE')
cur.execute('DROP TABLE IF EXISTS bicycles CASCADE')
cur.execute('DROP TABLE IF EXISTS users CASCADE')
conn.commit()
print('已删除所有旧表')

sql_statements = [
    '''CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        role VARCHAR(20) DEFAULT 'USER',
        student_id VARCHAR(50),
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE bicycles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        owner_id UUID REFERENCES users(id),
        title VARCHAR(200) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        condition INTEGER NOT NULL,
        status VARCHAR(20) DEFAULT 'PENDING_APPROVAL',
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE time_slots (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        bicycle_id UUID REFERENCES bicycles(id),
        appointment_type VARCHAR(20),
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        is_booked VARCHAR(10) DEFAULT 'false',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE appointments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        bicycle_id UUID REFERENCES bicycles(id),
        type VARCHAR(20),
        appointment_time TIMESTAMP,
        status VARCHAR(20) DEFAULT 'PENDING',
        notes TEXT,
        time_slot_id UUID REFERENCES time_slots(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE posts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        author_id UUID REFERENCES users(id),
        title VARCHAR(200) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE comments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
        author_id UUID REFERENCES users(id),
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE likes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE reviews (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        appointment_id UUID REFERENCES appointments(id),
        reviewer_id UUID REFERENCES users(id),
        rating INTEGER,
        content TEXT,
        review_type VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''
]

for sql in sql_statements:
    cur.execute(sql)
    print(f'执行: {sql[:50]}...')

conn.commit()
print('所有表创建成功！')

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
tables = cur.fetchall()
print('现有表:', [t[0] for t in tables])
conn.close()