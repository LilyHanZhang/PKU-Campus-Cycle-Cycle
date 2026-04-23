#!/bin/bash

echo "======================================"
echo "测试管理后台 API"
echo "======================================"
echo ""

# 1. 测试健康检查
echo "1. 测试后端健康检查..."
curl -s "https://pku-campus-cycle-cycle.onrender.com/health" | python3 -m json.tool
echo ""

# 2. 管理员登录
echo "2. 管理员登录..."
TOKEN=$(curl -s -X POST "https://pku-campus-cycle-cycle.onrender.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'ERROR'))")

if [ "$TOKEN" == "ERROR" ]; then
    echo "❌ 登录失败"
    exit 1
fi
echo "✓ 登录成功"
echo ""

# 3. 测试管理后台 API
echo "3. 测试管理后台 API..."
RESPONSE=$(curl -s "https://pku-campus-cycle-cycle.onrender.com/bicycles/admin/dashboard" \
  -H "Authorization: Bearer $TOKEN")

echo "$RESPONSE" | python3 -m json.tool
echo ""

# 4. 检查响应
PENDING=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('pending_bicycles_count', 'ERROR'))")
APPOINTMENTS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('pending_appointments_count', 'ERROR'))")

if [ "$PENDING" != "ERROR" ] && [ "$APPOINTMENTS" != "ERROR" ]; then
    echo "✅ 管理后台 API 正常！"
    echo "   - 待审核自行车：$PENDING"
    echo "   - 待处理预约：$APPOINTMENTS"
else
    echo "❌ 管理后台 API 异常"
    exit 1
fi

echo ""
echo "======================================"
echo "测试完成"
echo "======================================"
