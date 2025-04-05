@echo off
setlocal enabledelayedexpansion

:: 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python, 请安装Python 3.8或更高版本
    goto :eof
)

:: 检查是否存在虚拟环境，如果不存在则创建
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 确保上传目录存在
if not exist uploads mkdir uploads

:: 运行应用
echo 启动内网文件传输工具...
python main.py

pause 