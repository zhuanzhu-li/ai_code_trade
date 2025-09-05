# 前端测试指南

本文档介绍如何在Windows系统上运行前端测试。

## 快速开始

### 方法1: 使用跨平台脚本（推荐）
```bash
# 进入前端目录
cd frontpoint

# 运行完整测试流程
npm run test:full
```

### 方法2: 使用Windows批处理文件
```bash
# 进入前端目录
cd frontpoint

# 运行Windows批处理脚本
npm run test:win
```

### 方法3: 分步运行
```bash
# 进入前端目录
cd frontpoint

# 1. 安装依赖
npm install

# 2. 类型检查
npm run type-check

# 3. 代码检查
npm run lint

# 4. 运行测试
npm run test:run

# 5. 生成覆盖率报告
npm run test:coverage
```

## 测试脚本说明

### 可用的测试命令

| 命令 | 描述 | 平台 |
|------|------|------|
| `npm run test` | 启动测试监视模式 | 所有平台 |
| `npm run test:run` | 运行一次测试 | 所有平台 |
| `npm run test:coverage` | 生成覆盖率报告 | 所有平台 |
| `npm run test:ui` | 打开测试UI界面 | 所有平台 |
| `npm run test:watch` | 监视模式运行测试 | 所有平台 |
| `npm run test:all` | 运行所有检查（类型+代码+测试+覆盖率） | 所有平台 |
| `npm run test:ci` | CI环境测试 | 所有平台 |
| `npm run test:win` | Windows批处理脚本 | Windows |
| `npm run test:unix` | Unix/Linux脚本 | Unix/Linux/macOS |
| `npm run test:cross` | 跨平台Node.js脚本 | 所有平台 |
| `npm run test:full` | 完整测试流程（推荐） | 所有平台 |

## 测试覆盖率

### 目标覆盖率
- **总体覆盖率**: 80%（配置在vitest.config.ts中）
- **分支覆盖率**: 80%
- **函数覆盖率**: 80%
- **行覆盖率**: 80%
- **语句覆盖率**: 80%

### 覆盖率检查功能

项目已集成自动化覆盖率检查功能，确保代码质量达标：

#### 1. 自动覆盖率检查
所有测试脚本都会自动检查覆盖率是否达到设定阈值：

```bash
# Windows批处理脚本会自动检查50%覆盖率阈值
npm run test:win

# 跨平台脚本也包含覆盖率检查
npm run test:full
```

#### 2. 独立覆盖率检查工具
项目提供了独立的覆盖率检查脚本 `scripts/check-coverage.js`：

```bash
# 检查是否达到50%覆盖率（默认）
node scripts/check-coverage.js

# 检查是否达到自定义阈值
node scripts/check-coverage.js 80
```

#### 3. 覆盖率检查输出示例
```
🔍 检查测试覆盖率...
📊 覆盖率报告:
   语句覆盖率: 85.2% (1024/1200)
   分支覆盖率: 78.5% (157/200)
   函数覆盖率: 92.3% (120/130)
   行覆盖率: 84.7% (1016/1200)
   平均覆盖率: 85.2%
✅ 覆盖率检查通过！平均覆盖率 85.2% >= 50%
```

#### 4. 覆盖率不达标处理
当覆盖率不达标时，脚本会：
- 显示详细的覆盖率统计
- 提供改进建议
- 以非零退出代码结束（用于CI/CD集成）

### 查看覆盖率报告
运行 `npm run test:coverage` 后，覆盖率报告会生成在 `coverage/` 目录：

- `coverage/index.html` - 在浏览器中打开查看详细报告
- `coverage/frontpoint/index.html` - 项目特定的覆盖率报告
- `coverage/coverage-final.json` - JSON格式原始数据（用于自动化检查）

## 测试文件结构

