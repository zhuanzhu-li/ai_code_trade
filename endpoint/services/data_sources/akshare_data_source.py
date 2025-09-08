"""
AKShare数据源实现
基于akshare库获取A股市场数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_data_source import BaseDataSource

logger = logging.getLogger(__name__)

class AKShareDataSource(BaseDataSource):
    """AKShare数据源实现"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化AKShare数据源
        
        Args:
            config: 配置参数，可包含:
                - timeout: 请求超时时间
                - retry_times: 重试次数
                - delay: 请求间隔
                - base_url: 基础URL（如果需要）
        """
        super().__init__("AKShare", config)
        
        # 默认配置
        self.timeout = self.config.get('timeout', 30)
        self.retry_times = self.config.get('retry_times', 3)
        self.delay = self.config.get('delay', 1)  # 请求间隔，避免频率限制
        
        # 设置requests会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.retry_times,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 常用指数代码映射
        self.index_mapping = {
            '上证500': '000905',
            'SH000905': '000905',
            '000905': '000905',
            '沪深300': '000300',
            'SH000300': '000300', 
            '000300': '000300',
            '中证1000': '000852',
            'SH000852': '000852',
            '000852': '000852'
        }
    
    def connect(self) -> bool:
        """连接数据源（测试akshare可用性）"""
        try:
            # 测试获取一个简单的数据
            test_data = ak.stock_zh_a_spot_em()
            if test_data is not None and not test_data.empty:
                self.is_connected = True
                logger.info("AKShare数据源连接成功")
                return True
            else:
                logger.error("AKShare数据源测试失败")
                return False
        except Exception as e:
            logger.error(f"AKShare数据源连接失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.session:
            self.session.close()
        self.is_connected = False
        logger.info("AKShare数据源已断开连接")
    
    def get_stock_list(self, market: str = 'A股') -> List[Dict]:
        """
        获取A股股票列表
        
        Args:
            market: 市场类型，目前支持'A股'
            
        Returns:
            List[Dict]: 股票列表
        """
        try:
            logger.info(f"获取{market}股票列表...")
            
            # 获取A股实时数据（包含所有股票信息）
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                logger.warning("获取股票列表为空")
                return []
            
            stock_list = []
            for _, row in df.iterrows():
                try:
                    stock_info = {
                        'symbol': str(row['代码']),
                        'name': str(row['名称']),
                        'exchange': 'SH' if str(row['代码']).startswith('6') else 'SZ',
                        'asset_type': 'stock',
                        'is_active': True,
                        'latest_price': float(row.get('最新价', 0)),
                        'change_pct': float(row.get('涨跌幅', 0)),
                        'volume': float(row.get('成交量', 0)),
                        'market_cap': float(row.get('总市值', 0)) if '总市值' in row else None
                    }
                    stock_list.append(stock_info)
                except (ValueError, KeyError) as e:
                    logger.warning(f"处理股票数据时出错: {e}, 跳过股票: {row.get('代码', 'Unknown')}")
                    continue
            
            logger.info(f"成功获取{len(stock_list)}只股票信息")
            return stock_list
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def get_index_components(self, index_code: str) -> List[Dict]:
        """
        获取指数成分股
        
        Args:
            index_code: 指数代码或名称
            
        Returns:
            List[Dict]: 成分股列表
        """
        try:
            # 标准化指数代码
            standard_code = self.index_mapping.get(index_code, index_code)
            logger.info(f"获取指数{index_code}({standard_code})的成分股...")
            
            # 获取指数成分股
            if standard_code == '000905':  # 上证500
                df = ak.index_stock_cons(symbol=standard_code)
            elif standard_code == '000300':  # 沪深300
                df = ak.index_stock_cons(symbol=standard_code)
            elif standard_code == '000852':  # 中证1000
                df = ak.index_stock_cons(symbol=standard_code)
            else:
                # 尝试通用方法
                df = ak.index_stock_cons(symbol=standard_code)
            
            if df.empty:
                logger.warning(f"指数{index_code}成分股为空")
                return []
            
            components = []
            for _, row in df.iterrows():
                try:
                    component = {
                        'symbol': str(row.get('品种代码', row.get('代码', ''))),
                        'name': str(row.get('品种名称', row.get('名称', ''))),
                        'exchange': 'SH' if str(row.get('品种代码', row.get('代码', ''))).startswith('6') else 'SZ',
                        'weight': float(row.get('权重', 0)) if '权重' in row else None,
                        'index_code': standard_code,
                        'index_name': index_code
                    }
                    components.append(component)
                except (ValueError, KeyError) as e:
                    logger.warning(f"处理成分股数据时出错: {e}")
                    continue
            
            logger.info(f"成功获取{len(components)}只成分股")
            return components
            
        except Exception as e:
            logger.error(f"获取指数{index_code}成分股失败: {e}")
            return []
    
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
            period: 数据周期，目前支持'1d'
            
        Returns:
            pd.DataFrame: 历史数据
        """
        try:
            logger.info(f"获取{symbol}从{start_date}到{end_date}的历史数据...")
            
            # 添加请求延迟，避免频率限制
            if hasattr(self, '_last_request_time'):
                elapsed = time.time() - self._last_request_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
            
            # 格式化日期
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            # 获取股票历史数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period='daily',
                start_date=start_str,
                end_date=end_str,
                adjust='qfq'  # 前复权
            )
            
            self._last_request_time = time.time()
            
            if df.empty:
                logger.warning(f"股票{symbol}的历史数据为空")
                return pd.DataFrame()
            
            # 标准化列名
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close', 
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            }
            
            df = df.rename(columns=column_mapping)
            
            # 设置日期索引
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            # 确保数值类型
            numeric_columns = ['open', 'close', 'high', 'low', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"成功获取{symbol}的{len(df)}条历史数据")
            return df
            
        except Exception as e:
            logger.error(f"获取{symbol}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_latest_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取最新行情数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            Dict[str, Dict]: 最新数据字典
        """
        try:
            logger.info(f"获取{len(symbols)}只股票的最新行情数据...")
            
            # 获取实时行情数据
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                logger.warning("获取实时行情数据为空")
                return {}
            
            # 筛选指定股票
            df_filtered = df[df['代码'].isin(symbols)]
            
            latest_data = {}
            for _, row in df_filtered.iterrows():
                try:
                    symbol = str(row['代码'])
                    latest_data[symbol] = {
                        'symbol': symbol,
                        'name': str(row['名称']),
                        'latest_price': float(row['最新价']),
                        'open_price': float(row['今开']),
                        'high_price': float(row['最高']),
                        'low_price': float(row['最低']),
                        'close_price': float(row['昨收']),  # 昨收作为前一交易日收盘价
                        'volume': float(row['成交量']),
                        'amount': float(row['成交额']),
                        'change_amount': float(row['涨跌额']),
                        'change_pct': float(row['涨跌幅']),
                        'timestamp': datetime.now(),
                        'market_cap': float(row.get('总市值', 0)) if '总市值' in row else None
                    }
                except (ValueError, KeyError) as e:
                    logger.warning(f"处理股票{row.get('代码', 'Unknown')}最新数据时出错: {e}")
                    continue
            
            logger.info(f"成功获取{len(latest_data)}只股票的最新数据")
            return latest_data
            
        except Exception as e:
            logger.error(f"获取最新行情数据失败: {e}")
            return {}
    
    def get_trading_dates(self, start_date: date, end_date: date) -> List[date]:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[date]: 交易日期列表
        """
        try:
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            df = ak.stock_zh_a_trade_date()
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            # 筛选日期范围
            mask = (df['trade_date'] >= pd.to_datetime(start_date)) & \
                   (df['trade_date'] <= pd.to_datetime(end_date))
            
            trading_dates = df.loc[mask, 'trade_date'].dt.date.tolist()
            return trading_dates
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return []
    
    def is_trading_day(self, check_date: date) -> bool:
        """
        检查是否为交易日
        
        Args:
            check_date: 要检查的日期
            
        Returns:
            bool: 是否为交易日
        """
        try:
            trading_dates = self.get_trading_dates(check_date, check_date)
            return check_date in trading_dates
        except Exception:
            # 简单判断：周一到周五且不是节假日（简化版）
            return check_date.weekday() < 5
    
    def standardize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式
        
        Args:
            symbol: 原始股票代码
            
        Returns:
            str: 标准化后的股票代码（6位数字）
        """
        symbol = super().standardize_symbol(symbol)
        
        # 移除交易所前缀
        if '.' in symbol:
            symbol = symbol.split('.')[0]
        
        # 确保是6位数字
        if symbol.isdigit() and len(symbol) == 6:
            return symbol
        
        return symbol
    
    def health_check(self) -> Dict[str, any]:
        """健康检查"""
        base_health = super().health_check()
        
        try:
            # 测试获取少量数据
            test_start = datetime.now()
            df = ak.stock_zh_a_spot_em()
            test_end = datetime.now()
            
            akshare_health = {
                'api_accessible': not df.empty,
                'response_time_ms': int((test_end - test_start).total_seconds() * 1000),
                'sample_data_count': len(df) if not df.empty else 0
            }
        except Exception as e:
            akshare_health = {
                'api_accessible': False,
                'error': str(e)
            }
        
        base_health['akshare_specific'] = akshare_health
        return base_health
