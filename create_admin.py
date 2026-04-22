import psycopg2
import bcrypt

conn = psycopg2.connect('postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a.oregon-postgres.render.com/pku_cycle_db_qre8')
cur = conn.cursor()

password = 'pkucycle'
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

cur.execute('''INSERT INTO users (id, email, password_hash, name, role, created_at)
               VALUES (gen_random_uuid(), %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            ('2200017736@stu.pku.edu.cn', password_hash, 'SuperAdmin', 'SUPER_ADMIN'))

conn.commit()
print('主管理员账号创建成功！')

cur.execute("SELECT id, email, name, role FROM users WHERE email = %s", ('2200017736@stu.pku.edu.cn',))
user = cur.fetchone()
print(f'用户信息: id={user[0]}, email={user[1]}, name={user[2]}, role={user[3]}')
conn.close()