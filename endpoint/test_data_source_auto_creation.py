#!/usr/bin/env python3
"""
测试数据来源自动创建功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from endpoint.app import create_app
from endpoint.models import db, DataSource
from endpoint.services.data_sources.akshare_data_source import AkshareDataSource
from endpoint.services.market_data_service import MarketDataService

def test_data_source_auto_creation():
    """测试数据来源自动创建功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 数据来源自动创建功能测试 ===\n")
        
        # 1. 测试AKShare数据源直接创建记录
        print("1. 测试AKShare数据源直接创建记录...")
        akshare_source = AkshareDataSource()
        
        # 创建数据来源记录
        data_source_info = akshare_source.create_data_source_record()
        if data_source_info:
            print(f"✓ AKShare数据来源记录创建成功:")
            print(f"  - ID: {data_source_info['id']}")
            print(f"  - 名称: {data_source_info['name']}")
            print(f"  - URI: {data_source_info['uri']}")
            print(f"  - 描述: {data_source_info['description']}")
            print(f"  - 提供商类型: {data_source_info['provider_type']}")
            print(f"  - 优先级: {data_source_info['priority']}")
        else:
            print("✗ AKShare数据来源记录创建失败")
        
        # 2. 测试重复创建（应该返回已存在的记录）
        print("\n2. 测试重复创建...")
        data_source_info2 = akshare_source.create_data_source_record()
        if data_source_info2 and data_source_info2['id'] == data_source_info['id']:
            print("✓ 重复创建正确返回已存在的记录")
        else:
            print("✗ 重复创建处理异常")
        
        # 3. 测试MarketDataService自动创建数据来源
        print("\n3. 测试MarketDataService自动创建数据来源...")
        
        # 先删除现有的akshare数据来源记录
        existing = DataSource.query.filter_by(provider_type='akshare').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print("✓ 清理现有akshare数据来源记录")
        
        # 创建MarketDataService，应该自动创建数据来源记录
        market_service = MarketDataService('akshare')
        
        if market_service.data_source_record:
            print(f"✓ MarketDataService自动创建数据来源记录:")
            print(f"  - ID: {market_service.data_source_record.id}")
            print(f"  - 名称: {market_service.data_source_record.name}")
            print(f"  - URI: {market_service.data_source_record.uri}")
            print(f"  - 描述: {market_service.data_source_record.description}")
        else:
            print("✗ MarketDataService未能自动创建数据来源记录")
        
        # 4. 测试数据源连接测试功能
        print("\n4. 测试数据源连接测试功能...")
        test_result = akshare_source.test_connection()
        print(f"✓ 连接测试结果:")
        print(f"  - 状态: {test_result['status']}")
        print(f"  - 消息: {test_result['message']}")
        if 'test_data' in test_result:
            test_data = test_result['test_data']
            print(f"  - 股票数量: {test_data.get('stock_count', 0)}")
            print(f"  - API状态: {test_data.get('api_status', 'unknown')}")
            if 'sample_stocks' in test_data and test_data['sample_stocks']:
                print(f"  - 示例股票: {test_data['sample_stocks'][0]}")
        
        # 5. 测试数据来源统计
        print("\n5. 测试数据来源统计...")
        from sqlalchemy import func
        from endpoint.models import Symbol, MarketData
        
        stats = db.session.query(
            func.count(MarketData.id).label('total_records'),
            func.count(func.distinct(MarketData.symbol)).label('unique_symbols'),
            func.min(MarketData.timestamp).label('earliest_data'),
            func.max(MarketData.timestamp).label('latest_data')
        ).filter_by(data_source_id=market_service.data_source_record.id).first()
        
        print(f"✓ 数据来源统计:")
        print(f"  - 总记录数: {stats.total_records or 0}")
        print(f"  - 唯一股票数: {stats.unique_symbols or 0}")
        print(f"  - 最早数据: {stats.earliest_data or '无'}")
        print(f"  - 最新数据: {stats.latest_data or '无'}")
        
        # 6. 测试不同数据源的创建
        print("\n6. 测试不同数据源的创建...")
        
        # 测试Yahoo Finance数据源（如果存在）
        try:
            from endpoint.services.data_sources.yahoo_data_source import YahooDataSource
            yahoo_source = YahooDataSource()
            yahoo_info = yahoo_source.create_data_source_record()
            if yahoo_info:
                print(f"✓ Yahoo Finance数据来源创建成功: {yahoo_info['name']}")
            else:
                print("✗ Yahoo Finance数据来源创建失败")
        except ImportError:
            print("○ Yahoo Finance数据源未实现，跳过测试")
        
        # 测试Alpha Vantage数据源（如果存在）
        try:
            from endpoint.services.data_sources.alpha_vantage_data_source import AlphaVantageDataSource
            av_source = AlphaVantageDataSource()
            av_info = av_source.create_data_source_record()
            if av_info:
                print(f"✓ Alpha Vantage数据来源创建成功: {av_info['name']}")
            else:
                print("✗ Alpha Vantage数据来源创建失败")
        except ImportError:
            print("○ Alpha Vantage数据源未实现，跳过测试")
        
        # 7. 清理测试数据
        print("\n7. 清理测试数据...")
        try:
            # 删除测试创建的数据来源记录
            test_sources = DataSource.query.filter(
                DataSource.name.like('%测试%') | 
                DataSource.name.like('%Test%')
            ).all()
            
            for source in test_sources:
                db.session.delete(source)
            
            db.session.commit()
            print("✓ 测试数据清理完成")
        except Exception as e:
            print(f"⚠ 清理测试数据时出错: {e}")
        
        print("\n=== 所有测试完成！ ===")

if __name__ == "__main__":
    test_data_source_auto_creation()
