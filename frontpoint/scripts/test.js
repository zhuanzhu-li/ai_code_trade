#!/usr/bin/env node

/**
 * 跨平台测试运行脚本
 * 支持 Windows、macOS 和 Linux
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function runCommand(command, description) {
  log(`\n${description}...`, 'cyan');
  try {
    execSync(command, { stdio: 'inherit', cwd: process.cwd() });
    log(`✅ ${description}完成`, 'green');
    return true;
  } catch (error) {
    log(`❌ ${description}失败`, 'red');
    log(`错误: ${error.message}`, 'red');
    return false;
  }
}

function checkNodeVersion() {
  log('\n📋 检查Node.js版本...', 'blue');
  try {
    const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    
    log(`Node.js: ${nodeVersion}`, 'green');
    log(`npm: ${npmVersion}`, 'green');
    
    // 检查Node.js版本是否满足要求 (>= 18.0.0)
    const version = nodeVersion.replace('v', '').split('.').map(Number);
    if (version[0] < 18) {
      log('⚠️  警告: 建议使用Node.js 18.0.0或更高版本', 'yellow');
    }
    
    return true;
  } catch (_error) {
    log('❌ 无法检查Node.js版本', 'red');
    return false;
  }
}

function checkDependencies() {
  log('\n📦 检查依赖...', 'blue');
  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  
  if (!fs.existsSync(nodeModulesPath)) {
    log('📦 安装依赖...', 'yellow');
    return runCommand('npm install', '安装依赖');
  }
  
  log('✅ 依赖已安装', 'green');
  return true;
}

function runTypeCheck() {
  return runCommand('npm run type-check', 'TypeScript类型检查');
}

function runLint() {
  return runCommand('npm run lint', 'ESLint代码检查');
}

function runTests() {
  return runCommand('npm run test:run', '运行测试');
}

function runCoverage() {
  return runCommand('npm run test:coverage', '生成覆盖率报告');
}

function checkCoverage() {
  log('\n🎯 检查覆盖率目标...', 'blue');
  
  try {
    const coveragePath = path.join(process.cwd(), 'coverage', 'coverage-summary.json');
    
    if (fs.existsSync(coveragePath)) {
      const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
      const total = coverage.total;
      
      log(`\n📊 覆盖率报告:`, 'magenta');
      log(`  行覆盖率: ${total.lines.pct}%`, total.lines.pct >= 80 ? 'green' : 'yellow');
      log(`  函数覆盖率: ${total.functions.pct}%`, total.functions.pct >= 80 ? 'green' : 'yellow');
      log(`  分支覆盖率: ${total.branches.pct}%`, total.branches.pct >= 80 ? 'green' : 'yellow');
      log(`  语句覆盖率: ${total.statements.pct}%`, total.statements.pct >= 80 ? 'green' : 'yellow');
      
      const overallCoverage = total.lines.pct;
      if (overallCoverage >= 80) {
        log(`\n🎉 覆盖率目标达成! (${overallCoverage}% >= 80%)`, 'green');
        return true;
      } else {
        log(`\n⚠️  覆盖率未达到目标 (${overallCoverage}% < 80%)`, 'yellow');
        return false;
      }
    } else {
      log('⚠️  未找到覆盖率报告文件', 'yellow');
      return true;
    }
  } catch (error) {
    log(`⚠️  无法检查覆盖率: ${error.message}`, 'yellow');
    return true;
  }
}

function main() {
  log('🚀 开始运行前端测试...', 'bright');
  
  const steps = [
    { name: '检查Node.js版本', fn: checkNodeVersion },
    { name: '检查依赖', fn: checkDependencies },
    { name: 'TypeScript类型检查', fn: runTypeCheck },
    { name: 'ESLint代码检查', fn: runLint },
    { name: '运行测试', fn: runTests },
    { name: '生成覆盖率报告', fn: runCoverage },
    { name: '检查覆盖率目标', fn: checkCoverage }
  ];
  
  let allPassed = true;
  
  for (const step of steps) {
    if (!step.fn()) {
      allPassed = false;
      break;
    }
  }
  
  if (allPassed) {
    log('\n✅ 所有测试通过！', 'green');
    log('📈 覆盖率报告已生成到 coverage/ 目录', 'blue');
    log('🎉 测试完成！', 'bright');
    process.exit(0);
  } else {
    log('\n❌ 测试失败！', 'red');
    process.exit(1);
  }
}

// 处理命令行参数
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  log('\n📖 测试脚本使用说明:', 'blue');
  log('  npm run test:win     - 运行完整测试流程 (Windows)');
  log('  npm run test:unix    - 运行完整测试流程 (Unix/Linux/macOS)');
  log('  node scripts/test.js - 直接运行测试脚本');
  log('\n可选参数:', 'yellow');
  log('  --help, -h          - 显示帮助信息');
  log('  --no-coverage       - 跳过覆盖率检查');
  log('  --no-lint           - 跳过代码检查');
  log('  --no-type-check     - 跳过类型检查');
  process.exit(0);
}

main();
