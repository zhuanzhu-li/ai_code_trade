# 部署指南

本指南将帮助您部署量化交易系统前端应用。

## 部署方式

### 1. 传统部署

#### 环境要求

- Node.js 16.0+
- npm 7.0+ 或 yarn 1.22+
- Nginx 1.18+

#### 部署步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd frontpoint
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量**
   ```bash
   cp env.example .env
   # 编辑 .env 文件，配置 API 地址等
   ```

4. **构建应用**
   ```bash
   npm run build
   ```

5. **配置 Nginx**
   ```bash
   # 复制 nginx 配置
   sudo cp nginx.conf /etc/nginx/sites-available/quant-trading
   sudo ln -s /etc/nginx/sites-available/quant-trading /etc/nginx/sites-enabled/
   
   # 修改配置中的路径和域名
   sudo nano /etc/nginx/sites-available/quant-trading
   
   # 重启 Nginx
   sudo systemctl restart nginx
   ```

6. **部署文件**
   ```bash
   # 将 dist 目录内容复制到 Nginx 根目录
   sudo cp -r dist/* /var/www/html/
   ```

### 2. Docker 部署

#### 使用 Docker Compose（推荐）

1. **准备配置文件**
   ```bash
   # 复制环境变量文件
   cp env.example .env
   
   # 编辑 docker-compose.yml，配置服务
   nano docker-compose.yml
   ```

2. **启动服务**
   ```bash
   # 构建并启动所有服务
   docker-compose up -d --build
   
   # 查看服务状态
   docker-compose ps
   ```

3. **查看日志**
   ```bash
   # 查看所有服务日志
   docker-compose logs -f
   
   # 查看特定服务日志
   docker-compose logs -f frontend
   ```

#### 单独部署前端

1. **构建镜像**
   ```bash
   docker build -t quant-trading-frontend .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name quant-trading-frontend \
     -p 3000:80 \
     quant-trading-frontend
   ```

### 3. 云平台部署

#### Vercel 部署

1. **安装 Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **部署**
   ```bash
   vercel --prod
   ```

3. **配置环境变量**
   - 在 Vercel 控制台添加环境变量
   - 重新部署应用

#### Netlify 部署

1. **构建命令**
   ```bash
   npm run build
   ```

2. **发布目录**
   ```
   dist
   ```

3. **环境变量**
   - 在 Netlify 控制台添加环境变量

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | 后端 API 地址 | http://localhost:5000/api |
| VITE_APP_TITLE | 应用标题 | 量化交易系统 |
| VITE_APP_VERSION | 应用版本 | 1.0.0 |
| VITE_NODE_ENV | 环境模式 | development |
| VITE_ENABLE_MOCK | 是否启用模拟数据 | false |
| VITE_ENABLE_DEBUG | 是否启用调试模式 | true |

### Nginx 配置

主要配置项：

- **静态资源缓存**: 1年
- **Gzip 压缩**: 启用
- **安全头**: 已配置
- **API 代理**: 代理到后端服务
- **SPA 支持**: 所有路由重定向到 index.html

### Docker 配置

- **多阶段构建**: 减少镜像大小
- **Nginx 基础镜像**: Alpine Linux
- **健康检查**: /health 端点
- **网络配置**: 与后端服务通信

## 性能优化

### 构建优化

1. **代码分割**
   ```typescript
   // vite.config.ts
   build: {
     rollupOptions: {
       output: {
         manualChunks: {
           'element-plus': ['element-plus'],
           'echarts': ['echarts', 'vue-echarts'],
           'vue-vendor': ['vue', 'vue-router', 'pinia']
         }
       }
     }
   }
   ```

2. **资源压缩**
   - Gzip 压缩
   - 图片优化
   - 字体优化

### 运行时优化

1. **缓存策略**
   - 静态资源长期缓存
   - API 数据适当缓存

2. **懒加载**
   - 路由懒加载
   - 组件懒加载

## 监控和日志

### 应用监控

1. **性能监控**
   ```typescript
   // 添加性能监控
   import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'
   
   getCLS(console.log)
   getFID(console.log)
   getFCP(console.log)
   getLCP(console.log)
   getTTFB(console.log)
   ```

2. **错误监控**
   ```typescript
   // 添加错误监控
   window.addEventListener('error', (event) => {
     console.error('Global error:', event.error)
   })
   ```

### 日志配置

1. **Nginx 日志**
   ```nginx
   access_log /var/log/nginx/access.log main;
   error_log /var/log/nginx/error.log;
   ```

2. **Docker 日志**
   ```bash
   # 查看容器日志
   docker logs quant-trading-frontend
   
   # 实时查看日志
   docker logs -f quant-trading-frontend
   ```

## 安全配置

### HTTPS 配置

1. **获取 SSL 证书**
   ```bash
   # 使用 Let's Encrypt
   sudo certbot --nginx -d your-domain.com
   ```

2. **Nginx HTTPS 配置**
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       # SSL 配置
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
       ssl_prefer_server_ciphers off;
   }
   ```

### 安全头配置

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

## 故障排除

### 常见问题

1. **API 请求失败**
   - 检查后端服务是否运行
   - 检查 API 地址配置
   - 检查网络连接

2. **页面空白**
   - 检查控制台错误
   - 检查路由配置
   - 检查构建产物

3. **样式问题**
   - 检查 CSS 文件加载
   - 检查 Element Plus 配置
   - 检查浏览器兼容性

### 调试方法

1. **开发模式调试**
   ```bash
   npm run dev
   # 访问 http://localhost:3000
   ```

2. **生产模式调试**
   ```bash
   npm run build
   npm run preview
   # 访问 http://localhost:4173
   ```

3. **Docker 调试**
   ```bash
   # 进入容器
   docker exec -it quant-trading-frontend sh
   
   # 查看 Nginx 配置
   nginx -t
   
   # 查看日志
   tail -f /var/log/nginx/error.log
   ```

## 更新和维护

### 应用更新

1. **代码更新**
   ```bash
   git pull origin main
   npm install
   npm run build
   # 重新部署
   ```

2. **Docker 更新**
   ```bash
   docker-compose pull
   docker-compose up -d --build
   ```

### 备份策略

1. **配置文件备份**
   ```bash
   # 备份 Nginx 配置
   sudo cp /etc/nginx/sites-available/quant-trading /backup/
   
   # 备份环境变量
   cp .env /backup/
   ```

2. **数据备份**
   ```bash
   # 备份构建产物
   tar -czf frontend-backup-$(date +%Y%m%d).tar.gz dist/
   ```

## 扩展配置

### CDN 配置

1. **静态资源 CDN**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     base: 'https://cdn.your-domain.com/',
     build: {
       assetsDir: 'assets'
     }
   })
   ```

2. **API CDN**
   ```nginx
   location /api {
       proxy_pass https://api.your-domain.com;
   }
   ```

### 多环境部署

1. **环境配置**
   ```bash
   # 开发环境
   cp env.example .env.development
   
   # 测试环境
   cp env.example .env.staging
   
   # 生产环境
   cp env.example .env.production
   ```

2. **构建脚本**
   ```json
   {
     "scripts": {
       "build:dev": "vite build --mode development",
       "build:staging": "vite build --mode staging",
       "build:prod": "vite build --mode production"
     }
   }
   ```
