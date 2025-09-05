from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, parameters=None):
        default_params = {
            'lookback_period': 20,  # 回望期
            'rsi_period': 14,  # RSI周期
            'rsi_oversold': 30,  # RSI超卖线
            'rsi_overbought': 70,  # RSI超买线
            'volume_threshold': 1.5,  # 成交量阈值倍数
            'position_size_percentage': 0.1,  # 每次交易占投资组合的百分比
            'stop_loss_percentage': 0.02,  # 止损百分比
            'take_profit_percentage': 0.04  # 止盈百分比
        }
        
        if parameters:
            default_params.update(parameters)
        
        super().__init__('MomentumStrategy', default_params)
    
    def generate_signal(self, market_data):
        """生成动量交易信号"""
        try:
            if len(market_data) < self.parameters['lookback_period']:
                return {'action': 'hold', 'symbol': None}
            
            # 转换为DataFrame
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # 计算技术指标
            df['sma'] = df['close_price'].rolling(window=self.parameters['lookback_period']).mean()
            df['rsi'] = self._calculate_rsi(df['close_price'], self.parameters['rsi_period'])
            df['volume_sma'] = df['volume'].rolling(window=self.parameters['lookback_period']).mean()
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 动量信号逻辑
            signal = self._analyze_momentum(latest, prev, df)
            
            if signal['action'] != 'hold':
                signal['symbol'] = market_data[-1].get('symbol', 'UNKNOWN')
                self.log_signal(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"生成动量信号失败: {e}")
            return {'action': 'hold', 'symbol': None}
    
    def _analyze_momentum(self, latest, prev, df):
        """分析动量信号"""
        # 价格动量
        price_momentum = (latest['close_price'] - latest['sma']) / latest['sma']
        
        # 成交量确认
        volume_confirmation = latest['volume'] > (latest['volume_sma'] * self.parameters['volume_threshold'])
        
        # RSI条件
        rsi_oversold = latest['rsi'] < self.parameters['rsi_oversold']
        rsi_overbought = latest['rsi'] > self.parameters['rsi_overbought']
        rsi_bullish = latest['rsi'] > prev['rsi']  # RSI上升
        
        # 趋势确认
        trend_bullish = latest['close_price'] > latest['sma']
        trend_bearish = latest['close_price'] < latest['sma']
        
        # 买入信号
        if (price_momentum > 0.02 and  # 价格动量向上
            volume_confirmation and  # 成交量确认
            (rsi_oversold or (latest['rsi'] < 50 and rsi_bullish)) and  # RSI条件
            trend_bullish):  # 趋势向上
            
            return {
                'action': 'buy',
                'quantity': 0,  # 将在calculate_position_size中计算
                'price': latest['close_price'],
                'reason': 'Momentum buy signal'
            }
        
        # 卖出信号
        elif (price_momentum < -0.02 and  # 价格动量向下
              volume_confirmation and  # 成交量确认
              (rsi_overbought or (latest['rsi'] > 50 and not rsi_bullish)) and  # RSI条件
              trend_bearish):  # 趋势向下
            
            return {
                'action': 'sell',
                'quantity': 0,  # 将在calculate_position_size中计算
                'price': latest['close_price'],
                'reason': 'Momentum sell signal'
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
        
        return False
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
