from abc import ABC, abstractmethod
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name, parameters=None):
        self.name = name
        self.parameters = parameters or {}
        self.is_active = False
        self.positions = {}
        self.last_signal = None
        
    @abstractmethod
    def generate_signal(self, market_data):
        """生成交易信号
        
        Args:
            market_data: 市场数据
            
        Returns:
            dict: 交易信号 {'action': 'buy'/'sell'/'hold', 'symbol': str, 'quantity': float, 'price': float}
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal, portfolio_value, current_price):
        """计算持仓大小
        
        Args:
            signal: 交易信号
            portfolio_value: 投资组合价值
            current_price: 当前价格
            
        Returns:
            float: 建议的持仓数量
        """
        pass
    
    def should_exit_position(self, position, market_data):
        """判断是否应该平仓
        
        Args:
            position: 当前持仓
            market_data: 市场数据
            
        Returns:
            bool: 是否应该平仓
        """
        return False
    
    def get_stop_loss_price(self, entry_price, side):
        """获取止损价格
        
        Args:
            entry_price: 入场价格
            side: 交易方向 ('buy' or 'sell')
            
        Returns:
            float: 止损价格
        """
        stop_loss_percentage = self.parameters.get('stop_loss_percentage', 0.02)  # 默认2%
        
        if side == 'buy':
            return entry_price * (1 - stop_loss_percentage)
        else:
            return entry_price * (1 + stop_loss_percentage)
    
    def get_take_profit_price(self, entry_price, side):
        """获取止盈价格
        
        Args:
            entry_price: 入场价格
            side: 交易方向 ('buy' or 'sell')
            
        Returns:
            float: 止盈价格
        """
        take_profit_percentage = self.parameters.get('take_profit_percentage', 0.04)  # 默认4%
        
        if side == 'buy':
            return entry_price * (1 + take_profit_percentage)
        else:
            return entry_price * (1 - take_profit_percentage)
    
    def validate_signal(self, signal):
        """验证交易信号
        
        Args:
            signal: 交易信号
            
        Returns:
            bool: 信号是否有效
        """
        required_fields = ['action', 'symbol']
        
        if not all(field in signal for field in required_fields):
            logger.warning(f"交易信号缺少必要字段: {signal}")
            return False
        
        if signal['action'] not in ['buy', 'sell', 'hold']:
            logger.warning(f"无效的交易动作: {signal['action']}")
            return False
        
        if signal['action'] in ['buy', 'sell']:
            if 'quantity' not in signal or signal['quantity'] <= 0:
                logger.warning(f"无效的持仓数量: {signal.get('quantity', 'None')}")
                return False
        
        return True
    
    def log_signal(self, signal):
        """记录交易信号"""
        logger.info(f"策略 {self.name} 生成信号: {signal}")
        self.last_signal = signal
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'last_signal': self.last_signal
        }
