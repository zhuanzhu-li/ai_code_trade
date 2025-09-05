# 前端测试文档

本文档介绍了前端项目的测试配置、运行方式和测试覆盖情况。

## 测试框架

- **测试运行器**: Vitest
- **组件测试**: Vue Test Utils
- **模拟库**: Vitest Mock
- **覆盖率**: @vitest/coverage-v8

## 测试结构

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

## 运行测试

### 开发模式
```bash
npm run test
```

### 运行一次
```bash
npm run test:run
```

### 生成覆盖率报告
```bash
npm run test:coverage
```

### 测试UI界面
```bash
npm run test:ui
```

## 测试覆盖率目标

- **总体覆盖率**: 80%
- **分支覆盖率**: 80%
- **函数覆盖率**: 80%
- **行覆盖率**: 80%
- **语句覆盖率**: 80%

## 测试类型

### 1. API测试
- 测试API客户端的请求和响应处理
- 模拟HTTP请求和错误情况
- 验证请求参数和响应数据格式

### 2. 状态管理测试
- 测试Pinia store的状态变化
- 验证计算属性的正确性
- 测试异步操作和错误处理

### 3. 组件测试
- 测试Vue组件的渲染和交互
- 验证props和事件处理
- 测试用户交互和状态更新

### 4. 工具函数测试
- 测试纯函数的输入输出
- 验证边界条件和错误处理
- 确保函数的正确性和稳定性

## 测试最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 遵循 "should ... when ..." 格式
- 分组相关的测试用例

### 2. 测试结构
- 使用 `describe` 分组相关测试
- 使用 `it` 或 `test` 定义单个测试
- 使用 `beforeEach` 和 `afterEach` 设置和清理

### 3. 断言
- 使用明确的断言
- 测试期望的行为和边界情况
- 验证错误处理和异常情况

### 4. 模拟
- 模拟外部依赖
- 使用 `vi.mock()` 模拟模块
- 模拟用户交互和API调用

## 覆盖率报告

运行 `npm run test:coverage` 后，会在 `coverage/` 目录下生成详细的覆盖率报告：

- `coverage/index.html` - HTML格式的覆盖率报告
- `coverage/lcov-report/index.html` - LCOV格式的报告
- `coverage/coverage-final.json` - JSON格式的原始数据

## 持续集成

测试配置已集成到CI/CD流程中：

1. 每次提交都会运行测试
2. 覆盖率低于80%会阻止合并
3. 测试失败会阻止部署

## 调试测试

### 1. 使用测试UI
```bash
npm run test:ui
```
打开浏览器界面，可以：
- 查看测试结果
- 调试失败的测试
- 查看覆盖率详情

### 2. 调试特定测试
```bash
npm run test -- --reporter=verbose
```

### 3. 运行特定测试文件
```bash
npm run test stores/auth.test.ts
```

## 添加新测试

### 1. 创建测试文件
在相应的目录下创建 `.test.ts` 文件

### 2. 编写测试用例
```typescript
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('should render correctly', () => {
    // 测试逻辑
  })
})
```

### 3. 运行测试
```bash
npm run test
```

## 常见问题

### 1. 测试环境配置
确保 `vitest.config.ts` 和 `src/test/setup.ts` 配置正确

### 2. 模拟问题
检查模拟是否正确设置，特别是外部依赖

### 3. 异步测试
使用 `async/await` 或 `Promise` 处理异步操作

### 4. 组件测试
确保正确设置Vue Test Utils的全局配置

## 性能优化

### 1. 并行测试
Vitest默认并行运行测试，提高执行速度

### 2. 测试隔离
每个测试独立运行，避免相互影响

### 3. 模拟优化
只模拟必要的依赖，减少模拟开销

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
