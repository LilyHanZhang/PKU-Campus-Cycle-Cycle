#!/bin/bash

API_URL="https://pku-cycle-cycle.onrender.com"

echo "=========================================="
echo "测试 PKU Cycle Backend API"
echo "=========================================="
echo ""

# 测试健康检查
echo "1. 测试健康检查端点 /health"
curl -s -w "\nHTTP 状态码：%{http_code}\n" -X GET "$API_URL/health"
echo ""

# 测试根路径
echo "2. 测试根路径 /"
curl -s -w "\nHTTP 状态码：%{http_code}\n" -X GET "$API_URL/"
echo ""

# 测试 API 文档
echo "3. 测试 API 文档 /docs"
curl -s -w "\nHTTP 状态码：%{http_code}\n" -X GET "$API_URL/docs"
echo ""

# 测试用户注册
echo "4. 测试用户注册 /api/users/register"
curl -s -w "\nHTTP 状态码：%{http_code}\n" -X POST "$API_URL/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
echo ""

# 测试用户登录
echo "5. 测试用户登录 /api/users/login"
curl -s -w "\nHTTP 状态码：%{http_code}\n" -X POST "$API_URL/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
