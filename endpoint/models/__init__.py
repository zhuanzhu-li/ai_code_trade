from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 导入所有模型
from .user import User
from .portfolio import Portfolio, Position
from .strategy import Strategy, StrategyExecution
from .trade import Trade, Order
from .market_data import MarketData, Symbol
from .risk_management import RiskRule, RiskAlert
from .data_source import DataSource

__all__ = [
    'db', 'User', 'Portfolio', 'Position', 'Strategy', 'StrategyExecution',
    'Trade', 'Order', 'MarketData', 'Symbol', 'RiskRule', 'RiskAlert', 'DataSource'
]
