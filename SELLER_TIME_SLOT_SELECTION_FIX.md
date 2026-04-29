# 卖家时间段选择模块修复

## 问题描述

管理员提出时间段后，卖家无法在"我的时间段选择"模块中选择时间段（看不到相应的车辆）。

## 问题分析

在重构状态系统后，自行车的状态从 `LOCKED` 改为更明确的状态：
- `PENDING_SELLER_SLOT_SELECTION`：管理员已提出时间段，等待卖家选择
- `PENDING_BUYER_SLOT_SELECTION`：管理员已提出时间段，等待买家选择

但是前端页面仍在使用旧的 `LOCKED` 状态进行过滤和显示，导致卖家无法看到自行车。

## 修复方案

### 1. 前端过滤逻辑修复

**文件**：`frontend/src/app/my-time-slots/page.tsx`

**修复前**：
```typescript
const myBikes = bikesResponse.data.filter((b: any) => 
  String(b.owner_id) === user.id && 
  (b.status === 'LOCKED' || b.status === 'PENDING_APPROVAL')
);
```

**修复后**：
```typescript
const myBikes = bikesResponse.data.filter((b: any) => 
  String(b.owner_id) === user.id && 
  (b.status === 'PENDING_SELLER_SLOT_SELECTION' || b.status === 'PENDING_APPROVAL')
);
```

### 2. 前端状态显示修复

**文件**：`frontend/src/app/my-time-slots/page.tsx`

修复状态显示逻辑：
```typescript
// 状态显示
状态：{bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '待选择时间段' : '待审核'}

// 标签显示
{bike.status === 'PENDING_SELLER_SLOT_SELECTION' && (
  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
    请选择时间段
  </span>
)}

// 无时间段提示
) : bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? (
  <div className="text-center py-4 text-gray-500">
    <AlertCircle className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
    <p>管理员还未提出时间段，请耐心等待</p>
  </div>
) : null}
```

### 3. 管理员页面状态显示修复

**文件**：`frontend/src/app/admin/page.tsx`

更新状态显示，区分卖家线和买家线：
```typescript
状态：{
  bike.status === 'PENDING_APPROVAL' ? '待审核' :
  bike.status === 'IN_STOCK' ? '在库' :
  bike.status === 'PENDING_SELLER_SLOT_SELECTION' ? '等待卖家选择' :
  bike.status === 'PENDING_BUYER_SLOT_SELECTION' ? '等待买家选择' :
  bike.status === 'PENDING_ADMIN_CONFIRMATION_SELLER' ? '等待管理员确认（卖家）' :
  bike.status === 'PENDING_ADMIN_CONFIRMATION_BUYER' ? '等待管理员确认（买家）' :
  bike.status === 'RESERVED' ? '已预约' : '已售出'
}
```

更新状态标签颜色：
```typescript
className={`px-3 py-1 text-xs font-bold rounded-full ${
  bike.status === 'IN_STOCK' ? 'bg-green-100 text-green-700' :
  bike.status === 'PENDING_APPROVAL' ? 'bg-yellow-100 text-yellow-700' :
  bike.status === 'PENDING_SELLER_SLOT_SELECTION' || bike.status === 'PENDING_BUYER_SLOT_SELECTION' ? 'bg-orange-100 text-orange-700' :
  bike.status === 'PENDING_ADMIN_CONFIRMATION_SELLER' || bike.status === 'PENDING_ADMIN_CONFIRMATION_BUYER' ? 'bg-purple-100 text-purple-700' :
  bike.status === 'RESERVED' ? 'bg-blue-100 text-blue-700' :
  'bg-gray-200 text-gray-600'
}`}
```

## 测试验证

### 测试文件：`tests/unit/test_seller_time_slot_selection.py`

**测试场景**：
1. 管理员登记自行车
2. 管理员审核并提出时间段
3. 验证自行车状态为 `PENDING_SELLER_SLOT_SELECTION`
4. 卖家查看所有自行车，验证能过滤出目标自行车
5. 卖家查看时间段列表
6. 卖家选择时间段
7. 验证自行车状态变为 `PENDING_ADMIN_CONFIRMATION_SELLER`

### 测试结果

```bash
tests/unit/test_seller_time_slot_selection.py::TestSellerCanSeeTimeSlots::test_01_seller_can_see_bicycles_for_time_slot_selection

============================================================
测试卖家可以看到并选择时间段
============================================================

【步骤 1】管理员给自己登记自行车
   自行车 ID: 2de282a4-9d9f-46bf-9f36-b69978d447d6

【步骤 2】管理员审核并提出时间段
   提出时间段响应：已提出 2 个时间段，等待卖家选择
   自行车状态：PENDING_SELLER_SLOT_SELECTION

【步骤 3】获取所有自行车（模拟前端请求）
   所有自行车数量：1
   PENDING_SELLER_SLOT_SELECTION 状态的自行车：1
   ✅ 找到了测试自行车：2de282a4-9d9f-46bf-9f36-b69978d447d6

【步骤 4】获取自行车的时间段
   时间段数量：2
   时间段 1: 2026-05-01T06:46:01.075692 - 2026-05-01T08:46:01.075720
   时间段 2: 2026-05-01T10:46:01.075725 - 2026-05-01T12:46:01.075728

【步骤 5】卖家选择时间段
   选择响应：时间段选择成功，等待管理员确认
   选择后状态：PENDING_ADMIN_CONFIRMATION_SELLER
   剩余时间段数量：1

✅ 测试通过：卖家可以成功看到并选择时间段

1 passed in 7.59s ✅
```

## 修改的文件

1. **frontend/src/app/my-time-slots/page.tsx**
   - 更新过滤逻辑使用 `PENDING_SELLER_SLOT_SELECTION`
   - 更新状态显示逻辑
   - 更新无时间段提示逻辑

2. **frontend/src/app/admin/page.tsx**
   - 更新状态显示，区分卖家线和买家线
   - 更新状态标签颜色

3. **tests/unit/test_seller_time_slot_selection.py** (新增)
   - 添加卖家时间段选择功能测试

## 状态对比

| 场景 | 旧状态 | 新状态 | 前端显示 |
|------|--------|--------|----------|
| 管理员提出时间段后 | LOCKED | PENDING_SELLER_SLOT_SELECTION | 待选择时间段 |
| 卖家选择时间段后 | LOCKED | PENDING_ADMIN_CONFIRMATION_SELLER | (不在该页面显示) |
| 买家预约后 | LOCKED | PENDING_BUYER_SLOT_SELECTION | 等待买家选择 |
| 买家选择时间段后 | LOCKED | PENDING_ADMIN_CONFIRMATION_BUYER | (不在该页面显示) |

## 总结

✅ 修复了前端过滤逻辑，使用新的状态系统
✅ 更新了状态显示，更清晰明确
✅ 管理员页面可以区分卖家线和买家线
✅ 添加了完整的测试用例
✅ 测试验证通过（1/1）

现在卖家可以：
- ✅ 在"我的时间段选择"模块中看到 `PENDING_SELLER_SLOT_SELECTION` 状态的自行车
- ✅ 查看管理员提出的所有可选时间段
- ✅ 选择其中一个时间段
- ✅ 选择后状态正确变为 `PENDING_ADMIN_CONFIRMATION_SELLER`

问题已完全修复！🎉
