import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("等待自动部署完成并测试所有功能")
print("=" * 70)

# 等待 180 秒
print("\n等待部署完成（3 分钟）...")
for i in range(180, 0, -20):
    print(f"剩余 {i} 秒...")
    time.sleep(20)

print("\n开始测试 API...")
print("=" * 70)

# 测试函数
def test_api(name, method, url, **kwargs):
    try:
        response = getattr(requests, method)(url, **kwargs)
        print(f"{name}: {response.status_code}", end='')
        if response.status_code == 200:
            print(" ✓")
            return True, response
        else:
            print(f" ✗ - {response.text[:100]}")
            return False, response
    except Exception as e:
        print(f" ✗ - {e}")
        return False, None

# 登录
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
success, resp = test_api("登录", "post", f'{base_url}/auth/login', json=login_data)
if not success:
    print("登录失败，退出测试")
    exit(1)

token = resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 测试管理后台 API
print("\n--- 管理后台 API 测试 ---")
tests = [
    ("Appointments", "get", f'{base_url}/appointments/', {'headers': headers}),
    ("Users", "get", f'{base_url}/users/', {'headers': headers}),
    ("Bicycles", "get", f'{base_url}/bicycles/', {'headers': headers}),
    ("Pending Bicycles", "get", f'{base_url}/bicycles/?status=PENDING_APPROVAL', {'headers': headers}),
    ("Time Slots", "get", f'{base_url}/time_slots/', {'headers': headers}),
]

all_passed = True
for name, method, url, kwargs in tests:
    success, _ = test_api(name, method, url, **kwargs)
    if not success:
        all_passed = False

# 测试论坛 API
print("\n--- 论坛 API 测试 ---")

# 创建测试帖子
success, post_resp = test_api("创建帖子", "post", f'{base_url}/posts/', 
    json={"title": "测试帖子", "content": "这是测试内容"}, 
    headers=headers)

if success:
    post_id = post_resp.json()['id']
    
    # 测试评论
    success, comment_resp = test_api("创建评论", "post", f'{base_url}/posts/{post_id}/comments',
        json={"content": "测试评论"},
        headers=headers)
    
    if success:
        comment_id = comment_resp.json()['id']
        
        # 测试删除评论
        success, _ = test_api("删除评论", "delete", f'{base_url}/posts/{post_id}/comments/{comment_id}',
            headers=headers)
    
    # 测试获取评论列表
    success, _ = test_api("获取评论列表", "get", f'{base_url}/posts/{post_id}/comments',
        headers=headers)
    
    # 测试删除帖子
    success, _ = test_api("删除帖子", "delete", f'{base_url}/posts/{post_id}',
        headers=headers)

# 测试预约流程
print("\n--- 预约流程测试 ---")

# 1. 创建预约
success, apt_resp = test_api("创建预约", "post", f'{base_url}/appointments/',
    json={"bicycle_id": "00000000-0000-0000-0000-000000000000", "type": "pick-up"},
    headers=headers)

# 2. 创建时间段（需要管理员）
success, _ = test_api("创建时间段", "post", f'{base_url}/time_slots/',
    json={
        "bicycle_id": "00000000-0000-0000-0000-000000000000",
        "appointment_type": "pick-up",
        "start_time": "2024-12-01T10:00:00",
        "end_time": "2024-12-01T11:00:00"
    },
    headers=headers)

print("\n" + "=" * 70)
if all_passed:
    print("🎉 管理后台 API 全部通过！")
else:
    print("⚠️  部分 API 失败，请检查")
print("=" * 70)

# 运行单元测试
print("\n运行单元测试...")
import subprocess
result = subprocess.run(
    ['python', '-m', 'pytest', 'tests/unit/test_api.py', '-v', '--tb=short', '-x'],
    capture_output=True, text=True, timeout=120
)

# 显示测试结果
lines = result.stdout.split('\n')
for line in lines[-15:]:
    print(line)

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
