from . import db
from datetime import datetime
from decimal import Decimal

class Symbol(db.Model):
    """交易标的模型"""
    __tablename__ = 'symbols'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(50))  # 交易所
    asset_type = db.Column(db.String(20), nullable=False, default='stock')  # stock, crypto, forex
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系（通过symbol字段关联，不使用外键）
    # market_data可以通过symbol字段查询
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'exchange': self.exchange,
            'asset_type': self.asset_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Symbol {self.symbol}>'

class MarketData(db.Model):
    """市场数据模型"""
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)  # 直接存储股票代码
    timestamp = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Numeric(15, 8), nullable=False)
    high_price = db.Column(db.Numeric(15, 8), nullable=False)
    low_price = db.Column(db.Numeric(15, 8), nullable=False)
    close_price = db.Column(db.Numeric(15, 8), nullable=False)
    volume = db.Column(db.Numeric(20, 8), nullable=False, default=0)
    interval_type = db.Column(db.String(10), nullable=False, default='1d')  # 时间间隔
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        db.Index('idx_symbol_timestamp_interval', 'symbol', 'timestamp', 'interval_type'),
        db.Index('idx_symbol', 'symbol'),
        db.Index('idx_timestamp', 'timestamp'),
        db.Index('idx_interval_type', 'interval_type'),
    )
    
    def get_price_change(self):
        """获取价格变化"""
        return float(self.close_price) - float(self.open_price)
    
    def get_price_change_percentage(self):
        """获取价格变化百分比"""
        if self.open_price == 0:
            return 0
        return (self.get_price_change() / float(self.open_price)) * 100
    
    def get_high_low_spread(self):
        """获取高低价差"""
        return float(self.high_price) - float(self.low_price)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open_price': float(self.open_price),
            'high_price': float(self.high_price),
            'low_price': float(self.low_price),
            'close_price': float(self.close_price),
            'volume': float(self.volume),
            'interval_type': self.interval_type,
            'price_change': self.get_price_change(),
            'price_change_percentage': self.get_price_change_percentage(),
            'high_low_spread': self.get_high_low_spread(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MarketData {self.symbol} {self.timestamp}>'
