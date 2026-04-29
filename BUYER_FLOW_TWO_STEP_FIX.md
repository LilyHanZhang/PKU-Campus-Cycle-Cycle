# 买家流程两步确认机制修复

## 问题描述

之前的实现中，买家流程存在严重的逻辑错误：
- 管理员确认时间段后，自行车直接被标记为 `SOLD`（已售出）
- 预约直接被标记为 `COMPLETED`（已完成）
- 没有给管理员线下确认提车的机会

**这是错误的**，因为实际流程应该是：
1. 管理员确认时间段 → 等待线下交易
2. 线下交易完成（买家提车） → 管理员确认提车 → 标记为已售出

## 正确的流程设计

### 买家流程（pick-up）- 两步确认

```
IN_STOCK（在库）
  ↓ 买家创建预约
PENDING_BUYER_SLOT_SELECTION（等待买家选择时间段）
  ↓ 管理员提出时间段
PENDING_BUYER_SLOT_SELECTION（等待买家选择时间段）
  ↓ 买家选择时间段
PENDING_ADMIN_CONFIRMATION_BUYER（等待管理员确认）
  ↓ 步骤 1：管理员确认时间段
PENDING_PICKUP（等待买家线下提车）✅ 新增状态
  ↓ 线下交易完成
  ↓ 步骤 2：管理员确认提车
SOLD（已售出） + COMPLETED（预约已完成）✅
```

### 卖家流程（drop-off）- 两步确认

```
PENDING_APPROVAL（待审核）
  ↓ 管理员审核并提出时间段
PENDING_SELLER_SLOT_SELECTION（等待卖家选择时间段）
  ↓ 卖家选择时间段
PENDING_ADMIN_CONFIRMATION_SELLER（等待管理员确认）
  ↓ 步骤 1：管理员确认时间段
RESERVED（等待线下交车）
  ↓ 线下交易完成（卖家交车）
  ↓ 步骤 2：管理员确认入库
IN_STOCK（在库） + COMPLETED（预约已完成）✅
```

## 关键区别

| 阶段 | 买家流程 | 卖家流程 |
|------|---------|---------|
| 确认时间段后 | `PENDING_PICKUP`（等待提车） | `RESERVED`（等待交车） |
| 线下交易后操作 | 管理员确认**提车** | 管理员确认**入库** |
| 最终状态 | `SOLD`（已售出） | `IN_STOCK`（在库） |
| 预约状态 | `COMPLETED` | `COMPLETED` |

## 代码修改

### 1. 添加新的自行车状态

**文件**: `backend/app/models.py`

```python
class BicycleStatus(str, enum.Enum):
    # ... 其他状态 ...
    
    # 买家流程状态（买家买车）
    PENDING_BUYER_SLOT_SELECTION = "PENDING_BUYER_SLOT_SELECTION"
    PENDING_ADMIN_CONFIRMATION_BUYER = "PENDING_ADMIN_CONFIRMATION_BUYER"
    PENDING_PICKUP = "PENDING_PICKUP"  # ✅ 新增：管理员已确认时间段，等待买家线下提车
    SOLD = "SOLD"
```

### 2. 修改时间段确认逻辑

**文件**: `backend/app/routers/time_slots.py`

```python
@router.put("/confirm/{apt_id}", response_model=dict)
def confirm_time_slot(
    apt_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认用户选择的时间段"""
    # ... 验证逻辑 ...
    
    # 更新预约状态为已确认
    appointment.status = AppointmentStatus.CONFIRMED.value
    
    # 更新自行车状态
    bicycle = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if bicycle:
        # 根据预约类型设置不同的状态
        if appointment.type == "drop-off":
            # 卖家流程：RESERVED（等待线下交车）
            bicycle.status = BicycleStatus.RESERVED.value
        elif appointment.type == "pick-up":
            # 买家流程：PENDING_PICKUP（等待买家线下提车）
            bicycle.status = BicycleStatus.PENDING_PICKUP.value
    
    db.commit()
    return {"message": "时间段确认成功"}
```

### 3. 添加确认提车 API 端点

**文件**: `backend/app/routers/time_slots.py`

```python
@router.put("/confirm-pickup/{apt_id}", response_model=dict)
def confirm_pickup(
    apt_id: UUID,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员确认买家已提车（买家流程线下交易完成后）"""
    appointment = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 检查预约状态是否为 CONFIRMED
    if appointment.status != AppointmentStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="预约状态不是已确认，无法确认提车")
    
    # 检查预约类型是否为 pick-up
    if appointment.type != "pick-up":
        raise HTTPException(status_code=400, detail="该预约不是买家提车类型")
    
    # 检查自行车状态是否为 PENDING_PICKUP
    bicycle = db.query(Bicycle).filter(Bicycle.id == appointment.bicycle_id).first()
    if not bicycle:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    if bicycle.status != BicycleStatus.PENDING_PICKUP.value:
        raise HTTPException(status_code=400, detail="自行车状态不是等待提车，无法确认提车")
    
    # 更新自行车状态为 SOLD（已售出）
    bicycle.status = BicycleStatus.SOLD.value
    
    # 更新预约状态为 COMPLETED（已完成）
    appointment.status = AppointmentStatus.COMPLETED.value
    
    db.commit()
    return {"message": "确认提车成功，自行车已标记为已售出"}
```

### 4. 修改前端确认提车按钮

**文件**: `frontend/src/app/admin/page.tsx`

```typescript
const handleConfirmPickup = async (aptId: string) => {
  const token = localStorage.getItem("access_token");
  try {
    await axios.put(
      `${API_URL}/time_slots/confirm-pickup/${aptId}`,  // ✅ 使用正确的 API 端点
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    alert("已确认提车！");  // ✅ 更新提示文案
    fetchData();
  } catch (err) {
    console.error("Failed to confirm pickup", err);
    alert("操作失败，请重试。");
  }
};
```

