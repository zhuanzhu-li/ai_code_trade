from . import db
from datetime import datetime
from decimal import Decimal

class Portfolio(db.Model):
    """投资组合模型"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    initial_capital = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    current_value = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    cash_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    positions = db.relationship('Position', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='portfolio', lazy='dynamic')
    
    def get_total_value(self):
        """获取总价值"""
        positions_value = sum(pos.get_value() for pos in self.positions)
        return float(self.cash_balance) + positions_value
    
    def get_total_pnl(self):
        """获取总盈亏"""
        return self.get_total_value() - float(self.initial_capital)
    
    def get_total_pnl_percentage(self):
        """获取总盈亏百分比"""
        if self.initial_capital == 0:
            return 0
        return (self.get_total_pnl() / float(self.initial_capital)) * 100
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'initial_capital': float(self.initial_capital),
            'current_value': self.get_total_value(),
            'cash_balance': float(self.cash_balance),
            'total_pnl': self.get_total_pnl(),
            'total_pnl_percentage': self.get_total_pnl_percentage(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Portfolio {self.name}>'

class Position(db.Model):
    """持仓模型"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(15, 8), nullable=False, default=0)
    average_price = db.Column(db.Numeric(15, 8), nullable=False, default=0)
    current_price = db.Column(db.Numeric(15, 8), nullable=False, default=0)
    unrealized_pnl = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    realized_pnl = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_value(self):
        """获取持仓价值"""
        return float(self.quantity) * float(self.current_price)
    
    def get_unrealized_pnl(self):
        """获取未实现盈亏"""
        cost_basis = float(self.quantity) * float(self.average_price)
        current_value = self.get_value()
        return current_value - cost_basis
    
    def update_price(self, new_price):
        """更新价格"""
        self.current_price = new_price
        self.unrealized_pnl = self.get_unrealized_pnl()
    
    def add_quantity(self, quantity, price):
        """增加持仓数量"""
        if self.quantity == 0:
            self.average_price = price
            self.quantity = quantity
        else:
            # 计算新的平均价格
            total_cost = float(self.quantity) * float(self.average_price) + float(quantity) * float(price)
            total_quantity = float(self.quantity) + float(quantity)
            self.average_price = total_cost / total_quantity
            self.quantity = total_quantity
    
    def reduce_quantity(self, quantity):
        """减少持仓数量"""
        if quantity >= self.quantity:
            self.quantity = 0
            self.average_price = 0
        else:
            self.quantity -= quantity
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'quantity': float(self.quantity),
            'average_price': float(self.average_price),
            'current_price': float(self.current_price),
            'value': self.get_value(),
            'unrealized_pnl': self.get_unrealized_pnl(),
            'realized_pnl': float(self.realized_pnl),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Position {self.symbol}: {self.quantity}>'
