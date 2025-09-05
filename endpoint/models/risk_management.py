from . import db
from datetime import datetime
from decimal import Decimal
import json

class RiskRule(db.Model):
    """风险管理规则模型"""
    __tablename__ = 'risk_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rule_type = db.Column(db.String(50), nullable=False)  # 规则类型：position_size, daily_loss, drawdown等
    parameters = db.Column(db.Text)  # JSON格式的规则参数
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    alerts = db.relationship('RiskAlert', backref='risk_rule', lazy='dynamic')
    
    def get_parameters(self):
        """获取规则参数"""
        if self.parameters:
            return json.loads(self.parameters)
        return {}
    
    def set_parameters(self, params):
        """设置规则参数"""
        self.parameters = json.dumps(params)
    
    def check_rule(self, portfolio, trade_data=None):
        """检查规则是否触发"""
        params = self.get_parameters()
        
        if self.rule_type == 'position_size':
            return self._check_position_size_rule(portfolio, params, trade_data)
        elif self.rule_type == 'daily_loss':
            return self._check_daily_loss_rule(portfolio, params)
        elif self.rule_type == 'drawdown':
            return self._check_drawdown_rule(portfolio, params)
        elif self.rule_type == 'max_trades_per_day':
            return self._check_max_trades_rule(portfolio, params)
        
        return False, "未知的规则类型"
    
    def _check_position_size_rule(self, portfolio, params, trade_data):
        """检查持仓大小规则"""
        max_position_size = params.get('max_position_size', 0)
        max_position_percentage = params.get('max_position_percentage', 0)
        
        if trade_data:
            trade_value = trade_data.get('quantity', 0) * trade_data.get('price', 0)
            if trade_value > max_position_size:
                return True, f"交易金额 {trade_value} 超过最大持仓金额 {max_position_size}"
            
            if max_position_percentage > 0:
                portfolio_value = portfolio.get_total_value()
                if portfolio_value > 0:
                    position_percentage = (trade_value / portfolio_value) * 100
                    if position_percentage > max_position_percentage:
                        return True, f"交易金额占比 {position_percentage:.2f}% 超过最大占比 {max_position_percentage}%"
        
        return False, None
    
    def _check_daily_loss_rule(self, portfolio, params):
        """检查日损失规则"""
        max_daily_loss = params.get('max_daily_loss', 0)
        max_daily_loss_percentage = params.get('max_daily_loss_percentage', 0)
        
        # 这里需要计算当日的损失
        # 简化实现，实际应该查询当日交易记录
        daily_pnl = 0  # 实际应该从交易记录计算
        
        if daily_pnl < -max_daily_loss:
            return True, f"当日损失 {abs(daily_pnl)} 超过最大日损失 {max_daily_loss}"
        
        if max_daily_loss_percentage > 0:
            portfolio_value = portfolio.get_total_value()
            if portfolio_value > 0:
                daily_loss_percentage = (abs(daily_pnl) / portfolio_value) * 100
                if daily_loss_percentage > max_daily_loss_percentage:
                    return True, f"当日损失占比 {daily_loss_percentage:.2f}% 超过最大占比 {max_daily_loss_percentage}%"
        
        return False, None
    
    def _check_drawdown_rule(self, portfolio, params):
        """检查回撤规则"""
        max_drawdown_percentage = params.get('max_drawdown_percentage', 0)
        
        if max_drawdown_percentage > 0:
            # 这里需要计算最大回撤
            # 简化实现，实际应该查询历史净值
            current_value = portfolio.get_total_value()
            peak_value = current_value  # 实际应该查询历史峰值
            drawdown_percentage = ((peak_value - current_value) / peak_value) * 100
            
            if drawdown_percentage > max_drawdown_percentage:
                return True, f"当前回撤 {drawdown_percentage:.2f}% 超过最大回撤 {max_drawdown_percentage}%"
        
        return False, None
    
    def _check_max_trades_rule(self, portfolio, params):
        """检查最大交易次数规则"""
        max_trades = params.get('max_trades', 0)
        
        if max_trades > 0:
            # 查询当日交易次数
            from datetime import date
            today = date.today()
            today_trades = portfolio.trades.filter(
                db.func.date(Trade.created_at) == today
            ).count()
            
            if today_trades >= max_trades:
                return True, f"当日交易次数 {today_trades} 超过最大限制 {max_trades}"
        
        return False, None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule_type': self.rule_type,
            'parameters': self.get_parameters(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<RiskRule {self.name}>'

class RiskAlert(db.Model):
    """风险警报模型"""
    __tablename__ = 'risk_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    risk_rule_id = db.Column(db.Integer, db.ForeignKey('risk_rules.id'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # warning, error, critical
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def resolve(self):
        """解决警报"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'risk_rule_id': self.risk_rule_id,
            'portfolio_id': self.portfolio_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<RiskAlert {self.alert_type}: {self.message}>'
