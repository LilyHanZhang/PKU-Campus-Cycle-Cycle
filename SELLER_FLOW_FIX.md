# 卖家流程修复：管理员提出时间段

## 问题描述

当卖家登记自行车后（状态为 `PENDING_APPROVAL`），管理员想要提出时间段时，系统报错：
```
操作失败：自行车状态不正确，需要先审核通过
```

但审核通过应该是在提出时间段之后，用户确认时间段，线下交易之后才进行的操作。

## 正确的卖家流程

1. **卖家登记自行车** → 状态：`PENDING_APPROVAL`（待审核）
2. **管理员创建预约** → 创建 `drop-off` 类型预约
3. **管理员提出时间段** → 自动审核通过，状态变为 `LOCKED`
4. **卖家选择时间段** → 状态：`LOCKED`（已锁定）
5. **管理员确认预约** → 状态：`RESERVED`（已预约）
6. **线下交易完成** → 卖家将自行车送到，管理员取车
7. **管理员确认交易** → 状态：`SOLD`（已售）

## 代码修改

### 文件：`backend/app/routers/bicycles.py`

修改了 `propose_time_slots` 函数，支持为 `PENDING_APPROVAL` 状态的自行车提出时间段：

```python
@router.post("/{bike_id}/propose-slots", response_model=dict)
def propose_time_slots(
    bike_id: UUID,
    time_slots: List[dict],
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """管理员为自行车提出时间段（支持卖家和买家场景）"""
    bike = db.query(Bicycle).filter(Bicycle.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="自行车不存在")
    
    # 自行车状态可以是：
    # 1. PENDING_APPROVAL - 卖家登记后，管理员先审核通过再提出时间段
    # 2. IN_STOCK - 已审核通过的自行车
    # 3. LOCKED - 有预约的自行车
    if bike.status not in [BicycleStatus.PENDING_APPROVAL.value, BicycleStatus.IN_STOCK.value, BicycleStatus.LOCKED.value]:
        raise HTTPException(status_code=400, detail="自行车状态不正确")
    
    # 如果是 PENDING_APPROVAL 状态，先审核通过
    if bike.status == BicycleStatus.PENDING_APPROVAL.value:
        bike.status = BicycleStatus.IN_STOCK.value
    
    # ... 后续代码 ...
```

### 关键改动

1. **扩展支持的状态**：从 `[IN_STOCK, LOCKED]` 扩展到 `[PENDING_APPROVAL, IN_STOCK, LOCKED]`
2. **自动审核通过**：当自行车状态为 `PENDING_APPROVAL` 时，自动将其状态更新为 `IN_STOCK`
3. **添加详细注释**：说明支持的三种状态及其场景

## 单元测试

### 测试文件：`tests/unit/test_seller_propose_slots_final.py`

包含三个测试用例：

1. **test_propose_slots_for_pending_bicycle**
   - 测试为 PENDING_APPROVAL 状态的自行车提出时间段
   - 验证自行车状态自动变为 LOCKED

2. **test_propose_slots_requires_appointment**
   - 测试没有预约时提出时间段应该失败
   - 验证错误信息："没有待处理的预约"

3. **test_propose_slots_creates_correct_appointment_type**
   - 测试 drop-off 预约创建 pick-up 时间段
   - 验证时间段类型正确

### 运行测试

```bash
cd backend
python -m pytest ../tests/unit/test_seller_propose_slots_final.py -v -s
```

### 测试结果

```
======================== 3 passed, 3 warnings in 11.28s ========================
```

✅ 所有测试通过

## 测试流程总结

```
1. ✅ 卖家登记自行车（PENDING_APPROVAL）
2. ✅ 创建 drop-off 类型预约
3. ✅ 管理员提出时间段（自动审核通过）
4. ✅ 自行车状态变为 LOCKED
5. ✅ 验证时间段类型正确（pick-up）
```

## 相关文件

- 后端代码：`backend/app/routers/bicycles.py`
- 单元测试：`tests/unit/test_seller_propose_slots_final.py`
- 模型定义：`backend/app/models.py`

## 部署

代码已提交并推送到 GitHub，自动部署到 Render。

```bash
git add backend/app/routers/bicycles.py
git commit -m "fix: 允许为 PENDING_APPROVAL 状态的自行车提出时间段"
git push origin main
```

## 注意事项

1. **审核时机**：管理员提出时间段时自动审核通过，简化了操作流程
2. **状态流转**：PENDING_APPROVAL → IN_STOCK → LOCKED → RESERVED → SOLD
3. **预约类型**：
   - `drop-off`（卖家流程）：卖家送车，管理员取车
   - `pick-up`（买家流程）：买家取车，管理员交车
4. **时间段类型**：与预约类型相反
   - drop-off 预约 → pick-up 时间段
   - pick-up 预约 → drop-off 时间段
