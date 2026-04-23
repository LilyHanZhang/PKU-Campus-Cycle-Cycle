import requests

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

# 先登录获取 token
login_data = {
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
}

print('测试认证流程...')
print('=' * 60)

try:
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f'登录状态：{r.status_code}')
    
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f'✓ 登录成功，获取 token')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 测试 auth/me
        r = requests.get(f'{base_url}/auth/me', headers=headers, timeout=10)
        print(f'Auth/me: {r.status_code} - {r.json() if r.status_code == 200 else r.text}')
        
        # 测试 users API
        r = requests.get(f'{base_url}/users/', headers=headers, timeout=10)
        print(f'Users API: {r.status_code} - {len(r.json())} items')
        
        # 测试 bicycles API
        r = requests.get(f'{base_url}/bicycles/', headers=headers, timeout=10)
        print(f'Bicycles API: {r.status_code} - {len(r.json())} items')
        
        # 测试 appointments API
        print('\n测试 appointments API...')
        r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
        print(f'Appointments API 状态码：{r.status_code}')
        if r.status_code == 200:
            print(f'✓ 成功！返回 {len(r.json())} 条记录')
        else:
            print(f'✗ 失败：{r.text[:500]}')
            
        # 测试 appointments/user/{id}
        user_id = r.json()[0]['user_id'] if r.json() else None
        if user_id:
            print(f'\n测试 appointments/user/{user_id}...')
            r = requests.get(f'{base_url}/appointments/user/{user_id}', headers=headers, timeout=10)
            print(f'User appointments API: {r.status_code}')
            if r.status_code == 200:
                print(f'✓ 成功！返回 {len(r.json())} 条记录')
            else:
                print(f'✗ 失败：{r.text[:500]}')
    else:
        print(f'✗ 登录失败：{r.json()}')
        
except Exception as e:
    print(f'✗ 错误：{e}')
    import traceback
    traceback.print_exc()
