# API 文档

## 概述

量化交易系统提供RESTful API接口，支持用户管理、投资组合管理、交易执行、策略管理和风险管理等功能。

## 认证

所有API请求（除用户注册外）都需要在请求头中包含JWT token：

```
Authorization: Bearer <your-jwt-token>
```

## 响应格式

所有API响应都使用JSON格式：

### 成功响应
```json
{
    "data": {...},
    "message": "操作成功"
}
```

### 错误响应
```json
{
    "error": "错误描述",
    "code": "ERROR_CODE"
}
```

## 状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权
- `404` - 资源未找到
- `500` - 服务器内部错误

## 用户管理 API

### 创建用户

**POST** `/api/users`

创建新用户账户。

**请求体:**
```json
{
    "username": "string",     // 用户名，必填
    "email": "string",        // 邮箱，必填
    "password": "string"      // 密码，必填
}
```

**响应:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 获取用户信息

**GET** `/api/users/{user_id}`

获取指定用户的详细信息。

**响应:**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

## 投资组合管理 API

### 获取投资组合列表

**GET** `/api/portfolios`

获取用户的投资组合列表。

**查询参数:**
- `user_id` (integer): 用户ID，必填

**响应:**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "name": "我的投资组合",
        "description": "测试投资组合",
        "initial_capital": 10000.0,
        "current_value": 10500.0,
        "cash_balance": 5000.0,
        "total_pnl": 500.0,
        "total_pnl_percentage": 5.0,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 创建投资组合

**POST** `/api/portfolios`

创建新的投资组合。

**请求体:**
```json
{
    "name": "string",           // 投资组合名称，必填
    "description": "string",    // 描述，可选
    "user_id": 1,               // 用户ID，必填
    "initial_capital": 10000.0  // 初始资金，可选，默认0
}
```

**响应:**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "我的投资组合",
    "description": "测试投资组合",
    "initial_capital": 10000.0,
    "current_value": 10000.0,
    "cash_balance": 10000.0,
    "total_pnl": 0.0,
    "total_pnl_percentage": 0.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 获取投资组合详情

**GET** `/api/portfolios/{portfolio_id}`

获取指定投资组合的详细信息。

**响应:**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "我的投资组合",
    "description": "测试投资组合",
    "initial_capital": 10000.0,
    "current_value": 10500.0,
    "cash_balance": 5000.0,
    "total_pnl": 500.0,
    "total_pnl_percentage": 5.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 获取投资组合持仓

**GET** `/api/portfolios/{portfolio_id}/positions`

获取投资组合的持仓信息。

