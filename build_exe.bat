@echo off
echo ===== 文件快传应用打包工具 =====
echo.

REM 检查 Python 是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python，请确保安装了 Python 3.8-3.13
    exit /b 1
)

echo 确保安装所需依赖...
pip install -r requirements.txt

echo.
echo 开始打包应用程序...
echo.

REM 确保上传目录存在于打包前
if not exist uploads mkdir uploads

REM 使用自定义spec文件运行PyInstaller
pyinstaller --clean FileTransfer.spec

echo.
if %errorlevel% equ 0 (
    echo ===== 打包成功! =====
    echo 可执行文件位于: dist\FileTransfer.exe
    echo.
) else (
    echo 打包过程中出现错误，请检查上面的输出信息
    exit /b 1
)

echo 打包完成后测试注意事项:
echo 1. 检查界面是否正常显示
echo 2. 测试文件上传和下载功能
echo 3. 确认实时文件列表更新是否正常
echo.

pause 