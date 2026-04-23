#!/bin/bash
echo "等待部署完成..."
sleep 120

echo "开始测试 API..."
python test_cors_and_api.py
