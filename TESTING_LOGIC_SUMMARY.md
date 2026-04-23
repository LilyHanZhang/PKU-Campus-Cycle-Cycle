# 网站测试逻辑总结

## 测试概述

本文档总结了 PKU Campus Cycle Cycle 网站的完整测试逻辑，包括卖家流程、买家流程、取消流程、消息系统和管理后台。

## 核心业务流程

### 1. 卖家流程（Seller Flow）

**场景**：学生（卖家）将自行车卖给平台

**流程步骤**：

```
用户登记自行车 → 管理员审核 → 用户创建预约 (drop-off) → 管理员提出时间段 → 用户选择时间段 → 管理员确认 → 线下交易 → 管理员入库
```

**状态变化**：
1. `PENDING_APPROVAL` - 用户登记自行车，等待管理员审核
2. `IN_STOCK` - 管理员审核通过，自行车入库
3. 用户创建预约（type: `drop-off`）
4. `LOCKED` - 管理员提出时间段，等待用户选择
5. 用户选择时间段
6. `RESERVED` - 管理员确认时间段，等待线下交易 ⭐
7. `IN_STOCK` - 线下交易完成后，管理员确认入库

**关键 API 端点**：
- `POST /bicycles/` - 用户登记自行车
- `PUT /bicycles/{bike_id}/approve` - 管理员审核
- `POST /appointments/` - 用户创建预约（type: drop-off）
- `POST /bicycles/{bike_id}/propose-slots` - 管理员提出时间段
- `PUT /time_slots/select-bicycle/{bike_id}` - 用户选择时间段
- `POST /bicycles/{bike_id}/confirm` - 管理员确认时间段（状态变为 RESERVED）⭐
- `PUT /bicycles/{bike_id}/store-inventory` - 管理员入库（状态变为 IN_STOCK）

**appointment_type 逻辑**：
- 卖家流程（drop-off 预约）→ appointment_type: `pick-up`（管理员取车）

---

### 2. 买家流程（Buyer Flow）

**场景**：学生（买家）从平台购买自行车

**流程步骤**：

```
管理员创建自行车 → 用户创建预约 (pick-up) → 管理员提出时间段 → 用户选择时间段 → 管理员确认 → 线下交易完成
```

**状态变化**：
1. `IN_STOCK` - 管理员创建并审核自行车
2. 用户创建预约（type: `pick-up`）
3. `LOCKED` - 管理员提出时间段，等待用户选择
4. 用户选择时间段
5. `RESERVED` - 管理员确认时间段，等待线下交易 ⭐
6. `SOLD` - 线下交易完成后，管理员确认交易完成

**关键 API 端点**：
- `POST /bicycles/` - 管理员创建自行车（admin 角色）
- `PUT /bicycles/{bike_id}/approve` - 管理员审核
- `POST /appointments/` - 用户创建预约（type: pick-up）
- `POST /bicycles/{bike_id}/propose-slots` - 管理员提出时间段
- `PUT /time_slots/select-bicycle/{bike_id}` - 用户选择时间段
- `POST /bicycles/{bike_id}/confirm` - 管理员确认时间段（状态变为 RESERVED）⭐
- `PUT /appointments/{apt_id}/confirm-pickup` - 管理员确认取车（状态变为 SOLD）

**appointment_type 逻辑**：
- 买家流程（pick-up 预约）→ appointment_type: `drop-off`（买家来取车）

---

### 3. 取消流程（Cancel Flow）

**用户取消**：
- `POST /bicycles/{bike_id}/cancel` - 用户取消自行车登记
- 条件：自行车状态必须是 `LOCKED` 或 `PENDING_APPROVAL`
- 效果：删除相关时间段，自行车状态恢复为 `IN_STOCK`

**管理员取消**：
- `POST /bicycles/{bike_id}/cancel-by-admin` - 管理员取消自行车登记
- 条件：管理员权限
- 效果：删除自行车和相关时间段

**预约取消**：
- `PUT /appointments/{apt_id}/cancel` - 取消预约
- 条件：预约状态为 `PENDING` 或 `CONFIRMED`
- 效果：释放时间段，自行车状态恢复

---

### 4. 消息系统（Messaging System）

**功能**：
- 用户 ↔ 用户私信
- 用户 ↔ 管理员私信
- 系统自动通知（时间段提醒、交易确认等）

**关键 API 端点**：
- `POST /messages/` - 发送消息
- `GET /messages/` - 获取我的消息（发送和接收）
- `GET /messages/unread` - 获取未读消息数量
- `PUT /messages/{msg_id}/read` - 标记为已读

**Schema 注意事项**：
- `sender_id` 和 `receiver_id` 可能为 `None`（系统消息）
- 使用 `Optional[UUID]` 类型

---

### 5. 管理后台（Admin Dashboard）

