# API 文档

## 概述

量化交易系统提供RESTful API接口，支持用户管理、投资组合管理、交易执行、策略管理、风险管理和市场数据等功能。

**重要说明：** 所有API接口都使用统一的响应格式，具体格式请参考下方的"响应格式"章节。本文档中的接口示例将重点展示`data`字段的内容，完整的响应格式请按照统一格式进行包装。

## 认证

所有API请求（除用户注册、登录和系统信息外）都需要在请求头中包含JWT token：

```
Authorization: Bearer <your-jwt-token>
```

## 响应格式

所有API响应都使用统一的JSON格式：

### 统一响应格式
```json
{
    "code": xxx,    // 状态码，200为成功，10xxx为业务异常，50xxx为系统异常
    "msg": "xxx",   // 返回信息，code为200时固定为"成功！"，code为其它时返回异常的简述
    "data": xxx     // 返回的具体数据，异常时返回为空即可
}
```

### 成功响应示例
```json
{
    "code": 200,
    "msg": "成功！",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
    }
}
```

### 业务异常响应示例
```json
{
    "code": 10001,
    "msg": "缺少必要字段",
    "data": null
}
```

### 系统异常响应示例
```json
{
    "code": 50001,
    "msg": "内部服务器错误",
    "data": null
}
```

## 状态码规范

### 成功状态码
- `200` - 成功

### 业务异常状态码 (10xxx)
- `10001` - 缺少必要字段
- `10002` - 用户名已存在
- `10003` - 邮箱已存在
- `10004` - 用户名或密码错误
- `10005` - 账户已被禁用
- `10006` - 缺少用户名或密码
- `10007` - 投资组合不存在或无权限访问
- `10008` - 缺少指数代码
- `10009` - 缺少股票代码
- `10010` - 没有找到需要更新的股票
- `10011` - 资源未找到
- `10012` - 请求参数错误
- `10013` - 未授权访问

### 系统异常状态码 (50xxx)
- `50001` - 内部服务器错误
- `50002` - 数据源错误
- `50003` - 数据源初始化失败
- `50004` - 数据同步失败
- `50005` - 数据获取失败
- `50006` - 获取市场数据失败
- `50007` - 获取股票列表失败
- `50008` - 获取统计信息失败
- `50009` - 健康检查失败

### HTTP状态码
- `200` - 成功
- `400` - 业务异常
- `500` - 系统异常

## 用户认证 API

### 用户注册

**POST** `/api/auth/register`

创建新用户账户。

**请求体:**
```json
{
    "username": "string",     // 用户名，必填
    "email": "string",        // 邮箱，必填
    "password": "string"      // 密码，必填
}
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "注册成功",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**错误响应示例:**
```json
{
    "code": 10001,
    "msg": "缺少必要字段",
    "data": null
}
```

### 用户登录

**POST** `/api/auth/login`

用户登录获取访问令牌。

**请求体:**
```json
{
    "username": "string",     // 用户名，必填
    "password": "string"      // 密码，必填
}
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "登录成功",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**错误响应示例:**
```json
{
    "code": 10004,
    "msg": "用户名或密码错误",
    "data": null
}
```

### 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的信息。

