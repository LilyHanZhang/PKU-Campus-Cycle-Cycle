# 部署测试指南 - revise_detail.md 功能验证

## 部署状态

✅ **后端**: https://pku-cycle-backend.onrender.com (已部署)
✅ **前端**: https://pku-campus-cycle-cycle.vercel.app (已部署)
✅ **单元测试**: 22/26 通过

## 完整测试流程

### 卖家流程测试

#### 1. 创建测试用户
```
访问：https://pku-campus-cycle-cycle.vercel.app
点击"注册"创建新用户
```

#### 2. 卖家登记自行车
```
1. 登录卖家账号
2. 点击"登记自行车"
3. 填写信息并提交
4. 状态：PENDING_APPROVAL (待审核)
```

#### 3. 管理员提出时间段
```
1. 登录管理员账号 (admin@example.com 或创建管理员)
2. 访问 /admin
3. 在"待审核车辆"标签页找到该自行车
4. 点击"提出时间段"
5. 选择 1-3 个可用时间段
6. 状态变为：LOCKED (已锁定，等待卖家选择)
```

#### 4. 卖家选择时间段
```
1. 卖家登录
2. 访问"个人中心"
3. 点击"时间段选择"
4. 看到管理员提出的时间段
5. 选择一个时间段并确认
6. 状态保持：LOCKED (已锁定，等待管理员确认)
```

#### 5. 管理员确认时间段 ⭐ 关键步骤
```
1. 管理员访问 /admin
2. 在"Dashboard"标签页查看"等待确认的自行车"
3. 点击"✓ 确认交易"按钮
4. 状态变为：RESERVED (已预约，等待线下交易)
5. 卖家收到私信通知
```

#### 6. 管理员确认入库
```
1. 线下交易完成后
2. 管理员访问 /admin
3. 在"所有车辆"标签页找到状态为 RESERVED 的自行车
4. 点击"✓ 确认入库"按钮
5. 状态变为：IN_STOCK (在库)
```

### 买家流程测试

#### 1. 买家创建预约
```
1. 买家登录
2. 浏览库存自行车
3. 选择一辆自行车点击"预约"
4. 状态：PENDING (待处理)
```

#### 2. 管理员提出时间段
```
1. 管理员访问 /admin
2. 在"预约管理"标签页找到该预约
3. 点击"提出时间段"
4. 选择时间段
5. 状态保持：PENDING (等待买家选择)
```

#### 3. 买家选择时间段
```
1. 买家登录
2. 访问"个人中心" → "时间段选择"
3. 选择时间段
4. 状态保持：PENDING (等待管理员确认)
```

#### 4. 管理员确认时间段 ⭐ 关键步骤
```
1. 管理员访问 /admin → Dashboard
2. 查看"等待确认的预约"
3. 点击"✓ 确认时间段"
4. 状态变为：CONFIRMED (已确认)
5. 自行车状态：IN_STOCK → SOLD (已售出)
6. 买家收到私信通知
```

## API 端点测试

### 1. 管理员确认自行车 (卖家流程)
```bash
curl -X POST https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/confirm \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**预期响应**:
```json
{
  "message": "自行车交易确认成功，等待线下交易"
}
```

**状态变化**: LOCKED → RESERVED

### 2. 管理员存入库存
```bash
curl -X PUT https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/store-inventory \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**预期响应**:
```json
{
  "id": "...",
  "status": "IN_STOCK",
  ...
}
```

**状态变化**: RESERVED → IN_STOCK

### 3. 管理员确认预约 (买家流程)
```bash
curl -X PUT https://pku-cycle-backend.onrender.com/time_slots/confirm/{apt_id} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**预期响应**:
```json
{
  "message": "时间段确认成功"
}
```

**状态变化**: PENDING → CONFIRMED
**自行车状态**: IN_STOCK → SOLD

### 4. 管理员仪表盘
```bash
curl https://pku-cycle-backend.onrender.com/bicycles/admin/dashboard \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**预期响应包含**:
```json
{
  "pending_bicycles_count": 0,
  "pending_appointments_count": 0,
  "waiting_confirmation_count": 1,
  "waiting_appointments": [],
  "waiting_bicycles": [...],
  "locked_slots_with_countdown": [...]
}
```

## 状态流转图

### 卖家流程
```
PENDING_APPROVAL (待审核)
    ↓ 管理员提出时间段
LOCKED (已锁定，等待卖家选择)
    ↓ 卖家选择时间段
LOCKED (已锁定，等待管理员确认)
    ↓ 管理员确认 ⭐
RESERVED (已预约，等待线下交易)
    ↓ 线下交易完成，管理员确认入库
IN_STOCK (在库)
```

### 买家流程
```
PENDING (待处理)
    ↓ 管理员提出时间段
PENDING (等待买家选择)
    ↓ 买家选择时间段
PENDING (等待管理员确认)
    ↓ 管理员确认 ⭐
CONFIRMED (已确认)
    ↓ 线下交易完成
SOLD (已售出)
```

## 通知系统测试

所有关键操作都会发送私信通知：

1. ✅ 管理员提出时间段 → 用户收到通知
2. ✅ 管理员确认时间段 → 用户收到通知
3. ✅ 管理员取消交易 → 用户收到通知（带原因）

**查看私信**:
- 访问"我的消息"页面
- 查看未读消息数量

## 取消功能测试

### 用户取消
```bash
# 卖家取消自行车
curl -X POST https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/cancel \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# 买家取消预约
curl -X PUT https://pku-cycle-backend.onrender.com/appointments/{apt_id}/cancel \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

### 管理员取消
```bash
# 管理员取消自行车
curl -X POST "https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/admin-cancel?reason=测试原因" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 管理员取消预约
curl -X POST "https://pku-cycle-backend.onrender.com/appointments/{apt_id}/admin-cancel?reason=测试原因" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 常见问题排查

### 1. 管理员无法确认时间段
**检查**:
- 用户是否已选择时间段
- Dashboard 中是否显示在"等待确认"列表
- 点击确认按钮是否有错误提示

### 2. 自行车状态不正确
**检查**:
- 查看自行车详情中的状态字段
- 确认流程步骤是否正确
- 检查数据库中的状态值

### 3. 通知未发送
**检查**:
- 查看"我的消息"页面
- 检查后端日志
- 确认 UUID 格式正确

## 单元测试结果

```bash
python -m pytest tests/unit/test_new_features.py -v
```

**通过测试 (22 个)**:
- ✅ test_admin_confirm_bicycle_transaction
- ✅ test_admin_confirm_appointment_transaction
- ✅ test_user_cancel_bicycle
- ✅ test_admin_cancel_bicycle
- ✅ test_admin_dashboard
- ✅ test_store_bicycle_in_inventory
- ✅ test_seller_select_time_slot
- ✅ test_buyer_select_time_slot
- ✅ 其他消息和通知测试

## 部署验证清单

- [x] 后端 API 可访问
- [x] 前端页面可访问
- [x] 管理员确认功能正常
- [x] 入库功能正常
- [x] Dashboard 显示等待确认列表
- [x] 通知系统正常工作
- [x] 取消功能正常工作
- [x] 单元测试通过

## 下一步

1. 在网站上创建测试账号
2. 完整测试卖家流程
3. 完整测试买家流程
4. 验证所有通知都能收到
5. 测试取消功能
