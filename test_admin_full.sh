#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://pku-campus-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试管理后台完整 API"
echo "=========================================="
echo ""

# 1. 登录获取 token
echo "1. 登录获取 token"
login_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}')

access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$access_token" ]; then
    echo -e "${GREEN}✓ 登录成功${NC}"
    echo "Token: ${access_token:0:50}..."
else
    echo -e "${RED}✗ 登录失败${NC}"
    echo "响应：$login_response"
    exit 1
fi
echo ""

# 2. 测试 /auth/me
echo "2. 测试 /auth/me"
me_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/auth/me" \
    -H "Authorization: Bearer $access_token")
me_code=$(echo "$me_response" | tail -n1)
me_body=$(echo "$me_response" | head -n-1)

if [ "$me_code" == "200" ]; then
    echo -e "${GREEN}✓ /auth/me 正常 (200)${NC}"
    echo "用户信息：$me_body"
else
    echo -e "${RED}✗ /auth/me 失败 ($me_code)${NC}"
    echo "响应：$me_body"
fi
echo ""

# 3. 测试 /users/
echo "3. 测试 /users/"
users_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/users/" \
    -H "Authorization: Bearer $access_token")
users_code=$(echo "$users_response" | tail -n1)
users_body=$(echo "$users_response" | head -n-1)

if [ "$users_code" == "200" ]; then
    echo -e "${GREEN}✓ /users/ 正常 (200)${NC}"
    user_count=$(echo "$users_body" | grep -o '"id"' | wc -l)
    echo "用户数量：$user_count"
else
    echo -e "${RED}✗ /users/ 失败 ($users_code)${NC}"
    echo "响应：$users_body"
fi
echo ""

# 4. 测试 /bicycles/
echo "4. 测试 /bicycles/"
bikes_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/bicycles/" \
    -H "Authorization: Bearer $access_token")
bikes_code=$(echo "$bikes_response" | tail -n1)
bikes_body=$(echo "$bikes_response" | head -n-1)

if [ "$bikes_code" == "200" ]; then
    echo -e "${GREEN}✓ /bicycles/ 正常 (200)${NC}"
    bike_count=$(echo "$bikes_body" | grep -o '"id"' | wc -l)
    echo "车辆数量：$bike_count"
else
    echo -e "${RED}✗ /bicycles/ 失败 ($bikes_code)${NC}"
    echo "响应：$bikes_body"
fi
echo ""

# 5. 测试 /bicycles/?status=PENDING_APPROVAL
echo "5. 测试 /bicycles/?status=PENDING_APPROVAL"
pending_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/bicycles/?status=PENDING_APPROVAL" \
    -H "Authorization: Bearer $access_token")
pending_code=$(echo "$pending_response" | tail -n1)
pending_body=$(echo "$pending_response" | head -n-1)

if [ "$pending_code" == "200" ]; then
    echo -e "${GREEN}✓ /bicycles/?status=PENDING_APPROVAL 正常 (200)${NC}"
    pending_count=$(echo "$pending_body" | grep -o '"id"' | wc -l)
    echo "待审核车辆数量：$pending_count"
else
    echo -e "${RED}✗ /bicycles/?status=PENDING_APPROVAL 失败 ($pending_code)${NC}"
    echo "响应：$pending_body"
fi
echo ""

# 6. 测试 /appointments/
echo "6. 测试 /appointments/（关键测试）"
appointments_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/appointments/" \
    -H "Authorization: Bearer $access_token")
appointments_code=$(echo "$appointments_response" | tail -n1)
appointments_body=$(echo "$appointments_response" | head -n-1)

if [ "$appointments_code" == "200" ]; then
    echo -e "${GREEN}✓ /appointments/ 正常 (200)${NC}"
    apt_count=$(echo "$appointments_body" | grep -o '"id"' | wc -l)
    echo "预约数量：$apt_count"
    
    # 检查 CORS 头
    cors_check=$(curl -s -I -X GET "$API_URL/appointments/" \
        -H "Authorization: Bearer $access_token" | grep -i "access-control-allow-origin")
    if [ -n "$cors_check" ]; then
        echo -e "${GREEN}✓ CORS 头正常${NC}"
    else
        echo -e "${YELLOW}⚠ CORS 头可能缺失${NC}"
    fi
else
    echo -e "${RED}✗ /appointments/ 失败 ($appointments_code)${NC}"
    echo "响应：$appointments_body"
fi
echo ""

# 7. 测试 /time_slots/
echo "7. 测试 /time_slots/"
time_slots_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/time_slots/" \
    -H "Authorization: Bearer $access_token")
time_slots_code=$(echo "$time_slots_response" | tail -n1)
time_slots_body=$(echo "$time_slots_response" | head -n-1)

if [ "$time_slots_code" == "200" ]; then
    echo -e "${GREEN}✓ /time_slots/ 正常 (200)${NC}"
    slot_count=$(echo "$time_slots_body" | grep -o '"id"' | wc -l)
    echo "时间段数量：$slot_count"
else
    echo -e "${RED}✗ /time_slots/ 失败 ($time_slots_code)${NC}"
    echo "响应：$time_slots_body"
fi
echo ""

# 8. 测试 /messages/
echo "8. 测试 /messages/"
messages_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/messages/" \
    -H "Authorization: Bearer $access_token")
messages_code=$(echo "$messages_response" | tail -n1)
messages_body=$(echo "$messages_response" | head -n-1)

if [ "$messages_code" == "200" ]; then
    echo -e "${GREEN}✓ /messages/ 正常 (200)${NC}"
    msg_count=$(echo "$messages_body" | grep -o '"id"' | wc -l)
    echo "消息数量：$msg_count"
else
    echo -e "${RED}✗ /messages/ 失败 ($messages_code)${NC}"
    echo "响应：$messages_body"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""

# 总结
echo "总结："
if [ "$me_code" == "200" ] && [ "$users_code" == "200" ] && [ "$appointments_code" == "200" ]; then
    echo -e "${GREEN}✓ 所有管理后台 API 正常！${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分 API 存在问题${NC}"
    exit 1
fi
