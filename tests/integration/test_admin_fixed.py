import requests

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print('=' * 70)
print('测试管理后台 API')
print('=' * 70)

try:
    # 登录
    login_data = {
        "email": "2200017736@stu.pku.edu.cn",
        "password": "pkucycle"
    }
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f'\n1. 登录：{r.status_code}')
    
    if r.status_code != 200:
        print(f'✗ 登录失败：{r.text}')
        exit(1)
        
    token = r.json()['access_token']
    print(f'   ✓ 登录成功')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试 auth/me
    print(f'\n2. 获取用户信息：', end='')
    r = requests.get(f'{base_url}/auth/me', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'✓ {r.status_code}')
    else:
        print(f'✗ {r.status_code} - {r.text[:100]}')
    
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
    
    # 测试 appointments API - 这是管理后台出错的地方
    print(f'\n6. Appointments API（关键）：', end='')
    r = requests.get(f'{base_url}/appointments/', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'✓ {r.status_code} - {len(r.json())} 预约')
        print('\n' + '=' * 70)
        print('✓ 所有 API 测试通过！管理后台应该可以正常加载数据了')
        print('=' * 70)
    else:
        print(f'✗ {r.status_code}')
        print(f'   错误信息：{r.text[:200]}')
        print('\n' + '=' * 70)
        print('✗ Appointments API 失败，请检查后端日志')
        print('=' * 70)
        
except Exception as e:
    print(f'\n✗ 错误：{e}')
    import traceback
    traceback.print_exc()
