import yfinance as yf
import pandas as pd
import ccxt
from models import db, MarketData, Symbol
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataService:
    """数据服务类"""
    
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'okx': ccxt.okx(),
        }
    
    def get_market_data(self, symbol, start_date=None, end_date=None, limit=1000):
        """获取市场数据"""
        try:
            # 首先尝试从数据库获取
            symbol_obj = Symbol.query.filter_by(symbol=symbol).first()
            if not symbol_obj:
                # 如果数据库中没有，尝试从Yahoo Finance获取
                return self._get_yahoo_data(symbol, start_date, end_date, limit)
            
            # 从数据库查询
            query = MarketData.query.filter_by(symbol_id=symbol_obj.id)
            
            if start_date:
                query = query.filter(MarketData.timestamp >= start_date)
            if end_date:
                query = query.filter(MarketData.timestamp <= end_date)
            
            data = query.order_by(MarketData.timestamp.desc()).limit(limit).all()
            
            if not data:
                # 如果数据库中没有数据，从外部API获取
                return self._fetch_and_store_data(symbol, start_date, end_date, limit)
            
            return [d.to_dict() for d in data]
            
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return []
    
    def get_latest_price(self, symbol):
        """获取最新价格"""
        try:
            # 尝试从数据库获取最新价格
            symbol_obj = Symbol.query.filter_by(symbol=symbol).first()
            if symbol_obj:
                latest_data = MarketData.query.filter_by(symbol_id=symbol_obj.id)\
                    .order_by(MarketData.timestamp.desc()).first()
                if latest_data:
                    return {
                        'symbol': symbol,
                        'price': float(latest_data.close_price),
                        'timestamp': latest_data.timestamp.isoformat()
                    }
            
            # 从外部API获取最新价格
            return self._get_latest_price_from_api(symbol)
            
        except Exception as e:
            logger.error(f"获取最新价格失败: {e}")
            return None
    
    def _get_yahoo_data(self, symbol, start_date, end_date, limit):
        """从Yahoo Finance获取数据"""
        try:
            ticker = yf.Ticker(symbol)
            
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return []
            
            # 转换为字典格式
            result = []
            for timestamp, row in data.iterrows():
                result.append({
                    'symbol': symbol,
                    'timestamp': timestamp.isoformat(),
                    'open_price': float(row['Open']),
                    'high_price': float(row['High']),
                    'low_price': float(row['Low']),
                    'close_price': float(row['Close']),
                    'volume': float(row['Volume'])
                })
            
            return result[-limit:]  # 返回最新的limit条记录
            
        except Exception as e:
            logger.error(f"从Yahoo Finance获取数据失败: {e}")
            return []
    
    def _get_latest_price_from_api(self, symbol):
        """从API获取最新价格"""
        try:
            # 尝试从Binance获取
            if 'USDT' in symbol.upper():
                ticker = self.exchanges['binance'].fetch_ticker(symbol)
                return {
                    'symbol': symbol,
                    'price': ticker['last'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # 尝试从Yahoo Finance获取
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                latest = data.iloc[-1]
                return {
                    'symbol': symbol,
                    'price': float(latest['Close']),
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"从API获取最新价格失败: {e}")
            return None
    
    def _fetch_and_store_data(self, symbol, start_date, end_date, limit):
        """获取并存储数据"""
        try:
            # 从Yahoo Finance获取数据
            data = self._get_yahoo_data(symbol, start_date, end_date, limit)
            
            if not data:
                return []
            
            # 确保symbol在数据库中存在
            symbol_obj = Symbol.query.filter_by(symbol=symbol).first()
            if not symbol_obj:
                symbol_obj = Symbol(
                    symbol=symbol,
                    name=symbol,
                    exchange='Yahoo Finance',
                    asset_type='stock',
                    base_asset=symbol.split('.')[0] if '.' in symbol else symbol,
                    quote_asset='USD'
                )
                db.session.add(symbol_obj)
                db.session.commit()
            
            # 存储数据到数据库
            for item in data:
                market_data = MarketData(
                    symbol_id=symbol_obj.id,
                    timestamp=datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')),
                    open_price=item['open_price'],
                    high_price=item['high_price'],
                    low_price=item['low_price'],
                    close_price=item['close_price'],
                    volume=item['volume']
                )
                db.session.add(market_data)
            
            db.session.commit()
            
            return data
            
        except Exception as e:
            logger.error(f"获取并存储数据失败: {e}")
            return []
    
    def update_market_data(self, symbol):
        """更新市场数据"""
        try:
            # 获取最新价格
            latest_price = self.get_latest_price(symbol)
            if not latest_price:
                return False
            
            # 更新持仓的当前价格
            from models import Position
            positions = Position.query.join(Position.portfolio).filter_by(symbol=symbol).all()
            
            for position in positions:
                position.update_price(latest_price['price'])
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"更新市场数据失败: {e}")
            return False
    
    def get_technical_indicators(self, symbol, period=20):
        """获取技术指标"""
        try:
            data = self.get_market_data(symbol, limit=period * 2)
            if len(data) < period:
                return None
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # 计算移动平均线
            df['sma_20'] = df['close_price'].rolling(window=period).mean()
            df['sma_50'] = df['close_price'].rolling(window=50).mean()
            
            # 计算RSI
            df['rsi'] = self._calculate_rsi(df['close_price'], period)
            
            # 计算MACD
            macd_data = self._calculate_macd(df['close_price'])
            df['macd'] = macd_data['macd']
            df['macd_signal'] = macd_data['signal']
            df['macd_histogram'] = macd_data['histogram']
            
            # 计算布林带
            bb_data = self._calculate_bollinger_bands(df['close_price'], period)
            df['bb_upper'] = bb_data['upper']
            df['bb_middle'] = bb_data['middle']
            df['bb_lower'] = bb_data['lower']
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return None
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        
        return {
            'macd': macd,
            'signal': macd_signal,
            'histogram': macd_histogram
        }
    
    def _calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """计算布林带"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
