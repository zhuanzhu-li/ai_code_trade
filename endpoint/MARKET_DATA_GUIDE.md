# 市场数据获取系统使用指南

## 📋 概述

本系统基于AKShare实现了完整的A股市场数据获取功能，支持：

- 🏛️ **上证500成分股获取**：自动同步指数成分股信息
- 📊 **历史行情数据**：获取股票的OHLCV数据
- 🔄 **实时数据更新**：支持手动和定时获取最新行情
- 🎯 **灵活配置**：支持多数据源扩展
- ⏰ **定时任务**：自动化数据更新

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端页面      │───▶│   后端API       │───▶│   数据源        │
│  MarketData.vue │    │   routes.py     │    │  AKShareSource  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  市场数据服务    │    │   AKShare API   │
                       │MarketDataService│    │   (第三方)      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MySQL数据库   │
                       │ symbols/market_ │
                       │      data       │
                       └─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

安装必要依赖：
```bash
cd endpoint
pip install -r requirements.txt
```

确保数据库已初始化：
```bash
cd endpoint/database
python migrate.py init
```

### 2. 启动服务

启动后端服务：
```bash
cd endpoint
python run.py
```

启动前端服务：
```bash
cd frontpoint
npm run dev
```

### 3. 访问页面

访问 `http://localhost:3000/market-data` 进入市场数据管理页面。

## 📚 功能详解

### 1. 数据源架构

#### 抽象基类 `BaseDataSource`
```python
# endpoint/services/data_sources/base_data_source.py
class BaseDataSource(ABC):
    @abstractmethod
    def get_index_components(self, index_code: str) -> List[Dict]
    
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame
    
    @abstractmethod
    def get_latest_data(self, symbols: List[str]) -> Dict[str, Dict]
```

#### AKShare实现 `AKShareDataSource`
```python
# endpoint/services/data_sources/akshare_data_source.py
class AKShareDataSource(BaseDataSource):
    def get_index_components(self, index_code: str):
        # 使用 ak.index_stock_cons() 获取成分股
        
    def get_historical_data(self, symbol: str, start_date: date, end_date: date):
        # 使用 ak.stock_zh_a_hist() 获取历史数据
```

### 2. 市场数据服务

#### `MarketDataService` 核心功能
```python
# endpoint/services/market_data_service.py
class MarketDataService:
    def sync_index_components(self, index_code: str) -> int
    def fetch_historical_data(self, symbol: str, start_date=None, end_date=None) -> int
    def batch_fetch_latest_data(self, symbols: List[str]) -> Dict[str, int]
```

### 3. 数据库结构

#### 股票信息表 `symbols`
```sql
CREATE TABLE symbols (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(20) UNIQUE NOT NULL,    -- 股票代码
    name VARCHAR(100) NOT NULL,            -- 股票名称
    exchange VARCHAR(50),                  -- 交易所
    asset_type VARCHAR(20) DEFAULT 'stock', -- 资产类型
    is_active BOOLEAN DEFAULT TRUE,        -- 是否活跃
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 市场数据表 `market_data`
```sql
CREATE TABLE market_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(20) NOT NULL,           -- 股票代码
    timestamp DATETIME NOT NULL,           -- 时间戳
    open_price DECIMAL(15,8) NOT NULL,     -- 开盘价
    high_price DECIMAL(15,8) NOT NULL,     -- 最高价
    low_price DECIMAL(15,8) NOT NULL,      -- 最低价
    close_price DECIMAL(15,8) NOT NULL,    -- 收盘价
    volume DECIMAL(20,8) DEFAULT 0,        -- 成交量
    interval_type VARCHAR(10) DEFAULT '1d', -- 时间间隔
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4. API接口

#### 获取数据源列表
```http
GET /api/market-data/sources
```

#### 同步上证500成分股
```http
POST /api/market-data/sync/index-components
Content-Type: application/json

{
    "index_code": "上证500",
    "data_source": "akshare"
}
```

#### 获取最新行情数据
```http
POST /api/market-data/fetch/latest
Content-Type: application/json

{
    "symbols": ["000001", "000002"],  // 可选，不传则获取所有
    "data_source": "akshare"
}
```

