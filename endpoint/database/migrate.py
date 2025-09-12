#!/usr/bin/env python3
"""
数据库迁移管理工具
用于管理数据库版本升级和回滚

使用方法:
    python migrate.py --help                    # 查看帮助
    python migrate.py status                    # 查看当前版本状态
    python migrate.py list                      # 列出所有可用的迁移文件
    python migrate.py upgrade                   # 升级到最新版本
    python migrate.py upgrade v1.1.0           # 升级到指定版本
    python migrate.py downgrade v1.0.0         # 回滚到指定版本
    python migrate.py init                      # 初始化数据库结构
    python migrate.py validate                 # 验证数据库完整性
"""

import os
import sys
import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path
import pymysql
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
endpoint_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 尝试从多个位置加载环境变量
env_files = [
    os.path.join(project_root, '.env'),                    # 项目根目录
    os.path.join(endpoint_dir, '.env'),                    # endpoint目录
    os.path.join(os.path.dirname(__file__), '.env'),      # database目录
    os.path.join(os.path.dirname(__file__), 'db_config.env'),  # database目录的配置文件
]

env_file = None
for file_path in env_files:
    if os.path.exists(file_path):
        env_file = file_path
        break

if env_file:
    load_dotenv(env_file)
    print(f"✓ 加载配置文件: {env_file}")
else:
    print("警告: 未找到配置文件，将使用默认数据库配置")
    print("请创建以下任一配置文件:")
    for file_path in env_files:
        print(f"  - {file_path}")
    env_file = "未找到"

