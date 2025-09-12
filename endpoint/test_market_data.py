#!/usr/bin/env python3
"""
市场数据功能测试脚本
用于测试akshare数据源和市场数据服务功能
"""

import sys
import os
import time
from datetime import datetime, date, timedelta

from dotenv import load_dotenv

# 加载环境变量 - 必须在导入其他模块之前
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_sources.akshare_data_source import AKShareDataSource
from services.market_data_service import MarketDataService
from models import db, Symbol, MarketData
from app import create_app

def test_akshare_data_source():
    """测试AKShare数据源"""
    print("=== 测试AKShare数据源 ===")
    
    # 创建数据源实例
    data_source = AKShareDataSource()
    
    # 测试连接
    print("1. 测试连接...")
    if data_source.connect():
        print("✓ 连接成功")
    else:
        print("✗ 连接失败")
        return False
    
    # 测试获取上证500成分股
    print("2. 测试获取上证500成分股...")
    components = data_source.get_index_components('上证500')
    if components:
        print(f"✓ 成功获取{len(components)}只成分股")
        print("前5只成分股:")
        for i, comp in enumerate(components[:5]):
            print(f"  {i+1}. {comp['symbol']} - {comp['name']}")
    else:
        print("✗ 获取成分股失败")
        return False
    
    # 测试获取历史数据
    print("3. 测试获取历史数据...")
    if components:
        test_symbol = components[0]['symbol']
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        df = data_source.get_historical_data(test_symbol, start_date, end_date)
        if not df.empty:
            print(f"✓ 成功获取{test_symbol}的{len(df)}条历史数据")
            print("最近5天数据:")
            print(df.head())
        else:
            print(f"✗ 获取{test_symbol}历史数据失败")
            return False
    
    # 健康检查
    print("4. 健康检查...")
    health = data_source.health_check()
    print(f"✓ 健康状态: {health}")
    
    data_source.disconnect()
    return True

def test_market_data_service():
    """测试市场数据服务"""
    print("\n=== 测试市场数据服务 ===")
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        # 这里先等待5秒
        time.sleep(5)
        # 创建市场数据服务实例
        market_service = MarketDataService()

        
        # 测试初始化数据源
        print("1. 测试初始化数据源...")
        if market_service.initialize_data_source():
            print("✓ 数据源初始化成功")
        else:
            print("✗ 数据源初始化失败")
            return False
        
        # 测试同步上证500成分股
        print("2. 测试同步上证500成分股...")
        synced_count = market_service.sync_index_components('上证500')
        if synced_count > 0:
            print(f"✓ 成功同步{synced_count}只成分股")
        else:
            print("✗ 同步成分股失败")
            return False
        
        # 测试获取股票列表
        print("3. 测试获取股票列表...")
        symbols = Symbol.query.limit(5).all()
        if symbols:
            print(f"✓ 数据库中有{len(symbols)}只股票")
            for symbol in symbols:
                print(f"  - {symbol.symbol}: {symbol.name}")
        else:
            print("✗ 数据库中没有股票数据")
            return False
        
        # 测试获取历史数据
        print("4. 测试获取历史数据...")
        if symbols:
            test_symbol = symbols[0].symbol
            count = market_service.fetch_historical_data(test_symbol)
            if count > 0:
                print(f"✓ 成功获取{test_symbol}的{count}条历史数据")
            else:
                print(f"✗ 获取{test_symbol}历史数据失败")
                return False
        
        # 测试统计信息
        print("5. 测试统计信息...")
        stats = market_service.get_data_statistics()
        if stats:
            print(f"✓ 统计信息: {stats}")
        else:
            print("✗ 获取统计信息失败")
            return False
        
        # 健康检查
        print("6. 健康检查...")
        health = market_service.health_check()
        print(f"✓ 服务健康状态: {health}")
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    # 这里可以添加API测试
    # 需要启动Flask应用并发送HTTP请求
    print("API端点测试需要启动Flask应用后进行")
    return True

def main():
    """主测试函数"""
    print("开始市场数据功能测试")
    print("=" * 50)
    
    tests = [
        ("AKShare数据源", test_akshare_data_source),
        ("市场数据服务", test_market_data_service),
        ("API端点", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n开始测试: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} - 测试通过")
                passed += 1
            else:
                print(f"✗ {test_name} - 测试失败")
        except Exception as e:
            print(f"✗ {test_name} - 测试异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
