# 数据库版本管理系统

这个目录包含了量化交易系统的数据库表结构维护文件和版本管理工具。

## 📁 目录结构

```
database/
├── schema.sql                    # 完整的数据库表结构定义
├── migrations/                   # 版本升级SQL文件
│   ├── v1.0.0_initial_schema.sql       # v1.0.0 初始结构
│   ├── v1.1.0_add_performance_tracking.sql  # v1.1.0 性能跟踪
│   └── v1.2.0_add_advanced_features.sql     # v1.2.0 高级功能
├── migrate.py                    # Python迁移工具
├── migrate.bat                   # Windows批处理脚本
├── migrate.sh                    # Unix/Linux Shell脚本
└── README.md                     # 本文档
```

## 🚀 快速开始

### 1. 环境准备

确保已安装以下依赖：
- Python 3.6+
- pymysql
- python-dotenv

```bash
pip install pymysql python-dotenv
```

### 2. 配置数据库连接

在项目根目录的 `.env` 文件中配置数据库连接信息：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=quant_trading
```

### 3. 初始化数据库

**Windows用户:**
```cmd
cd endpoint\database
migrate.bat init
```

**Linux/Mac用户:**
```bash
cd endpoint/database
chmod +x migrate.sh
./migrate.sh init
```

**直接使用Python:**
```bash
cd endpoint/database
python migrate.py init
```

## 🔧 命令说明

### 查看帮助
```bash
python migrate.py --help
```

### 查看当前状态
```bash
python migrate.py status
```
显示当前数据库版本、已应用的版本和可用的迁移文件。

### 列出所有迁移
```bash
python migrate.py list
```
列出所有可用的迁移文件及其应用状态。

### 升级数据库
```bash
# 升级到最新版本
python migrate.py upgrade

# 升级到指定版本
python migrate.py upgrade v1.2.0
```

### 验证数据库完整性
```bash
python migrate.py validate
```
检查数据库表结构是否完整，验证关键表是否存在。

## 📋 版本说明

### v1.0.0 - 初始版本
- 用户管理表 (users)
- 投资组合管理表 (portfolios, positions)
- 交易管理表 (trades, orders)
- 策略管理表 (strategies, strategy_executions)
- 市场数据表 (market_data, symbols)
- 风险管理表 (risk_rules, risk_alerts)
- 系统管理表 (schema_versions)

### v1.1.0 - 性能跟踪
- 投资组合性能历史表 (portfolio_performance_history)
- 策略性能指标表 (strategy_performance_metrics)
- 新增性能统计字段
- 优化查询索引
- 创建常用视图

### v1.2.0 - 高级功能
- 用户通知系统 (user_notifications)
- API密钥管理 (user_api_keys)
- 回测系统 (backtests, backtest_results, backtest_trades)
- 系统配置表 (system_settings)
- 用户偏好设置 (user_preferences)
- 高级视图和存储过程

## 📊 表结构说明

### 核心业务表

#### 用户管理
- `users`: 用户基本信息
- `user_preferences`: 用户偏好设置
- `user_api_keys`: 用户API密钥管理

#### 投资组合
- `portfolios`: 投资组合基本信息
- `positions`: 持仓明细
- `portfolio_performance_history`: 性能历史记录

#### 交易系统
- `trades`: 交易记录
- `orders`: 订单管理

#### 策略系统
- `strategies`: 策略定义
- `strategy_executions`: 策略执行记录
- `strategy_performance_metrics`: 策略性能指标

#### 市场数据
- `market_data`: 历史市场数据
- `symbols`: 标的信息

#### 风险管理
- `risk_rules`: 风险规则
- `risk_alerts`: 风险警报

#### 回测系统
- `backtests`: 回测任务
- `backtest_results`: 回测结果
- `backtest_trades`: 回测交易记录

#### 系统管理
- `schema_versions`: 数据库版本管理
- `system_settings`: 系统配置
- `user_notifications`: 用户通知

### 索引优化

所有表都包含了合适的索引以优化查询性能：
- 主键索引
- 外键索引
- 常用查询字段的复合索引
- 时间字段索引

### 视图和存储过程

系统包含多个视图简化常用查询：
- `portfolio_overview`: 投资组合概览
- `strategy_execution_overview`: 策略执行概览
- `user_statistics`: 用户统计
- `trading_statistics`: 交易统计

## 🔄 版本升级流程

1. **备份数据库**（重要！）
   ```bash
   mysqldump -u root -p quant_trading > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **查看当前状态**
   ```bash
   python migrate.py status
   ```

