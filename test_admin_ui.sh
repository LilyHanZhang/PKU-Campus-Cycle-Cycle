#!/bin/bash

# 管理后台 UI 更新测试脚本
# 测试新的蓝色主题、顶部导航布局、数据卡片等功能

API_URL="https://pku-campus-cycle-cycle.onrender.com"
TOKEN=""

echo "========================================"
echo "管理后台 UI 更新测试"
echo "========================================"
echo ""

# 1. 测试 API 是否可访问
echo "1. 测试 API 连接..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$RESPONSE" == "200" ]; then
    echo "✓ API 文档可访问"
else
    echo "✗ API 文档访问失败：$RESPONSE"
    exit 1
fi

# 2. 测试登录（使用管理员账号）
echo ""
echo "2. 测试管理员登录..."
# 注意：这里需要使用实际的管理员账号
# 假设已有管理员账号：admin@example.com / admin123
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123")

# 检查是否登录成功
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "✓ 管理员登录成功"
else
    echo "⚠ 管理员登录失败（可能需要手动登录）"
    echo "响应：$LOGIN_RESPONSE"
fi

# 3. 测试管理后台数据接口
if [ -n "$TOKEN" ]; then
    echo ""
    echo "3. 测试管理后台数据接口..."
    
    # 测试用户信息
    USER_RESPONSE=$(curl -s "$API_URL/auth/me" \
      -H "Authorization: Bearer $TOKEN")
    if echo "$USER_RESPONSE" | grep -q "role"; then
        echo "✓ 用户信息获取成功"
        ROLE=$(echo "$USER_RESPONSE" | grep -o '"role":"[^"]*' | cut -d'"' -f4)
        echo "  角色：$ROLE"
    else
        echo "✗ 用户信息获取失败"
    fi
    
    # 测试仪表盘数据
    DASHBOARD_RESPONSE=$(curl -s "$API_URL/bicycles/admin/dashboard" \
      -H "Authorization: Bearer $TOKEN")
    if echo "$DASHBOARD_RESPONSE" | grep -q "pending_bicycles_count"; then
        echo "✓ 仪表盘数据获取成功"
    else
        echo "✗ 仪表盘数据获取失败"
    fi
    
    # 测试用户列表
    USERS_RESPONSE=$(curl -s "$API_URL/users/" \
      -H "Authorization: Bearer $TOKEN")
    if echo "$USERS_RESPONSE" | grep -q "email"; then
        echo "✓ 用户列表获取成功"
    else
        echo "✗ 用户列表获取失败"
    fi
    
    # 测试车辆列表
    BIKES_RESPONSE=$(curl -s "$API_URL/bicycles/" \
      -H "Authorization: Bearer $TOKEN")
    if echo "$BIKES_RESPONSE" | grep -q "brand"; then
        echo "✓ 车辆列表获取成功"
    else
        echo "✗ 车辆列表获取失败"
    fi
    
    # 测试预约列表
    APTS_RESPONSE=$(curl -s "$API_URL/appointments/" \
      -H "Authorization: Bearer $TOKEN")
    if echo "$APTS_RESPONSE" | grep -q "status"; then
        echo "✓ 预约列表获取成功"
    else
        echo "✗ 预约列表获取失败"
    fi
fi

# 4. 测试前端页面
echo ""
echo "4. 测试前端页面..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://pku-campus-cycle-cycle.vercel.app/admin")
if [ "$FRONTEND_RESPONSE" == "200" ]; then
    echo "✓ 管理后台页面可访问"
else
    echo "⚠ 管理后台页面访问状态：$FRONTEND_RESPONSE"
    echo "  （可能需要登录验证）"
fi

echo ""
echo "========================================"
echo "测试完成！"
echo "========================================"
echo ""
echo "请手动访问以下地址测试新的管理后台 UI："
echo "🌐 前端地址：https://pku-campus-cycle-cycle.vercel.app/admin"
echo "📊 API 文档：$API_URL/docs"
echo ""
echo "新功能特性："
echo "✨ 蓝色主题，专业稳重"
echo "✨ 顶部导航布局，现代简洁"
echo "✨ 数据概览卡片（4 个统计指标）"
echo "✨ 快捷操作面板"
echo "✨ 内联交互方式"
echo "✨ 响应式布局"
echo "✨ 搜索过滤功能"
echo ""
