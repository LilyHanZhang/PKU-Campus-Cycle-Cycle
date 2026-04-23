#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://pku-campus-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试时间线功能"
echo "=========================================="
echo ""

# 1. 登录获取管理员 token
echo "1. 管理员登录"
admin_login_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}')

admin_token=$(echo "$admin_login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$admin_token" ]; then
    echo -e "${GREEN}✓ 管理员登录成功${NC}"
else
    echo -e "${RED}✗ 管理员登录失败${NC}"
    exit 1
fi

# 2. 登录获取用户 token
echo "2. 用户登录"
user_login_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test_timeline@test.com","password":"test123"}')

user_token=$(echo "$user_login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$user_token" ]; then
    echo -e "${GREEN}✓ 用户登录成功${NC}"
else
    echo -e "${YELLOW}⚠ 用户不存在，尝试注册${NC}"
    register_response=$(curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email":"test_timeline@test.com","password":"test123","name":"Test Timeline"}')
    user_login_response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test_timeline@test.com","password":"test123"}')
    user_token=$(echo "$user_login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$user_token" ]; then
        echo -e "${GREEN}✓ 用户注册并登录成功${NC}"
    else
        echo -e "${RED}✗ 用户登录失败${NC}"
        exit 1
    fi
fi
echo ""

# 3. 管理员创建自行车
echo "3. 管理员创建自行车"
bike_response=$(curl -s -X POST "$API_URL/bicycles/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $admin_token" \
    -d '{"brand":"Timeline Test Bike","condition":8,"price":100}')

bike_id=$(echo "$bike_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$bike_id" ]; then
    echo -e "${GREEN}✓ 自行车创建成功${NC}"
    echo "自行车 ID: $bike_id"
else
    echo -e "${RED}✗ 自行车创建失败${NC}"
    exit 1
fi
echo ""

# 4. 用户创建预约
echo "4. 用户创建预约"
apt_response=$(curl -s -X POST "$API_URL/appointments/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $user_token" \
    -d "{\"bicycle_id\":\"$bike_id\",\"type\":\"pick-up\"}")

apt_id=$(echo "$apt_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$apt_id" ]; then
    echo -e "${GREEN}✓ 预约创建成功${NC}"
    echo "预约 ID: $apt_id"
else
    echo -e "${RED}✗ 预约创建失败${NC}"
    exit 1
fi
echo ""

# 5. 管理员创建时间段
echo "5. 管理员创建时间段"
start_time=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%S")
end_time=$(date -u -v+2H +"%Y-%m-%dT%H:%M:%S")

time_slot_response=$(curl -s -X POST "$API_URL/time_slots/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $admin_token" \
    -d "{\"bicycle_id\":\"$bike_id\",\"appointment_type\":\"pick-up\",\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}")

time_slot_id=$(echo "$time_slot_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$time_slot_id" ]; then
    echo -e "${GREEN}✓ 时间段创建成功${NC}"
    echo "时间段 ID: $time_slot_id"
else
    echo -e "${RED}✗ 时间段创建失败${NC}"
    exit 1
fi
echo ""

# 6. 用户选择时间段（等待管理员确认）
echo "6. 用户选择时间段"
select_response=$(curl -s -X PUT "$API_URL/time_slots/select/$apt_id?time_slot_id=$time_slot_id" \
    -H "Authorization: Bearer $user_token")

select_message=$(echo "$select_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)

if echo "$select_message" | grep -q "等待管理员确认"; then
    echo -e "${GREEN}✓ 用户选择时间段成功${NC}"
    echo "消息：$select_message"
else
    echo -e "${RED}✗ 用户选择时间段失败${NC}"
    echo "响应：$select_response"
    exit 1
fi
echo ""

# 7. 管理员确认时间段
echo "7. 管理员确认时间段"
confirm_response=$(curl -s -X PUT "$API_URL/time_slots/confirm/$apt_id" \
    -H "Authorization: Bearer $admin_token")

confirm_message=$(echo "$confirm_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)

if [ "$confirm_message" == "时间段确认成功" ]; then
    echo -e "${GREEN}✓ 管理员确认时间段成功${NC}"
    echo "消息：$confirm_message"
else
    echo -e "${RED}✗ 管理员确认时间段失败${NC}"
    echo "响应：$confirm_response"
    exit 1
fi
echo ""

# 8. 测试管理员更改时间段
echo "8. 测试管理员更改时间段"
new_start_time=$(date -u -v+3H +"%Y-%m-%dT%H:%M:%S")
new_end_time=$(date -u -v+4H +"%Y-%m-%dT%H:%M:%S")

new_time_slot_response=$(curl -s -X POST "$API_URL/time_slots/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $admin_token" \
    -d "{\"bicycle_id\":\"$bike_id\",\"appointment_type\":\"pick-up\",\"start_time\":\"$new_start_time\",\"end_time\":\"$new_end_time\"}")

new_time_slot_id=$(echo "$new_time_slot_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$new_time_slot_id" ]; then
    echo -e "${GREEN}✓ 新时间段创建成功${NC}"
    
    change_response=$(curl -s -X PUT "$API_URL/time_slots/change/$apt_id?new_time_slot_id=$new_time_slot_id" \
        -H "Authorization: Bearer $admin_token")
    
    change_message=$(echo "$change_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    
    if echo "$change_message" | grep -q "更改成功"; then
        echo -e "${GREEN}✓ 管理员更改时间段成功${NC}"
        echo "消息：$change_message"
    else
        echo -e "${YELLOW}⚠ 更改时间段失败（可能是功能问题）${NC}"
        echo "响应：$change_response"
    fi
else
    echo -e "${RED}✗ 新时间段创建失败${NC}"
fi
echo ""

# 9. 测试用户取消预约
echo "9. 测试用户取消预约"
# 先重新选择一个时间段
curl -s -X PUT "$API_URL/time_slots/select/$apt_id?time_slot_id=$time_slot_id" \
    -H "Authorization: Bearer $user_token" > /dev/null
curl -s -X PUT "$API_URL/time_slots/confirm/$apt_id" \
    -H "Authorization: Bearer $admin_token" > /dev/null

cancel_response=$(curl -s -X PUT "$API_URL/appointments/$apt_id/cancel" \
    -H "Authorization: Bearer $user_token")

if echo "$cancel_response" | grep -q "CANCELLED\|成功"; then
    echo -e "${GREEN}✓ 用户取消预约成功${NC}"
else
    echo -e "${YELLOW}⚠ 取消预约可能失败${NC}"
    echo "响应：$cancel_response"
fi
echo ""

echo "=========================================="
echo "时间线功能测试完成"
echo "=========================================="
