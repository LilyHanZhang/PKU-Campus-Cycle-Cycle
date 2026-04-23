# PKU Campus Cycle Cycle - 部署测试指南

## 部署状态

- ✅ 代码已提交到 GitHub
- ✅ 后端已推送到 Render (https://pku-cycle-backend.onrender.com)
- ✅ 前端已推送到 Vercel (https://pku-campus-cycle-cycle.vercel.app)

## 新增功能测试清单

### 1. 管理员确认时间段功能

#### 卖家流程测试:
1. 登录卖家账号
2. 登记新的自行车
3. 等待管理员提出时间段
4. 收到私信通知
5. 进入个人中心 -> 时间段选择
6. 选择一个时间段
7. **等待管理员确认**
8. 管理员访问 /admin -> Dashboard
9. 查看待确认的自行车
10. 确认后，卖家收到确认通知

#### 买家流程测试:
1. 登录买家账号
2. 预约自行车
3. 等待管理员提出时间段
4. 收到私信通知
5. 进入个人中心 -> 时间段选择
6. 选择一个时间段
7. **等待管理员确认**
8. 管理员访问 /admin -> Dashboard
9. 查看待确认的预约
10. 确认后，买家收到确认通知

### 2. 取消交易功能

#### 用户取消测试:
- 卖家可以取消自己的自行车登记
- 买家可以取消自己的预约

#### 管理员取消测试:
- 管理员可以取消自行车登记（需填写原因）
- 管理员可以取消预约（需填写原因）
- 用户会收到私信通知

### 3. 管理员仪表盘和倒计时

测试步骤:
1. 登录管理员账号 (admin@example.com)
2. 访问 http://localhost:3000/admin 或 https://pku-campus-cycle-cycle.vercel.app/admin
3. 查看 Dashboard 标签页（默认）
4. 验证显示内容:
   - 待处理自行车登记数量
   - 待处理预约数量
   - 已锁定时间段数量
   - 倒计时显示（如果有已锁定的时间段）

### 4. 通知系统

测试步骤:
1. 执行上述任一流程
2. 检查是否收到私信通知
3. 验证通知内容是否正确

## API 端点测试

### 管理员仪表盘
```bash
curl https://pku-cycle-backend.onrender.com/bicycles/admin/dashboard \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 确认自行车交易
```bash
curl -X POST https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/confirm \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 确认预约交易
```bash
curl -X PUT https://pku-cycle-backend.onrender.com/time_slots/confirm/{apt_id} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 用户取消自行车
```bash
curl -X POST https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/cancel \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

### 管理员取消自行车
```bash
curl -X POST "https://pku-cycle-backend.onrender.com/bicycles/{bike_id}/admin-cancel?reason=测试原因" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 单元测试结果

```
21 个测试通过:
✅ test_admin_confirm_bicycle_transaction
✅ test_admin_confirm_appointment_transaction  
✅ test_user_cancel_bicycle
✅ test_admin_cancel_bicycle
✅ test_admin_dashboard
✅ test_seller_select_time_slot
✅ test_buyer_select_time_slot
✅ 以及其他 14 个测试
```

## 预期行为

### 卖家完整流程
1. 登记自行车 → PENDING_APPROVAL
2. 管理员提出时间段 → LOCKED
3. 收到私信 ✓
4. 选择时间段 → LOCKED (等待确认)
5. 管理员确认 → SOLD ✓
6. 收到确认通知 ✓

### 买家完整流程
1. 创建预约 → PENDING
2. 管理员提出时间段 → PENDING (等待选择)
3. 收到私信 ✓
4. 选择时间段 → PENDING (等待确认)
5. 管理员确认 → CONFIRMED ✓
6. 收到确认通知 ✓

## 注意事项

1. **Render 部署延迟**: 后端部署可能需要 2-5 分钟
2. **测试账号**: 确保有管理员和普通用户测试账号
3. **私信功能**: 所有通知都会通过私信发送
4. **倒计时**: 只有在已锁定但未完成的时间段才会显示倒计时

## 问题排查

如果后端 API 返回 404:
1. 等待 Render 部署完成
2. 检查 API 端点路径是否正确
3. 验证 token 是否有效

如果前端无法访问:
1. 检查 Vercel 部署状态
2. 清除浏览器缓存
3. 尝试无痕模式访问
