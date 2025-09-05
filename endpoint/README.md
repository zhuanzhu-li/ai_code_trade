# 量化交易系统 API

一个基于Python Flask的个人量化交易系统后端API，采用前后端分离架构，支持多种交易策略、实时市场数据获取、风险管理和投资组合管理。

## 功能特性

### 核心功能
- 🏦 **投资组合管理**: 创建和管理多个投资组合
- 📊 **实时市场数据**: 支持Yahoo Finance和加密货币交易所数据
- 🤖 **交易策略**: 内置动量策略和均值回归策略
- ⚠️ **风险管理**: 多层次风险控制和警报系统
- 📈 **交易记录**: 完整的交易历史记录和统计分析
- 🔐 **用户认证**: JWT token认证系统
- 🌐 **RESTful API**: 完整的REST API接口
- 📱 **前后端分离**: 纯后端API服务，支持任何前端框架

### 交易策略
- **动量策略 (Momentum Strategy)**: 基于价格动量和RSI指标
- **均值回归策略 (Mean Reversion Strategy)**: 基于布林带和RSI指标
- **可扩展架构**: 支持自定义策略开发

### 风险管理
- 持仓大小限制
- 日损失限制
- 最大回撤控制
- 交易频率限制
- 实时风险警报

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **数据获取**: yfinance, ccxt
- **技术分析**: pandas, numpy, ta-lib
- **认证**: JWT
- **API**: RESTful API
- **CORS**: 支持跨域请求

## 项目结构

```
quant_trading_system/
├── app/                    # Flask应用主目录
│   ├── __init__.py        # 应用工厂函数
│   └── routes.py          # API路由
├── models/                 # 数据库模型
│   ├── __init__.py
│   ├── user.py            # 用户模型
│   ├── portfolio.py       # 投资组合模型
│   ├── strategy.py        # 策略模型
│   ├── trade.py           # 交易模型
│   ├── market_data.py     # 市场数据模型
│   └── risk_management.py # 风险管理模型
├── services/              # 业务逻辑服务
│   ├── trading_service.py # 交易服务
│   ├── data_service.py    # 数据服务
│   └── risk_service.py    # 风险服务
├── strategies/            # 交易策略
│   ├── base_strategy.py   # 策略基类
│   ├── momentum_strategy.py      # 动量策略
│   └── mean_reversion_strategy.py # 均值回归策略
├── utils/                 # 工具类
│   └── auth.py            # 认证工具
├── tests/                 # 测试文件
├── migrations/            # 数据库迁移
├── logs/                  # 日志文件
├── config.py              # 配置文件
├── app.py                 # 应用入口
├── run.py                 # 启动脚本
├── setup.py               # 安装脚本
├── api_client_example.py  # API客户端示例
├── requirements.txt       # 依赖包
└── README.md             # 项目文档
```

## 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- pip

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd quant_trading_system

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

```bash
# 创建MySQL数据库
mysql -u root -p
CREATE DATABASE quant_trading;
CREATE DATABASE quant_trading_dev;

# 配置数据库连接
cp env.example .env
# 编辑.env文件，设置数据库连接信息
```

### 4. 环境变量配置

创建`.env`文件并配置以下变量：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost/quant_trading
DEV_DATABASE_URL=mysql+pymysql://root:password@localhost/quant_trading_dev

# 安全配置
SECRET_KEY=your-secret-key-here

# 交易配置
TRADING_ENABLED=False
MAX_POSITION_SIZE=10000
MAX_DAILY_LOSS=1000

# 交易所API密钥（可选）
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### 5. 初始化数据库

```bash
# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development
$env:FLASK_APP="app.py";
$env:FLASK_ENV="development";

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. 运行应用

```bash
python app.py
```

访问 http://localhost:5000/api/info 查看API信息。

## API使用示例

### 快速开始

```python
from api_client_example import QuantTradingAPIClient

# 创建API客户端
client = QuantTradingAPIClient("http://localhost:5000/api")

# 用户注册
client.register("testuser", "test@example.com", "password123")

# 创建投资组合
portfolio = client.create_portfolio("我的投资组合", "测试投资组合", 10000)

# 执行交易
trade = client.execute_trade(portfolio['id'], "AAPL", "buy", 10, 150.0)

# 获取仪表板统计
stats = client.get_dashboard_stats()
print(f"总资产价值: ${stats['total_value']:.2f}")
```

### 运行API客户端示例

```bash
python api_client_example.py
```

## API文档

### 用户管理

#### 创建用户
```http
POST /api/users
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

