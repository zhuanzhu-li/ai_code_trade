# AI量化交易系统

一个基于Python Flask + Vue3的现代化量化交易系统，采用前后端分离架构，支持多种交易策略、实时市场数据获取、风险管理和投资组合管理。

## 🚀 项目特性

### 核心功能
- 🏦 **投资组合管理**: 创建和管理多个投资组合
- 📊 **实时市场数据**: 支持Yahoo Finance和加密货币交易所数据
- 🤖 **智能交易策略**: 内置动量策略和均值回归策略
- ⚠️ **风险管理**: 多层次风险控制和警报系统
- 📈 **交易记录**: 完整的交易历史记录和统计分析
- 🔐 **用户认证**: JWT token认证系统
- 🌐 **RESTful API**: 完整的REST API接口
- 📱 **现代化前端**: Vue3 + TypeScript + Element Plus

### 技术栈

#### 后端 (endpoint/)
- **框架**: Flask 2.3.3
- **数据库**: MySQL 8.0 + SQLAlchemy ORM
- **认证**: JWT Token
- **数据获取**: yfinance, ccxt
- **技术分析**: pandas, numpy, ta-lib
- **任务调度**: APScheduler
- **API**: RESTful API + CORS支持

#### 前端 (frontpoint/)
- **框架**: Vue 3.5.13 + TypeScript
- **UI库**: Element Plus 2.8.8
- **状态管理**: Pinia 2.2.6
- **路由**: Vue Router 4.5.0
- **图表**: ECharts 5.5.1
- **构建工具**: Vite 6.0.7
- **HTTP客户端**: Axios 1.7.9

## 📁 项目结构

```
ai_code_trade/
├── endpoint/                 # 后端API服务
│   ├── app/                 # Flask应用主目录
│   ├── models/              # 数据库模型
│   ├── services/            # 业务逻辑服务
│   ├── strategies/          # 交易策略
│   ├── utils/               # 工具类
│   ├── tests/               # 测试文件
│   ├── migrations/          # 数据库迁移
│   ├── logs/                # 日志文件
│   ├── requirements.txt     # Python依赖
│   ├── setup.py            # 安装脚本
│   └── run.py              # 启动脚本
├── frontpoint/              # 前端应用
│   ├── src/                # 源代码
│   │   ├── api/            # API服务层
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # 状态管理
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── types/          # 类型定义
│   ├── package.json        # Node.js依赖
│   └── vite.config.ts      # Vite配置
├── README.md               # 项目说明文档
└── .gitignore             # Git忽略文件
```

## 🛠️ 快速开始

### 环境要求

- **后端**: Python 3.8+, MySQL 8.0+
- **前端**: Node.js 18.0+, npm 8.0+

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai_code_trade
```

### 2. 后端设置

```bash
# 进入后端目录
cd endpoint

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑.env文件，设置数据库连接信息

# 初始化数据库
python setup.py

# 启动后端服务
python run.py
```

后端服务将在 http://localhost:5000 启动

### 3. 前端设置

```bash
# 进入前端目录
cd frontpoint

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

## 📖 使用指南

### 1. 用户注册和登录
- 访问前端应用，注册新用户
- 使用用户名和密码登录系统

### 2. 创建投资组合
- 在投资组合页面创建新的投资组合
- 设置初始资金和风险参数

### 3. 配置交易策略
- 选择动量策略或均值回归策略
- 调整策略参数（如RSI周期、持仓大小等）

### 4. 开始交易
- 在交易页面执行买卖操作
- 监控实时市场数据和持仓情况

### 5. 风险管理
- 设置风险规则和警报
- 监控投资组合的风险指标

## 🔧 开发指南

### 后端开发

#### 添加新的交易策略
1. 继承 `BaseStrategy` 类
2. 实现 `generate_signal` 和 `calculate_position_size` 方法
3. 在策略管理中添加新策略类型

```python
from strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def generate_signal(self, market_data):
        # 实现信号生成逻辑
        pass
    
    def calculate_position_size(self, signal, portfolio_value, current_price):
        # 实现持仓大小计算逻辑
        pass
```

#### 添加新的数据源
1. 在 `DataService` 中添加新的数据获取方法
2. 实现数据格式标准化
3. 添加错误处理和重试机制

### 前端开发

#### 添加新页面
1. 在 `src/views/` 中创建新的Vue组件
2. 在 `src/router/index.ts` 中添加路由配置
3. 在 `src/stores/` 中添加相关的状态管理

#### 添加新的API接口
1. 在 `src/api/index.ts` 中添加新的API方法
2. 在相应的store中调用API方法
3. 在组件中使用store中的数据

## 🚀 部署指南

### 后端部署

#### 使用Gunicorn部署
```bash
# 安装Gunicorn
pip install gunicorn

# 运行生产服务器
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### 使用Docker部署
```bash
# 构建镜像
docker build -t quant-trading-backend .

# 运行容器
docker run -p 5000:5000 quant-trading-backend
```

### 前端部署

#### 构建生产版本
```bash
# 构建
npm run build

# 预览
npm run preview
```

#### 使用Nginx部署
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

## 📊 API文档

### 主要接口

#### 用户管理
- `POST /api/users` - 创建用户
- `GET /api/users/{user_id}` - 获取用户信息
- `POST /api/auth/login` - 用户登录

#### 投资组合管理
- `GET /api/portfolios` - 获取投资组合列表
- `POST /api/portfolios` - 创建投资组合
- `PUT /api/portfolios/{id}` - 更新投资组合
- `DELETE /api/portfolios/{id}` - 删除投资组合

#### 交易管理
- `POST /api/trades` - 执行交易
- `GET /api/trades` - 获取交易记录
- `GET /api/trades/{id}` - 获取交易详情

#### 策略管理
- `GET /api/strategies` - 获取策略列表
- `POST /api/strategies` - 创建策略
- `POST /api/strategies/{id}/execute` - 执行策略

#### 市场数据
- `GET /api/market-data/{symbol}` - 获取市场数据
- `GET /api/market-data/{symbol}/latest` - 获取最新价格

详细的API文档请参考 [endpoint/API_DOCUMENTATION.md](endpoint/API_DOCUMENTATION.md)

## 🧪 测试

### 后端测试
```bash
cd endpoint
python -m pytest tests/
```

### 前端测试
```bash
cd frontpoint
npm run test
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## ⚠️ 免责声明

本软件仅供学习和研究目的。使用本软件进行实际交易的风险由用户自行承担。作者不对任何投资损失负责。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/ai-code-trade

---

**重要提醒**: 本系统仅供学习和研究使用，实际交易存在风险，请谨慎使用并遵守相关法律法规。
