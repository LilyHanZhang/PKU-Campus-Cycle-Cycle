#!/bin/bash

API_URL="https://pku-campus-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试时间线新功能"
echo "=========================================="
echo ""

# 登录
admin_token=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

user_token=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test_timeline@test.com","password":"test123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "✓ 管理员和用户登录成功"
echo ""

# 测试 1：卖家场景 - 管理员为自行车提出时间段
echo "1. 测试卖家场景：管理员为自行车提出时间段"
bike_response=$(curl -s -X POST "$API_URL/bicycles/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $user_token" \
    -d '{"brand":"Seller Test Bike","condition":8,"price":100}')

bike_id=$(echo "$bike_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$bike_id" ]; then
    start_time=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%S")
    end_time=$(date -u -v+2H +"%Y-%m-%dT%H:%M:%S")
    
    propose_response=$(curl -s -X POST "$API_URL/bicycles/$bike_id/propose-slots" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $admin_token" \
        -d "[{\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}]")
    
    propose_message=$(echo "$propose_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    
    if echo "$propose_message" | grep -q "已提出.*个时间段"; then
        echo -e "${GREEN}✓ 卖家场景：提出时间段成功${NC}"
        echo "  消息：$propose_message"
    else
        echo -e "${RED}✗ 卖家场景：提出时间段失败${NC}"
        echo "  响应：$propose_response"
    fi
else
    echo -e "${RED}✗ 创建自行车失败${NC}"
fi
echo ""

# 测试 2：买家场景 - 管理员为预约提出时间段
echo "2. 测试买家场景：管理员为预约提出时间段"
# 创建并批准自行车
bike2_response=$(curl -s -X POST "$API_URL/bicycles/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $admin_token" \
    -d '{"brand":"Buyer Test Bike","condition":7,"price":80}')

bike2_id=$(echo "$bike2_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

curl -s -X PUT "$API_URL/bicycles/$bike2_id/approve" \
    -H "Authorization: Bearer $admin_token" > /dev/null

# 创建预约
apt_response=$(curl -s -X POST "$API_URL/appointments/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $user_token" \
    -d "{\"bicycle_id\":\"$bike2_id\",\"type\":\"pick-up\"}")

apt_id=$(echo "$apt_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$apt_id" ]; then
    start_time2=$(date -u -v+3H +"%Y-%m-%dT%H:%M:%S")
    end_time2=$(date -u -v+4H +"%Y-%m-%dT%H:%M:%S")
    
    propose2_response=$(curl -s -X POST "$API_URL/appointments/$apt_id/propose-slots" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $admin_token" \
        -d "[{\"start_time\":\"$start_time2\",\"end_time\":\"$end_time2\"}]")
    
    propose2_message=$(echo "$propose2_response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    
    if echo "$propose2_message" | grep -q "已提出.*个时间段"; then
        echo -e "${GREEN}✓ 买家场景：提出时间段成功${NC}"
        echo "  消息：$propose2_message"
    else
        echo -e "${RED}✗ 买家场景：提出时间段失败${NC}"
        echo "  响应：$propose2_response"
    fi
else
    echo -e "${RED}✗ 创建预约失败${NC}"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
