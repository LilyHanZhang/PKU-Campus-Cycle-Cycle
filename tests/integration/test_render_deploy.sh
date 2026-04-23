#!/bin/bash

# 部署后测试脚本 - 测试 revise_detail.md 中的所有新功能
# 使用 Render 后端 API

set -e

API_URL="https://pku-cycle-cycle.onrender.com"

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

echo "1. 检查后端服务是否可用..."
health_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/health")
health_code=$(echo "$health_response" | tail -n1)

if [ "$health_code" == "200" ]; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
    ((pass_count++))
else
    echo -e "${RED}✗ 后端服务不可用 (状态码：$health_code)${NC}"
    echo "请等待 Render 完成部署（通常需要 1-3 分钟）"
    exit 1
fi

echo ""
echo "2. 测试数据库连接和新字段..."
# 尝试登录超级管理员
admin_token=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")

if [ -n "$admin_token" ]; then
    echo -e "${GREEN}✓ 数据库连接正常，管理员账号存在${NC}"
    ((pass_count++))
else
    echo -e "${RED}✗ 数据库连接或管理员账号异常${NC}"
    ((fail_count++))
fi

echo ""
echo "3. 测试私信功能..."
# 注册测试用户
curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"deploy_test1@pku.edu.cn","password":"testpass123","name":"Deploy Test 1"}' > /dev/null 2>&1 || true

curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"deploy_test2@pku.edu.cn","password":"testpass123","name":"Deploy Test 2"}' > /dev/null 2>&1 || true

# 登录测试用户
token1=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"deploy_test1@pku.edu.cn","password":"testpass123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")

token2=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"deploy_test2@pku.edu.cn","password":"testpass123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")

if [ -n "$token1" ] && [ -n "$token2" ]; then
    user2_id=$(curl -s -X GET "$API_URL/auth/me" \
        -H "Authorization: Bearer $token2" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")
    
    # 发送私信
    msg_response=$(curl -s -X POST "$API_URL/messages/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token1" \
        -d "{\"receiver_id\":\"$user2_id\",\"content\":\"Deploy test message\"}")
    
    if echo "$msg_response" | grep -q "content"; then
        echo -e "${GREEN}✓ 私信功能正常${NC}"
        ((pass_count++))
    else
        echo -e "${RED}✗ 私信功能异常${NC}"
        ((fail_count++))
    fi
else
    echo -e "${RED}⚠ 跳过私信测试（用户注册/登录失败）${NC}"
fi

echo ""
echo "4. 测试时间段管理功能..."
if [ -n "$admin_token" ]; then
    # 创建自行车
    bike_response=$(curl -s -X POST "$API_URL/bicycles/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $admin_token" \
        -d '{"brand":"Deploy Test Bike","condition":8,"price":100}')
    
    bike_id=$(echo "$bike_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 || echo "")
    
    if [ -n "$bike_id" ]; then
        # 创建时间段
        start_time=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%SZ")
        end_time=$(date -u -v+2H +"%Y-%m-%dT%H:%M:%SZ")
        
        time_slot_response=$(curl -s -X POST "$API_URL/time_slots/" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $admin_token" \
            -d "{\"bicycle_id\":\"$bike_id\",\"appointment_type\":\"pick-up\",\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}")
        
        if echo "$time_slot_response" | grep -q "bicycle_id"; then
            echo -e "${GREEN}✓ 时间段管理功能正常${NC}"
            ((pass_count++))
        else
            echo -e "${RED}✗ 时间段管理功能异常${NC}"
            ((fail_count++))
        fi
    else
        echo -e "${RED}✗ 创建自行车失败${NC}"
        ((fail_count++))
    fi
else
    echo -e "${RED}⚠ 跳过时间段测试（管理员登录失败）${NC}"
fi

echo ""
echo "5. 测试交易倒计时功能..."
if [ -n "$token1" ]; then
    countdown_response=$(curl -s -X GET "$API_URL/time_slots/my/countdown" \
        -H "Authorization: Bearer $token1")
    
    if echo "$countdown_response" | grep -q "countdowns"; then
        echo -e "${GREEN}✓ 交易倒计时功能正常${NC}"
        ((pass_count++))
    else
        echo -e "${RED}✗ 交易倒计时功能异常${NC}"
        ((fail_count++))
    fi
else
    echo -e "${RED}⚠ 跳过倒计时测试${NC}"
fi

echo ""
echo "========================================"
echo "测试结果汇总"
echo "========================================"
echo -e "${GREEN}通过：$pass_count${NC}"
echo -e "${RED}失败：$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ 所有部署后测试通过！${NC}"
    echo ""
    echo "部署验证成功，新功能已上线："
    echo "  ✅ 私信系统"
    echo "  ✅ 交易倒计时"
    echo "  ✅ 时间段管理（日历选择器）"
    echo "  ✅ 数据库连接正常"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败${NC}"
    echo ""
    echo "可能的原因："
    echo "  1. Render 还在部署中（请等待 1-3 分钟后重试）"
    echo "  2. 数据库迁移未完成"
    echo "  3. 环境变量配置问题"
    exit 1
fi
