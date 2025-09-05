from . import db
from datetime import datetime
from decimal import Decimal

class Trade(db.Model):
    """交易记录模型"""
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    strategy_execution_id = db.Column(db.Integer, db.ForeignKey('strategy_executions.id'))
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Numeric(15, 8), nullable=False)
    price = db.Column(db.Numeric(15, 8), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # quantity * price
    fee = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    pnl = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='completed')  # pending, completed, cancelled
    executed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_net_amount(self):
        """获取净金额（扣除手续费）"""
        return float(self.amount) - float(self.fee)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'strategy_execution_id': self.strategy_execution_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'amount': float(self.amount),
            'fee': float(self.fee),
            'net_amount': self.get_net_amount(),
            'pnl': float(self.pnl),
            'status': self.status,
            'executed_at': self.executed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Trade {self.symbol} {self.side} {self.quantity}@{self.price}>'

class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    strategy_execution_id = db.Column(db.Integer, db.ForeignKey('strategy_executions.id'))
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    order_type = db.Column(db.String(20), nullable=False)  # 'market', 'limit', 'stop'
    quantity = db.Column(db.Numeric(15, 8), nullable=False)
    price = db.Column(db.Numeric(15, 8))  # 限价单价格
    stop_price = db.Column(db.Numeric(15, 8))  # 止损价格
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, filled, cancelled, rejected
    filled_quantity = db.Column(db.Numeric(15, 8), nullable=False, default=0)
    average_fill_price = db.Column(db.Numeric(15, 8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_remaining_quantity(self):
        """获取剩余数量"""
        return float(self.quantity) - float(self.filled_quantity)
    
    def is_fully_filled(self):
        """是否完全成交"""
        return self.filled_quantity >= self.quantity
    
    def fill_order(self, quantity, price):
        """部分或完全成交订单"""
        fill_quantity = min(quantity, self.get_remaining_quantity())
        self.filled_quantity += fill_quantity
        
        if self.average_fill_price is None:
            self.average_fill_price = price
        else:
            # 计算新的平均成交价
            total_cost = float(self.average_fill_price) * (float(self.filled_quantity) - float(fill_quantity)) + float(price) * float(fill_quantity)
            self.average_fill_price = total_cost / float(self.filled_quantity)
        
        if self.is_fully_filled():
            self.status = 'filled'
        
        return fill_quantity
    
    def cancel_order(self):
        """取消订单"""
        self.status = 'cancelled'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'strategy_execution_id': self.strategy_execution_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type,
            'quantity': float(self.quantity),
            'price': float(self.price) if self.price else None,
            'stop_price': float(self.stop_price) if self.stop_price else None,
            'status': self.status,
            'filled_quantity': float(self.filled_quantity),
            'remaining_quantity': self.get_remaining_quantity(),
            'average_fill_price': float(self.average_fill_price) if self.average_fill_price else None,
            'is_fully_filled': self.is_fully_filled(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Order {self.symbol} {self.side} {self.quantity}@{self.price}>'
