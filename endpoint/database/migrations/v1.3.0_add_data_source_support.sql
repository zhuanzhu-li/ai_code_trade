-- =====================================================
-- 版本: v1.3.0
-- 描述: 添加数据来源支持
-- 创建时间: 2024-12-19
-- 作者: AI量化交易系统
-- 升级说明: 添加数据来源表，为symbols和market_data表增加数据来源标识
-- =====================================================

-- 检查当前版本
SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1;

-- =====================================================
-- 1. 创建数据来源表
-- =====================================================
CREATE TABLE IF NOT EXISTS `data_sources` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '数据来源ID',
    `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '数据来源名称',
    `uri` VARCHAR(500) NOT NULL COMMENT '数据来源URI',
    `description` TEXT COMMENT '数据来源描述',
    `provider_type` VARCHAR(50) NOT NULL COMMENT '提供商类型(akshare/yahoo/alpha_vantage等)',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `priority` INT DEFAULT 1 COMMENT '优先级(数字越小优先级越高)',
    `config` TEXT COMMENT 'JSON格式的配置信息',
    `last_updated` DATETIME NULL COMMENT '最后更新时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`),
    INDEX `idx_provider_type` (`provider_type`),
    INDEX `idx_is_active` (`is_active`),
    INDEX `idx_priority` (`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据来源表';

-- =====================================================
-- 2. 为symbols表添加数据来源字段
-- =====================================================

-- 添加 data_source_id 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'symbols' 
       AND COLUMN_NAME = 'data_source_id') = 0,
    'ALTER TABLE `symbols` ADD COLUMN `data_source_id` INT NULL COMMENT ''数据来源ID'' AFTER `asset_type`',
    'SELECT ''Column data_source_id already exists in symbols'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加外键约束
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'symbols' 
       AND CONSTRAINT_NAME = 'fk_symbols_data_source') = 0,
    'ALTER TABLE `symbols` ADD CONSTRAINT `fk_symbols_data_source` FOREIGN KEY (`data_source_id`) REFERENCES `data_sources`(`id`) ON DELETE SET NULL',
    'SELECT ''Foreign key fk_symbols_data_source already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 3. 为market_data表添加数据来源字段
-- =====================================================

-- 添加 data_source_id 列
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'market_data' 
       AND COLUMN_NAME = 'data_source_id') = 0,
    'ALTER TABLE `market_data` ADD COLUMN `data_source_id` INT NULL COMMENT ''数据来源ID'' AFTER `symbol`',
    'SELECT ''Column data_source_id already exists in market_data'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加外键约束
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'market_data' 
       AND CONSTRAINT_NAME = 'fk_market_data_data_source') = 0,
    'ALTER TABLE `market_data` ADD CONSTRAINT `fk_market_data_data_source` FOREIGN KEY (`data_source_id`) REFERENCES `data_sources`(`id`) ON DELETE SET NULL',
    'SELECT ''Foreign key fk_market_data_data_source already exists'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加索引
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
       AND TABLE_NAME = 'market_data' 
       AND INDEX_NAME = 'idx_data_source_id') = 0,
    'ALTER TABLE `market_data` ADD INDEX `idx_data_source_id` (`data_source_id`)',
    'SELECT ''Index idx_data_source_id already exists in market_data'' AS message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 4. 插入默认数据来源
-- =====================================================
INSERT IGNORE INTO `data_sources` (`name`, `uri`, `description`, `provider_type`, `is_active`, `priority`, `config`) VALUES
('AKShare', 'https://akshare.akfamily.xyz/', 'AKShare开源财经数据接口库，提供股票、期货、外汇等数据', 'akshare', TRUE, 1, '{"api_base": "https://akshare.akfamily.xyz/", "timeout": 30}'),
('Yahoo Finance', 'https://finance.yahoo.com/', 'Yahoo Finance免费股票数据接口', 'yahoo', TRUE, 2, '{"api_base": "https://query1.finance.yahoo.com/v8/finance/chart/", "timeout": 30}'),
('Alpha Vantage', 'https://www.alphavantage.co/', 'Alpha Vantage专业金融数据API', 'alpha_vantage', TRUE, 3, '{"api_base": "https://www.alphavantage.co/query", "timeout": 30}'),
('Tushare', 'https://tushare.pro/', 'Tushare专业金融数据服务', 'tushare', TRUE, 4, '{"api_base": "https://api.tushare.pro", "timeout": 30}'),
('东方财富', 'https://quote.eastmoney.com/', '东方财富网股票数据接口', 'eastmoney', TRUE, 5, '{"api_base": "https://quote.eastmoney.com", "timeout": 30}');

-- =====================================================
-- 5. 更新现有symbols的数据来源
-- =====================================================
-- 将现有的symbols关联到默认的AKShare数据源
UPDATE `symbols` 
SET `data_source_id` = (SELECT id FROM `data_sources` WHERE `name` = 'AKShare' LIMIT 1)
WHERE `data_source_id` IS NULL;

-- =====================================================
-- 6. 创建数据来源管理视图
-- =====================================================
CREATE OR REPLACE VIEW `data_source_statistics` AS
SELECT 
    ds.id,
    ds.name,
    ds.provider_type,
    ds.is_active,
    ds.priority,
    ds.last_updated,
    COUNT(DISTINCT s.id) as symbol_count,
    COUNT(DISTINCT md.id) as market_data_count,
    MAX(md.created_at) as latest_data_time
FROM data_sources ds
LEFT JOIN symbols s ON ds.id = s.data_source_id
LEFT JOIN market_data md ON ds.id = md.data_source_id
GROUP BY ds.id, ds.name, ds.provider_type, ds.is_active, ds.priority, ds.last_updated
ORDER BY ds.priority, ds.name;

-- =====================================================
-- 7. 创建数据来源性能监控视图
-- =====================================================
CREATE OR REPLACE VIEW `data_source_performance` AS
SELECT 
    ds.id,
    ds.name,
    ds.provider_type,
    COUNT(md.id) as total_records,
    COUNT(DISTINCT md.symbol) as unique_symbols,
    MIN(md.timestamp) as earliest_data,
    MAX(md.timestamp) as latest_data,
    COUNT(md.id) / DATEDIFF(MAX(md.timestamp), MIN(md.timestamp)) as avg_records_per_day
FROM data_sources ds
LEFT JOIN market_data md ON ds.id = md.data_source_id
WHERE ds.is_active = TRUE
GROUP BY ds.id, ds.name, ds.provider_type
HAVING total_records > 0
ORDER BY total_records DESC;

-- =====================================================
-- 8. 记录版本更新
-- =====================================================
INSERT INTO `schema_versions` (`version`, `description`) 
VALUES ('v1.3.0', '添加数据来源支持，为symbols和market_data表增加数据来源标识');

-- =====================================================
-- 升级完成
-- =====================================================
