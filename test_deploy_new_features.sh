#!/bin/bash

API_URL="https://pku-campus-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试时间线新功能 - 部署环境"
echo "=========================================="
echo ""

# 获取 token
admin_token=$(curl -s -X POST "$API_URL/auth/login" -H "Content-Type: application/json" -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
user_token=$(curl -s -X POST "$API_URL/auth/login" -H "Content-Type: application/json" -d '{"email":"test_timeline@test.com","password":"test123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "✓ 登录成功"
echo ""

# 测试 1
echo "测试 1: 卖家场景 - 管理员为自行车提出时间段"
bike_response=$(curl -s -X POST "$API_URL/bicycles/" -H "Content-Type: application/json" -H "Authorization: Bearer $user_token" -d '{"brand":"Seller Test","condition":8,"price":100}')
bike_id=$(echo "$bike_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "  创建自行车：$bike_id"

start_time=$(python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()+timedelta(hours=1)).isoformat())")
end_time=$(python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()+timedelta(hours=2)).isoformat())")

propose_response=$(curl -s -X POST "$API_URL/bicycles/$bike_id/propose-slots" -H "Content-Type: application/json" -H "Authorization: Bearer $admin_token" -d "[{\"start_time\":\"$start_time\",\"end_time\":\"$end_time\"}]")
propose_message=$(echo "$propose_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message',''))")
echo "  响应：$propose_message"

if [[ "$propose_message" == *"已提出"* ]]; then
    echo "  ✓ 通过"
else
    echo "  ✗ 失败"
fi
echo ""

# 测试 2
echo "测试 2: 买家场景 - 管理员为预约提出时间段"
bike2_response=$(curl -s -X POST "$API_URL/bicycles/" -H "Content-Type: application/json" -H "Authorization: Bearer $admin_token" -d '{"brand":"Buyer Test","condition":7,"price":80}')
bike2_id=$(echo "$bike2_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "  创建自行车：$bike2_id"

curl -s -X PUT "$API_URL/bicycles/$bike2_id/approve" -H "Authorization: Bearer $admin_token" > /dev/null

apt_response=$(curl -s -X POST "$API_URL/appointments/" -H "Content-Type: application/json" -H "Authorization: Bearer $user_token" -d "{\"bicycle_id\":\"$bike2_id\",\"type\":\"pick-up\"}")
apt_id=$(echo "$apt_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
echo "  创建预约：$apt_id"

start_time2=$(python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()+timedelta(hours=3)).isoformat())")
end_time2=$(python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()+timedelta(hours=4)).isoformat())")

propose2_response=$(curl -s -X POST "$API_URL/appointments/$apt_id/propose-slots" -H "Content-Type: application/json" -H "Authorization: Bearer $admin_token" -d "[{\"start_time\":\"$start_time2\",\"end_time\":\"$end_time2\"}]")
propose2_message=$(echo "$propose2_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message',''))")
echo "  响应：$propose2_message"

if [[ "$propose2_message" == *"已提出"* ]]; then
    echo "  ✓ 通过"
else
    echo "  ✗ 失败"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
