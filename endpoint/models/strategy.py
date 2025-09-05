from . import db
from datetime import datetime
from decimal import Decimal
import json

class Strategy(db.Model):
    """交易策略模型"""
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategy_type = db.Column(db.String(50), nullable=False)  # 策略类型：momentum, mean_reversion, arbitrage等
    parameters = db.Column(db.Text)  # JSON格式的策略参数
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    executions = db.relationship('StrategyExecution', backref='strategy', lazy='dynamic')
    
    def get_parameters(self):
        """获取策略参数"""
        if self.parameters:
            return json.loads(self.parameters)
        return {}
    
    def set_parameters(self, params):
        """设置策略参数"""
        self.parameters = json.dumps(params)
    
    def get_performance_metrics(self):
        """获取策略表现指标"""
        executions = self.executions.filter_by(is_active=True).all()
        if not executions:
            return {}
        
        total_trades = sum(len(exec.trades) for exec in executions)
        winning_trades = sum(len([t for t in exec.trades if t.pnl > 0]) for exec in executions)
        total_pnl = sum(sum(t.pnl for t in exec.trades) for exec in executions)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_pnl': float(total_pnl),
            'active_executions': len(executions)
        }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type,
            'parameters': self.get_parameters(),
            'is_active': self.is_active,
            'performance': self.get_performance_metrics(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Strategy {self.name}>'

class StrategyExecution(db.Model):
    """策略执行模型"""
    __tablename__ = 'strategy_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    initial_capital = db.Column(db.Numeric(15, 2), nullable=False)
    current_value = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    trades = db.relationship('Trade', backref='strategy_execution', lazy='dynamic')
    
    def get_total_pnl(self):
        """获取总盈亏"""
        return float(self.current_value) - float(self.initial_capital)
    
    def get_total_pnl_percentage(self):
        """获取总盈亏百分比"""
        if self.initial_capital == 0:
            return 0
        return (self.get_total_pnl() / float(self.initial_capital)) * 100
    
    def stop_execution(self):
        """停止策略执行"""
        self.is_active = False
        self.end_time = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'portfolio_id': self.portfolio_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'initial_capital': float(self.initial_capital),
            'current_value': float(self.current_value),
            'total_pnl': self.get_total_pnl(),
            'total_pnl_percentage': self.get_total_pnl_percentage(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<StrategyExecution {self.strategy.name}>'