#### 获取用户信息
```http
GET /api/users/{user_id}
Authorization: Bearer <token>
```

### 投资组合管理

#### 获取投资组合列表
```http
GET /api/portfolios?user_id={user_id}
Authorization: Bearer <token>
```

#### 创建投资组合
```http
POST /api/portfolios
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "我的投资组合",
    "description": "测试投资组合",
    "user_id": 1,
    "initial_capital": 10000
}
```

### 交易管理

#### 执行交易
```http
POST /api/trades
Content-Type: application/json
Authorization: Bearer <token>

{
    "portfolio_id": 1,
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10,
    "price": 150.0
}
```

#### 获取交易记录
```http
GET /api/trades?portfolio_id={portfolio_id}&limit=100
Authorization: Bearer <token>
```

### 策略管理

#### 创建策略
```http
POST /api/strategies
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "动量策略",
    "description": "基于动量的交易策略",
    "user_id": 1,
    "strategy_type": "momentum",
    "parameters": {
        "lookback_period": 20,
        "rsi_period": 14,
        "position_size_percentage": 0.1
    }
}
```

#### 执行策略
```http
POST /api/strategies/{strategy_id}/execute
Content-Type: application/json
Authorization: Bearer <token>

{
    "portfolio_id": 1,
    "start_time": "2024-01-01T00:00:00Z",
    "initial_capital": 10000
}
```

### 市场数据

#### 获取市场数据
```http
GET /api/market-data/{symbol}?start_date=2024-01-01&end_date=2024-01-31&limit=1000
Authorization: Bearer <token>
```

#### 获取最新价格
```http
GET /api/market-data/{symbol}/latest
Authorization: Bearer <token>
```

### 风险管理

#### 创建风险规则
```http
POST /api/risk-rules
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "持仓大小限制",
    "description": "限制单个持仓的最大金额",
    "rule_type": "position_size",
    "parameters": {
        "max_position_size": 5000,
        "max_position_percentage": 20
    }
}
```

#### 获取风险警报
```http
GET /api/risk-alerts?portfolio_id={portfolio_id}
Authorization: Bearer <token>
```

## 使用指南

### 1. 创建用户和投资组合

1. 通过API创建用户账户
2. 创建投资组合并设置初始资金
3. 配置风险参数

### 2. 选择交易策略

1. 创建交易策略并设置参数
2. 将策略绑定到投资组合
3. 启动策略执行

### 3. 监控交易

1. 查看仪表板了解整体表现
2. 监控风险警报
3. 分析交易记录

### 4. 风险管理

1. 设置风险规则
2. 监控风险指标
3. 及时处理风险警报

## 开发指南

### 添加新策略

1. 继承`BaseStrategy`类
2. 实现`generate_signal`方法
3. 实现`calculate_position_size`方法
4. 在策略管理中添加新策略类型

```python
from strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, parameters=None):
        super().__init__('MyCustomStrategy', parameters)
    
    def generate_signal(self, market_data):
        # 实现信号生成逻辑
        pass
    
    def calculate_position_size(self, signal, portfolio_value, current_price):
        # 实现持仓大小计算逻辑
        pass
```

### 添加新的数据源

1. 在`DataService`中添加新的数据获取方法
2. 实现数据格式标准化
3. 添加错误处理和重试机制

### 自定义风险规则

1. 继承`RiskRule`类
2. 实现`check_rule`方法
3. 在风险管理服务中注册新规则

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_models.py

# 生成测试覆盖率报告
python -m pytest --cov=. tests/
```

## 部署

### 生产环境配置

1. 设置环境变量
2. 配置数据库
3. 设置日志
4. 配置反向代理（Nginx）
5. 使用WSGI服务器（Gunicorn）

```bash
# 安装Gunicorn
pip install gunicorn

# 运行生产服务器
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 注意事项

1. **风险提示**: 本系统仅供学习和研究使用，实际交易存在风险
2. **数据准确性**: 请确保市场数据的准确性和及时性
3. **资金安全**: 建议在模拟环境中充分测试后再进行实盘交易
4. **合规性**: 请遵守当地法律法规和交易所规则

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/quant-trading-system

---

**免责声明**: 本软件仅供学习和研究目的。使用本软件进行实际交易的风险由用户自行承担。作者不对任何投资损失负责。