class DatabaseMigrator:
    def __init__(self):
        # 尝试从DATABASE_URL解析数据库配置
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # 解析DATABASE_URL格式: mysql+pymysql://user:password@host:port/database
            import re
            match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):?(\d+)?/(.+)', database_url)
            if match:
                user, password, host, port, database = match.groups()
                self.db_config = {
                    'host': host,
                    'port': int(port) if port else 3306,
                    'user': user,
                    'password': password,
                    'database': database,
                    'charset': 'utf8mb4'
                }
            else:
                # 如果解析失败，使用默认配置
                self.db_config = self._get_default_config()
        else:
            # 使用独立的环境变量配置
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'quant_trading'),
                'charset': 'utf8mb4'
            }
        
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.schema_file = Path(__file__).parent / 'schema.sql'
        self.connection = None
        
        # 调试信息：显示配置
        print(f"数据库配置: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
        print(f"用户: {self.db_config['user']}")
        print(f"环境文件路径: {env_file}")
        print(f"环境文件存在: {os.path.exists(env_file)}")
        
    def _get_default_config(self):
        """获取默认数据库配置"""
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'quant_trading',
            'charset': 'utf8mb4'
        }
        
    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(**self.db_config)
            print(f"✓ 已连接到数据库: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_sql(self, sql, params=None):
        """执行SQL语句"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def get_current_version(self):
        """获取当前数据库版本"""
        try:
            result = self.execute_sql(
                "SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1"
            )
            return result[0][0] if result else None
        except Exception:
            return None
    
    def get_all_versions(self):
        """获取所有已应用的版本"""
        try:
            result = self.execute_sql(
                "SELECT version, description, applied_at FROM schema_versions ORDER BY applied_at"
            )
            return result
        except Exception:
            return []
    
    def version_exists(self, version):
        """检查版本是否已存在"""
        try:
            result = self.execute_sql(
                "SELECT COUNT(*) FROM schema_versions WHERE version = %s",
                (version,)
            )
            return result[0][0] > 0
        except Exception:
            return False
    
    def calculate_file_checksum(self, file_path):
        """计算文件校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def parse_version_from_filename(self, filename):
        """从文件名解析版本号"""
        match = re.match(r'v(\d+\.\d+\.\d+)', filename)
        return match.group(0) if match else None
    
    def get_migration_files(self):
        """获取所有迁移文件"""
        migration_files = []
        if self.migrations_dir.exists():
            for file_path in sorted(self.migrations_dir.glob('*.sql')):
                version = self.parse_version_from_filename(file_path.name)
                if version:
                    migration_files.append({
                        'version': version,
                        'file_path': file_path,
                        'filename': file_path.name
                    })
        return migration_files
    
    def version_to_tuple(self, version):
        """将版本字符串转换为元组用于比较"""
        return tuple(map(int, version.lstrip('v').split('.')))
    
    def execute_migration_file(self, file_path):
        """执行迁移文件"""
        print(f"执行迁移文件: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 解析SQL语句，正确处理DELIMITER语法
        statements = self._parse_sql_statements(sql_content)
        
        # 执行所有语句
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    print(f"执行语句 {i}/{len(statements)}")
                    self.execute_sql(statement)
                except Exception as e:
                    print(f"✗ SQL执行失败: {e}")
                    print(f"SQL语句: {statement[:200]}...")
                    raise
    
    def _parse_sql_statements(self, sql_content):
        """解析SQL语句，正确处理DELIMITER语法"""
        statements = []
        current_statement = ""
        current_delimiter = ";"
        in_delimiter_block = False
        
        lines = sql_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('--'):
                i += 1
                continue
            
            # 处理DELIMITER命令
            if line.upper().startswith('DELIMITER'):
                parts = line.split()
                if len(parts) > 1:
                    new_delimiter = parts[1]
                    if new_delimiter == '//':
                        current_delimiter = '//'
                        in_delimiter_block = True
                    else:
                        current_delimiter = new_delimiter
                        in_delimiter_block = False
                i += 1
                continue
            
            # 检查是否是结束delimiter
            if in_delimiter_block and line == '//':
                # 添加当前语句（如果有内容）
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ""
                current_delimiter = ";"
                in_delimiter_block = False
                i += 1
                continue
            
            # 添加当前行到语句
            current_statement += line + "\n"
            
            # 检查是否到达语句结束
            if line.endswith(current_delimiter):
                # 移除结尾的delimiter
                if current_delimiter == ';':
                    statement_content = current_statement.rstrip().rstrip(';')
                else:
                    statement_content = current_statement.rstrip().rstrip(current_delimiter)
                
                if statement_content.strip():
                    statements.append(statement_content.strip())
                current_statement = ""
            
            i += 1
        
        # 添加最后一个语句（如果有）
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def init_database(self):
        """初始化数据库结构"""
        print("初始化数据库结构...")
        
        if not self.schema_file.exists():
            print(f"✗ 找不到schema文件: {self.schema_file}")
            return False
        
        try:
            self.execute_migration_file(self.schema_file)
            print("✓ 数据库结构初始化完成")
            return True
        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
            return False
    
    def upgrade_to_version(self, target_version=None):
        """升级到指定版本"""
        current_version = self.get_current_version()
        migration_files = self.get_migration_files()
        
        if not migration_files:
            print("✗ 没有找到迁移文件")
            return False
        
        # 如果没有指定目标版本，升级到最新版本
        if target_version is None:
            target_version = migration_files[-1]['version']
        
        print(f"当前版本: {current_version or 'None'}")
        print(f"目标版本: {target_version}")
        
        # 如果数据库为空，先初始化
        if current_version is None:
            if not self.init_database():
                return False
            current_version = self.get_current_version()
        
        # 找到需要应用的迁移文件
        migrations_to_apply = []
        for migration in migration_files:
            # 跳过已应用的版本
            if current_version and self.version_to_tuple(migration['version']) <= self.version_to_tuple(current_version):
                continue
            
            # 只应用到目标版本
            if self.version_to_tuple(migration['version']) <= self.version_to_tuple(target_version):
                migrations_to_apply.append(migration)
        
        if not migrations_to_apply:
            print("✓ 数据库已经是最新版本")
            return True
        
        # 应用迁移
        for migration in migrations_to_apply:
            try:
                print(f"\n应用迁移: {migration['version']}")
                self.execute_migration_file(migration['file_path'])
                print(f"✓ 迁移 {migration['version']} 应用成功")
            except Exception as e:
                print(f"✗ 迁移 {migration['version']} 应用失败: {e}")
                return False
        
        print(f"\n✓ 数据库升级完成，当前版本: {self.get_current_version()}")
        return True
    
    def rollback_version(self, target_version):
        """回滚到指定版本"""
        current_version = self.get_current_version()
        
        if not current_version:
            print("✗ 数据库未初始化，无法回滚")
            return False
        
        print(f"当前版本: {current_version}")
        print(f"回滚到版本: {target_version}")
        
        # 检查回滚脚本是否存在
        rollback_file = self.migrations_dir.parent / f'rollback_{target_version}.sql'
        
        if not rollback_file.exists():
            print(f"✗ 找不到回滚脚本: {rollback_file}")
            print("请手动创建回滚脚本或联系管理员")
            return False
        
        try:
            print(f"\n执行回滚脚本: {rollback_file.name}")
            self.execute_migration_file(rollback_file)
            print(f"✓ 回滚完成")
            return True
        except Exception as e:
            print(f"✗ 回滚失败: {e}")
            return False
    
    def show_status(self):
        """显示当前状态"""
        current_version = self.get_current_version()
        migration_files = self.get_migration_files()
        applied_versions = self.get_all_versions()
        
        print(f"当前数据库版本: {current_version or 'None'}")
        print(f"可用迁移文件数: {len(migration_files)}")
        print(f"已应用版本数: {len(applied_versions)}")
        
        if applied_versions:
            print("\n已应用的版本:")
            for version, description, applied_at in applied_versions:
                print(f"  {version:<10} - {description} ({applied_at})")
        
        if migration_files:
            print("\n可用的迁移文件:")
            for migration in migration_files:
                status = "✓ 已应用" if self.version_exists(migration['version']) else "○ 未应用"
                print(f"  {migration['version']:<10} - {migration['filename']} {status}")
    
    def list_migrations(self):
        """列出所有迁移文件"""
        migration_files = self.get_migration_files()
        
        if not migration_files:
            print("没有找到迁移文件")
            return
        
        print("可用的迁移文件:")
        for migration in migration_files:
            status = "✓ 已应用" if self.version_exists(migration['version']) else "○ 未应用"
            print(f"  {migration['version']:<10} - {migration['filename']} {status}")
    
    def validate_database(self):
        """验证数据库完整性"""
        print("验证数据库完整性...")
        
        # 检查关键表是否存在
        required_tables = [
            'users', 'portfolios', 'positions', 'trades', 'orders',
            'strategies', 'strategy_executions', 'market_data', 'symbols',
            'risk_rules', 'risk_alerts', 'data_sources', 'schema_versions'
        ]
        
        try:
            result = self.execute_sql("SHOW TABLES")
            existing_tables = [row[0] for row in result]
            
            missing_tables = []
            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"✗ 缺少表: {', '.join(missing_tables)}")
                return False
            else:
                print("✓ 所有必需的表都存在")
            
            # 检查版本表
            current_version = self.get_current_version()
            if current_version:
                print(f"✓ 当前数据库版本: {current_version}")
            else:
                print("⚠ 警告: 无法确定数据库版本")
            
            return True
            
        except Exception as e:
            print(f"✗ 数据库验证失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='数据库迁移管理工具')
    parser.add_argument('command', choices=['init', 'status', 'list', 'upgrade', 'rollback', 'validate'],
                       help='要执行的命令')
    parser.add_argument('version', nargs='?', help='目标版本号 (用于upgrade/rollback命令)')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if not migrator.connect():
        sys.exit(1)
    
    try:
        if args.command == 'init':
            success = migrator.init_database()
        elif args.command == 'status':
            migrator.show_status()
            success = True
        elif args.command == 'list':
            migrator.list_migrations()
            success = True
        elif args.command == 'upgrade':
            success = migrator.upgrade_to_version(args.version)
        elif args.command == 'rollback':
            if not args.version:
                print("回滚命令需要指定目标版本")
                success = False
            else:
                success = migrator.rollback_version(args.version)
        elif args.command == 'validate':
            success = migrator.validate_database()
        else:
            print(f"未知命令: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"操作失败: {e}")
        sys.exit(1)
    finally:
        migrator.disconnect()

if __name__ == '__main__':
    main()
