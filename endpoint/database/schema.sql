-- =====================================================
-- 量化交易系统数据库表结构定义
-- 创建时间: 2024-12-19
-- 版本: v1.0.0
-- 描述: 完整的数据库表结构定义，包含所有核心业务表
-- =====================================================

-- 设置字符集和时区
SET NAMES utf8mb4;
SET TIME_ZONE = '+00:00';

-- =====================================================
-- 1. 用户管理表
-- =====================================================

-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(80) NOT NULL UNIQUE COMMENT '用户名',
    `email` VARCHAR(120) NOT NULL UNIQUE COMMENT '邮箱',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 2. 投资组合管理表
-- =====================================================

-- 投资组合表
CREATE TABLE IF NOT EXISTS `portfolios` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '投资组合ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '投资组合名称',
    `description` TEXT COMMENT '描述',
    `initial_capital` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '初始资金',
    `current_value` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '当前价值',
    `cash_balance` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '现金余额',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_name` (`name`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投资组合表';

-- 持仓表
CREATE TABLE IF NOT EXISTS `positions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '持仓ID',
    `portfolio_id` INT NOT NULL COMMENT '投资组合ID',
    `symbol` VARCHAR(20) NOT NULL COMMENT '标的代码',
    `quantity` DECIMAL(15,8) NOT NULL DEFAULT 0.00000000 COMMENT '持仓数量',
    `average_price` DECIMAL(15,8) NOT NULL DEFAULT 0.00000000 COMMENT '平均价格',
    `current_price` DECIMAL(15,8) NOT NULL DEFAULT 0.00000000 COMMENT '当前价格',
    `unrealized_pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '未实现盈亏',
    `realized_pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '已实现盈亏',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_portfolio_symbol` (`portfolio_id`, `symbol`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='持仓表';

-- =====================================================
-- 3. 交易管理表
-- =====================================================

-- 交易记录表
CREATE TABLE IF NOT EXISTS `trades` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '交易ID',
    `portfolio_id` INT NOT NULL COMMENT '投资组合ID',
    `strategy_execution_id` INT NULL COMMENT '策略执行ID',
    `symbol` VARCHAR(20) NOT NULL COMMENT '标的代码',
    `side` VARCHAR(10) NOT NULL COMMENT '交易方向(buy/sell)',
    `quantity` DECIMAL(15,8) NOT NULL COMMENT '交易数量',
    `price` DECIMAL(15,8) NOT NULL COMMENT '交易价格',
    `amount` DECIMAL(15,2) NOT NULL COMMENT '交易金额',
    `fee` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '手续费',
    `pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '盈亏',
    `status` VARCHAR(20) NOT NULL DEFAULT 'completed' COMMENT '状态(pending/completed/cancelled)',
    `executed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_side` (`side`),
    INDEX `idx_executed_at` (`executed_at`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易记录表';

-- 订单表
CREATE TABLE IF NOT EXISTS `orders` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `portfolio_id` INT NOT NULL COMMENT '投资组合ID',
    `strategy_execution_id` INT NULL COMMENT '策略执行ID',
    `symbol` VARCHAR(20) NOT NULL COMMENT '标的代码',
    `side` VARCHAR(10) NOT NULL COMMENT '交易方向(buy/sell)',
    `order_type` VARCHAR(20) NOT NULL COMMENT '订单类型(market/limit/stop)',
    `quantity` DECIMAL(15,8) NOT NULL COMMENT '订单数量',
    `price` DECIMAL(15,8) NULL COMMENT '限价单价格',
    `stop_price` DECIMAL(15,8) NULL COMMENT '止损价格',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态(pending/filled/cancelled/rejected)',
    `filled_quantity` DECIMAL(15,8) NOT NULL DEFAULT 0.00000000 COMMENT '已成交数量',
    `average_fill_price` DECIMAL(15,8) NULL COMMENT '平均成交价',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- =====================================================
-- 4. 策略管理表
-- =====================================================

-- 策略表
CREATE TABLE IF NOT EXISTS `strategies` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '策略ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '策略名称',
    `description` TEXT COMMENT '策略描述',
    `strategy_type` VARCHAR(50) NOT NULL COMMENT '策略类型',
    `parameters` TEXT COMMENT 'JSON格式的策略参数',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_strategy_type` (`strategy_type`),
    INDEX `idx_name` (`name`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='策略表';

-- 策略执行表
CREATE TABLE IF NOT EXISTS `strategy_executions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '策略执行ID',
    `strategy_id` INT NOT NULL COMMENT '策略ID',
    `portfolio_id` INT NOT NULL COMMENT '投资组合ID',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NULL COMMENT '结束时间',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `initial_capital` DECIMAL(15,2) NOT NULL COMMENT '初始资金',
    `current_value` DECIMAL(15,2) NOT NULL COMMENT '当前价值',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    INDEX `idx_strategy_id` (`strategy_id`),
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_start_time` (`start_time`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='策略执行表';

-- 为trades表添加外键约束（需要在strategy_executions表创建后）
ALTER TABLE `trades` 
ADD CONSTRAINT `fk_trades_strategy_execution` 
FOREIGN KEY (`strategy_execution_id`) REFERENCES `strategy_executions`(`id`) ON DELETE SET NULL;

-- 为orders表添加外键约束
ALTER TABLE `orders` 
ADD CONSTRAINT `fk_orders_strategy_execution` 
FOREIGN KEY (`strategy_execution_id`) REFERENCES `strategy_executions`(`id`) ON DELETE SET NULL;

-- =====================================================
-- 5. 市场数据表
-- =====================================================

-- 标的信息表
CREATE TABLE IF NOT EXISTS `symbols` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '标的ID',
    `symbol` VARCHAR(20) NOT NULL UNIQUE COMMENT '标的代码',
    `name` VARCHAR(100) NOT NULL COMMENT '标的名称',
    `exchange` VARCHAR(50) COMMENT '交易所',
    `asset_type` VARCHAR(20) NOT NULL COMMENT '资产类型(stock/crypto/forex)',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_symbol` (`symbol`),
    INDEX `idx_asset_type` (`asset_type`),
    INDEX `idx_exchange` (`exchange`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标的信息表';

-- 市场数据表
CREATE TABLE IF NOT EXISTS `market_data` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '市场数据ID',
    `symbol` VARCHAR(20) NOT NULL COMMENT '标的代码',
    `timestamp` DATETIME NOT NULL COMMENT '时间戳',
    `open_price` DECIMAL(15,8) NOT NULL COMMENT '开盘价',
    `high_price` DECIMAL(15,8) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(15,8) NOT NULL COMMENT '最低价',
    `close_price` DECIMAL(15,8) NOT NULL COMMENT '收盘价',
    `volume` DECIMAL(20,8) NOT NULL DEFAULT 0.00000000 COMMENT '成交量',
    `interval_type` VARCHAR(10) NOT NULL DEFAULT '1d' COMMENT '时间间隔(1m/5m/15m/1h/1d)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_symbol_timestamp_interval` (`symbol`, `timestamp`, `interval_type`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_timestamp` (`timestamp`),
    INDEX `idx_interval_type` (`interval_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='市场数据表';

-- =====================================================
-- 6. 风险管理表
-- =====================================================

-- 风险规则表
CREATE TABLE IF NOT EXISTS `risk_rules` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '风险规则ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `portfolio_id` INT NULL COMMENT '投资组合ID(NULL表示全局规则)',
    `rule_type` VARCHAR(50) NOT NULL COMMENT '规则类型',
    `rule_name` VARCHAR(100) NOT NULL COMMENT '规则名称',
    `parameters` TEXT COMMENT 'JSON格式的规则参数',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_rule_type` (`rule_type`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险规则表';

-- 风险警报表
CREATE TABLE IF NOT EXISTS `risk_alerts` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '风险警报ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `portfolio_id` INT NULL COMMENT '投资组合ID',
    `risk_rule_id` INT NULL COMMENT '风险规则ID',
    `alert_type` VARCHAR(50) NOT NULL COMMENT '警报类型',
    `message` TEXT NOT NULL COMMENT '警报消息',
    `severity` VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '严重程度(low/medium/high/critical)',
    `is_read` BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`risk_rule_id`) REFERENCES `risk_rules`(`id`) ON DELETE SET NULL,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_alert_type` (`alert_type`),
    INDEX `idx_severity` (`severity`),
    INDEX `idx_is_read` (`is_read`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险警报表';

-- =====================================================
-- 7. 系统管理表
-- =====================================================

-- 数据库版本管理表
CREATE TABLE IF NOT EXISTS `schema_versions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '版本ID',
    `version` VARCHAR(20) NOT NULL UNIQUE COMMENT '版本号',
    `description` TEXT COMMENT '版本描述',
    `applied_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '应用时间',
    `checksum` VARCHAR(64) COMMENT '文件校验和',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_version` (`version`),
    INDEX `idx_applied_at` (`applied_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库版本管理表';

-- 插入当前版本记录
INSERT IGNORE INTO `schema_versions` (`version`, `description`) 
VALUES ('v1.0.0', '初始数据库结构创建');

-- =====================================================
-- 8. 初始化数据
-- =====================================================

-- 插入一些常用的标的信息
INSERT IGNORE INTO `symbols` (`symbol`, `name`, `exchange`, `asset_type`) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 'stock'),
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'stock'),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'stock'),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'stock'),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'stock'),
('BTC-USD', 'Bitcoin USD', 'Crypto', 'crypto'),
('ETH-USD', 'Ethereum USD', 'Crypto', 'crypto'),
('BNB-USD', 'Binance Coin USD', 'Crypto', 'crypto');

-- =====================================================
-- 结束
-- =====================================================
