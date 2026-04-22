import requests

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print('测试后端服务状态...')
print('=' * 50)

# 测试健康检查
try:
    r = requests.get(f'{base_url}/health', timeout=10)
    print(f'✓ Health check: {r.status_code} - {r.json()}')
except Exception as e:
    print(f'✗ Health check failed: {e}')

# 测试 bicycles API（公开）
try:
    r = requests.get(f'{base_url}/bicycles/', timeout=10)
    print(f'✓ Bicycles API: {r.status_code} - {len(r.json())} items')
except Exception as e:
    print(f'✗ Bicycles API failed: {e}')

# 测试 appointments API（需要认证）
try:
    r = requests.get(f'{base_url}/appointments/', timeout=10)
    print(f'✓ Appointments API: {r.status_code}')
    if r.status_code != 200:
        print(f'  Response: {r.json()}')
except Exception as e:
    print(f'✗ Appointments API failed: {e}')