**成功响应:**
```json
{
    "code": 200,
    "msg": "成功！",
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

**错误响应示例:**
```json
{
    "code": 10013,
    "msg": "未授权访问",
    "data": null
}
```

## 用户管理 API

### 创建用户

**POST** `/api/users`

创建新用户账户（管理员功能）。

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
- `user_id` (integer): 用户ID，可选（默认使用当前用户）

**响应:**
```json
[
    {
        "id": 1,
        "user_id": 1,
        "name": "我的投资组合",
        "description": "主要投资组合",
        "initial_capital": 10000.0,
        "current_value": 10500.0,
        "cash_balance": 500.0,
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
    "name": "string",         // 投资组合名称，必填
    "description": "string",  // 描述，可选
    "user_id": 1,             // 用户ID，必填
    "initial_capital": 10000.0 // 初始资金，可选
}
```

**响应:**
```json
{
    "id": 1,
    "user_id": 1,
    "name": "我的投资组合",
    "description": "主要投资组合",
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
    "description": "主要投资组合",
    "initial_capital": 10000.0,
    "current_value": 10500.0,
    "cash_balance": 500.0,
    "total_pnl": 500.0,
    "total_pnl_percentage": 5.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 获取投资组合持仓

**GET** `/api/portfolios/{portfolio_id}/positions`

获取指定投资组合的持仓信息。

**响应:**
```json
[
    {
        "id": 1,
        "portfolio_id": 1,
        "symbol": "AAPL",
        "quantity": 100,
        "average_price": 150.0,
        "current_price": 155.0,
        "value": 15500.0,
        "unrealized_pnl": 500.0,
        "realized_pnl": 0.0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

## 交易管理 API

### 获取交易记录

**GET** `/api/trades`

获取交易记录列表。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选
- `symbol` (string): 交易标的，可选
- `limit` (integer): 返回记录数限制，可选（默认100）

**响应:**
```json
[
    {
        "id": 1,
        "portfolio_id": 1,
        "strategy_execution_id": 1,
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.0,
        "amount": 15000.0,
        "fee": 15.0,
        "net_amount": 14985.0,
        "pnl": 0.0,
        "status": "completed",
        "executed_at": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### 创建交易

**POST** `/api/trades`

创建新的交易记录。

**请求体:**
```json
{
    "portfolio_id": 1,        // 投资组合ID，必填
    "symbol": "AAPL",         // 交易标的，必填
    "side": "buy",            // 交易方向：buy/sell，必填
    "quantity": 100,          // 数量，必填
    "price": 150.0,           // 价格，必填
    "strategy_execution_id": 1 // 策略执行ID，可选
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
    "quantity": 100,
    "price": 150.0,
    "amount": 15000.0,
    "fee": 15.0,
    "net_amount": 14985.0,
    "pnl": 0.0,
    "status": "completed",
    "executed_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
}
```

## 策略管理 API

### 获取策略列表

**GET** `/api/strategies`

获取用户的策略列表。

**查询参数:**
- `user_id` (integer): 用户ID，可选（默认使用当前用户）

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
            "total_trades": 10,
            "winning_trades": 6,
            "win_rate": 60.0,
            "total_pnl": 500.0,
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
    "name": "string",         // 策略名称，必填
    "description": "string",  // 策略描述，可选
    "user_id": 1,             // 用户ID，必填
    "strategy_type": "momentum", // 策略类型：momentum/mean_reversion，必填
    "parameters": {           // 策略参数，可选
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
    "portfolio_id": 1,        // 投资组合ID，必填
    "start_time": "2024-01-01T00:00:00Z", // 开始时间，可选
    "initial_capital": 10000.0 // 初始资金，可选
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

### 获取最新价格

**GET** `/api/market-data/{symbol}/latest`

获取指定标的的最新价格。

**响应:**
```json
{
    "symbol": "AAPL",
    "price": 155.0,
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 获取市场数据

**GET** `/api/market-data/{symbol}`

获取指定标的的历史市场数据。

**查询参数:**
- `start_date` (string): 开始日期，格式：YYYY-MM-DD，可选
- `end_date` (string): 结束日期，格式：YYYY-MM-DD，可选
- `limit` (integer): 返回记录数限制，可选（默认1000）

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
        "low_price": 149.0,
        "close_price": 154.0,
        "volume": 1000000,
        "price_change": 4.0,
        "price_change_percentage": 2.67,
        "high_low_spread": 6.0,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

### 获取股票列表

**GET** `/api/market-data/symbols`

获取可用的股票列表。

**查询参数:**
- `page` (integer): 页码，可选（默认1）
- `per_page` (integer): 每页记录数，可选（默认50）
- `search` (string): 搜索关键词，可选

**响应:**
```json
{
    "symbols": [
        {
            "id": 1,
            "symbol": "AAPL",
            "name": "苹果公司",
            "market": "NASDAQ",
            "sector": "科技",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 50,
        "total": 100,
        "total_pages": 2
    }
}
```

### 获取数据源列表

**GET** `/api/market-data/sources`

获取可用的数据源列表。

**响应:**
```json
{
    "sources": ["akshare", "yfinance", "tushare"],
    "default": "akshare"
}
```

### 同步股票列表

**POST** `/api/market-data/sync/symbols`

同步股票列表到数据库。

**请求体:**
```json
{
    "market": "A股",          // 市场类型，可选（默认"A股"）
    "data_source": "akshare"  // 数据源，可选（默认"akshare"）
}
```

**响应:**
```json
{
    "message": "股票列表同步完成",
    "synced_count": 5000,
    "market": "A股",
    "data_source": "akshare"
}
```

### 同步指数成分股

**POST** `/api/market-data/sync/index-components`

同步指数成分股到数据库。

**请求体:**
```json
{
    "index_code": "000001",   // 指数代码，必填
    "data_source": "akshare"  // 数据源，可选（默认"akshare"）
}
```

**响应:**
```json
{
    "message": "000001成分股同步完成",
    "synced_count": 500,
    "index_code": "000001",
    "data_source": "akshare"
}
```

### 获取最新行情数据

**POST** `/api/market-data/fetch/latest`

手动获取最新行情数据。

**请求体:**
```json
{
    "symbols": ["AAPL", "GOOGL"], // 股票代码列表，可选
    "data_source": "akshare"      // 数据源，可选（默认"akshare"）
}
```

**响应:**
```json
{
    "message": "最新行情数据获取完成",
    "total_symbols": 2,
    "successful_symbols": 2,
    "failed_symbols": 0,
    "data_source": "akshare"
}
```

### 获取历史数据

**POST** `/api/market-data/fetch/historical`

获取指定股票的历史数据。

**请求体:**
```json
{
    "symbol": "AAPL",         // 股票代码，必填
    "start_date": "2024-01-01", // 开始日期，可选
    "end_date": "2024-01-31",   // 结束日期，可选
    "data_source": "akshare"    // 数据源，可选（默认"akshare"）
}
```

**响应:**
```json
{
    "message": "AAPL历史数据获取完成",
    "symbol": "AAPL",
    "records_added": 30,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "data_source": "akshare"
}
```

### 获取市场数据统计

**GET** `/api/market-data/statistics`

获取市场数据统计信息。

**响应:**
```json
{
    "total_symbols": 5000,
    "total_records": 1000000,
    "last_update": "2024-01-01T00:00:00Z",
    "data_sources": ["akshare", "yfinance"],
    "coverage": {
        "stocks": 4000,
        "indices": 100,
        "crypto": 900
    }
}
```

### 市场数据健康检查

**GET** `/api/market-data/health`

检查市场数据服务的健康状态。

**响应:**
```json
{
    "status": "healthy",
    "data_sources": {
        "akshare": "available",
        "yfinance": "available"
    },
    "last_check": "2024-01-01T00:00:00Z",
    "uptime": "99.9%"
}
```

## 风险管理 API

### 获取风险规则列表

**GET** `/api/risk-rules`

获取风险规则列表。

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
    "name": "string",         // 规则名称，必填
    "description": "string",  // 规则描述，可选
    "rule_type": "position_size", // 规则类型，必填
    "parameters": {           // 规则参数，可选
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

## 仪表板 API

### 获取统计数据

**GET** `/api/dashboard/stats`

获取仪表板统计数据。

**响应:**
```json
{
    "total_value": 100000.0,
    "total_pnl": 5000.0,
    "total_pnl_percentage": 5.0,
    "active_portfolios": 3,
    "active_strategies": 2,
    "total_trades": 100,
    "win_rate": 65.0,
    "risk_alerts": 2
}
```

### 获取表现数据

**GET** `/api/dashboard/performance`

获取投资组合表现数据。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选
- `period` (string): 时间周期，可选（默认"30d"）

**响应:**
```json
{
    "period": "30d",
    "total_return": 5.0,
    "daily_returns": [0.1, -0.2, 0.3, ...],
    "volatility": 0.15,
    "sharpe_ratio": 1.2,
    "max_drawdown": -2.5
}
```

### 获取持仓汇总

**GET** `/api/dashboard/positions`

获取持仓汇总信息。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选

**响应:**
```json
{
    "total_positions": 10,
    "total_value": 50000.0,
    "top_holdings": [
        {
            "symbol": "AAPL",
            "value": 10000.0,
            "percentage": 20.0
        }
    ],
    "sector_allocation": {
        "科技": 40.0,
        "金融": 30.0,
        "医疗": 20.0,
        "其他": 10.0
    }
}
```

### 获取最近交易

**GET** `/api/dashboard/recent-trades`

获取最近的交易记录。

**查询参数:**
- `portfolio_id` (integer): 投资组合ID，可选
- `limit` (integer): 返回记录数限制，可选（默认10）

**响应:**
```json
[
    {
        "id": 1,
        "portfolio_id": 1,
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.0,
        "executed_at": "2024-01-01T00:00:00Z"
    }
]
```

## 系统 API

### 健康检查

**GET** `/api/health`

检查系统健康状态。

**响应:**
```json
{
    "status": "healthy",
    "message": "量化交易系统API服务正常运行",
    "version": "1.0.0"
}
```

### 系统信息

**GET** `/api/info`

获取系统信息。

**响应:**
```json
{
    "name": "量化交易系统",
    "version": "1.0.0",
    "description": "基于Flask的个人量化交易系统API",
    "author": "Your Name",
    "contact": "your.email@example.com"
}
```

## 错误代码

| 错误代码 | 描述 |
|---------|------|
| `MISSING_FIELDS` | 缺少必要字段 |
| `USERNAME_EXISTS` | 用户名已存在 |
| `EMAIL_EXISTS` | 邮箱已存在 |
| `MISSING_CREDENTIALS` | 缺少用户名或密码 |
| `INVALID_CREDENTIALS` | 用户名或密码错误 |
| `ACCOUNT_DISABLED` | 账户已被禁用 |
| `PORTFOLIO_NOT_FOUND` | 投资组合不存在或无权限访问 |
| `STRATEGY_NOT_FOUND` | 策略未找到 |
| `SYMBOL_NOT_FOUND` | 交易标的未找到 |
| `DATA_SOURCE_ERROR` | 数据源错误 |
| `SYNC_ERROR` | 同步失败 |
| `FETCH_ERROR` | 获取数据失败 |
| `GET_DATA_ERROR` | 获取市场数据失败 |
| `GET_SYMBOLS_ERROR` | 获取股票列表失败 |
| `GET_STATS_ERROR` | 获取统计信息失败 |
| `HEALTH_CHECK_ERROR` | 健康检查失败 |
| `UNAUTHORIZED` | 未授权访问 |
| `FORBIDDEN` | 禁止访问 |
| `NOT_FOUND` | 资源未找到 |
| `BAD_REQUEST` | 请求参数错误 |
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

# 用户登录
def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json()

# 获取投资组合列表
def get_portfolios():
    url = f"{BASE_URL}/portfolios"
    response = requests.get(url, headers=headers)
    return response.json()

# 创建交易
def create_trade(portfolio_id, symbol, side, quantity, price):
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
```

### JavaScript 示例

```javascript
const API_BASE_URL = 'http://localhost:5000/api';

// 用户登录
async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

// 获取投资组合列表
async function getPortfolios(token) {
    const response = await fetch(`${API_BASE_URL}/portfolios`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
}

// 创建交易
async function createTrade(token, tradeData) {
    const response = await fetch(`${API_BASE_URL}/trades`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(tradeData)
    });
    return await response.json();
}
```

## 注意事项

1. **认证**: 除了注册、登录和系统信息接口外，所有接口都需要JWT token认证
2. **数据格式**: 所有请求和响应都使用JSON格式
3. **错误处理**: 请根据HTTP状态码和错误代码进行适当的错误处理
4. **分页**: 支持分页的接口会返回分页信息
5. **时间格式**: 所有时间字段都使用ISO 8601格式（UTC时间）
6. **权限控制**: 用户只能访问自己的数据，系统会进行权限验证
7. **数据验证**: 所有输入数据都会进行验证，请确保提供正确的数据格式
8. **频率限制**: 建议控制API调用频率，避免对系统造成过大压力

## 更新日志

### v1.1.0 (2024-01-15)
- **重大更新**: 统一所有API接口的响应格式
- 新增统一的响应格式规范：`{code, msg, data}`
- 新增业务异常状态码规范 (10xxx)
- 新增系统异常状态码规范 (50xxx)
- 更新所有接口使用统一的错误处理
- 更新前端API客户端以支持新响应格式
- 完善API文档，添加完整的接口示例

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持用户管理、投资组合管理、交易管理、策略管理
- 支持市场数据获取和风险管理
- 提供完整的仪表板API

## 完整接口示例

### 用户注册接口完整示例

**请求:**
```bash
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "注册成功",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**错误响应:**
```json
{
    "code": 10002,
    "msg": "用户名已存在",
    "data": null
}
```

### 获取投资组合列表完整示例

**请求:**
```bash
GET /api/portfolios
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "成功！",
    "data": [
        {
            "id": 1,
            "user_id": 1,
            "name": "我的投资组合",
            "description": "主要投资组合",
            "initial_capital": 10000.0,
            "current_value": 10500.0,
            "cash_balance": 500.0,
            "total_pnl": 500.0,
            "total_pnl_percentage": 5.0,
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

**错误响应:**
```json
{
    "code": 10013,
    "msg": "未授权访问",
    "data": null
}
```

### 创建交易完整示例

**请求:**
```bash
POST /api/trades
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "portfolio_id": 1,
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 100,
    "price": 150.0
}
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "交易创建成功",
    "data": {
        "id": 1,
        "portfolio_id": 1,
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.0,
        "amount": 15000.0,
        "fee": 15.0,
        "net_amount": 14985.0,
        "pnl": 0.0,
        "status": "completed",
        "executed_at": "2024-01-01T10:00:00Z",
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

**错误响应:**
```json
{
    "code": 10001,
    "msg": "缺少必要字段",
    "data": null
}
```

## 注意事项

1. **统一响应格式**: 所有接口都使用相同的响应格式，包含`code`、`msg`和`data`字段
2. **状态码规范**: 成功使用200，业务异常使用10xxx，系统异常使用50xxx
3. **错误处理**: 前端应根据`code`字段判断请求是否成功
4. **认证**: 大部分接口需要JWT token认证
5. **分页**: 列表接口支持分页参数`page`和`per_page`
6. **时间格式**: 所有时间字段使用ISO 8601格式