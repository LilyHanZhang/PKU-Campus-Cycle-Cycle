# 卖家时间段选择显示位置修复

## 问题描述

卖家选择时间段后，在管理后台显示在错误的位置：
- ❌ 出现在"等待确认的预约（买家已选时间段）"列表中
- ❌ 管理后台让管理员"提出时间段"（实际上时间段已经是管理员提出的）
- ❌ 没有显示在"等待确认的自行车（卖家已选时间段）"列表中

## 根本原因

### 问题 1：`waiting_bicycles` 查询逻辑错误

在 [`bicycles.py`](file:///Users/zhanghong/Documents/Curriculum/Computer Science/Vibe Coding/PKU-Campus-Cycle-Cycle/backend/app/routers/bicycles.py#L703-L714) 的 `get_admin_dashboard` 函数中：

```python
# ❌ 错误的代码
# 查询所有 is_booked="true" 的自行车，没有区分卖家和买家流程
locked_bike_ids = db.query(TimeSlot.bicycle_id).filter(
    TimeSlot.is_booked == "true"
).distinct()
```

这个查询**没有区分时间段类型**，导致卖家和买家流程的自行车都出现在 `waiting_bicycles` 列表中。

### 时间段类型区分

- **卖家流程**：
  - 预约类型：`drop-off`（卖家送车）
  - 时间段类型：`pick-up`（管理员从指定地点取车）
  
- **买家流程**：
  - 预约类型：`pick-up`（买家取车）
  - 时间段类型：`drop-off`（管理员送车/买家取车）

## 修复方案

### 修复 1：`waiting_bicycles` 只查询卖家流程

**文件**：`backend/app/routers/bicycles.py`

**修改内容**：

```python
# ✅ 正确的代码
# 获取等待管理员确认的自行车（卖家已选择时间段）
# 查询 LOCKED 状态且有已预订时间段的自行车
# 并且时间段类型是 pick-up（卖家流程的时间段类型）
locked_bike_ids = db.query(TimeSlot.bicycle_id).filter(
    TimeSlot.is_booked == "true",
    TimeSlot.appointment_type == "pick-up"  # 只查询卖家流程的时间段
).distinct()
waiting_bicycles = db.query(Bicycle).filter(
    Bicycle.status == BicycleStatus.LOCKED.value,
    Bicycle.id.in_(locked_bike_ids)
).all()
```

### 修复 2：`waiting_appointments` 只查询买家流程

**文件**：`backend/app/routers/bicycles.py`

**修改内容**：

```python
# ✅ 正确的代码
# 获取待处理的预约（用户已选择时间段，等待管理员确认）
# 只查询买家流程的预约（pick-up = 买家取车，需要管理员确认）
# 卖家流程（drop-off）不需要出现在这里
waiting_appointments = db.query(Appointment).filter(
    Appointment.status == AppointmentStatus.PENDING.value,
    Appointment.time_slot_id != None,
    Appointment.type == "pick-up"  # 只查询买家流程
).all()
```

### 修复 3：区分卖家和买家流程的通知消息

**文件**：`backend/app/routers/time_slots.py`

**修改内容**：

```python
# ✅ 正确的代码
admins = db.query(User).filter(User.role.in_([Role.ADMIN.value, Role.SUPER_ADMIN.value])).all()
for admin in admins:
    if appointment and appointment.type == "drop-off":
        # 卖家流程：通知管理员确认入库
        send_message_to_user(
            db=db,
            sender_id=None,
            receiver_id=admin.id,
            content=f"卖家已选择时间段，请确认入库。自行车 ID: {bike_id}"
        )
    else:
        # 买家流程：通知管理员确认提车
        send_message_to_user(
            db=db,
            sender_id=None,
            receiver_id=admin.id,
            content=f"买家已选择时间段，请确认提车。自行车 ID: {bike_id}"
        )
```

## 时间线对比

### 卖家流程（正确）
```
1. 卖家登记自行车 → PENDING_APPROVAL
2. 管理员审核并提出时间段
   → 创建预约：type="drop-off"
   → 创建时间段：appointment_type="pick-up", is_booked="false"
3. 卖家选择时间段
   → 设置 is_booked="true"
   → 自行车状态：LOCKED
   → 预约状态：PENDING
   → ✅ 出现在 waiting_bicycles 列表中（时间段类型=pick-up）
   → ❌ 不出现在 waiting_appointments 列表中
4. 管理员确认时间段
   → 预约状态：CONFIRMED
   → 自行车状态：RESERVED
   → ✅ 出现在车辆管理（RESERVED 状态，可确认入库）
   → ✅ 出现在预约管理（显示"等待线下交车完成"）
```

### 买家流程（正确）
```
1. 买家登记自行车 → PENDING_APPROVAL
2. 管理员审核 → IN_STOCK
3. 管理员提出时间段
   → 创建预约：type="pick-up"
   → 创建时间段：appointment_type="drop-off", is_booked="false"
4. 买家选择时间段
   → 设置 is_booked="true"
   → 自行车状态：LOCKED
   → 预约状态：PENDING
   → ❌ 不出现在 waiting_bicycles 列表中（时间段类型=drop-off）
   → ✅ 出现在 waiting_appointments 列表中（预约类型=pick-up）
5. 管理员确认时间段
   → 预约状态：CONFIRMED
   → 自行车状态：SOLD
   → ✅ 出现在预约管理（显示"确认提车"按钮）
```

## 测试用例

### 新增测试文件

**文件**：`tests/unit/test_seller_buyer_display_lists.py`

**测试场景**：

1. **测试 1**：卖家选择时间段后出现在 `waiting_bicycles` 列表中
   - 创建卖家流程自行车
   - 提出时间段、选择时间段
   - 验证出现在 `waiting_bicycles` 列表中
   - 验证不出现在 `waiting_appointments` 列表中

2. **测试 2**：买家选择时间段后出现在 `waiting_appointments` 列表中
   - 创建买家流程自行车
   - 审核、提出时间段、选择时间段
   - 验证出现在 `waiting_appointments` 列表中
   - 验证不出现在 `waiting_bicycles` 列表中

3. **测试 3**：管理后台两个列表完全分离
   - 验证同一辆自行车不会同时出现在两个列表中
   - 验证 `waiting_appointments` 中的预约都是 `pick-up` 类型

### 测试结果

```
tests/unit/test_seller_buyer_display_lists.py::TestSellerBuyerDisplayLists::test_01_seller_flow_shows_in_waiting_bicycles PASSED [ 33%]
tests/unit/test_seller_buyer_display_lists.py::TestSellerBuyerDisplayLists::test_02_buyer_flow_shows_in_waiting_appointments PASSED [ 66%]
tests/unit/test_seller_buyer_display_lists.py::TestSellerBuyerDisplayLists::test_03_dashboard_lists_separation PASSED [100%]

tests/unit/test_seller_buyer_display_lists.py - 3/3 PASSED ✅
tests/unit/test_admin_dashboard_display.py - 3/3 PASSED ✅
tests/unit/test_same_user_flow.py - 3/3 PASSED ✅
tests/unit/test_seller_is_admin.py - 2/2 PASSED ✅
tests/unit/test_notification_system.py - 4/4 PASSED ✅

总计：15/15 测试通过 ✅
```

## 修改的文件

1. **backend/app/routers/bicycles.py**
   - 修改 `waiting_bicycles` 查询：添加 `TimeSlot.appointment_type == "pick-up"` 过滤
   - 修改 `waiting_appointments` 查询：添加 `Appointment.type == "pick-up"` 过滤
   - 确保卖家和买家流程显示在正确的列表中

2. **backend/app/routers/time_slots.py**
   - 修改通知消息：区分卖家和买家流程
   - 卖家流程：通知"确认入库"
   - 买家流程：通知"确认提车"

3. **tests/unit/test_seller_buyer_display_lists.py** (新增)
   - 测试卖家流程显示在 `waiting_bicycles` 列表
   - 测试买家流程显示在 `waiting_appointments` 列表
   - 测试两个列表完全分离

## 总结

✅ 修复了 `waiting_bicycles` 查询没有区分时间段类型的问题
✅ 修复了 `waiting_appointments` 查询没有区分预约类型的问题
✅ 卖家选择时间段后显示在"等待确认的自行车（卖家已选时间段）"列表中
✅ 买家选择时间段后显示在"等待确认的预约（买家已选时间段）"列表中
✅ 两个列表完全分离，没有重叠
✅ 区分卖家和买家流程的通知消息
✅ 添加了完整的单元测试
✅ 所有测试通过（15/15）

现在管理后台可以正确区分卖家和买家流程，显示在正确的列表中！🎉