**功能模块**：

#### 5.1 待处理事项
- 待审核自行车（PENDING_APPROVAL）
- 待确认预约（用户已选时间段，等待管理员确认）
- 待处理自行车（LOCKED 状态，等待用户选择时间段）

#### 5.2 时间段管理
- 为自行车提出时间段
- 确认用户选择的时间段
- 更改时间段

#### 5.3 交易管理
- 确认交易完成（卖家流程 → RESERVED → IN_STOCK）
- 确认取车完成（买家流程 → SOLD）
- 取消交易

#### 5.4 倒计时提醒
- 显示即将到期的时间段
- 计算剩余时间（秒）

**关键 API 端点**：
- `GET /bicycles/admin/dashboard` - 获取管理后台数据
- `GET /time_slots/my/countdown` - 获取用户的倒计时

**Dashboard 数据结构**：
```json
{
  "pending_bicycles_count": 0,
  "pending_appointments_count": 0,
  "waiting_confirmation_count": 0,
  "pending_bicycles": [...],
  "waiting_appointments": [...],
  "waiting_bicycles": [...],
  "locked_slots_with_countdown": [...]
}
```

---

## 测试脚本

### 单元测试
- 位置：`tests/unit/test_new_features.py`
- 数量：26 个测试用例
- 覆盖范围：
  - 时间段管理（创建、更新、删除）
  - 用户选择时间段
  - 消息系统
  - 完整买卖流程
  - 取消功能
  - 管理后台

### 集成测试
- 位置：`test_complete_api.py`
- 测试内容：
  - 完整的卖家流程
  - 完整的买家流程
  - 取消流程
  - 消息系统
  - 管理后台

### 综合测试
- 位置：`test_final_comprehensive.py`
- 测试内容：
  - revise_detail.md 中描述的所有功能
  - 时间线验证
  - 状态变化验证

---

## 关键验证点

### 1. 状态变化验证
- 卖家流程：`PENDING_APPROVAL` → `IN_STOCK` → `LOCKED` → `RESERVED` → `IN_STOCK`
- 买家流程：`IN_STOCK` → `LOCKED` → `RESERVED` → `SOLD`

### 2. appointment_type 验证
- 卖家流程（drop-off 预约）→ `pick-up`
- 买家流程（pick-up 预约）→ `drop-off`

### 3. 确认端点验证
- 卖家流程：`POST /bicycles/{bike_id}/confirm` → 状态变为 `RESERVED`
- 买家流程：`POST /bicycles/{bike_id}/confirm` → 状态变为 `RESERVED`，然后 `PUT /appointments/{apt_id}/confirm-pickup` → `SOLD`

### 4. 时间段验证
- 管理员提出时间段后，自行车状态变为 `LOCKED`
- 用户选择时间段后，发送通知给管理员
- 管理员确认后，时间段 `is_booked` 变为 `true`

---

## 常见问题与解决方案

### 1. propose-slots 返回 400
**原因**：
- 自行车状态不是 `IN_STOCK`
- 没有待处理的预约

**解决方案**：
- 确保自行车已审核通过
- 确保有 `PENDING` 状态的预约

### 2. 消息系统 UUID 验证错误
**原因**：
- `sender_id` 或 `receiver_id` 为 `None`
- Schema 要求必需字段

**解决方案**：
- 使用 `Optional[UUID]` 类型

### 3. Dashboard 属性错误
**原因**：
- `Bicycle` 模型没有 `time_slot_id` 字段

**解决方案**：
- 通过 `TimeSlot` 查询获取时间段 ID

---

## 测试账号

### 管理员账号
- Email: `2200017736@stu.pku.edu.cn`
- Password: `pkucycle`
- Role: `ADMIN`

### 测试用户
- 动态创建（避免重复）
- Email: `test_{timestamp}@example.com`
- Password: `test123`
- Role: `USER`

---

## 部署环境

### 后端
- URL: `https://pku-campus-cycle-cycle.onrender.com`
- 数据库：PostgreSQL (Render)
- 自动部署：Git push 触发

### 前端
- URL: `https://pku-campus-cycle-cycle.vercel.app`
- 自动部署：Git push 触发

### 环境变量
- `NEXT_PUBLIC_API_URL`: 后端 API 地址
- `DATABASE_URL`: 数据库连接字符串

---

## 测试执行顺序

1. **单元测试** - 验证各个功能模块
   ```bash
   cd backend
   python -m pytest ../tests/unit/test_new_features.py -v
   ```

2. **集成测试** - 验证完整流程
   ```bash
   python test_complete_api.py
   ```

3. **综合测试** - 验证 revise_detail.md 所有功能
   ```bash
   python test_final_comprehensive.py
   ```

4. **手动测试** - 在网站上实际操作验证

---

## 日期
2026-04-23
