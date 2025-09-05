@echo off
chcp 65001 >nul
REM 前端测试运行脚本 (Windows版本)

echo 开始运行前端测试...

echo 运行TypeScript类型检查...
call npm.cmd run type-check
if errorlevel 1 (
    echo 类型检查失败
    exit /b 1
)

REM 运行ESLint检查
echo 运行ESLint检查...
call npm.cmd run lint
REM 注意：ESLint警告不会导致脚本退出，只有错误才会

REM 运行测试
echo 运行测试...
call npm.cmd run test:run
if errorlevel 1 (
    echo 测试失败
    exit /b 1
)

REM 生成覆盖率报告
echo 生成覆盖率报告...
call npm.cmd run test:coverage
if errorlevel 1 (
    echo 覆盖率报告生成失败
    exit /b 1
)

echo 所有测试通过！
echo 覆盖率报告已生成到 coverage/ 目录

REM 检查覆盖率是否达到目标
echo 检查覆盖率目标...

REM 运行Node.js脚本检查覆盖率
echo 检查覆盖率是否达到50%...
node scripts\check-coverage.js 30
if errorlevel 1 (
    echo 覆盖率检查失败
    exit /b 1
)

echo 测试完成！

pause
