# 脚本说明文档

本文档详细说明项目中所有可用的npm脚本和测试脚本的功能。

## NPM 脚本

### 开发相关脚本

| 脚本 | 命令 | 描述 |
|------|------|------|
| `dev` | `vite` | 启动开发服务器 |
| `build` | `vue-tsc && vite build` | 构建生产版本（包含类型检查） |
| `preview` | `vite preview` | 预览生产版本 |

### 代码质量脚本

| 脚本 | 命令 | 描述 |
|------|------|------|
| `lint` | `eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix` | 运行ESLint检查并自动修复 |
| `type-check` | `vue-tsc --noEmit` | TypeScript类型检查 |

### 测试脚本

#### 基础测试脚本
| 脚本 | 命令 | 描述 |
|------|------|------|
| `test` | `npx vitest` | 启动测试监视模式 |
| `test:run` | `npx vitest run` | 运行一次测试 |
| `test:ui` | `npx vitest --ui` | 启动测试UI界面 |
| `test:watch` | `npx vitest --watch` | 监视模式运行测试 |

#### 覆盖率测试脚本
| 脚本 | 命令 | 描述 |
|------|------|------|
| `test:coverage` | `npx vitest run --coverage` | 运行测试并生成覆盖率报告 |
| `test:ci` | `npx vitest run --reporter=verbose --coverage` | CI环境测试（详细输出） |

#### 综合测试脚本
| 脚本 | 命令 | 描述 |
|------|------|------|
| `test:all` | `npm run type-check && npm run lint && npm run test:coverage` | 运行完整检查流程 |
| `test:full` | `node scripts/test.js` | 跨平台完整测试脚本 |
| `test:win` | `scripts\\test.bat` | Windows批处理测试脚本 |
| `test:unix` | `scripts/test.sh` | Unix/Linux测试脚本 |
| `test:cross` | `node scripts/test.js` | 跨平台Node.js测试脚本 |

### 维护脚本

| 脚本 | 命令 | 描述 |
|------|------|------|
| `clean` | `rimraf node_modules package-lock.json dist` | 清理项目文件 |
| `reinstall` | `npm run clean && npm install` | 重新安装依赖 |

## 测试脚本详解

### 1. Windows批处理脚本 (`scripts/test.bat`)

**功能特性:**
- 自动检查Node.js和npm版本
- 自动安装缺失的依赖
- 运行TypeScript类型检查
- 运行ESLint代码检查
- 运行单元测试
- 生成覆盖率报告
- **自动检查覆盖率是否达到50%阈值**
- 支持中文输出和错误处理

**使用方法:**
```bash
# 通过npm运行
npm run test:win

# 或直接运行
cd frontpoint
scripts\test.bat
```

**覆盖率检查功能:**
- 自动调用 `scripts/check-coverage.js` 检查覆盖率
- 如果覆盖率低于50%，脚本会失败并显示详细信息
- 提供改进建议

### 2. 覆盖率检查脚本 (`scripts/check-coverage.js`)

**功能特性:**
- 解析 `coverage/coverage-final.json` 文件
- 计算语句、分支、函数、行覆盖率
- 计算平均覆盖率
- 支持自定义阈值
- 提供详细的覆盖率统计
- 以适当的退出代码结束（0=成功，1=失败）

**使用方法:**
```bash
# 使用默认阈值（50%）
node scripts/check-coverage.js

# 使用自定义阈值
node scripts/check-coverage.js 80

# 检查是否达到项目配置的80%阈值
node scripts/check-coverage.js 80
```

**输出示例:**
```
🔍 检查测试覆盖率...
📊 覆盖率报告:
   语句覆盖率: 37.13% (504/1357)
   分支覆盖率: 82.21% (134/163)
   函数覆盖率: 57.45% (27/47)
   行覆盖率: 37.13% (504/1357)
   平均覆盖率: 53.48%
✅ 覆盖率检查通过！平均覆盖率 53.48% >= 50%
```

### 3. 跨平台测试脚本 (`scripts/test.js`)

**功能特性:**
- 支持Windows、macOS、Linux
- Node.js实现，无需额外依赖
- 包含完整的测试流程
- 自动错误处理和退出代码
- 彩色输出支持

## 覆盖率配置

### Vitest配置 (`vitest.config.ts`)

项目在 `vitest.config.ts` 中配置了覆盖率阈值：

```typescript
coverage: {
  provider: 'v8',
  reporter: ['text', 'json', 'html'],
  thresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

### 覆盖率文件排除

以下文件和目录被排除在覆盖率统计之外：
- `node_modules/`
- `src/test/`
- `**/*.d.ts`
- `**/*.config.*`
- `**/coverage/**`
- `**/dist/**`

## 最佳实践

### 1. 日常开发
```bash
# 开发时运行监视模式
npm run test:watch

# 提交前运行完整检查
npm run test:all
```

### 2. 持续集成
```bash
# CI环境使用详细输出
npm run test:ci

# 或使用跨平台脚本
npm run test:full
```

### 3. 覆盖率监控
```bash
# 定期检查覆盖率
npm run test:coverage

# 在浏览器中查看详细报告
open coverage/index.html
```

## 故障排除

### 1. 覆盖率检查失败
```bash
# 查看详细覆盖率报告
npm run test:coverage
open coverage/index.html

# 使用较低阈值临时通过（不推荐）
node scripts/check-coverage.js 30
```

### 2. 脚本执行失败
```bash
# 检查Node.js版本
node --version

# 重新安装依赖
npm run reinstall

# 清理并重新开始
npm run clean
npm install
```

### 3. Windows特定问题
- 确保以管理员身份运行命令提示符
- 检查PowerShell执行策略
- 确保npm.cmd在PATH中

## 扩展脚本

如需添加新的测试脚本，请：

1. 在 `scripts/` 目录创建脚本文件
2. 在 `package.json` 中添加对应的npm脚本
3. 更新本文档
4. 确保脚本包含适当的错误处理和退出代码

## 相关文档

- [TESTING.md](./TESTING.md) - 详细测试指南
- [README.md](./README.md) - 项目总览
- [vitest.config.ts](./vitest.config.ts) - 测试配置
