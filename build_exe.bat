@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ===== 文件快传应用打包工具 =====
echo.

:: 设置环境变量
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

REM 检查 Python 是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python，请确保安装了 Python 3.8-3.13
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt >nul
pip install colorama tqdm >nul

REM 确保上传目录存在
if not exist uploads mkdir uploads

echo 开始打包应用程序...

:: 使用临时文件来存储输出
if not exist "temp" mkdir temp

:: 运行打包命令，并将输出通过管道传递给 build_progress.py
(pyinstaller --clean FileTransfer.spec 2>&1) | python build_progress.py
set PYINSTALLER_ERROR=%ERRORLEVEL%

:: 清理临时文件
if exist "temp" rd /s /q temp

if %PYINSTALLER_ERROR% equ 0 (
    echo ===== 打包成功! =====
    echo 可执行文件位于: dist\FileTransfer.exe
    echo.
    echo 打包完成后测试注意事项：
    echo ^| 1. 检查界面是否正常显示
    echo ^| 2. 测试文件上传和下载功能
    echo ^| 3. 确认实时文件列表更新是否正常
    echo.

    :: 清理PyInstaller生成的临时文件
    if exist "build" (
        echo 正在清理构建文件...
        rd /s /q build
    )
    if exist "__pycache__" rd /s /q __pycache__
) else (
    echo 打包过程中出现错误，请检查日志文件
    exit /b 1
)

echo 按任意键退出...
pause
