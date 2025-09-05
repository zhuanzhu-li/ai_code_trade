#!/bin/bash

# 前端测试运行脚本

echo "🚀 开始运行前端测试..."

# 检查Node.js版本
echo "📋 检查Node.js版本..."
node --version
npm --version

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 运行类型检查
echo "🔍 运行TypeScript类型检查..."
npm run type-check

if [ $? -ne 0 ]; then
    echo "❌ 类型检查失败"
    exit 1
fi

# 运行ESLint检查
echo "🔍 运行ESLint检查..."
npm run lint

if [ $? -ne 0 ]; then
    echo "❌ ESLint检查失败"
    exit 1
fi

# 运行测试
echo "🧪 运行测试..."
npm run test:run

if [ $? -ne 0 ]; then
    echo "❌ 测试失败"
    exit 1
fi

# 生成覆盖率报告
echo "📊 生成覆盖率报告..."
npm run test:coverage

if [ $? -ne 0 ]; then
    echo "❌ 覆盖率报告生成失败"
    exit 1
fi

echo "✅ 所有测试通过！"
echo "📈 覆盖率报告已生成到 coverage/ 目录"

# 检查覆盖率是否达到目标
echo "🎯 检查覆盖率目标..."

# 这里可以添加覆盖率检查逻辑
# 例如检查覆盖率是否达到80%

echo "🎉 测试完成！"