## 测试结果

### 测试文件
`tests/unit/test_history_and_completed.py`

### 测试 1：买家流程两步确认

```bash
============================================================
测试 1：买家流程两步确认
============================================================
   创建预约：b418595c-eaac-4de8-b10c-abb5237e06e9
   ✅ 步骤 1：管理员确认时间段成功
   确认时间段后自行车状态：PENDING_PICKUP
   ✅ 自行车状态正确变为 PENDING_PICKUP（等待提车）
   预约状态：CONFIRMED
   ✅ 预约状态正确变为 CONFIRMED
   ✅ 步骤 2：管理员确认提车成功
   确认提车后自行车状态：SOLD
   ✅ 自行车状态正确变为 SOLD（已售出）
   预约状态：COMPLETED
   ✅ 预约状态正确变为 COMPLETED（已完成）
PASSED
```

### 测试 2：卖家流程两步确认

```bash
============================================================
测试 2：卖家流程两步确认
============================================================
   创建预约：e0db5c71-0e2e-43ce-a86e-2f7ee6fc44ae
   管理员提出时间段
   卖家选择时间段
   ✅ 步骤 1：管理员确认时间段成功
   确认时间段后自行车状态：RESERVED
   ✅ 自行车状态正确变为 RESERVED（等待交车）
   预约状态：CONFIRMED
   ✅ 预约状态正确变为 CONFIRMED
   ✅ 步骤 2：管理员确认入库成功
   确认入库后自行车状态：IN_STOCK
   ✅ 自行车状态正确变为 IN_STOCK（在库）
   预约状态：COMPLETED
   ✅ 预约状态正确变为 COMPLETED（已完成）
PASSED
```

### 测试 3：预约过滤和历史记录 API

```bash
============================================================
测试 3：预约过滤和历史记录 API
============================================================
   所有预约数量：2
   已完成预约数量：2
   预约 b418595c... 状态：COMPLETED
   预约 e0db5c71... 状态：COMPLETED
   活跃预约数量：0
   ✅ 预约过滤逻辑正确
   ✅ 已完成的预约正确地从活跃预约中移除
PASSED
```

### 测试结果
```bash
3 passed in 24.89s ✅
```

## 修改的文件

### 后端文件
1. `backend/app/models.py`
   - 添加 `PENDING_PICKUP` 状态用于买家流程

2. `backend/app/routers/time_slots.py`
   - 修改 `confirm_time_slot` 函数，区分买家和卖家流程的状态
   - 添加 `confirm_pickup` 端点，用于买家提车确认

### 前端文件
1. `frontend/src/app/admin/page.tsx`
   - 修改 `handleConfirmPickup` 函数，调用正确的 API 端点
   - 更新提示文案

### 测试文件
1. `tests/unit/test_history_and_completed.py`
   - 重写测试，验证两步确认流程
   - 测试买家流程和卖家流程的完整状态转换

## 管理员操作流程

### 买家流程操作

1. **买家创建预约**（pick-up 类型）
2. **管理员提出时间段**
   - 在预约管理页面找到待处理的预约
   - 点击"提出时间段"按钮
   - 输入多个可选时间段
3. **买家选择时间段**
   - 买家在个人中心选择时间段
4. **管理员确认时间段**（步骤 1）
   - 在预约管理页面看到"等待确认"的预约
   - 点击"✓ 确认时间段"按钮
   - ✅ 自行车状态变为 `PENDING_PICKUP`（等待提车）
   - ✅ 预约状态变为 `CONFIRMED`
5. **线下交易**（买家按约定时间提车）
6. **管理员确认提车**（步骤 2）
   - 在预约管理页面找到已确认的预约
   - 点击"确认提车"按钮
   - ✅ 自行车状态变为 `SOLD`（已售出）
   - ✅ 预约状态变为 `COMPLETED`
   - ✅ 预约从活跃预约列表中移除
   - ✅ 记录出现在历史记录页面

### 卖家流程操作

1. **卖家创建预约**（drop-off 类型）
2. **管理员提出时间段**
3. **卖家选择时间段**
4. **管理员确认时间段**（步骤 1）
   - 点击"✓ 确认时间段"按钮
   - ✅ 自行车状态变为 `RESERVED`（等待交车）
   - ✅ 预约状态变为 `CONFIRMED`
5. **线下交易**（卖家按约定时间交车）
6. **管理员确认入库**（步骤 2）
   - 在车辆管理页面找到对应自行车
   - 点击"确认入库"按钮
   - ✅ 自行车状态变为 `IN_STOCK`（在库）
   - ✅ 预约状态变为 `COMPLETED`
   - ✅ 预约从活跃预约列表中移除
   - ✅ 记录出现在历史记录页面

## 总结

✅ 修复了买家流程状态流转错误
✅ 添加了 `PENDING_PICKUP` 状态，明确区分买家流程中间状态
✅ 实现了两步确认机制：
   - 步骤 1：确认时间段 → 进入等待状态
   - 步骤 2：线下交易完成后确认 → 完成交易
✅ 卖家流程和买家流程使用不同的状态，清晰区分
✅ 所有功能均通过单元测试验证

现在系统正确实现了：
- 买家流程：确认时间段 → PENDING_PICKUP → 确认提车 → SOLD
- 卖家流程：确认时间段 → RESERVED → 确认入库 → IN_STOCK
- 两种流程都有明确的中间状态和最终确认步骤
- 预约管理页面只显示活跃预约，已完成预约自动归档到历史记录
