@echo off
REM FreeP2W 打包脚本

echo ================================================================================
echo FreeP2W - 打包为 exe
echo ================================================================================
echo.

REM 检查 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo.
    echo 请先安装: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [2/3] 开始打包...
echo.
pyinstaller freep2w.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo.
echo 输出目录: dist\freep2w\
echo 可执行文件: dist\freep2w\freep2w.exe
echo.
echo ================================================================================
echo 使用方法:
echo   freep2w.exe input.pdf
echo   freep2w.exe input.pdf -o output.docx
echo ================================================================================
echo.

pause
