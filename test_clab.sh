#!/bin/bash

echo "======================================"
echo "测试 cLab 部署"
echo "======================================"
echo ""

# 配置
BASE_URL="http://10.129.245.117:8000"

# 1. 测试健康检查
echo "1. 测试后端健康检查..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# 2. 管理员登录
echo "2. 管理员登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}')

echo "登录响应："
echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# 提取 token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'ERROR'))")

if [ "$TOKEN" == "ERROR" ]; then
    echo "❌ 登录失败 - 无法获取 token"
    exit 1
fi
echo "✓ 登录成功，获取 token"
echo ""

# 3. 测试获取当前用户信息
echo "3. 测试获取当前用户信息..."
USER_RESPONSE=$(curl -s "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

echo "用户信息："
echo "$USER_RESPONSE" | python3 -m json.tool
echo ""

# 检查是否是管理员
ROLE=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('role', 'ERROR'))")
if [ "$ROLE" == "ERROR" ]; then
    echo "❌ 无法获取用户角色"
    exit 1
fi
echo "✓ 用户角色：$ROLE"
echo ""

# 4. 测试管理后台 API
echo "4. 测试管理后台 API..."
ADMIN_RESPONSE=$(curl -s "$BASE_URL/bicycles/admin/dashboard" \
  -H "Authorization: Bearer $TOKEN")

echo "管理后台响应："
echo "$ADMIN_RESPONSE" | python3 -m json.tool
echo ""

# 5. 测试其他 API
echo "5. 测试 Users API..."
USERS_RESPONSE=$(curl -s "$BASE_URL/users/" \
  -H "Authorization: Bearer $TOKEN")
echo "Users API 状态码：$?"
echo ""

echo "6. 测试 Bicycles API..."
BICYCLES_RESPONSE=$(curl -s "$BASE_URL/bicycles/" \
  -H "Authorization: Bearer $TOKEN")
echo "Bicycles API 状态码：$?"
echo ""

echo "7. 测试 Appointments API..."
APPOINTMENTS_RESPONSE=$(curl -s "$BASE_URL/appointments/" \
  -H "Authorization: Bearer $TOKEN")
echo "Appointments API 状态码：$?"
echo ""

echo "8. 测试 Messages API..."
MESSAGES_RESPONSE=$(curl -s "$BASE_URL/messages/" \
  -H "Authorization: Bearer $TOKEN")
echo "Messages API 状态码：$?"
echo ""

# 总结
echo ""
echo "======================================"
echo "测试总结"
echo "======================================"
echo ""

if [ "$ROLE" == "SUPER_ADMIN" ] || [ "$ROLE" == "ADMIN" ]; then
    echo "✅ 管理员登录成功！"
    echo "   - 用户角色：$ROLE"
    echo "   - Token 有效"
    echo ""
    echo "📊 访问地址:"
    echo "   前端：http://10.129.245.117:3000"
    echo "   后端：http://10.129.245.117:8000/docs"
    echo ""
    echo "🔐 登录信息:"
    echo "   邮箱：2200017736@stu.pku.edu.cn"
    echo "   密码：pkucycle"
else
    echo "❌ 测试失败"
    exit 1
fi

echo ""
echo "======================================"
echo "测试完成"
echo "======================================"
