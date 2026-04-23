import requests
import traceback

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

login_data = {
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
}

print('详细测试 appointments API...')
print('=' * 70)

try:
    # 登录
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试 appointments API
    print('发送请求到：GET /appointments/')
    r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
    
    print(f'状态码：{r.status_code}')
    print(f'响应头：{dict(r.headers)}')
    print(f'响应内容：{r.text[:500]}')
    
    if r.status_code == 500:
        print('\n服务器内部错误！可能是：')
        print('1. 数据库连接问题')
        print('2. 代码序列化错误')
        print('3. 缺少依赖包')
        
except Exception as e:
    print(f'错误：{e}')
    traceback.print_exc()
