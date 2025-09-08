#!/usr/bin/env python3
"""
修复 v1.2.0 迁移失败的脚本
用于清理部分失败的迁移并重新应用
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from migrate import DatabaseMigrator

def fix_v1_2_0_migration():
    """修复v1.2.0迁移"""
    print("修复 v1.2.0 迁移失败问题")
    print("=" * 50)
    
    migrator = DatabaseMigrator()
    
    if not migrator.connect():
        print("✗ 数据库连接失败")
        return False
    
    try:
        # 1. 删除可能存在的v1.2.0版本记录
        print("1. 清理版本记录...")
        migrator.execute_sql("DELETE FROM schema_versions WHERE version = 'v1.2.0'")
        print("✓ 版本记录清理完成")
        
        # 2. 执行回滚脚本清理部分创建的内容
        rollback_file = Path(__file__).parent / 'rollback_v1.2.0.sql'
        if rollback_file.exists():
            print("2. 执行回滚脚本...")
            migrator.execute_migration_file(rollback_file)
            print("✓ 回滚脚本执行完成")
        else:
            print("2. 跳过回滚脚本（文件不存在）")
        
        # 3. 重新应用v1.2.0迁移
        print("3. 重新应用v1.2.0迁移...")
        success = migrator.upgrade_to_version('v1.2.0')
        
        if success:
            print("✓ v1.2.0迁移修复完成")
            return True
        else:
            print("✗ v1.2.0迁移修复失败")
            return False
            
    except Exception as e:
        print(f"✗ 修复过程中出现错误: {e}")
        return False
    finally:
        migrator.disconnect()

def main():
    """主函数"""
    success = fix_v1_2_0_migration()
    
    if success:
        print("\n" + "=" * 50)
        print("修复完成！可以继续使用数据库了。")
    else:
        print("\n" + "=" * 50)
        print("修复失败，请检查错误信息并手动处理。")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
