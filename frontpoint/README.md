# 量化交易系统前端

基于 Vue3 + TypeScript 的现代化量化交易系统前端应用。

## 功能特性

### 核心功能
- 🏦 **投资组合管理**: 创建和管理多个投资组合
- 📊 **实时市场数据**: 支持多种标的的实时价格和K线图
- 🤖 **交易策略**: 内置动量策略和均值回归策略
- ⚠️ **风险管理**: 多层次风险控制和警报系统
- 📈 **交易记录**: 完整的交易历史记录和统计分析
- 🔐 **用户认证**: JWT token认证系统
- 📱 **响应式设计**: 支持桌面端和移动端

### 技术特性
- ⚡ **Vue 3**: 使用 Composition API 和 `<script setup>`
- 🔷 **TypeScript**: 完整的类型支持
- 🎨 **Element Plus**: 现代化的UI组件库
- 📊 **ECharts**: 强大的图表库
- 🗂️ **Pinia**: 状态管理
- 🛣️ **Vue Router**: 路由管理
- 🔧 **Vite**: 快速的构建工具

## 项目结构

```
frontpoint/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API服务层
│   │   └── index.ts       # API客户端
│   ├── components/        # 公共组件
│   │   └── Layout/        # 布局组件
│   ├── stores/            # 状态管理
│   │   ├── auth.ts        # 认证状态
│   │   ├── portfolio.ts   # 投资组合状态
│   │   ├── trading.ts     # 交易状态
│   │   ├── strategy.ts    # 策略状态
│   │   └── market.ts      # 市场数据状态
│   ├── styles/            # 全局样式
│   │   └── index.scss     # 主样式文件
│   ├── types/             # 类型定义
│   │   └── index.ts       # 通用类型
│   ├── views/             # 页面组件
│   │   ├── Login.vue      # 登录页
│   │   ├── Register.vue   # 注册页
│   │   ├── Dashboard.vue  # 仪表板
│   │   ├── Portfolios.vue # 投资组合管理
│   │   ├── Trading.vue    # 交易管理
│   │   ├── Strategies.vue # 策略管理
│   │   ├── Market.vue     # 市场数据
│   │   ├── Risk.vue       # 风险管理
│   │   └── Settings.vue   # 系统设置
│   ├── router/            # 路由配置
│   │   └── index.ts       # 路由定义
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── package.json           # 项目配置
├── vite.config.ts         # Vite配置
├── tsconfig.json          # TypeScript配置
└── README.md             # 项目文档
```

## 安装和运行

### 环境要求

- Node.js 16.0+
- npm 7.0+ 或 yarn 1.22+

### 安装依赖

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install
```

### 开发环境

```bash
# 启动开发服务器
npm run dev

# 或使用 yarn
yarn dev
```

访问 http://localhost:3000 查看应用。

### 构建生产版本

```bash
# 构建生产版本
npm run build

# 或使用 yarn
yarn build
```

### 预览生产版本

```bash
# 预览生产版本
npm run preview

# 或使用 yarn
yarn preview
```

## 开发指南

### 代码规范

项目使用 ESLint 进行代码检查：

```bash
# 检查代码
npm run lint

# 自动修复
npm run lint --fix
```

### 类型检查

```bash
# TypeScript 类型检查
npm run type-check
```

### 测试

项目包含完整的单元测试套件，支持自动化覆盖率检查：

```bash
# 运行所有测试
npm run test:run

# 生成覆盖率报告
npm run test:coverage

# 运行完整测试流程（推荐）
npm run test:full

# Windows用户可以使用批处理脚本
npm run test:win
```

#### 覆盖率检查

项目集成了自动化覆盖率检查功能：

- **目标覆盖率**: 项目配置为80%，测试脚本检查50%阈值
- **自动检查**: 所有测试脚本都会自动验证覆盖率
- **详细报告**: 生成HTML格式的覆盖率报告

**相关文档:**
- [TESTING.md](./TESTING.md) - 详细测试指南
- [SCRIPTS.md](./SCRIPTS.md) - 脚本功能说明

### 项目配置

#### Vite 配置

项目使用 Vite 作为构建工具，配置文件为 `vite.config.ts`：

- 自动导入 Element Plus 组件
- 路径别名 `@` 指向 `src` 目录
- 开发环境代理 API 请求到后端服务

#### TypeScript 配置

TypeScript 配置文件为 `tsconfig.json`：

- 严格模式启用
- 支持 Vue 单文件组件
- 路径映射配置

### 状态管理

使用 Pinia 进行状态管理，主要 store：

- `useAuthStore`: 用户认证状态
- `usePortfolioStore`: 投资组合状态
- `useTradingStore`: 交易状态
- `useStrategyStore`: 策略状态
- `useMarketStore`: 市场数据状态

### API 集成

所有 API 请求通过 `src/api/index.ts` 中的 `apiClient` 进行：

- 自动添加 JWT token
- 统一错误处理
- 请求/响应拦截器

### 路由配置

路由配置在 `src/router/index.ts`：

- 路由守卫保护需要认证的页面
- 自动重定向到登录页
- 面包屑导航支持

## 部署指南

### 构建配置

1. 确保后端 API 服务正在运行
2. 修改 `vite.config.ts` 中的代理配置（如需要）
3. 运行构建命令

### 环境变量

创建 `.env` 文件配置环境变量：

```env
# API 基础URL
VITE_API_BASE_URL=http://localhost:5000/api

# 应用标题
VITE_APP_TITLE=量化交易系统
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/quant-trading-frontend

---

**免责声明**: 本软件仅供学习和研究目的。使用本软件进行实际交易的风险由用户自行承担。作者不对任何投资损失负责。
