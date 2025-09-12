"""
市场数据服务
负责管理股票数据的获取、存储和更新
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
from sqlalchemy import and_, desc, func

from models import db, MarketData, Symbol, DataSource
from services.data_sources import create_data_source, AKShareDataSource

logger = logging.getLogger(__name__)

class MarketDataService:
    """市场数据服务类"""
    
    def __init__(self, data_source_name: str = 'akshare', config: Optional[Dict] = None):
        """
        初始化市场数据服务
        
        Args:
            data_source_name: 数据源名称
            config: 数据源配置
        """
        self.data_source_name = data_source_name
        self.data_source = create_data_source(data_source_name, config)
        self.default_start_date = date(2024, 1, 1)
        
        # 获取或创建数据来源记录
        self.data_source_record = self._get_or_create_data_source_record()
    
    def _get_or_create_data_source_record(self) -> Optional[DataSource]:
        """获取或创建数据来源记录"""
        try:
            # 首先尝试根据provider_type查找
            data_source = DataSource.query.filter_by(provider_type=self.data_source_name).first()
            
            if not data_source:
                # 使用数据源的create_data_source_record方法创建记录
                data_source_info = self.data_source.create_data_source_record()
                if data_source_info:
                    # 重新查询获取完整的数据来源对象
                    data_source = DataSource.query.filter_by(provider_type=self.data_source_name).first()
                    logger.info(f"使用数据源方法创建数据来源记录: {data_source.name if data_source else 'Unknown'}")
                else:
                    logger.warning(f"数据源 {self.data_source_name} 创建记录失败，使用默认方法")
                    # 如果数据源方法失败，使用默认方法
                    data_source = DataSource(
                        name=f"{self.data_source_name.title()}数据源",
                        uri=f"https://{self.data_source_name}.example.com",
                        description=f"基于{self.data_source_name}的数据源",
                        provider_type=self.data_source_name,
                        is_active=True,
                        priority=1
                    )
                    db.session.add(data_source)
                    db.session.commit()
                    logger.info(f"使用默认方法创建数据来源记录: {data_source.name}")
            
            return data_source
            
        except Exception as e:
            logger.error(f"获取或创建数据来源记录失败: {e}")
            return None
    
    def initialize_data_source(self) -> bool:
        """初始化数据源连接"""
        try:
            return self.data_source.connect()
        except Exception as e:
            logger.error(f"初始化数据源失败: {e}")
            return False
    
    def sync_symbols(self, market: str = 'A股') -> int:
        """
        同步股票列表到数据库
        
        Args:
            market: 市场类型
            
        Returns:
            int: 同步的股票数量
        """
        try:
            logger.info(f"开始同步{market}股票列表...")
            
            # 获取股票列表
            stock_list = self.data_source.get_stock_list(market)
            
            if not stock_list:
                logger.warning("获取股票列表为空")
                return 0
            
            synced_count = 0
            
            for stock_info in stock_list:
                try:
                    symbol_code = stock_info['symbol']
                    
                    # 查找或创建股票记录
                    symbol = Symbol.query.filter_by(symbol=symbol_code).first()
                    
                    if symbol:
                        # 更新现有记录
                        symbol.name = stock_info['name']
                        symbol.exchange = stock_info['exchange']
                        symbol.is_active = stock_info.get('is_active', True)
                        symbol.data_source_id = self.data_source_record.id if self.data_source_record else None
                        symbol.updated_at = datetime.utcnow()
                    else:
                        # 创建新记录
                        symbol = Symbol(
                            symbol=symbol_code,
                            name=stock_info['name'],
                            exchange=stock_info['exchange'],
                            asset_type=stock_info.get('asset_type', 'stock'),
                            is_active=stock_info.get('is_active', True),
                            data_source_id=self.data_source_record.id if self.data_source_record else None
                        )
                        db.session.add(symbol)
                    
                    synced_count += 1
                    
                    # 批量提交，提高性能
                    if synced_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"已同步{synced_count}只股票...")
                        
                except Exception as e:
                    logger.error(f"同步股票{stock_info.get('symbol', 'Unknown')}失败: {e}")
                    continue
            
            # 最终提交
            db.session.commit()
            
            logger.info(f"股票列表同步完成，共同步{synced_count}只股票")
            return synced_count
            
        except Exception as e:
            logger.error(f"同步股票列表失败: {e}")
            db.session.rollback()
            return 0
    
    def sync_index_components(self, index_code: str) -> int:
        """
        同步指数成分股
        
        Args:
            index_code: 指数代码（如'上证500'）
            
        Returns:
            int: 同步的成分股数量
        """
        try:
            logger.info(f"开始同步{index_code}成分股...")
            
            # 获取成分股列表
            components = self.data_source.get_index_components(index_code)
            
            if not components:
                logger.warning(f"获取{index_code}成分股为空")
                return 0
            
            synced_count = 0
            
            for component in components:
                try:
                    symbol_code = component['symbol']
                    
                    # 查找或创建股票记录
                    symbol = Symbol.query.filter_by(symbol=symbol_code).first()
                    
                    if symbol:
                        # 更新现有记录
                        symbol.name = component['name']
                        symbol.exchange = component['exchange']
                        symbol.is_active = True
                        symbol.data_source_id = self.data_source_record.id if self.data_source_record else None
                        symbol.updated_at = datetime.utcnow()
                    else:
                        # 创建新记录
                        symbol = Symbol(
                            symbol=symbol_code,
                            name=component['name'],
                            exchange=component['exchange'],
                            asset_type='stock',
                            is_active=True,
                            data_source_id=self.data_source_record.id if self.data_source_record else None
                        )
                        db.session.add(symbol)
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"同步成分股{component.get('symbol', 'Unknown')}失败: {e}")
                    continue
            
            db.session.commit()
            
            logger.info(f"{index_code}成分股同步完成，共同步{synced_count}只股票")
            return synced_count
            
        except Exception as e:
            logger.error(f"同步{index_code}成分股失败: {e}")
            db.session.rollback()
            return 0
    
    def get_last_trading_date(self, symbol: str) -> Optional[date]:
        """
        获取某股票在数据库中的最后交易日期
        
        Args:
            symbol: 股票代码
            
        Returns:
            Optional[date]: 最后交易日期
        """
        try:
            last_record = MarketData.query.filter_by(symbol=symbol)\
                .order_by(desc(MarketData.timestamp)).first()
            
            if last_record:
                return last_record.timestamp.date()
            
            return None
            
        except Exception as e:
            logger.error(f"获取{symbol}最后交易日期失败: {e}")
            return None
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        force_update: bool = False
    ) -> int:
        """
        获取并存储历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期，如果为None则使用数据库中的最后日期
            end_date: 结束日期，如果为None则使用今天
            force_update: 是否强制更新（覆盖已有数据）
            
        Returns:
            int: 新增的数据条数
        """
        try:
            if not end_date:
                end_date = date.today()
            
            if not start_date:
                last_date = self.get_last_trading_date(symbol)
                if last_date:
                    # 从最后日期的下一天开始
                    start_date = last_date + timedelta(days=1)
                else:
                    # 如果没有历史数据，从默认开始日期开始
                    start_date = self.default_start_date
            
            # 如果开始日期大于等于结束日期，说明已经是最新数据
            if start_date >= end_date:
                logger.info(f"{symbol}数据已是最新，无需更新")
                return 0
            
            logger.info(f"获取{symbol}从{start_date}到{end_date}的历史数据...")
            
            # 从数据源获取历史数据
            df = self.data_source.get_historical_data(symbol, start_date, end_date)
            
            if df.empty:
                logger.warning(f"{symbol}历史数据为空")
                return 0
            
            # 格式化数据
            formatted_data = self.data_source.format_market_data(df, symbol)
            
            if not formatted_data:
                logger.warning(f"{symbol}格式化后数据为空")
                return 0
            
            # 存储到数据库
            stored_count = 0
            
            for data_point in formatted_data:
                try:
                    # 检查是否已存在（如果不是强制更新）
                    if not force_update:
                        existing = MarketData.query.filter(
                            and_(
                                MarketData.symbol == symbol,
                                MarketData.timestamp == data_point['timestamp'],
                                MarketData.interval_type == data_point['interval_type']
                            )
                        ).first()
                        
                        if existing:
                            continue
                    
                    # 创建新记录
                    market_data = MarketData(
                        symbol=data_point['symbol'],
                        data_source_id=self.data_source_record.id if self.data_source_record else None,
                        timestamp=data_point['timestamp'],
                        open_price=data_point['open_price'],
                        high_price=data_point['high_price'],
                        low_price=data_point['low_price'],
                        close_price=data_point['close_price'],
                        volume=data_point['volume'],
                        interval_type=data_point['interval_type']
                    )
                    
                    db.session.add(market_data)
                    stored_count += 1
                    
                    # 批量提交
                    if stored_count % 100 == 0:
                        db.session.commit()
                        
                except Exception as e:
                    logger.error(f"存储{symbol}数据点失败: {e}")
                    continue
            
            # 最终提交
            db.session.commit()
            
            logger.info(f"{symbol}历史数据获取完成，新增{stored_count}条记录")
            return stored_count
            
        except Exception as e:
            logger.error(f"获取{symbol}历史数据失败: {e}")
            db.session.rollback()
            return 0
    
    def batch_fetch_latest_data(self, symbols: List[str]) -> Dict[str, int]:
        """
        批量获取最新数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            Dict[str, int]: 每只股票新增的数据条数
        """
        try:
            logger.info(f"批量获取{len(symbols)}只股票的最新数据...")
            
            results = {}
            
            # 分批处理，避免一次性处理太多股票
            batch_size = 50
            for i in range(0, len(symbols), batch_size):
                batch_symbols = symbols[i:i + batch_size]
                
                for symbol in batch_symbols:
                    try:
                        count = self.fetch_historical_data(symbol)
                        results[symbol] = count
                        
                        # 添加小延迟，避免请求频率过高
                        import time
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"获取{symbol}数据失败: {e}")
                        results[symbol] = 0
                
                logger.info(f"已处理{min(i + batch_size, len(symbols))}/{len(symbols)}只股票")
            
            total_count = sum(results.values())
            logger.info(f"批量获取完成，共新增{total_count}条记录")
            
            return results
            
        except Exception as e:
            logger.error(f"批量获取最新数据失败: {e}")
            return {}
    
    def get_market_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        从数据库获取市场数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制条数
            
        Returns:
            List[Dict]: 市场数据列表
        """
        try:
            query = MarketData.query.filter_by(symbol=symbol)
            
            if start_date:
                query = query.filter(MarketData.timestamp >= start_date)
            
            if end_date:
                query = query.filter(MarketData.timestamp <= end_date)
            
            query = query.order_by(desc(MarketData.timestamp))
            
            if limit:
                query = query.limit(limit)
            
            records = query.all()
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"获取{symbol}市场数据失败: {e}")
            return []
    
    def get_data_statistics(self) -> Dict:
        """
        获取数据统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            stats = {
                'total_symbols': Symbol.query.filter_by(is_active=True).count(),
                'total_records': MarketData.query.count(),
                'data_date_range': {},
                'symbols_with_data': 0
            }
            
            # 获取数据日期范围
            date_range = db.session.query(
                func.min(MarketData.timestamp).label('min_date'),
                func.max(MarketData.timestamp).label('max_date')
            ).first()
            
            if date_range.min_date and date_range.max_date:
                stats['data_date_range'] = {
                    'start': date_range.min_date.isoformat(),
                    'end': date_range.max_date.isoformat()
                }
            
            # 获取有数据的股票数量
            stats['symbols_with_data'] = db.session.query(MarketData.symbol)\
                .distinct().count()
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据统计失败: {e}")
            return {}
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            health_info = {
                'service_name': 'MarketDataService',
                'data_source': self.data_source_name,
                'data_source_record': self.data_source_record.to_dict() if self.data_source_record else None,
                'data_source_health': self.data_source.health_check(),
                'database_stats': self.get_data_statistics(),
                'last_check': datetime.now().isoformat()
            }
            
            return health_info
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                'service_name': 'MarketDataService',
                'status': 'error',
                'error': str(e)
            }
