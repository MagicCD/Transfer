@echo off
chcp 65001 > nul
echo 开始构建内网文件传输工具...
python build_exe.py
echo.
echo 按任意键退出...
pause > nul