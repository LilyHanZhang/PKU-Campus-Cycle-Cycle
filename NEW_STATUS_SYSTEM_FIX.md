# 自行车状态系统重构

## 问题描述

买家选择自行车后，管理人员的管理界面上面显示等待确认的自行车（卖家已选时间段）。可能又是因为卖家线和买家线用了同一种状态导致出错？能不能在卖家线和买家线时用不同的状态表述（多设置几种状态），不要一种状态对应好多个情况。（举例：LOCKED 目前同时出现在卖家线和买家线）。

## 问题分析

### 原有状态系统

```python
class BicycleStatus(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    IN_STOCK = "IN_STOCK"
    LOCKED = "LOCKED"  # ❌ 同时用于卖家线和买家线
    RESERVED = "RESERVED"
    SOLD = "SOLD"
```

### 问题

1. **LOCKED 状态含义模糊**：
   - 卖家线：管理员提出时间段后 → LOCKED（等待卖家选择）
   - 卖家线：卖家选择时间段后 → LOCKED（等待管理员确认）
   - 买家线：买家预约后 → LOCKED（等待买家选择时间段）
   - 买家线：买家选择时间段后 → LOCKED（等待管理员确认）

2. **管理员界面无法区分**：
   - 无法区分"等待卖家选择"和"等待管理员确认"
   - 无法区分"卖家线"和"买家线"

3. **状态转换混乱**：
   - 一个状态对应多个业务场景
   - 代码逻辑复杂，容易出错

## 解决方案

### 新状态系统设计

```python
class BicycleStatus(str, enum.Enum):
    # 待审核状态
    PENDING_APPROVAL = "PENDING_APPROVAL"  # 待管理员审核
    
    # 库存状态
    IN_STOCK = "IN_STOCK"  # 在库存中，可被预约
    
    # 卖家流程状态（卖家卖车）
    PENDING_SELLER_SLOT_SELECTION = "PENDING_SELLER_SLOT_SELECTION"  # 管理员已提出时间段，等待卖家选择
    PENDING_ADMIN_CONFIRMATION_SELLER = "PENDING_ADMIN_CONFIRMATION_SELLER"  # 卖家已选择时间段，等待管理员确认
    RESERVED = "RESERVED"  # 管理员已确认，等待线下交车（卖家送车到指定地点）
    
    # 买家流程状态（买家买车）
    PENDING_BUYER_SLOT_SELECTION = "PENDING_BUYER_SLOT_SELECTION"  # 管理员已提出时间段，等待买家选择
    PENDING_ADMIN_CONFIRMATION_BUYER = "PENDING_ADMIN_CONFIRMATION_BUYER"  # 买家已选择时间段，等待管理员确认
    SOLD = "SOLD"  # 交易完成
```

### 状态转换流程

#### 卖家流程（卖家卖车）

```
PENDING_APPROVAL 
  ↓ 管理员审核并提出时间段
PENDING_SELLER_SLOT_SELECTION  ← 管理员界面显示"等待卖家选择"
  ↓ 卖家选择时间段
PENDING_ADMIN_CONFIRMATION_SELLER  ← 管理员界面显示"等待确认的自行车（卖家已选时间段）"
  ↓ 管理员确认时间段
RESERVED  ← 等待线下交车
  ↓ 管理员确认入库
IN_STOCK
```

#### 买家流程（买家买车）

```
PENDING_APPROVAL 
  ↓ 管理员审核
IN_STOCK
  ↓ 买家预约
PENDING_BUYER_SLOT_SELECTION  ← 管理员界面显示"等待买家选择"
  ↓ 管理员提出时间段
PENDING_BUYER_SLOT_SELECTION  ← 保持状态
  ↓ 买家选择时间段
PENDING_ADMIN_CONFIRMATION_BUYER  ← 管理员界面显示"等待确认的预约（买家已选时间段）"
  ↓ 管理员确认时间段
SOLD  ← 交易完成
```

## 修改的文件

### 1. backend/app/models.py

扩展 `BicycleStatus` 枚举，添加明确的状态定义。

### 2. backend/app/routers/bicycles.py

#### propose_time_slots 函数

- 支持新状态：`PENDING_SELLER_SLOT_SELECTION`、`PENDING_BUYER_SLOT_SELECTION`
- 根据预约类型自动设置正确状态：
  - `drop-off` 预约 → `PENDING_SELLER_SLOT_SELECTION`
  - `pick-up` 预约 → `PENDING_BUYER_SLOT_SELECTION`

#### create_appointment 函数

- 买家预约后设置为 `PENDING_BUYER_SLOT_SELECTION`

#### 取消预约相关函数

