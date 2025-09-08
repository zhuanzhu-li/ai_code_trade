-- =====================================================
-- 版本: v1.2.0
-- 描述: 添加高级功能支持
-- 创建时间: 2024-12-19
-- 作者: AI量化交易系统
-- 升级说明: 添加通知系统、API密钥管理、回测功能等高级特性
-- =====================================================

-- 检查当前版本
SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1;

-- =====================================================
-- 1. 用户通知系统
-- =====================================================
CREATE TABLE IF NOT EXISTS `user_notifications` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '通知ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(200) NOT NULL COMMENT '通知标题',
    `message` TEXT NOT NULL COMMENT '通知内容',
    `notification_type` VARCHAR(50) NOT NULL COMMENT '通知类型(trade/risk/system/strategy)',
    `priority` VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '优先级(low/normal/high/urgent)',
    `is_read` BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    `read_at` DATETIME NULL COMMENT '读取时间',
    `related_id` INT NULL COMMENT '相关对象ID',
    `related_type` VARCHAR(50) NULL COMMENT '相关对象类型(trade/portfolio/strategy)',
    `expires_at` DATETIME NULL COMMENT '过期时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_notification_type` (`notification_type`),
    INDEX `idx_priority` (`priority`),
    INDEX `idx_is_read` (`is_read`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户通知表';

-- =====================================================
-- 2. API密钥管理
-- =====================================================
CREATE TABLE IF NOT EXISTS `user_api_keys` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT 'API密钥ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `key_name` VARCHAR(100) NOT NULL COMMENT '密钥名称',
    `api_key` VARCHAR(64) NOT NULL UNIQUE COMMENT 'API密钥',
    `api_secret` VARCHAR(255) NULL COMMENT 'API密钥(加密存储)',
    `exchange` VARCHAR(50) NOT NULL COMMENT '交易所名称',
    `permissions` JSON COMMENT '权限配置',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `is_testnet` BOOLEAN DEFAULT FALSE COMMENT '是否测试网',
    `last_used_at` DATETIME NULL COMMENT '最后使用时间',
    `expires_at` DATETIME NULL COMMENT '过期时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_api_key` (`api_key`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_exchange` (`exchange`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户API密钥表';

-- =====================================================
-- 3. 回测系统
-- =====================================================
CREATE TABLE IF NOT EXISTS `backtests` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '回测ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `strategy_id` INT NOT NULL COMMENT '策略ID',
    `name` VARCHAR(100) NOT NULL COMMENT '回测名称',
    `description` TEXT COMMENT '回测描述',
    `start_date` DATE NOT NULL COMMENT '开始日期',
    `end_date` DATE NOT NULL COMMENT '结束日期',
    `initial_capital` DECIMAL(15,2) NOT NULL COMMENT '初始资金',
    `symbols` JSON NOT NULL COMMENT '回测标的列表',
    `parameters` JSON COMMENT '回测参数',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态(pending/running/completed/failed)',
    `progress` INT DEFAULT 0 COMMENT '进度百分比',
    `started_at` DATETIME NULL COMMENT '开始时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `error_message` TEXT NULL COMMENT '错误信息',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_strategy_id` (`strategy_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='回测表';

-- 回测结果表
CREATE TABLE IF NOT EXISTS `backtest_results` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '回测结果ID',
    `backtest_id` INT NOT NULL COMMENT '回测ID',
    `final_value` DECIMAL(15,2) NOT NULL COMMENT '最终价值',
    `total_return` DECIMAL(8,4) NOT NULL COMMENT '总收益率(%)',
    `annual_return` DECIMAL(8,4) NOT NULL COMMENT '年化收益率(%)',
    `max_drawdown` DECIMAL(8,4) NOT NULL COMMENT '最大回撤(%)',
    `sharpe_ratio` DECIMAL(8,4) NULL COMMENT '夏普比率',
    `sortino_ratio` DECIMAL(8,4) NULL COMMENT '索提诺比率',
    `calmar_ratio` DECIMAL(8,4) NULL COMMENT 'Calmar比率',
    `volatility` DECIMAL(8,4) NOT NULL COMMENT '波动率(%)',
    `total_trades` INT NOT NULL DEFAULT 0 COMMENT '总交易次数',
    `winning_trades` INT NOT NULL DEFAULT 0 COMMENT '盈利交易次数',
    `win_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '胜率(%)',
    `avg_win` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '平均盈利',
    `avg_loss` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '平均亏损',
    `profit_factor` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '盈利因子',
    `max_consecutive_wins` INT NOT NULL DEFAULT 0 COMMENT '最大连续盈利',
    `max_consecutive_losses` INT NOT NULL DEFAULT 0 COMMENT '最大连续亏损',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`backtest_id`) REFERENCES `backtests`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_backtest_id` (`backtest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='回测结果表';

-- 回测交易记录表
CREATE TABLE IF NOT EXISTS `backtest_trades` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '回测交易ID',
    `backtest_id` INT NOT NULL COMMENT '回测ID',
    `symbol` VARCHAR(20) NOT NULL COMMENT '标的代码',
    `side` VARCHAR(10) NOT NULL COMMENT '交易方向',
    `quantity` DECIMAL(15,8) NOT NULL COMMENT '交易数量',
    `price` DECIMAL(15,8) NOT NULL COMMENT '交易价格',
    `amount` DECIMAL(15,2) NOT NULL COMMENT '交易金额',
    `pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '盈亏',
    `commission` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '手续费',
    `executed_at` DATETIME NOT NULL COMMENT '执行时间',
    `signal_data` JSON COMMENT '信号数据',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`backtest_id`) REFERENCES `backtests`(`id`) ON DELETE CASCADE,
    INDEX `idx_backtest_id` (`backtest_id`),
    INDEX `idx_symbol` (`symbol`),
    INDEX `idx_executed_at` (`executed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='回测交易记录表';

-- =====================================================
-- 4. 系统配置表
-- =====================================================
CREATE TABLE IF NOT EXISTS `system_settings` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '设置ID',
    `setting_key` VARCHAR(100) NOT NULL UNIQUE COMMENT '设置键',
    `setting_value` TEXT NOT NULL COMMENT '设置值',
    `setting_type` VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '设置类型(string/number/boolean/json)',
    `category` VARCHAR(50) NOT NULL DEFAULT 'general' COMMENT '设置分类',
    `description` TEXT COMMENT '设置描述',
    `is_public` BOOLEAN DEFAULT FALSE COMMENT '是否公开(前端可访问)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_setting_key` (`setting_key`),
    INDEX `idx_category` (`category`),
    INDEX `idx_is_public` (`is_public`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统设置表';

-- =====================================================
-- 5. 用户偏好设置
-- =====================================================
CREATE TABLE IF NOT EXISTS `user_preferences` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '偏好ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `preference_key` VARCHAR(100) NOT NULL COMMENT '偏好键',
    `preference_value` TEXT NOT NULL COMMENT '偏好值',
    `preference_type` VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '偏好类型',
    `category` VARCHAR(50) NOT NULL DEFAULT 'general' COMMENT '偏好分类',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_user_preference` (`user_id`, `preference_key`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户偏好设置表';

-- =====================================================
-- 6. 添加新字段到现有表
-- =====================================================

-- 为用户表添加更多字段（安全添加，检查列是否存在）
-- 添加 first_name 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'first_name') = 0,
    'ALTER TABLE `users` ADD COLUMN `first_name` VARCHAR(50) NULL COMMENT ''名'' AFTER `email`',
    'SELECT ''Column first_name already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 last_name 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'last_name') = 0,
    'ALTER TABLE `users` ADD COLUMN `last_name` VARCHAR(50) NULL COMMENT ''姓'' AFTER `first_name`',
    'SELECT ''Column last_name already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 phone 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'phone') = 0,
    'ALTER TABLE `users` ADD COLUMN `phone` VARCHAR(20) NULL COMMENT ''电话'' AFTER `last_name`',
    'SELECT ''Column phone already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 timezone 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'timezone') = 0,
    'ALTER TABLE `users` ADD COLUMN `timezone` VARCHAR(50) DEFAULT ''UTC'' COMMENT ''时区'' AFTER `phone`',
    'SELECT ''Column timezone already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 language 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'language') = 0,
    'ALTER TABLE `users` ADD COLUMN `language` VARCHAR(10) DEFAULT ''zh'' COMMENT ''语言'' AFTER `timezone`',
    'SELECT ''Column language already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 email_verified 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'email_verified') = 0,
    'ALTER TABLE `users` ADD COLUMN `email_verified` BOOLEAN DEFAULT FALSE COMMENT ''邮箱已验证'' AFTER `language`',
    'SELECT ''Column email_verified already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 two_factor_enabled 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'two_factor_enabled') = 0,
    'ALTER TABLE `users` ADD COLUMN `two_factor_enabled` BOOLEAN DEFAULT FALSE COMMENT ''双因子认证'' AFTER `email_verified`',
    'SELECT ''Column two_factor_enabled already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 last_login_at 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'last_login_at') = 0,
    'ALTER TABLE `users` ADD COLUMN `last_login_at` DATETIME NULL COMMENT ''最后登录时间'' AFTER `two_factor_enabled`',
    'SELECT ''Column last_login_at already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 login_attempts 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'login_attempts') = 0,
    'ALTER TABLE `users` ADD COLUMN `login_attempts` INT DEFAULT 0 COMMENT ''登录尝试次数'' AFTER `last_login_at`',
    'SELECT ''Column login_attempts already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 locked_until 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'users' 
       AND COLUMN_NAME = 'locked_until') = 0,
    'ALTER TABLE `users` ADD COLUMN `locked_until` DATETIME NULL COMMENT ''锁定到期时间'' AFTER `login_attempts`',
    'SELECT ''Column locked_until already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 为策略表添加版本控制（安全添加）
-- 添加 version 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND COLUMN_NAME = 'version') = 0,
    'ALTER TABLE `strategies` ADD COLUMN `version` VARCHAR(20) DEFAULT ''1.0.0'' COMMENT ''策略版本'' AFTER `parameters`',
    'SELECT ''Column version already exists in strategies'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 parent_strategy_id 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND COLUMN_NAME = 'parent_strategy_id') = 0,
    'ALTER TABLE `strategies` ADD COLUMN `parent_strategy_id` INT NULL COMMENT ''父策略ID'' AFTER `version`',
    'SELECT ''Column parent_strategy_id already exists in strategies'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 tags 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND COLUMN_NAME = 'tags') = 0,
    'ALTER TABLE `strategies` ADD COLUMN `tags` JSON COMMENT ''标签'' AFTER `parent_strategy_id`',
    'SELECT ''Column tags already exists in strategies'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 is_public 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND COLUMN_NAME = 'is_public') = 0,
    'ALTER TABLE `strategies` ADD COLUMN `is_public` BOOLEAN DEFAULT FALSE COMMENT ''是否公开'' AFTER `tags`',
    'SELECT ''Column is_public already exists in strategies'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 performance_summary 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND COLUMN_NAME = 'performance_summary') = 0,
    'ALTER TABLE `strategies` ADD COLUMN `performance_summary` JSON COMMENT ''性能摘要'' AFTER `is_public`',
    'SELECT ''Column performance_summary already exists in strategies'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加外键约束（安全添加）
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'strategies' 
       AND CONSTRAINT_NAME = 'fk_strategies_parent') = 0,
    'ALTER TABLE `strategies` ADD CONSTRAINT `fk_strategies_parent` FOREIGN KEY (`parent_strategy_id`) REFERENCES `strategies`(`id`) ON DELETE SET NULL',
    'SELECT ''Foreign key fk_strategies_parent already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 7. 插入默认系统设置
-- =====================================================
INSERT IGNORE INTO `system_settings` (`setting_key`, `setting_value`, `setting_type`, `category`, `description`, `is_public`) VALUES
('app.name', 'AI量化交易系统', 'string', 'general', '应用名称', TRUE),
('app.version', '1.2.0', 'string', 'general', '应用版本', TRUE),
('trading.default_commission_rate', '0.001', 'number', 'trading', '默认手续费率', FALSE),
('trading.max_position_size', '10000', 'number', 'trading', '最大持仓金额', FALSE),
('trading.max_daily_loss', '1000', 'number', 'trading', '最大日亏损', FALSE),
('risk.max_drawdown_threshold', '0.2', 'number', 'risk', '最大回撤阈值', FALSE),
('data.default_data_source', 'yahoo', 'string', 'data', '默认数据源', FALSE),
('notification.email_enabled', 'true', 'boolean', 'notification', '邮件通知启用', FALSE),
('notification.max_notifications_per_user', '100', 'number', 'notification', '每用户最大通知数', FALSE),
('backtest.max_concurrent_backtests', '3', 'number', 'backtest', '最大并发回测数', FALSE);

-- =====================================================
-- 8. 创建高级视图
-- =====================================================

-- 用户统计视图
CREATE OR REPLACE VIEW `user_statistics` AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at as user_created_at,
    u.last_login_at,
    COUNT(DISTINCT p.id) as portfolio_count,
    COUNT(DISTINCT s.id) as strategy_count,
    COUNT(DISTINCT t.id) as trade_count,
    COUNT(DISTINCT b.id) as backtest_count,
    COUNT(DISTINCT n.id) as notification_count,
    COUNT(DISTINCT CASE WHEN n.is_read = FALSE THEN n.id END) as unread_notification_count,
    COALESCE(SUM(p.current_value), 0) as total_portfolio_value,
    COALESCE(SUM(p.current_value - p.initial_capital), 0) as total_pnl
FROM users u
LEFT JOIN portfolios p ON u.id = p.user_id AND p.is_active = TRUE
LEFT JOIN strategies s ON u.id = s.user_id AND s.is_active = TRUE
LEFT JOIN trades t ON p.id = t.portfolio_id
LEFT JOIN backtests b ON u.id = b.user_id
LEFT JOIN user_notifications n ON u.id = n.user_id
WHERE u.is_active = TRUE
GROUP BY u.id;

-- 交易统计视图
CREATE OR REPLACE VIEW `trading_statistics` AS
SELECT 
    DATE(t.executed_at) as trade_date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN t.side = 'buy' THEN 1 END) as buy_trades,
    COUNT(CASE WHEN t.side = 'sell' THEN 1 END) as sell_trades,
    COUNT(CASE WHEN t.pnl > 0 THEN 1 END) as profitable_trades,
    COUNT(CASE WHEN t.pnl < 0 THEN 1 END) as losing_trades,
    SUM(t.amount) as total_volume,
    SUM(t.fee) as total_fees,
    SUM(t.pnl) as total_pnl,
    AVG(t.pnl) as avg_pnl,
    MAX(t.pnl) as max_profit,
    MIN(t.pnl) as max_loss
FROM trades t
WHERE t.status = 'completed'
GROUP BY DATE(t.executed_at)
ORDER BY trade_date DESC;

-- =====================================================
-- 9. 创建存储过程（暂时跳过，可在后续版本中添加）
-- =====================================================
-- 注意: 存储过程创建被暂时移除，以避免SQL解析复杂性
-- 可以在后续版本中通过单独的迁移文件添加

-- =====================================================
-- 10. 记录版本更新
-- =====================================================
INSERT INTO `schema_versions` (`version`, `description`) 
VALUES ('v1.2.0', '添加通知系统、API密钥管理、回测功能和高级特性支持');

-- =====================================================
-- 升级完成
-- =====================================================