```
src/test/
├── setup.ts                 # 测试环境配置
├── api/                     # API测试
│   └── api.test.ts         # API客户端测试
├── stores/                  # 状态管理测试
│   ├── auth.test.ts        # 认证状态测试
│   ├── portfolio.test.ts   # 投资组合状态测试
│   ├── trading.test.ts     # 交易状态测试
│   ├── strategy.test.ts    # 策略状态测试
│   └── market.test.ts      # 市场数据状态测试
├── components/              # 组件测试
│   └── Layout.test.ts      # 布局组件测试
├── views/                   # 页面测试
│   └── Login.test.ts       # 登录页面测试
├── utils/                   # 工具函数测试
│   ├── format.test.ts      # 格式化工具测试
│   └── validation.test.ts  # 验证工具测试
└── README.md               # 测试文档
```

## 常见问题

### 1. 权限问题
如果遇到权限问题，请以管理员身份运行命令提示符或PowerShell。

### 2. Node.js版本问题
确保使用Node.js 18.0.0或更高版本：
```bash
node --version
```

### 3. 依赖安装问题
如果依赖安装失败，尝试清理缓存：
```bash
npm cache clean --force
npm install
```

### 4. 测试失败
如果测试失败，查看详细错误信息：
```bash
npm run test:run -- --reporter=verbose
```

### 5. 覆盖率不达标
如果覆盖率检查失败，可以：

#### 检查覆盖率详情
```bash
# 生成详细的覆盖率报告
npm run test:coverage

# 在浏览器中查看报告
open coverage/index.html  # macOS
start coverage/index.html # Windows
```

#### 分析覆盖率不足的原因
- **语句覆盖率低**: 检查是否有未执行的代码行
- **分支覆盖率低**: 检查是否有未测试的条件分支（if/else、switch等）
- **函数覆盖率低**: 检查是否有未调用的函数
- **行覆盖率低**: 检查是否有未覆盖的代码行

#### 提高覆盖率的方法
- 添加缺失的测试用例
- 测试错误处理分支
- 测试边界条件和异常情况
- 移除无用的死代码

#### 临时降低阈值（不推荐）
如果需要临时降低覆盖率阈值：
```bash
# 使用较低的阈值（如30%）
node scripts/check-coverage.js 30
```

## 调试测试

### 1. 使用测试UI
```bash
npm run test:ui
```
这会打开一个Web界面，可以：
- 查看测试结果
- 调试失败的测试
- 查看覆盖率详情

### 2. 监视模式
```bash
npm run test:watch
```
文件变化时自动重新运行测试。

### 3. 运行特定测试
```bash
# 运行特定测试文件
npm run test:run stores/auth.test.ts

# 运行特定测试套件
npm run test:run -- --grep "auth"
```

## 持续集成

### GitHub Actions
项目已配置GitHub Actions，每次推送都会自动运行测试。

### 本地CI测试
```bash
npm run test:ci
```

## 最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 遵循 "should ... when ..." 格式
- 分组相关的测试用例

### 2. 测试结构
```typescript
describe('ComponentName', () => {
  describe('when condition', () => {
    it('should do something', () => {
      // 测试逻辑
    })
  })
})
```

### 3. 断言
- 使用明确的断言
- 测试期望的行为和边界情况
- 验证错误处理和异常情况

### 4. 模拟
- 模拟外部依赖
- 使用 `vi.mock()` 模拟模块
- 模拟用户交互和API调用

## 性能优化

### 1. 并行测试
Vitest默认并行运行测试，提高执行速度。

### 2. 测试隔离
每个测试独立运行，避免相互影响。

### 3. 模拟优化
只模拟必要的依赖，减少模拟开销。

## 维护指南

### 1. 定期更新
- 保持测试框架版本更新
- 定期检查测试覆盖率
- 清理过时的测试用例

### 2. 代码审查
- 确保新代码有对应测试
- 检查测试质量和覆盖率
- 验证测试的可靠性

### 3. 文档更新
- 及时更新测试文档
- 记录测试策略变更
- 维护测试最佳实践

## 支持

如果遇到问题，请：
1. 查看本文档的常见问题部分
2. 检查测试日志和错误信息
3. 参考项目README文件
4. 提交Issue到项目仓库