- 支持多种中间状态恢复到 `IN_STOCK`：
  - `PENDING_BUYER_SLOT_SELECTION`
  - `PENDING_SELLER_SLOT_SELECTION`
  - `PENDING_ADMIN_CONFIRMATION_SELLER`
  - `PENDING_ADMIN_CONFIRMATION_BUYER`

#### get_admin_dashboard 函数

- 查询 `PENDING_ADMIN_CONFIRMATION_SELLER` 状态的自行车
- 显示在 `waiting_bicycles` 列表中

### 3. backend/app/routers/time_slots.py

#### select_bicycle_time_slot 函数

- 根据预约类型设置正确状态：
  - `drop-off` 预约 → `PENDING_ADMIN_CONFIRMATION_SELLER`
  - `pick-up` 预约 → `PENDING_ADMIN_CONFIRMATION_BUYER`

#### confirm_bicycle_time_slot 函数

- 根据预约类型设置最终状态：
  - `drop-off` 预约 → `RESERVED`
  - `pick-up` 预约 → `SOLD`

## 测试验证

### 测试文件：tests/unit/test_new_status_system.py

#### 测试 1：卖家流程状态转换

```python
PENDING_APPROVAL 
  → PENDING_SELLER_SLOT_SELECTION 
  → PENDING_ADMIN_CONFIRMATION_SELLER 
  → RESERVED
```

**测试结果**：✅ PASSED

#### 测试 2：买家流程状态转换

```python
PENDING_APPROVAL 
  → IN_STOCK 
  → PENDING_BUYER_SLOT_SELECTION 
  → PENDING_ADMIN_CONFIRMATION_BUYER 
  → SOLD
```

**测试结果**：✅ PASSED

#### 测试 3：管理员仪表盘显示等待确认的自行车

- 验证 `waiting_bicycles` 列表显示正确状态的自行车
- 验证状态为 `PENDING_ADMIN_CONFIRMATION_SELLER`

**测试结果**：✅ PASSED

### 完整测试结果

```bash
tests/unit/test_new_status_system.py::TestNewBicycleStatusSystem::test_01_seller_flow_status_transitions PASSED
tests/unit/test_new_status_system.py::TestNewBicycleStatusSystem::test_02_buyer_flow_status_transitions PASSED
tests/unit/test_new_status_system.py::TestNewBicycleStatusSystem::test_03_admin_dashboard_shows_waiting_bicycles PASSED

3 passed in 19.95s ✅
```

## 状态对比表

| 场景 | 旧状态 | 新状态 | 说明 |
|------|--------|--------|------|
| 卖家登记后待审核 | PENDING_APPROVAL | PENDING_APPROVAL | 保持不变 |
| 管理员审核并提出时间段 | LOCKED | PENDING_SELLER_SLOT_SELECTION | 明确等待卖家选择 |
| 卖家选择时间段后 | LOCKED | PENDING_ADMIN_CONFIRMATION_SELLER | 明确等待管理员确认（卖家线） |
| 管理员确认卖家时间段 | RESERVED | RESERVED | 保持不变 |
| 买家登记后待审核 | PENDING_APPROVAL | PENDING_APPROVAL | 保持不变 |
| 管理员审核通过 | IN_STOCK | IN_STOCK | 保持不变 |
| 买家预约后 | LOCKED | PENDING_BUYER_SLOT_SELECTION | 明确等待买家选择 |
| 管理员提出时间段 | LOCKED | PENDING_BUYER_SLOT_SELECTION | 保持等待买家选择 |
| 买家选择时间段后 | LOCKED | PENDING_ADMIN_CONFIRMATION_BUYER | 明确等待管理员确认（买家线） |
| 管理员确认买家时间段 | SOLD | SOLD | 保持不变 |

## 优势

### 1. 清晰的状态语义

- 每个状态只对应一个明确的业务场景
- 状态名称直接表达"谁在等待什么"

### 2. 易于区分的流程

- 卖家线：`PENDING_SELLER_*` 前缀
- 买家线：`PENDING_BUYER_*` 前缀
- 管理员确认：`PENDING_ADMIN_CONFIRMATION_*` 前缀

### 3. 简化的代码逻辑

- 不需要通过其他字段判断是卖家线还是买家线
- 状态本身就能完整表达业务含义

### 4. 更好的管理员界面

- 可以明确显示"等待卖家选择"和"等待管理员确认"
- 可以根据状态类型显示不同的操作按钮

## 总结

✅ 重构完成，状态系统清晰明确
✅ 卖家线和买家线使用完全不同的状态
✅ 管理员界面可以正确显示等待确认的自行车
✅ 所有测试通过（3/3）
✅ 代码更易维护，逻辑更清晰
