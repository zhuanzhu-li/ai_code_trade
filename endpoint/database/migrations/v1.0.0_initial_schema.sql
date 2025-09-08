-- =====================================================
-- 版本: v1.0.0
-- 描述: 初始数据库结构创建
-- 创建时间: 2024-12-19
-- 作者: AI量化交易系统
-- =====================================================

-- 执行主要的schema创建脚本
SOURCE schema.sql;

-- 记录版本信息
INSERT IGNORE INTO `schema_versions` (`version`, `description`, `checksum`) 
VALUES ('v1.0.0', '初始数据库结构创建', SHA2(LOAD_FILE('schema.sql'), 256));
