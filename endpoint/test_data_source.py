#!/usr/bin/env python3
"""
数据来源功能测试脚本
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from endpoint.app import create_app
from endpoint.models import db, DataSource, Symbol, MarketData

def test_data_source_functionality():
    """测试数据来源功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 数据来源功能测试 ===\n")
        
        # 1. 测试创建数据来源
        print("1. 测试创建数据来源...")
        data_source = DataSource(
            name="测试数据源",
            uri="https://test.example.com",
            description="这是一个测试数据源",
            provider_type="test",
            is_active=True,
            priority=1,
            config={"api_key": "test_key", "timeout": 30}
        )
        
        db.session.add(data_source)
        db.session.commit()
        print(f"✓ 创建数据来源成功: {data_source.name} (ID: {data_source.id})")
        
        # 2. 测试创建带数据来源的Symbol
        print("\n2. 测试创建带数据来源的Symbol...")
        symbol = Symbol(
            symbol="TEST001",
            name="测试股票",
            exchange="TEST",
            asset_type="stock",
            data_source_id=data_source.id,
            is_active=True
        )
        
        db.session.add(symbol)
        db.session.commit()
        print(f"✓ 创建Symbol成功: {symbol.symbol} (数据来源: {symbol.data_source.name})")
        
        # 3. 测试创建带数据来源的MarketData
        print("\n3. 测试创建带数据来源的MarketData...")
        market_data = MarketData(
            symbol="TEST001",
            data_source_id=data_source.id,
            timestamp=datetime.now(),
            open_price=100.0,
            high_price=105.0,
            low_price=95.0,
            close_price=102.0,
            volume=1000.0,
            interval_type="1d"
        )
        
        db.session.add(market_data)
        db.session.commit()
        print(f"✓ 创建MarketData成功: {market_data.symbol} (数据来源: {market_data.data_source.name})")
        
        # 4. 测试关联查询
        print("\n4. 测试关联查询...")
        
        # 查询数据来源的所有symbols
        symbols = Symbol.query.filter_by(data_source_id=data_source.id).all()
        print(f"✓ 数据来源 {data_source.name} 关联的Symbols数量: {len(symbols)}")
        
        # 查询数据来源的所有market_data
        market_data_count = MarketData.query.filter_by(data_source_id=data_source.id).count()
        print(f"✓ 数据来源 {data_source.name} 关联的MarketData数量: {market_data_count}")
        
        # 5. 测试to_dict方法
        print("\n5. 测试to_dict方法...")
        symbol_dict = symbol.to_dict()
        print(f"✓ Symbol to_dict包含数据来源信息: {'data_source' in symbol_dict}")
        print(f"  - data_source_id: {symbol_dict.get('data_source_id')}")
        print(f"  - data_source: {symbol_dict.get('data_source') is not None}")
        
        market_data_dict = market_data.to_dict()
        print(f"✓ MarketData to_dict包含数据来源信息: {'data_source' in market_data_dict}")
        print(f"  - data_source_id: {market_data_dict.get('data_source_id')}")
        print(f"  - data_source: {market_data_dict.get('data_source') is not None}")
        
        # 6. 测试数据来源统计
        print("\n6. 测试数据来源统计...")
        from sqlalchemy import func
        stats = db.session.query(
            func.count(MarketData.id).label('total_records'),
            func.count(func.distinct(MarketData.symbol)).label('unique_symbols'),
            func.min(MarketData.timestamp).label('earliest_data'),
            func.max(MarketData.timestamp).label('latest_data')
        ).filter_by(data_source_id=data_source.id).first()
        
        print(f"✓ 数据来源统计:")
        print(f"  - 总记录数: {stats.total_records}")
        print(f"  - 唯一股票数: {stats.unique_symbols}")
        print(f"  - 最早数据: {stats.earliest_data}")
        print(f"  - 最新数据: {stats.latest_data}")
        
        # 7. 清理测试数据
        print("\n7. 清理测试数据...")
        db.session.delete(market_data)
        db.session.delete(symbol)
        db.session.delete(data_source)
        db.session.commit()
        print("✓ 测试数据清理完成")
        
        print("\n=== 所有测试通过！ ===")

if __name__ == "__main__":
    test_data_source_functionality()
