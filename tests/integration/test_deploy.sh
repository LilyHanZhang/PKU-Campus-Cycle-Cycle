#!/bin/bash

# 部署后测试脚本 - 测试 revise_detail.md 中的所有新功能

set -e

API_URL="${1:-http://localhost:8000}"

echo "========================================"
echo "部署后测试 - revise_detail.md 新功能"
echo "========================================"
echo "API URL: $API_URL"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

# 测试函数
test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4
    local data=$5
    local headers=$6
    
    echo -n "测试：$name ... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$endpoint" $headers)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            $headers \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((pass_count++))
    else
        echo -e "${RED}✗ 失败 (期望：$expected_status, 实际：$http_code)${NC}"
        echo "响应：$body"
        ((fail_count++))
    fi
}

echo "1. 注册测试用户..."
# 注册用户 1
curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test1@pku.edu.cn","password":"testpass123","name":"Test User 1"}' > /dev/null

# 注册用户 2
curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test2@pku.edu.cn","password":"testpass123","name":"Test User 2"}' > /dev/null

echo "2. 登录获取 token..."
token1=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test1@pku.edu.cn","password":"testpass123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

token2=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test2@pku.edu.cn","password":"testpass123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

admin_token=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "3. 测试私信功能..."
user2_id=$(curl -s -X GET "$API_URL/auth/me" \
    -H "Authorization: Bearer $token2" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

test_api "用户发送私信" "POST" "/messages/" "200" \
    "{\"receiver_id\":\"$user2_id\",\"content\":\"Hello from user 1\"}" \
    "-H \"Authorization: Bearer $token1\""

test_api "获取我的私信" "GET" "/messages/" "200" "" \
    "-H \"Authorization: Bearer $token1\""

test_api "获取未读消息数" "GET" "/messages/unread" "200" "" \
    "-H \"Authorization: Bearer $token2\""

echo ""
echo "4. 测试时间段管理功能..."
# 创建自行车
bike_response=$(curl -s -X POST "$API_URL/bicycles/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token1" \
    -d '{"brand":"Test Bike","condition":8,"price":100}')

bike_id=$(echo "$bike_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# 管理员审核
curl -s -X PUT "$API_URL/bicycles/$bike_id/approve" \
    -H "Authorization: Bearer $admin_token" > /dev/null

# 创建预约
apt_response=$(curl -s -X POST "$API_URL/appointments/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token1" \
    -d "{\"bicycle_id\":\"$bike_id\",\"type\":\"pick-up\"}")

apt_id=$(echo "$apt_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

# 创建时间段
start_time=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%S")
end_time=$(date -u -v+2H +"%Y-%m-%dT%H:%M:%S")

time_slot_response=$(curl -s -X POST "$API_URL/time_slots/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $admin_token" \
    -d "{\"bicycle_id\":\"$bike_id\",\"appointment_type\":\"pick-up\",\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}")

time_slot_id=$(echo "$time_slot_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

test_api "创建时间段" "POST" "/time_slots/" "200" \
    "{\"bicycle_id\":\"$bike_id\",\"appointment_type\":\"pick-up\",\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}" \
    "-H \"Authorization: Bearer $admin_token\""

# 用户选择时间段
test_api "用户选择时间段" "PUT" "/time_slots/select/$apt_id?time_slot_id=$time_slot_id" "200" "" \
    "-H \"Authorization: Bearer $token1\""

echo ""
echo "5. 测试交易倒计时功能..."
test_api "获取交易倒计时" "GET" "/time_slots/my/countdown" "200" "" \
    "-H \"Authorization: Bearer $token1\""

echo ""
echo "6. 测试完整的预约流程..."
# 管理员确认提车
test_api "管理员确认提车" "PUT" "/appointments/$apt_id/confirm-pickup" "200" "" \
    "-H \"Authorization: Bearer $admin_token\""

# 用户评价
test_api "用户评价" "POST" "/time_slots/reviews" "200" \
    "{\"appointment_id\":\"$apt_id\",\"rating\":5,\"content\":\"Great!\",\"review_type\":\"buyer_review\"}" \
    "-H \"Authorization: Bearer $token1\""

echo ""
echo "========================================"
echo "测试结果汇总"
echo "========================================"
echo -e "${GREEN}通过：$pass_count${NC}"
echo -e "${RED}失败：$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败${NC}"
    exit 1
fi
