from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self, parameters=None):
        default_params = {
            'lookback_period': 20,  # 回望期
            'bollinger_period': 20,  # 布林带周期
            'bollinger_std': 2,  # 布林带标准差
            'rsi_period': 14,  # RSI周期
            'rsi_oversold': 30,  # RSI超卖线
            'rsi_overbought': 70,  # RSI超买线
            'position_size_percentage': 0.1,  # 每次交易占投资组合的百分比
            'stop_loss_percentage': 0.02,  # 止损百分比
            'take_profit_percentage': 0.04  # 止盈百分比
        }
        
        if parameters:
            default_params.update(parameters)
        
        super().__init__('MeanReversionStrategy', default_params)
    
    def generate_signal(self, market_data):
        """生成均值回归交易信号"""
        try:
            if len(market_data) < self.parameters['lookback_period']:
                return {'action': 'hold', 'symbol': None}
            
            # 转换为DataFrame
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # 计算技术指标
            df['sma'] = df['close_price'].rolling(window=self.parameters['lookback_period']).mean()
            df['std'] = df['close_price'].rolling(window=self.parameters['bollinger_period']).std()
            df['bb_upper'] = df['sma'] + (df['std'] * self.parameters['bollinger_std'])
            df['bb_lower'] = df['sma'] - (df['std'] * self.parameters['bollinger_std'])
            df['rsi'] = self._calculate_rsi(df['close_price'], self.parameters['rsi_period'])
            
            # 获取最新数据
            latest = df.iloc[-1]
            
            # 均值回归信号逻辑
            signal = self._analyze_mean_reversion(latest, df)
            
            if signal['action'] != 'hold':
                signal['symbol'] = market_data[-1].get('symbol', 'UNKNOWN')
                self.log_signal(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"生成均值回归信号失败: {e}")
            return {'action': 'hold', 'symbol': None}
    
    def _analyze_mean_reversion(self, latest, df):
        """分析均值回归信号"""
        current_price = latest['close_price']
        sma = latest['sma']
        bb_upper = latest['bb_upper']
        bb_lower = latest['bb_lower']
        rsi = latest['rsi']
        
        # 计算价格偏离程度
        price_deviation = (current_price - sma) / sma
        
        # 买入信号：价格低于下轨且RSI超卖
        if (current_price <= bb_lower and 
            rsi < self.parameters['rsi_oversold'] and
            price_deviation < -0.02):  # 价格偏离均值超过2%
            
            return {
                'action': 'buy',
                'quantity': 0,  # 将在calculate_position_size中计算
                'price': current_price,
                'reason': 'Mean reversion buy signal - price below lower Bollinger Band'
            }
        
        # 卖出信号：价格高于上轨且RSI超买
        elif (current_price >= bb_upper and 
              rsi > self.parameters['rsi_overbought'] and
              price_deviation > 0.02):  # 价格偏离均值超过2%
            
            return {
                'action': 'sell',
                'quantity': 0,  # 将在calculate_position_size中计算
                'price': current_price,
                'reason': 'Mean reversion sell signal - price above upper Bollinger Band'
            }
        
        return {'action': 'hold', 'symbol': None}
    
    def calculate_position_size(self, signal, portfolio_value, current_price):
        """计算持仓大小"""
        if signal['action'] == 'hold':
            return 0
        
        position_size_percentage = self.parameters['position_size_percentage']
        position_value = portfolio_value * position_size_percentage
        quantity = position_value / current_price
        
        return quantity
    
    def should_exit_position(self, position, market_data):
        """判断是否应该平仓"""
        if not market_data:
            return False
        
        latest = market_data[-1]
        current_price = latest['close_price']
        
        # 止损检查
        stop_loss_price = self.get_stop_loss_price(position['average_price'], position['side'])
        if position['side'] == 'buy' and current_price <= stop_loss_price:
            return True
        elif position['side'] == 'sell' and current_price >= stop_loss_price:
            return True
        
        # 止盈检查
        take_profit_price = self.get_take_profit_price(position['average_price'], position['side'])
        if position['side'] == 'buy' and current_price >= take_profit_price:
            return True
        elif position['side'] == 'sell' and current_price <= take_profit_price:
            return True
        
        # 均值回归平仓：价格回到均值附近
        if len(market_data) >= self.parameters['lookback_period']:
            df = pd.DataFrame(market_data[-self.parameters['lookback_period']:])
            sma = df['close_price'].mean()
            
            # 如果价格回到均值附近（1%以内），平仓
            if abs(current_price - sma) / sma < 0.01:
                return True
        
        return False
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
