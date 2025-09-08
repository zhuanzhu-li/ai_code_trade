@echo off
REM 数据库迁移工具 - Windows批处理脚本
REM 用法: migrate.bat [command] [version]

setlocal enabledelayedexpansion

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH中
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查是否安装了必要的依赖
python -c "import pymysql" >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到pymysql模块，请运行: pip install pymysql
    exit /b 1
)

REM 执行Python迁移脚本
python migrate.py %*

endlocal
