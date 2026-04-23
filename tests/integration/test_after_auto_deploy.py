import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("等待自动部署完成并测试")
print("=" * 70)

# 等待 180 秒
print("\n等待部署完成（3 分钟）...")
for i in range(180, 0, -20):
    print(f"剩余 {i} 秒...")
    time.sleep(20)

print("\n开始测试 API...")
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
    
    # 测试管理后台关键 API
    tests = [
        ("Appointments (关键)", f'{base_url}/appointments/'),
        ("Users", f'{base_url}/users/'),
        ("Bicycles", f'{base_url}/bicycles/'),
        ("Pending Bicycles", f'{base_url}/bicycles/?status=PENDING_APPROVAL'),
        ("Time Slots", f'{base_url}/time_slots/'),
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
        print("🎉 所有管理后台 API 测试通过！")
        print("✓ 可以正常使用管理后台了！")
    else:
        print("❌ 部分 API 失败")
    print("=" * 70)
    
    # 运行单元测试
    print("\n运行单元测试...")
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', 'tests/unit/test_api.py', '-v', '--tb=short'],
        capture_output=True, text=True, timeout=60
    )
    
    # 显示测试结果摘要
    lines = result.stdout.split('\n')
    for line in lines[-10:]:
        print(line)
    
except Exception as e:
    print(f"\n✗ 测试失败：{e}")
    import traceback
    traceback.print_exc()
