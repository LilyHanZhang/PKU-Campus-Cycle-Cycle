#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="https://pku-campus-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试管理后台 API 端点"
echo "=========================================="
echo ""

# 1. 测试健康检查
echo "1. 测试健康检查 /health"
health_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/health")
health_code=$(echo "$health_response" | tail -n1)
health_body=$(echo "$health_response" | head -n-1)

if [ "$health_code" == "200" ]; then
    echo -e "${GREEN}✓ 健康检查通过 (200)${NC}"
    echo "响应：$health_body"
else
    echo -e "${RED}✗ 健康检查失败 ($health_code)${NC}"
    echo "响应：$health_body"
fi
echo ""

# 2. 测试根路径
echo "2. 测试根路径 /"
root_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/")
root_code=$(echo "$root_response" | tail -n1)
root_body=$(echo "$root_response" | head -n-1)

if [ "$root_code" == "200" ]; then
    echo -e "${GREEN}✓ 根路径可访问 (200)${NC}"
    echo "响应：$root_body"
else
    echo -e "${RED}✗ 根路径不可访问 ($root_code)${NC}"
    echo "响应：$root_body"
fi
echo ""

# 3. 测试 API 文档
echo "3. 测试 API 文档 /docs"
docs_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/docs")
docs_code=$(echo "$docs_response" | tail -n1)

if [ "$docs_code" == "200" ]; then
    echo -e "${GREEN}✓ API 文档可访问 (200)${NC}"
else
    echo -e "${RED}✗ API 文档不可访问 ($docs_code)${NC}"
fi
echo ""

# 4. 测试 OpenAPI JSON
echo "4. 测试 OpenAPI JSON /openapi.json"
openapi_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/openapi.json")
openapi_code=$(echo "$openapi_response" | tail -n1)

if [ "$openapi_code" == "200" ]; then
    echo -e "${GREEN}✓ OpenAPI JSON 可访问 (200)${NC}"
    # 显示路径列表
    echo "可用的端点："
    echo "$openapi_response" | head -n-1 | grep -o '"\/[^"]*"' | sort | uniq | head -20
else
    echo -e "${RED}✗ OpenAPI JSON 不可访问 ($openapi_code)${NC}"
fi
echo ""

# 5. 测试自行车列表端点
echo "5. 测试自行车列表 /bicycles/ (无需认证)"
bikes_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/bicycles/")
bikes_code=$(echo "$bikes_response" | tail -n1)
bikes_body=$(echo "$bikes_response" | head -n-1)

if [ "$bikes_code" == "200" ]; then
    echo -e "${GREEN}✓ 自行车列表可访问 (200)${NC}"
    echo "响应：$bikes_body"
else
    echo -e "${RED}✗ 自行车列表不可访问 ($bikes_code)${NC}"
    echo "响应：$bikes_body"
fi
echo ""

# 6. 测试用户列表端点（需要认证）
echo "6. 测试用户列表 /users/ (需要认证)"
users_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/users/")
users_code=$(echo "$users_response" | tail -n1)
users_body=$(echo "$users_response" | head -n-1)

if [ "$users_code" == "200" ] || [ "$users_code" == "401" ]; then
    echo -e "${GREEN}✓ 用户列表端点存在 (返回 $users_code)${NC}"
    if [ "$users_code" == "401" ]; then
        echo "注意：需要认证（这是正常的）"
    fi
    echo "响应：$users_body"
else
    echo -e "${RED}✗ 用户列表端点异常 ($users_code)${NC}"
    echo "响应：$users_body"
fi
echo ""

# 7. 测试预约列表端点（需要认证）
echo "7. 测试预约列表 /appointments/ (需要认证)"
appointments_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/appointments/")
appointments_code=$(echo "$appointments_response" | tail -n1)
appointments_body=$(echo "$appointments_response" | head -n-1)

if [ "$appointments_code" == "200" ] || [ "$appointments_code" == "401" ]; then
    echo -e "${GREEN}✓ 预约列表端点存在 (返回 $appointments_code)${NC}"
    if [ "$appointments_code" == "401" ]; then
        echo "注意：需要认证（这是正常的）"
    fi
    echo "响应：$appointments_body"
else
    echo -e "${RED}✗ 预约列表端点异常 ($appointments_code)${NC}"
    echo "响应：$appointments_body"
fi
echo ""

# 8. 测试认证端点
echo "8. 测试注册端点 /auth/register"
register_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test_render@test.com","password":"test123","name":"Test Render"}')
register_code=$(echo "$register_response" | tail -n1)
register_body=$(echo "$register_response" | head -n-1)

if [ "$register_code" == "200" ] || [ "$register_code" == "400" ]; then
    echo -e "${GREEN}✓ 注册端点存在 (返回 $register_code)${NC}"
    echo "响应：$register_body"
else
    echo -e "${RED}✗ 注册端点异常 ($register_code)${NC}"
    echo "响应：$register_body"
fi
echo ""

# 9. 测试登录端点
echo "9. 测试登录端点 /auth/login"
login_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"2200017736@stu.pku.edu.cn","password":"pkucycle"}')
login_code=$(echo "$login_response" | tail -n1)
login_body=$(echo "$login_response" | head -n-1)

if [ "$login_code" == "200" ]; then
    echo -e "${GREEN}✓ 登录端点正常 (200)${NC}"
    # 提取 token
    access_token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$access_token" ]; then
        echo -e "${GREEN}✓ 获取到 access_token${NC}"
        echo "Token 前 50 字符：${access_token:0:50}..."
        
        # 保存 token 供后续测试使用
        echo "$access_token" > /tmp/render_token.txt
        echo "Token 已保存到 /tmp/render_token.txt"
    fi
else
    echo -e "${RED}✗ 登录端点异常 ($login_code)${NC}"
    echo "响应：$login_body"
fi
echo ""

# 10. 使用 token 测试 /users/ 端点
echo "10. 使用 token 测试 /users/ (带认证)"
if [ -f /tmp/render_token.txt ]; then
    token=$(cat /tmp/render_token.txt)
    users_auth_response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/users/" \
        -H "Authorization: Bearer $token")
    users_auth_code=$(echo "$users_auth_response" | tail -n1)
    users_auth_body=$(echo "$users_auth_response" | head -n-1)
    
    if [ "$users_auth_code" == "200" ]; then
        echo -e "${GREEN}✓ 带认证的 /users/ 端点正常 (200)${NC}"
        echo "响应：$users_auth_body"
    else
        echo -e "${RED}✗ 带认证的 /users/ 端点异常 ($users_auth_code)${NC}"
        echo "响应：$users_auth_body"
    fi
else
    echo -e "${YELLOW}⚠ 跳过测试（无 token）${NC}"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""

# 总结
echo "总结："
if [ "$health_code" == "200" ] && [ "$root_code" == "200" ] && [ "$login_code" == "200" ]; then
    echo -e "${GREEN}✓ 所有基础端点正常${NC}"
else
    echo -e "${RED}✗ 部分端点存在问题，请检查上方的详细输出${NC}"
fi