**响应:**
```json
[
    {
        "id": 1,
        "portfolio_id": 1,
        "symbol": "AAPL",
        "quantity": 10.0,
        "average_price": 150.0,
        "current_price": 155.0,
        "value": 1550.0,
        "unrealized_pnl": 50.0,
        "realized_pnl": 0.0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

## 交易管理 API

### 执行交易

**POST** `/api/trades`

执行买卖交易。

**请求体:**
```json
{
    "portfolio_id": 1,                    // 投资组合ID，必填
    "symbol": "AAPL",                     // 交易标的，必填
    "side": "buy",                        // 交易方向：buy/sell，必填
    "quantity": 10.0,                     // 交易数量，必填
    "price": 150.0,                       // 交易价格，必填
    "strategy_execution_id": 1            // 策略执行ID，可选
}
```

**响应:**
```json
{
    "id": 1,
    "portfolio_id": 1,
    "strategy_execution_id": 1,
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10.0,
    "price": 150.0,
    "amount": 1500.0,
    "fee": 1.5,
    "net_amount": 1498.5,
    "pnl": 0.0,
    "status": "completed",
    "executed_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### 获取交易记录

**GET** `/api/trades`

获取交易记录列表。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选
- `symbol` (string): 交易标的，可选
- `limit` (integer): 返回记录数限制，可选，默认100

**响应:**
```json
[
    {
        "id": 1,
        "portfolio_id": 1,
        "strategy_execution_id": 1,
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 10.0,
        "price": 150.0,
        "amount": 1500.0,
        "fee": 1.5,
        "net_amount": 1498.5,
        "pnl": 0.0,
        "status": "completed",
        "executed_at": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

## 策略管理 API

### 获取策略列表

**GET** `/api/strategies`

获取用户的交易策略列表。

**查询参数:**
- `user_id` (integer): 用户ID，必填

**响应:**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "name": "动量策略",
        "description": "基于动量的交易策略",
        "strategy_type": "momentum",
        "parameters": {
            "lookback_period": 20,
            "rsi_period": 14,
            "position_size_percentage": 0.1
        },
        "is_active": true,
        "performance": {
            "total_trades": 50,
            "winning_trades": 35,
            "win_rate": 70.0,
            "total_pnl": 1500.0,
            "active_executions": 1
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 创建策略

**POST** `/api/strategies`

创建新的交易策略。

**请求体:**
```json
{
    "name": "string",                    // 策略名称，必填
    "description": "string",             // 策略描述，可选
    "user_id": 1,                        // 用户ID，必填
    "strategy_type": "momentum",         // 策略类型，必填
    "parameters": {                      // 策略参数，可选
        "lookback_period": 20,
        "rsi_period": 14,
        "position_size_percentage": 0.1
    }
}
```

**响应:**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "动量策略",
    "description": "基于动量的交易策略",
    "strategy_type": "momentum",
    "parameters": {
        "lookback_period": 20,
        "rsi_period": 14,
        "position_size_percentage": 0.1
    },
    "is_active": true,
    "performance": {
        "total_trades": 0,
        "winning_trades": 0,
        "win_rate": 0.0,
        "total_pnl": 0.0,
        "active_executions": 0
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 执行策略

**POST** `/api/strategies/{strategy_id}/execute`

启动策略执行。

**请求体:**
```json
{
    "portfolio_id": 1,                   // 投资组合ID，必填
    "start_time": "2024-01-01T00:00:00Z", // 开始时间，可选
    "initial_capital": 10000.0           // 初始资金，可选
}
```

**响应:**
```json
{
    "id": 1,
    "strategy_id": 1,
    "portfolio_id": 1,
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": null,
    "is_active": true,
    "initial_capital": 10000.0,
    "current_value": 10000.0,
    "total_pnl": 0.0,
    "total_pnl_percentage": 0.0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

## 市场数据 API

### 获取市场数据

**GET** `/api/market-data/{symbol}`

获取指定标的的历史市场数据。

**路径参数:**
- `symbol` (string): 交易标的代码，如 "AAPL", "BTCUSDT"

**查询参数:**
- `start_date` (string): 开始日期，格式：YYYY-MM-DD，可选
- `end_date` (string): 结束日期，格式：YYYY-MM-DD，可选
- `limit` (integer): 返回记录数限制，可选，默认1000

**响应:**
```json
[
    {
        "id": 1,
        "symbol_id": 1,
        "symbol": "AAPL",
        "timestamp": "2024-01-01T00:00:00Z",
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000.0,
        "price_change": 3.0,
        "price_change_percentage": 2.0,
        "high_low_spread": 7.0,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### 获取最新价格

**GET** `/api/market-data/{symbol}/latest`

获取指定标的的最新价格。

**路径参数:**
- `symbol` (string): 交易标的代码

**响应:**
```json
{
    "symbol": "AAPL",
    "price": 153.25,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## 风险管理 API

### 获取风险规则列表

**GET** `/api/risk-rules`

获取所有活跃的风险规则。

**响应:**
```json
[
    {
        "id": 1,
        "name": "持仓大小限制",
        "description": "限制单个持仓的最大金额",
        "rule_type": "position_size",
        "parameters": {
            "max_position_size": 5000.0,
            "max_position_percentage": 20.0
        },
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 创建风险规则

**POST** `/api/risk-rules`

创建新的风险规则。

**请求体:**
```json
{
    "name": "string",                    // 规则名称，必填
    "description": "string",             // 规则描述，可选
    "rule_type": "position_size",        // 规则类型，必填
    "parameters": {                      // 规则参数，可选
        "max_position_size": 5000.0,
        "max_position_percentage": 20.0
    }
}
```

**响应:**
```json
{
    "id": 1,
    "name": "持仓大小限制",
    "description": "限制单个持仓的最大金额",
    "rule_type": "position_size",
    "parameters": {
        "max_position_size": 5000.0,
        "max_position_percentage": 20.0
    },
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

### 获取风险警报

**GET** `/api/risk-alerts`

获取风险警报列表。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选
- `is_resolved` (boolean): 是否已解决，可选

**响应:**
```json
[
    {
        "id": 1,
        "risk_rule_id": 1,
        "portfolio_id": 1,
        "alert_type": "warning",
        "message": "AAPL持仓超过20%限制",
        "is_resolved": false,
        "resolved_at": null,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

## 错误代码

| 错误代码 | 描述 |
|---------|------|
| `INVALID_PARAMETERS` | 请求参数无效 |
| `UNAUTHORIZED` | 未授权访问 |
| `FORBIDDEN` | 禁止访问 |
| `NOT_FOUND` | 资源未找到 |
| `INSUFFICIENT_FUNDS` | 资金不足 |
| `POSITION_INSUFFICIENT` | 持仓不足 |
| `RISK_VIOLATION` | 风险规则违反 |
| `STRATEGY_NOT_FOUND` | 策略未找到 |
| `PORTFOLIO_NOT_FOUND` | 投资组合未找到 |
| `SYMBOL_NOT_FOUND` | 交易标的未找到 |
| `INTERNAL_ERROR` | 服务器内部错误 |

## 使用示例

### Python 示例

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:5000/api"

# 请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-jwt-token"
}

# 创建用户
def create_user(username, email, password):
    url = f"{BASE_URL}/users"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json()

# 创建投资组合
def create_portfolio(name, user_id, initial_capital=10000):
    url = f"{BASE_URL}/portfolios"
    data = {
        "name": name,
        "user_id": user_id,
        "initial_capital": initial_capital
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 执行交易
def execute_trade(portfolio_id, symbol, side, quantity, price):
    url = f"{BASE_URL}/trades"
    data = {
        "portfolio_id": portfolio_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 获取市场数据
def get_market_data(symbol, start_date=None, end_date=None):
    url = f"{BASE_URL}/market-data/{symbol}"
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 创建用户
    user = create_user("testuser", "test@example.com", "password123")
    print(f"创建用户: {user}")
    
    # 创建投资组合
    portfolio = create_portfolio("我的投资组合", user["id"], 10000)
    print(f"创建投资组合: {portfolio}")
    
    # 执行交易
    trade = execute_trade(portfolio["id"], "AAPL", "buy", 10, 150.0)
    print(f"执行交易: {trade}")
    
    # 获取市场数据
    market_data = get_market_data("AAPL", "2024-01-01", "2024-01-31")
    print(f"市场数据: {len(market_data)} 条记录")
```

### JavaScript 示例

```javascript
// 基础配置
const BASE_URL = "http://localhost:5000/api";
const headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-jwt-token"
};

// 创建用户
async function createUser(username, email, password) {
    const response = await fetch(`${BASE_URL}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        })
    });
    return await response.json();
}

