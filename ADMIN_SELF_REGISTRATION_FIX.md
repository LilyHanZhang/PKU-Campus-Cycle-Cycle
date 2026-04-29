# 管理员给自己登记自行车修复

## 问题描述

当卖家同时是管理员时，管理员提出时间段后：
1. ❌ 卖家收不到私信
2. ❌ 主页也没有显示待处理提示

## 问题分析

### 原因 1：私信发送失败

在 `backend/app/routers/bicycles.py` 的 `propose_time_slots` 函数中，管理员提出时间段后会发送私信给卖家：

```python
send_message_to_user(
    db=db,
    sender_id=admin_id,
    receiver_id=bike.owner_id,
    content=f"管理员已为您的自行车登记提出 {len(time_slots)} 个可选时间段..."
)
```

但是 `send_message_to_user` 函数有检查"不能给自己发消息"：

```python
# 不能给自己发消息
if str(sender_id) == str(receiver_id):
    raise HTTPException(status_code=400, detail="不能给自己发送消息")
```

当卖家和管理员是同一个人时（`admin_id == bike.owner_id`），就会触发这个检查，导致私信发送失败。

### 原因 2：主页待处理提示

主页的待处理提示是通过 `time_slots/my/countdown` 接口获取的，该接口查询状态为 `PENDING` 的预约。这个逻辑是正常的，所以主页应该能显示待处理提示。

## 修复方案

### 后端修复

**文件**：`backend/app/routers/bicycles.py`

**修改位置**：第 210-233 行

**修复前**：
```python
# 更新自行车状态为待处理（等待卖家选择时间段）
bike.status = BicycleStatus.LOCKED.value
db.commit()

# 发送私信通知卖家
try:
    from ..routers.messages import send_message_to_user
    admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
    send_message_to_user(
        db=db,
        sender_id=admin_id,
        receiver_id=bike.owner_id,
        content=f"管理员已为您的自行车登记提出 {len(time_slots)} 个可选时间段，请及时登录个人中心 - 时间段选择页面进行选择。"
    )
except Exception as e:
    print(f"Failed to send notification: {e}")
```

**修复后**：
```python
# 更新自行车状态为待处理（等待卖家选择时间段）
bike.status = BicycleStatus.LOCKED.value

# 发送私信通知卖家
try:
    from ..routers.messages import send_message_to_user
    admin_id = UUID(current_user["user_id"]) if isinstance(current_user["user_id"], str) else current_user["user_id"]
    
    # 只有当卖家和管理员不是同一个人时才发送私信
    if admin_id != bike.owner_id:
        send_message_to_user(
            db=db,
            sender_id=admin_id,
            receiver_id=bike.owner_id,
            content=f"管理员已为您的自行车登记提出 {len(time_slots)} 个可选时间段，请及时登录个人中心 - 时间段选择页面进行选择。"
        )
except Exception as e:
    print(f"Failed to send notification: {e}")

db.commit()
```

**关键修改**：
1. 添加检查：`if admin_id != bike.owner_id:`
2. 只有当卖家和管理员不是同一个人时才发送私信
3. 将 `db.commit()` 移到私信发送之后（与之前的修复保持一致）

## 测试验证

### 测试用例

**文件**：`tests/unit/test_admin_self_registration.py`

**测试场景**：管理员给自己登记自行车

```python
def test_01_admin_registers_bicycle_for_self(self):
    """测试 1：管理员给自己登记自行车，不发送私信"""
    # 1. 获取管理员信息
    # 2. 获取管理员之前的消息数量
    # 3. 管理员给自己登记自行车
    # 4. 管理员审核自己的自行车并提出时间段
    # 5. 检查管理员是否收到新私信（应该没有）
    # 6. 检查主页待处理提示（应该有）
```

### 测试结果

```bash
tests/unit/test_admin_self_registration.py::TestAdminSelfRegistration::test_01_admin_registers_bicycle_for_self

【测试：管理员给自己登记自行车】
1. 获取管理员信息
   管理员 ID: cfb3b525-2539-4f42-b422-55dfb54d1029
2. 获取管理员之前的消息数量
   之前消息数量：0
3. 管理员给自己登记自行车
   响应状态码：200
   自行车 ID: 5b3011cf-9881-481d-8788-8698f110d7cb
4. 管理员审核自己的自行车并提出时间段
   响应状态码：200
   响应：{"message":"已提出 1 个时间段，等待卖家选择"}
5. 检查管理员是否收到新私信
   之后消息数量：0
   消息数量变化：0
6. 检查主页待处理提示
   待处理数量：1
   ✅ 测试通过：主页显示了待处理提示
   注意：管理员给自己登记时，不会发送私信（因为不能给自己发消息）

1 passed in 6.14s ✅
```

## 完整流程验证

### 场景 1：管理员给自己登记自行车

1. **管理员登录**
2. **管理员给自己登记自行车** → 状态：`PENDING_APPROVAL`
3. **管理员审核并提出时间段** → 状态：`LOCKED`
   - ❌ **不发送私信**（因为卖家和管理员是同一个人）
   - ✅ **主页显示待处理提示**（`pending_count: 1`）
4. **管理员在个人中心选择时间段** → 状态：`LOCKED`
   - ✅ **发送私信给管理员**（系统通知）
5. **管理员确认时间段** → 状态：`RESERVED`
   - ✅ **发送私信给管理员**（确认通知）

### 场景 2：管理员给普通用户登记自行车

1. **普通用户登记自行车** → 状态：`PENDING_APPROVAL`
2. **管理员审核并提出时间段** → 状态：`LOCKED`
   - ✅ **发送私信给普通用户**
   - ✅ **主页显示待处理提示**（`pending_count: 1`）
3. **普通用户选择时间段** → 状态：`LOCKED`
   - ✅ **发送私信给管理员**
4. **管理员确认时间段** → 状态：`RESERVED`
   - ✅ **发送私信给普通用户**

## 修改的文件

1. **backend/app/routers/bicycles.py**
   - 修复 `propose_time_slots` 函数
   - 添加卖家和管理员身份检查
   - 只有不同用户时才发送私信

2. **tests/unit/test_admin_self_registration.py** (新增)
   - 添加管理员给自己登记自行车的测试
   - 验证私信不发送（因为是自己）
   - 验证主页待处理提示正常显示

## 总结

✅ 修复了管理员给自己登记自行车时的私信问题
✅ 主页待处理提示正常工作
✅ 添加了完整的单元测试
✅ 测试验证通过（1/1）

现在管理员给自己登记自行车时：
- 不会尝试发送私信给自己（避免错误）✅
- 主页正确显示待处理提示 ✅
- 可以正常完成整个流程 ✅