#### 获取历史数据
```http
POST /api/market-data/fetch/historical
Content-Type: application/json

{
    "symbol": "000001",
    "start_date": "2024-01-01",      // 可选
    "end_date": "2024-12-31",        // 可选
    "force_update": false,           // 是否强制更新
    "data_source": "akshare"
}
```

### 5. 定时任务

#### `SchedulerService` 定时任务管理
```python
# endpoint/services/scheduler_service.py
class SchedulerService:
    def add_daily_market_data_job(self):
        # 每个工作日早上9:00获取最新数据
        
    def add_after_market_data_job(self):
        # 每个工作日下午15:30获取收盘数据
        
    def add_weekly_symbol_sync_job(self):
        # 每周日凌晨2:00同步股票列表
```

## 🎯 使用场景

### 场景1：初次使用系统

1. **同步成分股**：点击"同步上证500成分股"按钮
2. **获取历史数据**：系统会自动从2024年1月1日开始获取数据
3. **查看结果**：在股票列表中查看同步的股票

### 场景2：日常数据更新

1. **手动更新**：点击"获取最新行情数据"按钮
2. **自动更新**：系统每个交易日自动获取最新数据
3. **监控状态**：查看统计信息了解数据状态

### 场景3：获取特定股票数据

1. **搜索股票**：在股票列表中搜索特定股票
2. **获取数据**：点击"获取数据"按钮获取该股票的最新数据
3. **查看数据**：点击"查看数据"查看历史数据

## ⚙️ 配置说明

### 数据源配置
```python
# 在前端页面可以配置：
config = {
    'dataSource': 'akshare',    # 数据源类型
    'batchSize': 50             # 批量处理大小
}
```

### AKShare配置
```python
# endpoint/services/data_sources/akshare_data_source.py
config = {
    'timeout': 30,              # 请求超时时间
    'retry_times': 3,           # 重试次数
    'delay': 1                  # 请求间隔
}
```

## 🔧 故障排除

### 常见问题

1. **AKShare连接失败**
   ```
   错误: 数据源初始化失败
   解决: 检查网络连接，确保能访问AKShare API
   ```

2. **数据获取为空**
   ```
   错误: 获取成分股为空
   解决: 检查指数代码是否正确，网络是否稳定
   ```

3. **数据库连接失败**
   ```
   错误: 数据库连接失败
   解决: 检查数据库配置，确保MySQL服务运行正常
   ```

### 调试方法

1. **查看日志**：
   ```bash
   tail -f endpoint/logs/trading.log
   ```

2. **测试数据源**：
   ```bash
   cd endpoint
   python test_market_data.py
   ```

3. **检查数据库**：
   ```sql
   SELECT COUNT(*) FROM symbols;
   SELECT COUNT(*) FROM market_data;
   ```

## 📈 性能优化

### 1. 批量处理
- 使用批量获取避免频繁请求
- 设置合适的批量大小（推荐50）

### 2. 请求频率控制
- 添加请求间隔避免被限制
- 使用重试机制处理临时失败

### 3. 数据库优化
- 使用索引加速查询
- 定期清理过期数据

## 🔄 扩展指南

### 添加新数据源

1. **创建数据源类**：
   ```python
   class NewDataSource(BaseDataSource):
       def get_index_components(self, index_code: str):
           # 实现获取成分股逻辑
           pass
   ```

2. **注册数据源**：
   ```python
   # endpoint/services/data_sources/__init__.py
   DATA_SOURCES = {
       'akshare': AKShareDataSource,
       'new_source': NewDataSource,
   }
   ```

3. **更新前端配置**：在前端页面添加新数据源选项

### 添加新指数

修改 `AKShareDataSource.index_mapping` 添加新的指数映射：
```python
self.index_mapping = {
    '上证500': '000905',
    '沪深300': '000300',
    '新指数': '指数代码',
}
```

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 运行测试脚本检查功能状态
3. 查看系统日志获取详细错误信息
4. 提交Issue到项目仓库

---

**免责声明**: 本系统仅供学习和研究使用，使用第三方数据源时请遵守相关服务条款。