// 创建投资组合
async function createPortfolio(name, userId, initialCapital = 10000) {
    const response = await fetch(`${BASE_URL}/portfolios`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            name: name,
            user_id: userId,
            initial_capital: initialCapital
        })
    });
    return await response.json();
}

// 执行交易
async function executeTrade(portfolioId, symbol, side, quantity, price) {
    const response = await fetch(`${BASE_URL}/trades`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            portfolio_id: portfolioId,
            symbol: symbol,
            side: side,
            quantity: quantity,
            price: price
        })
    });
    return await response.json();
}

// 获取市场数据
async function getMarketData(symbol, startDate = null, endDate = null) {
    let url = `${BASE_URL}/market-data/${symbol}`;
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    if (params.toString()) {
        url += `?${params.toString()}`;
    }
    
    const response = await fetch(url, { headers: headers });
    return await response.json();
}

// 使用示例
async function main() {
    try {
        // 创建用户
        const user = await createUser("testuser", "test@example.com", "password123");
        console.log("创建用户:", user);
        
        // 创建投资组合
        const portfolio = await createPortfolio("我的投资组合", user.id, 10000);
        console.log("创建投资组合:", portfolio);
        
        // 执行交易
        const trade = await executeTrade(portfolio.id, "AAPL", "buy", 10, 150.0);
        console.log("执行交易:", trade);
        
        // 获取市场数据
        const marketData = await getMarketData("AAPL", "2024-01-01", "2024-01-31");
        console.log("市场数据:", marketData.length, "条记录");
        
    } catch (error) {
        console.error("错误:", error);
    }
}

main();
```

## 限制和注意事项

1. **请求频率限制**: 默认限制为1000次/小时
2. **数据量限制**: 单次查询最多返回1000条记录
3. **Token有效期**: JWT token默认24小时有效
4. **数据精度**: 价格和数量支持8位小数精度
5. **时区**: 所有时间戳使用UTC时区

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基本的用户管理、投资组合管理、交易执行功能
- 支持动量策略和均值回归策略
- 支持基础风险管理功能
