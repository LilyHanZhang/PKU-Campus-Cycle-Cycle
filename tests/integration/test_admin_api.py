import requests

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

# 先登录获取 token
login_data = {
    "email": "2200017736@stu.pku.edu.cn",
    "password": "pkucycle"
}

print('=' * 70)
print('测试管理后台 API')
print('=' * 70)

try:
    # 登录
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f'\n1. 登录：{r.status_code}')
    
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f'   ✓ 登录成功')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 测试 auth/me
        print(f'\n2. 获取用户信息：', end='')
        r = requests.get(f'{base_url}/auth/me', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f'✓ {r.status_code}')
        else:
            print(f'✗ {r.status_code} - {r.text}')
        
        # 测试 users API
        print(f'\n3. Users API：', end='')
        r = requests.get(f'{base_url}/users/', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f'✓ {r.status_code} - {len(r.json())} 用户')
        else:
            print(f'✗ {r.status_code} - {r.text[:100]}')
        
        # 测试 bicycles API
        print(f'\n4. Bicycles API：', end='')
        r = requests.get(f'{base_url}/bicycles/', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f'✓ {r.status_code} - {len(r.json())} 车辆')
        else:
            print(f'✗ {r.status_code} - {r.text[:100]}')
        
        # 测试 bicycles?status=PENDING_APPROVAL
        print(f'\n5. Pending Bicycles API：', end='')
        r = requests.get(f'{base_url}/bicycles/?status=PENDING_APPROVAL', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f'✓ {r.status_code} - {len(r.json())} 待审核')
        else:
            print(f'✗ {r.status_code} - {r.text[:100]}')
        
        # 测试 appointments API
        print(f'\n6. Appointments API：', end='')
        r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
        if r.status_code == 200:
            print(f'✓ {r.status_code} - {len(r.json())} 预约')
        else:
            print(f'✗ {r.status_code} - {r.text[:200]}')
        
        print('\n' + '=' * 70)
        print('测试完成！')
        print('=' * 70)
    else:
        print(f'✗ 登录失败：{r.json()}')
        
except Exception as e:
    print(f'\n✗ 错误：{e}')
    import traceback
    traceback.print_exc()
