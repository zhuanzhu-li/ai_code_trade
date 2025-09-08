-- =====================================================
-- 回滚脚本: v1.2.0 -> v1.1.0
-- 用于清理部分失败的 v1.2.0 迁移
-- =====================================================

-- 删除 v1.2.0 版本记录（如果存在）
DELETE FROM `schema_versions` WHERE version = 'v1.2.0';

-- 删除可能已经创建的表（安全删除）
DROP TABLE IF EXISTS `user_notifications`;
DROP TABLE IF EXISTS `user_api_keys`;
DROP TABLE IF EXISTS `backtest_trades`;
DROP TABLE IF EXISTS `backtest_results`;
DROP TABLE IF EXISTS `backtests`;
DROP TABLE IF EXISTS `system_settings`;
DROP TABLE IF EXISTS `user_preferences`;

-- 删除可能已经添加的视图
DROP VIEW IF EXISTS `user_statistics`;
DROP VIEW IF EXISTS `trading_statistics`;

-- 删除可能已经添加的用户表字段
ALTER TABLE `users` DROP COLUMN IF EXISTS `first_name`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `last_name`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `phone`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `timezone`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `language`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `email_verified`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `two_factor_enabled`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `last_login_at`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `login_attempts`;
ALTER TABLE `users` DROP COLUMN IF EXISTS `locked_until`;

-- 删除可能已经添加的策略表字段
ALTER TABLE `strategies` DROP FOREIGN KEY IF EXISTS `fk_strategies_parent`;
ALTER TABLE `strategies` DROP COLUMN IF EXISTS `version`;
ALTER TABLE `strategies` DROP COLUMN IF EXISTS `parent_strategy_id`;
ALTER TABLE `strategies` DROP COLUMN IF EXISTS `tags`;
ALTER TABLE `strategies` DROP COLUMN IF EXISTS `is_public`;
ALTER TABLE `strategies` DROP COLUMN IF EXISTS `performance_summary`;

-- 删除可能已经添加的投资组合字段
ALTER TABLE `portfolios` DROP COLUMN IF EXISTS `total_return`;
ALTER TABLE `portfolios` DROP COLUMN IF EXISTS `max_drawdown`;
ALTER TABLE `portfolios` DROP COLUMN IF EXISTS `sharpe_ratio`;
ALTER TABLE `portfolios` DROP COLUMN IF EXISTS `last_performance_update`;

-- 删除可能已经添加的策略执行字段
ALTER TABLE `strategy_executions` DROP COLUMN IF EXISTS `total_trades`;
ALTER TABLE `strategy_executions` DROP COLUMN IF EXISTS `winning_trades`;
ALTER TABLE `strategy_executions` DROP COLUMN IF EXISTS `win_rate`;
ALTER TABLE `strategy_executions` DROP COLUMN IF EXISTS `max_drawdown`;
ALTER TABLE `strategy_executions` DROP COLUMN IF EXISTS `sharpe_ratio`;

SELECT 'v1.2.0 回滚完成' AS message;