3. **执行升级**
   ```bash
   python migrate.py upgrade
   ```

4. **验证升级结果**
   ```bash
   python migrate.py validate
   ```

## ⚠️ 注意事项

1. **备份重要性**: 在执行任何迁移操作前，请务必备份数据库
2. **环境配置**: 确保 `.env` 文件中的数据库配置正确
3. **权限要求**: 数据库用户需要有 CREATE、ALTER、DROP 等权限
4. **版本顺序**: 版本升级必须按顺序进行，不能跳跃升级
5. **测试环境**: 建议先在测试环境验证迁移脚本

## 🛠️ 故障排除

### 常见问题

1. **连接失败 (2003错误)**
   ```
   ✗ 数据库连接失败: (2003, "Can't connect to MySQL server on 'localhost'")
   ```
   **解决方案:**
   - 检查MySQL服务是否运行: `net start mysql` (Windows) 或 `sudo service mysql start` (Linux)
   - 确认端口3306是否被占用
   - 检查防火墙设置
   - 验证配置文件中的数据库地址和端口

2. **配置文件未找到**
   ```
   警告: 未找到配置文件，将使用默认数据库配置
   ```
   **解决方案:**
   - 复制 `db_config.env` 文件并根据实际情况修改
   - 或者创建 `.env` 文件在项目根目录
   - 确保配置文件包含正确的数据库连接信息

3. **SQL语法错误 (1064错误)**
   ```
   (1064, "You have an error in your SQL syntax...")
   ```
   **解决方案:**
   - 检查SQL文件语法
   - 确认MySQL版本兼容性
   - 查看具体的SQL语句输出

4. **重复列错误 (1060错误)**
   ```
   (1060, "Duplicate column name 'first_name'")
   ```
   **解决方案:**
   - 运行修复脚本: `python fix_v1.2.0.py`
   - 或者手动回滚: `python migrate.py rollback v1.2.0`
   - 然后重新升级: `python migrate.py upgrade v1.2.0`

5. **依赖缺失**
   ```bash
   pip install pymysql python-dotenv
   ```

6. **权限不足 (1045错误)**
   ```sql
   GRANT ALL PRIVILEGES ON quant_trading.* TO 'your_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

7. **字符编码问题**
   - 确保数据库使用 utf8mb4 字符集
   - 检查连接字符集配置

### 测试工具

运行测试脚本来诊断问题:
```bash
python test_migration.py
```

这个脚本会测试:
- 配置文件加载
- 数据库连接
- SQL解析功能
- 迁移文件检测

### 手动执行SQL

如果自动迁移失败，可以手动执行SQL文件：

```bash
mysql -u root -p quant_trading < schema.sql
mysql -u root -p quant_trading < migrations/v1.1.0_add_performance_tracking.sql
```

## 📝 开发指南

### 添加新的迁移

1. 创建新的迁移文件：`vX.Y.Z_description.sql`
2. 在文件中包含版本信息和升级说明
3. 添加必要的表结构变更
4. 更新 `schema_versions` 表
5. 测试迁移脚本

### 迁移文件模板

```sql
-- =====================================================
-- 版本: vX.Y.Z
-- 描述: 迁移描述
-- 创建时间: YYYY-MM-DD
-- 作者: 开发者姓名
-- 升级说明: 详细的升级说明
-- =====================================================

-- 检查当前版本
SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1;

-- 你的SQL变更语句

-- 记录版本更新
INSERT INTO `schema_versions` (`version`, `description`) 
VALUES ('vX.Y.Z', '迁移描述');
```

## 📞 支持

如果在使用过程中遇到问题，请：
1. 查看本文档的故障排除部分
2. 检查日志输出信息
3. 提交Issue到项目仓库

---

**重要提醒**: 在生产环境中使用前，请务必在测试环境中充分验证所有迁移脚本。
