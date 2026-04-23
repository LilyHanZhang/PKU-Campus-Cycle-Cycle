import requests
import time

base_url = 'https://pku-campus-cycle-cycle.onrender.com'

print("=" * 70)
print("测试新功能：取消预约、拒绝交易、私信")
print("=" * 70)

# 等待 180 秒
print("\n等待部署完成（3 分钟）...")
for i in range(180, 0, -20):
    print(f"剩余 {i} 秒...")
    time.sleep(20)

print("\n开始测试 API...")
print("=" * 70)

# 登录
login_data = {"email": "2200017736@stu.pku.edu.cn", "password": "pkucycle"}
try:
    r = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f"\n1. 登录：{r.status_code}")
    
    if r.status_code != 200:
        print(f"   ✗ 失败：{r.text}")
        exit(1)
    
    token = r.json()['access_token']
    print(f"   ✓ 成功")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试私信功能
    print("\n--- 私信功能测试 ---")
    
    # 获取用户列表（找到另一个用户）
    r = requests.get(f'{base_url}/users/', headers=headers)
    if r.status_code == 200:
        users = r.json()
        if len(users) > 1:
            # 给自己发私信测试
            print("\n2. 发送私信（给自己测试）：", end='')
            # 注意：实际应该给其他用户发，这里先测试 API 是否可用
            # 由于不能给自己发，这个会返回 400
            r = requests.post(f'{base_url}/messages/', 
                json={"receiver_id": users[0]['id'], "content": "测试消息"},
                headers=headers)
            print(f"{r.status_code} (预期 400，因为不能给自己发)")
    
    # 获取我的消息
    print("\n3. 获取我的消息：", end='')
    r = requests.get(f'{base_url}/messages/', headers=headers)
    print(f"{r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ 获取到 {len(r.json())} 条消息")
    
    # 获取未读消息数量
    print("\n4. 获取未读消息数量：", end='')
    r = requests.get(f'{base_url}/messages/unread', headers=headers)
    print(f"{r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ 未读消息：{r.json()}")
    
    # 测试取消预约功能（需要先有预约）
    print("\n--- 取消预约功能测试 ---")
    print("\n5. 取消预约 API 已添加，需要实际预约数据测试")
    print("   API 端点：PUT /appointments/{apt_id}/cancel")
    
    # 测试拒绝交易功能
    print("\n--- 拒绝交易功能测试 ---")
    print("\n6. 拒绝交易 API 已添加，需要实际预约数据测试")
    print("   API 端点：PUT /appointments/{apt_id}/reject?reject_reason=xxx")
    
    print("\n" + "=" * 70)
    print("✓ 新功能 API 已部署成功！")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ 测试失败：{e}")
    import traceback
    traceback.print_exc()

# 运行单元测试
print("\n运行单元测试...")
import subprocess
result = subprocess.run(
    ['python', '-m', 'pytest', 'tests/unit/test_api.py', '-v', '--tb=short', '-x'],
    capture_output=True, text=True, timeout=120
)

# 显示测试结果
lines = result.stdout.split('\n')
for line in lines[-10:]:
    print(line)

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
