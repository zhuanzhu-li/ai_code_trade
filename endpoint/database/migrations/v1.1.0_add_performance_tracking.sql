-- =====================================================
-- 版本: v1.1.0
-- 描述: 添加性能跟踪相关表
-- 创建时间: 2024-12-19
-- 作者: AI量化交易系统
-- 升级说明: 添加投资组合性能历史记录和策略性能指标表
-- =====================================================

-- 检查当前版本
SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1;

-- =====================================================
-- 1. 投资组合性能历史表
-- =====================================================
CREATE TABLE IF NOT EXISTS `portfolio_performance_history` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '性能记录ID',
    `portfolio_id` INT NOT NULL COMMENT '投资组合ID',
    `date` DATE NOT NULL COMMENT '日期',
    `total_value` DECIMAL(15,2) NOT NULL COMMENT '总价值',
    `cash_balance` DECIMAL(15,2) NOT NULL COMMENT '现金余额',
    `positions_value` DECIMAL(15,2) NOT NULL COMMENT '持仓价值',
    `daily_pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '日盈亏',
    `daily_return` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '日收益率(%)',
    `cumulative_return` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '累计收益率(%)',
    `max_drawdown` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '最大回撤(%)',
    `sharpe_ratio` DECIMAL(8,4) NULL COMMENT '夏普比率',
    `volatility` DECIMAL(8,4) NULL COMMENT '波动率(%)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`portfolio_id`) REFERENCES `portfolios`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_portfolio_date` (`portfolio_id`, `date`),
    INDEX `idx_portfolio_id` (`portfolio_id`),
    INDEX `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投资组合性能历史表';

-- =====================================================
-- 2. 策略性能指标表
-- =====================================================
CREATE TABLE IF NOT EXISTS `strategy_performance_metrics` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '性能指标ID',
    `strategy_execution_id` INT NOT NULL COMMENT '策略执行ID',
    `date` DATE NOT NULL COMMENT '日期',
    `total_trades` INT NOT NULL DEFAULT 0 COMMENT '总交易次数',
    `winning_trades` INT NOT NULL DEFAULT 0 COMMENT '盈利交易次数',
    `losing_trades` INT NOT NULL DEFAULT 0 COMMENT '亏损交易次数',
    `win_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '胜率(%)',
    `avg_win` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '平均盈利',
    `avg_loss` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '平均亏损',
    `profit_factor` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '盈利因子',
    `max_consecutive_wins` INT NOT NULL DEFAULT 0 COMMENT '最大连续盈利次数',
    `max_consecutive_losses` INT NOT NULL DEFAULT 0 COMMENT '最大连续亏损次数',
    `total_pnl` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '总盈亏',
    `max_drawdown` DECIMAL(8,4) NOT NULL DEFAULT 0.0000 COMMENT '最大回撤(%)',
    `recovery_factor` DECIMAL(8,4) NULL COMMENT '恢复因子',
    `calmar_ratio` DECIMAL(8,4) NULL COMMENT 'Calmar比率',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    FOREIGN KEY (`strategy_execution_id`) REFERENCES `strategy_executions`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_strategy_execution_date` (`strategy_execution_id`, `date`),
    INDEX `idx_strategy_execution_id` (`strategy_execution_id`),
    INDEX `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='策略性能指标表';

-- =====================================================
-- 3. 添加新的索引以优化查询性能
-- =====================================================

-- 为trades表添加复合索引
ALTER TABLE `trades` ADD INDEX `idx_portfolio_symbol_executed` (`portfolio_id`, `symbol`, `executed_at`);

-- 为positions表添加复合索引
ALTER TABLE `positions` ADD INDEX `idx_portfolio_updated` (`portfolio_id`, `updated_at`);

-- 为market_data表添加复合索引
ALTER TABLE `market_data` ADD INDEX `idx_symbol_timestamp_desc` (`symbol`, `timestamp` DESC);

-- =====================================================
-- 4. 更新现有表结构（如果需要）
-- =====================================================

-- 为portfolios表添加性能统计字段
ALTER TABLE `portfolios` 
ADD COLUMN `total_return` DECIMAL(8,4) DEFAULT 0.0000 COMMENT '总收益率(%)' AFTER `cash_balance`,
ADD COLUMN `max_drawdown` DECIMAL(8,4) DEFAULT 0.0000 COMMENT '最大回撤(%)' AFTER `total_return`,
ADD COLUMN `sharpe_ratio` DECIMAL(8,4) NULL COMMENT '夏普比率' AFTER `max_drawdown`,
ADD COLUMN `last_performance_update` DATETIME NULL COMMENT '最后性能更新时间' AFTER `sharpe_ratio`;

-- 为strategy_executions表添加性能统计字段
ALTER TABLE `strategy_executions`
ADD COLUMN `total_trades` INT DEFAULT 0 COMMENT '总交易次数' AFTER `current_value`,
ADD COLUMN `winning_trades` INT DEFAULT 0 COMMENT '盈利交易次数' AFTER `total_trades`,
ADD COLUMN `win_rate` DECIMAL(5,2) DEFAULT 0.00 COMMENT '胜率(%)' AFTER `winning_trades`,
ADD COLUMN `max_drawdown` DECIMAL(8,4) DEFAULT 0.0000 COMMENT '最大回撤(%)' AFTER `win_rate`,
ADD COLUMN `sharpe_ratio` DECIMAL(8,4) NULL COMMENT '夏普比率' AFTER `max_drawdown`;

-- =====================================================
-- 5. 创建视图以简化常用查询
-- =====================================================

-- 投资组合概览视图
CREATE OR REPLACE VIEW `portfolio_overview` AS
SELECT 
    p.id,
    p.user_id,
    p.name,
    p.initial_capital,
    p.current_value,
    p.cash_balance,
    p.total_return,
    p.max_drawdown,
    p.sharpe_ratio,
    COUNT(DISTINCT pos.id) as position_count,
    COUNT(DISTINCT t.id) as trade_count,
    p.created_at,
    p.updated_at
FROM portfolios p
LEFT JOIN positions pos ON p.id = pos.portfolio_id AND pos.quantity > 0
LEFT JOIN trades t ON p.id = t.portfolio_id
WHERE p.is_active = TRUE
GROUP BY p.id;

-- 策略执行概览视图
CREATE OR REPLACE VIEW `strategy_execution_overview` AS
SELECT 
    se.id,
    se.strategy_id,
    s.name as strategy_name,
    s.strategy_type,
    se.portfolio_id,
    p.name as portfolio_name,
    se.start_time,
    se.end_time,
    se.is_active,
    se.initial_capital,
    se.current_value,
    se.total_trades,
    se.winning_trades,
    se.win_rate,
    se.max_drawdown,
    se.sharpe_ratio,
    ROUND(((se.current_value - se.initial_capital) / se.initial_capital * 100), 2) as total_return_pct,
    COUNT(t.id) as actual_trade_count,
    se.created_at,
    se.updated_at
FROM strategy_executions se
JOIN strategies s ON se.strategy_id = s.id
JOIN portfolios p ON se.portfolio_id = p.id
LEFT JOIN trades t ON se.id = t.strategy_execution_id
GROUP BY se.id;

-- =====================================================
-- 6. 记录版本更新
-- =====================================================
INSERT INTO `schema_versions` (`version`, `description`) 
VALUES ('v1.1.0', '添加性能跟踪相关表和视图，优化查询索引');

-- =====================================================
-- 升级完成
-- =====================================================
