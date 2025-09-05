from models import db, RiskRule, RiskAlert, Portfolio, Trade
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskService:
    """风险管理服务类"""
    
    def check_trade_risk(self, portfolio, trade_data):
        """检查交易风险"""
        violations = []
        
        # 获取所有活跃的风险规则
        rules = RiskRule.query.filter_by(is_active=True).all()
        
        for rule in rules:
            try:
                is_violated, message = rule.check_rule(portfolio, trade_data)
                if is_violated:
                    violations.append(message)
                    # 创建风险警报
                    self._create_risk_alert(rule, portfolio, 'warning', message)
            except Exception as e:
                logger.error(f"风险规则检查失败: {e}")
                continue
        
        return violations
    
    def check_portfolio_risk(self, portfolio):
        """检查投资组合风险"""
        alerts = []
        
        # 获取所有活跃的风险规则
        rules = RiskRule.query.filter_by(is_active=True).all()
        
        for rule in rules:
            try:
                is_violated, message = rule.check_rule(portfolio)
                if is_violated:
                    alerts.append(message)
                    # 创建风险警报
                    self._create_risk_alert(rule, portfolio, 'error', message)
            except Exception as e:
                logger.error(f"投资组合风险检查失败: {e}")
                continue
        
        return alerts
    
    def _create_risk_alert(self, rule, portfolio, alert_type, message):
        """创建风险警报"""
        alert = RiskAlert(
            risk_rule_id=rule.id,
            portfolio_id=portfolio.id,
            alert_type=alert_type,
            message=message
        )
        
        db.session.add(alert)
        db.session.commit()
        
        logger.warning(f"风险警报: {message}")
    
    def get_portfolio_risk_metrics(self, portfolio):
        """获取投资组合风险指标"""
        try:
            # 计算总价值
            total_value = portfolio.get_total_value()
            
            # 计算总盈亏
            total_pnl = portfolio.get_total_pnl()
            total_pnl_percentage = portfolio.get_total_pnl_percentage()
            
            # 计算最大回撤
            max_drawdown = self._calculate_max_drawdown(portfolio)
            
            # 计算波动率
            volatility = self._calculate_volatility(portfolio)
            
            # 计算夏普比率
            sharpe_ratio = self._calculate_sharpe_ratio(portfolio)
            
            # 计算VaR (Value at Risk)
            var_95 = self._calculate_var(portfolio, confidence_level=0.95)
            var_99 = self._calculate_var(portfolio, confidence_level=0.99)
            
            return {
                'total_value': total_value,
                'total_pnl': total_pnl,
                'total_pnl_percentage': total_pnl_percentage,
                'max_drawdown': max_drawdown,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'var_95': var_95,
                'var_99': var_99
            }
            
        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}
    
    def _calculate_max_drawdown(self, portfolio):
        """计算最大回撤"""
        try:
            # 获取历史净值数据
            trades = portfolio.trades.order_by(Trade.executed_at.asc()).all()
            
            if not trades:
                return 0
            
            # 计算净值序列
            nav_series = []
            current_value = float(portfolio.initial_capital)
            
            for trade in trades:
                if trade.side == 'buy':
                    current_value -= float(trade.amount)
                else:
                    current_value += float(trade.amount)
                nav_series.append(current_value)
            
            if not nav_series:
                return 0
            
            # 计算最大回撤
            peak = nav_series[0]
            max_drawdown = 0
            
            for value in nav_series:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return max_drawdown * 100  # 转换为百分比
            
        except Exception as e:
            logger.error(f"计算最大回撤失败: {e}")
            return 0
    
    def _calculate_volatility(self, portfolio, period=30):
        """计算波动率"""
        try:
            # 获取最近30天的交易数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            trades = portfolio.trades.filter(
                Trade.executed_at >= start_date,
                Trade.executed_at <= end_date
            ).order_by(Trade.executed_at.asc()).all()
            
            if len(trades) < 2:
                return 0
            
            # 计算日收益率
            returns = []
            for i in range(1, len(trades)):
                prev_value = float(trades[i-1].amount)
                curr_value = float(trades[i].amount)
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
            
            if not returns:
                return 0
            
            # 计算标准差
            import numpy as np
            volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
            return volatility * 100  # 转换为百分比
            
        except Exception as e:
            logger.error(f"计算波动率失败: {e}")
            return 0
    
    def _calculate_sharpe_ratio(self, portfolio, risk_free_rate=0.02):
        """计算夏普比率"""
        try:
            # 获取年化收益率
            total_pnl_percentage = portfolio.get_total_pnl_percentage()
            annual_return = total_pnl_percentage / 100
            
            # 获取年化波动率
            volatility = self._calculate_volatility(portfolio) / 100
            
            if volatility == 0:
                return 0
            
            sharpe_ratio = (annual_return - risk_free_rate) / volatility
            return sharpe_ratio
            
        except Exception as e:
            logger.error(f"计算夏普比率失败: {e}")
            return 0
    
    def _calculate_var(self, portfolio, confidence_level=0.95):
        """计算VaR (Value at Risk)"""
        try:
            # 获取历史交易数据
            trades = portfolio.trades.order_by(Trade.executed_at.desc()).limit(100).all()
            
            if len(trades) < 10:
                return 0
            
            # 计算交易盈亏
            pnls = [float(trade.pnl) for trade in trades if trade.pnl != 0]
            
            if not pnls:
                return 0
            
            # 计算VaR
            import numpy as np
            var = np.percentile(pnls, (1 - confidence_level) * 100)
            return abs(var)
            
        except Exception as e:
            logger.error(f"计算VaR失败: {e}")
            return 0
    
    def get_active_alerts(self, portfolio_id=None):
        """获取活跃的风险警报"""
        query = RiskAlert.query.filter_by(is_resolved=False)
        
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        
        alerts = query.order_by(RiskAlert.created_at.desc()).all()
        return [alert.to_dict() for alert in alerts]
    
    def resolve_alert(self, alert_id):
        """解决风险警报"""
        alert = RiskAlert.query.get_or_404(alert_id)
        alert.resolve()
        db.session.commit()
        
        return alert
