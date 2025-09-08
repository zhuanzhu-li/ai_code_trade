"""
数据源抽象基类
定义了获取股票数据的统一接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BaseDataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化数据源
        
        Args:
            name: 数据源名称
            config: 配置参数
        """
        self.name = name
        self.config = config or {}
        self.is_connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """
        连接数据源
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def get_stock_list(self, market: str = 'A股') -> List[Dict]:
        """
        获取股票列表
        
        Args:
            market: 市场类型
            
        Returns:
            List[Dict]: 股票列表，包含股票代码、名称等信息
        """
        pass
    
    @abstractmethod
    def get_index_components(self, index_code: str) -> List[Dict]:
        """
        获取指数成分股
        
        Args:
            index_code: 指数代码
            
        Returns:
            List[Dict]: 成分股列表
        """
        pass
    
    @abstractmethod
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: date, 
        end_date: date,
        period: str = '1d'
    ) -> pd.DataFrame:
        """
        获取历史行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 数据周期 (1d, 1h, 5m等)
            
        Returns:
            pd.DataFrame: 历史数据
        """
        pass
    
    @abstractmethod
    def get_latest_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取最新行情数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            Dict[str, Dict]: 最新数据字典
        """
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        验证股票代码格式
        
        Args:
            symbol: 股票代码
            
        Returns:
            bool: 是否有效
        """
        return bool(symbol and isinstance(symbol, str) and len(symbol) >= 6)
    
    def standardize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式
        
        Args:
            symbol: 原始股票代码
            
        Returns:
            str: 标准化后的股票代码
        """
        return symbol.upper().strip()
    
    def format_market_data(self, raw_data: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        格式化市场数据为统一格式
        
        Args:
            raw_data: 原始数据
            symbol: 股票代码
            
        Returns:
            List[Dict]: 格式化后的数据
        """
        if raw_data.empty:
            return []
        
        formatted_data = []
        
        for index, row in raw_data.iterrows():
            try:
                data_point = {
                    'symbol': symbol,
                    'timestamp': pd.to_datetime(index) if isinstance(index, str) else index,
                    'open_price': float(row.get('open', row.get('开盘', 0))),
                    'high_price': float(row.get('high', row.get('最高', 0))),
                    'low_price': float(row.get('low', row.get('最低', 0))),
                    'close_price': float(row.get('close', row.get('收盘', 0))),
                    'volume': float(row.get('volume', row.get('成交量', 0))),
                    'interval_type': '1d'
                }
                
                # 确保价格数据有效
                if all(data_point[key] >= 0 for key in ['open_price', 'high_price', 'low_price', 'close_price']):
                    formatted_data.append(data_point)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"格式化数据时出错: {e}, 跳过该行数据")
                continue
        
        return formatted_data
    
    def get_data_range(self, symbol: str) -> Tuple[Optional[date], Optional[date]]:
        """
        获取数据源中某股票的数据范围
        
        Args:
            symbol: 股票代码
            
        Returns:
            Tuple[Optional[date], Optional[date]]: (开始日期, 结束日期)
        """
        # 默认实现，子类可以重写
        return None, None
    
    def health_check(self) -> Dict[str, any]:
        """
        健康检查
        
        Returns:
            Dict: 健康状态信息
        """
        return {
            'name': self.name,
            'is_connected': self.is_connected,
            'config': {k: '***' if 'key' in k.lower() or 'secret' in k.lower() else v 
                      for k, v in self.config.items()},
            'last_check': datetime.now().isoformat()
        }
    
    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self):
        return self.__str__()
