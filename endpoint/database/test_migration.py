#!/usr/bin/env python3
"""
数据库迁移测试脚本
用于测试迁移工具的基本功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from migrate import DatabaseMigrator

def test_config_loading():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    
    migrator = DatabaseMigrator()
    
    print(f"数据库主机: {migrator.db_config['host']}")
    print(f"数据库端口: {migrator.db_config['port']}")
    print(f"数据库用户: {migrator.db_config['user']}")
    print(f"数据库名称: {migrator.db_config['database']}")
    
    return True

def test_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    migrator = DatabaseMigrator()
    
    if migrator.connect():
        print("✓ 数据库连接成功")
        migrator.disconnect()
        return True
    else:
        print("✗ 数据库连接失败")
        return False

def test_migration_files():
    """测试迁移文件解析"""
    print("\n=== 测试迁移文件解析 ===")
    
    migrator = DatabaseMigrator()
    migration_files = migrator.get_migration_files()
    
    print(f"找到 {len(migration_files)} 个迁移文件:")
    for migration in migration_files:
        print(f"  - {migration['version']}: {migration['filename']}")
    
    return len(migration_files) > 0

def test_sql_parsing():
    """测试SQL解析功能"""
    print("\n=== 测试SQL解析功能 ===")
    
    migrator = DatabaseMigrator()
    
    # 测试简单SQL
    simple_sql = """
    -- 这是注释
    CREATE TABLE test (id INT PRIMARY KEY);
    INSERT INTO test VALUES (1);
    DROP TABLE test;
    """
    
    statements = migrator._parse_sql_statements(simple_sql)
    print(f"解析出 {len(statements)} 个SQL语句:")
    for i, stmt in enumerate(statements, 1):
        print(f"  {i}: {stmt[:50]}...")
    
    return len(statements) == 3

def main():
    """主测试函数"""
    print("数据库迁移工具测试")
    print("=" * 50)
    
    tests = [
        ("配置加载", test_config_loading),
        ("迁移文件解析", test_migration_files),
        ("SQL解析", test_sql_parsing),
        ("数据库连接", test_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {test_name} - 通过")
                passed += 1
            else:
                print(f"✗ {test_name} - 失败")
        except Exception as e:
            print(f"✗ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！")
        return True
    else:
        print("✗ 部分测试失败，请检查配置")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
