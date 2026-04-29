# 同一个用户卖家和买家流程混淆问题修复

## 问题描述

当管理员使用同一个账号既作为卖家又作为买家时，确认时间段后，自行车状态出现混淆：
- 卖家流程确认后，自行车状态变成 `RESERVED`（正确）
- 买家流程确认后，自行车状态也变成 `RESERVED`（❌ 错误，应该是 `SOLD`）

## 根本原因

在 [`time_slots.py`](file:///Users/zhanghong/Documents/Curriculum/Computer Science/Vibe Coding/PKU-Campus-Cycle-Cycle/backend/app/routers/time_slots.py#L380-L431) 的 `confirm_bicycle_time_slot` 函数中，存在以下问题：

### 1. 硬编码预约类型
```python
# ❌ 错误的代码
appointment = Appointment(
    user_id=bicycle.owner_id,
    bicycle_id=bike_id,
    type="drop-off",  # 硬编码为卖家流程
    status=AppointmentStatus.CONFIRMED.value,
    time_slot_id=time_slot.id
)
db.add(appointment)
```

无论实际是什么流程，都创建 `drop-off` 类型的预约，导致买家流程也被当作卖家流程处理。

### 2. 查询逻辑错误
```python
# ❌ 错误的代码
time_slot = db.query(TimeSlot).filter(
    TimeSlot.bicycle_id == bike_id,
    TimeSlot.is_booked == "true"
).first()
```

查询已预订时间段，而不是查询已有的待处理预约。

### 3. 创建新预约而不是更新已有预约
函数创建新的预约记录，而不是更新用户选择时间段时创建的预约。

## 修复方案

### 修改 `confirm_bicycle_time_slot` 函数

**文件**：`backend/app/routers/time_slots.py`

**修复内容**：

1. **查询待处理预约而不是创建新预约**
```python
# ✅ 正确的代码
appointment = db.query(Appointment).filter(
    Appointment.bicycle_id == bike_id,
    Appointment.status == AppointmentStatus.PENDING.value
).first()

if not appointment:
    raise HTTPException(status_code=400, detail="该自行车没有待处理的预约")
```

2. **根据预约类型设置自行车状态**
```python
# ✅ 正确的代码
# drop-off = 卖家流程（卖家送车） -> RESERVED（等待线下交易）
# pick-up = 买家流程（买家取车） -> SOLD（交易完成）
if appointment.type == "drop-off":
    bicycle.status = BicycleStatus.RESERVED.value
elif appointment.type == "pick-up":
    bicycle.status = BicycleStatus.SOLD.value
```

3. **根据预约类型发送不同的通知消息**
```python
# ✅ 正确的代码
if appointment.type == "drop-off":
    content = f"管理员已确认时间段，请按时将自行车送到指定地点。自行车 ID: {bike_id}"
else:
    content = f"管理员已确认时间段，请按时来取车。自行车 ID: {bike_id}"

send_message_to_user(
    db=db,
    sender_id=admin_id,
    receiver_id=appointment.user_id,  # 使用预约用户 ID，而不是自行车所有者 ID
    content=content
)
```

## 测试用例

### 新增测试文件

**文件**：`tests/unit/test_same_user_flow.py`

**测试场景**：

1. **测试 1**：同一个用户的卖家和买家流程完全隔离
   - 管理员作为卖家登记自行车并完成流程
   - 管理员作为买家登记自行车并完成流程
   - 验证卖家流程自行车状态为 `RESERVED`
   - 验证买家流程自行车状态为 `SOLD`

2. **测试 2**：卖家流程确认后自行车状态为 `RESERVED`
   - 创建卖家自行车
   - 提出时间段、选择时间段、确认时间段
   - 验证最终状态为 `RESERVED`

3. **测试 3**：买家流程确认后自行车状态为 `SOLD`
   - 创建买家自行车
   - 审核、提出时间段、选择时间段、确认时间段
   - 验证最终状态为 `SOLD`

### 测试结果

```
tests/unit/test_same_user_flow.py::TestSameUserSellerAndBuyer::test_01_same_user_seller_and_buyer_flow_isolation PASSED [ 33%]
tests/unit/test_same_user_flow.py::TestSameUserSellerAndBuyer::test_02_seller_flow_confirmed_bike_status PASSED [ 66%]
tests/unit/test_same_user_flow.py::TestSameUserSellerAndBuyer::test_03_buyer_flow_confirmed_bike_status PASSED [100%]

tests/unit/test_same_user_flow.py - 3/3 PASSED ✅
tests/unit/test_seller_is_admin.py - 2/2 PASSED ✅
tests/unit/test_notification_system.py - 4/4 PASSED ✅
tests/unit/test_homepage_notifications.py - 4/4 PASSED ✅

总计：13/13 测试通过 ✅
```

## 修改的文件

1. **backend/app/routers/time_slots.py**
   - 修复 `confirm_bicycle_time_slot` 函数
   - 查询待处理预约而不是创建新预约
   - 根据预约类型设置自行车状态
   - 根据预约类型发送不同的通知消息

2. **tests/unit/test_same_user_flow.py** (新增)
   - 测试同一个用户的卖家和买家流程隔离
   - 验证卖家流程确认后状态为 `RESERVED`
   - 验证买家流程确认后状态为 `SOLD`

## 验证流程

### 卖家流程（正确）
```
1. 用户登记自行车 → PENDING_APPROVAL
2. 管理员提出时间段
   → 创建预约：type="drop-off"
   → 创建时间段：appointment_type="pick-up"
3. 用户选择时间段
   → 更新预约的 time_slot_id
4. 管理员确认时间段
   → 查询待处理预约：type="drop-off"
   → 设置自行车状态：RESERVED ✅
   → 发送通知："请按时将自行车送到指定地点"
```

### 买家流程（正确）
```
1. 用户登记自行车 → PENDING_APPROVAL
2. 管理员审核 → IN_STOCK
3. 管理员提出时间段
   → 创建预约：type="pick-up"
   → 创建时间段：appointment_type="drop-off"
4. 用户选择时间段
   → 更新预约的 time_slot_id
5. 管理员确认时间段
   → 查询待处理预约：type="pick-up"
   → 设置自行车状态：SOLD ✅
   → 发送通知："请按时来取车"
```

## 总结

✅ 修复了 `confirm_bicycle_time_slot` 函数硬编码预约类型的问题
✅ 修复了查询逻辑错误，改为查询待处理预约
✅ 修复了创建新预约而不是更新已有预约的问题
✅ 根据预约类型正确设置自行车状态
✅ 根据预约类型发送不同的通知消息
✅ 确保同一个用户的卖家和买家流程完全隔离
✅ 添加了完整的单元测试
✅ 所有测试通过（13/13）

现在同一个用户可以同时进行卖家和买家流程，不会发生混淆！🎉
