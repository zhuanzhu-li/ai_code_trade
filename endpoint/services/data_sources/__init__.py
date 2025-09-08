"""
数据源模块
提供统一的股票数据获取接口
"""

from .base_data_source import BaseDataSource
from .akshare_data_source import AKShareDataSource

# 数据源注册表
DATA_SOURCES = {
    'akshare': AKShareDataSource,
}

def create_data_source(source_name: str, config: dict = None):
    """
    创建数据源实例
    
    Args:
        source_name: 数据源名称
        config: 配置参数
        
    Returns:
        BaseDataSource: 数据源实例
    """
    if source_name not in DATA_SOURCES:
        raise ValueError(f"不支持的数据源: {source_name}")
    
    return DATA_SOURCES[source_name](config)

def list_available_sources():
    """获取可用的数据源列表"""
    return list(DATA_SOURCES.keys())

__all__ = [
    'BaseDataSource',
    'AKShareDataSource', 
    'DATA_SOURCES',
    'create_data_source',
    'list_available_sources'
]
