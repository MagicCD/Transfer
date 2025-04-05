#!/bin/bash

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3, 请安装Python 3.8或更高版本"
    exit 1
fi

# 检查是否存在虚拟环境，如果不存在则创建
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 确保上传目录存在
mkdir -p uploads

# 运行应用
echo "启动内网文件传输工具..."
python main.py 