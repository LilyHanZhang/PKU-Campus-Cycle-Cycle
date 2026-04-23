import requests
import time
import subprocess
import json

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("自动等待部署完成并测试")
print("=" * 70)

# 检查部署状态
def check_deploy_status():
    try:
        result = subprocess.run(
            ['curl', '-H', 'Authorization: Bearer rnd_PikBeUTpV99ai6DBbtI4ubTxeHTu', 
             'https://api.render.com/v1/services/srv-d7gef29j2pic738crt9g/deploys?limit=1'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        if data:
            status = data[0]['deploy']['status']
            commit_id = data[0]['deploy']['commit']['id'][:7]
            print(f"部署状态：{status} (commit: {commit_id})")
            return status
    except Exception as e:
        print(f"检查部署状态失败：{e}")
    return None

# 等待部署完成
print("\n等待部署完成...")
max_wait = 10  # 最多检查 10 次
for i in range(max_wait):
    status = check_deploy_status()
    if status == 'live':
        print("✓ 部署完成！")
        break
    elif status in ['build_in_progress', 'update_in_progress', 'running']:
        print(f"  等待中... ({i+1}/{max_wait})")
        time.sleep(30)
    else:
        print(f"  未知状态：{status}")
        time.sleep(30)
else:
    print("⚠️  等待超时，开始测试...")

# 开始测试
print("\n" + "=" * 70)
print("开始测试 API")
print("=" * 70)

login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}

try:
    # 登录
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f"\n1. 登录：{r.status_code}")
    
    if r.status_code != 200:
        print(f"   ✗ 失败：{r.text}")
        exit(1)
    
    token = r.json()['access_token']
    print(f"   ✓ 成功")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试关键 API
    tests = [
        ("Appointments", f'{base_url}/appointments/'),
        ("Users", f'{base_url}/users/'),
        ("Bicycles", f'{base_url}/bicycles/'),
        ("Pending Bicycles", f'{base_url}/bicycles/?status=PENDING_APPROVAL'),
    ]
    
    all_passed = True
    for name, url in tests:
        print(f"\n{name} API：", end='')
        r = requests.get(url, headers=headers, timeout=10)
        print(f"{r.status_code}", end='')
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f" - {len(data)} 条记录", end='')
            print(" ✓")
        else:
            print(f" ✗ - {r.text[:100]}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有 API 测试通过！管理后台应该可以正常使用了！")
    else:
        print("❌ 部分 API 失败，请检查日志")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ 测试失败：{e}")
    import traceback
    traceback.print_exc()
