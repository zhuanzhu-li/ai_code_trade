#!/usr/bin/env python3
"""
量化交易系统安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失败: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✓ Python版本: {sys.version}")

def check_mysql():
    """检查MySQL是否安装"""
    try:
        subprocess.run(["mysql", "--version"], check=True, capture_output=True)
        print("✓ MySQL已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ MySQL未安装，请先安装MySQL")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ['logs', 'static', 'templates', 'migrations/versions']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✓ 目录创建完成")

def install_dependencies():
    """安装Python依赖"""
    if not run_command("pip install -r requirements.txt", "安装Python依赖"):
        return False
    return True

def setup_database():
    """设置数据库"""
    print("请确保MySQL服务正在运行，并且已创建数据库")
    print("数据库配置示例:")
    print("CREATE DATABASE quant_trading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("CREATE DATABASE quant_trading_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("CREATE USER 'quant_user'@'localhost' IDENTIFIED BY 'your_password';")
    print("GRANT ALL PRIVILEGES ON quant_trading.* TO 'quant_user'@'localhost';")
    print("GRANT ALL PRIVILEGES ON quant_trading_dev.* TO 'quant_user'@'localhost';")
    print("FLUSH PRIVILEGES;")
    
    input("按回车键继续...")
    return True

def create_env_file():
    """创建环境配置文件"""
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env文件已存在")
        return True
    
    env_example = Path('env.example')
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ 已创建.env文件，请编辑配置")
        return True
    else:
        print("✗ 未找到env.example文件")
        return False

def initialize_database():
    """初始化数据库"""
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    if not run_command("flask db init", "初始化数据库迁移"):
        return False
    
    if not run_command("flask db migrate -m 'Initial migration'", "创建初始迁移"):
        return False
    
    if not run_command("flask db upgrade", "应用数据库迁移"):
        return False
    
    return True

def main():
    """主安装函数"""
    print("=" * 50)
    print("量化交易系统安装程序")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查MySQL
    if not check_mysql():
        print("请先安装MySQL，然后重新运行此脚本")
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    if not install_dependencies():
        print("依赖安装失败，请检查网络连接和Python环境")
        sys.exit(1)
    
    # 创建环境配置文件
    if not create_env_file():
        print("环境配置文件创建失败")
        sys.exit(1)
    
    # 设置数据库
    if not setup_database():
        print("数据库设置失败")
        sys.exit(1)
    
    # 初始化数据库
    if not initialize_database():
        print("数据库初始化失败")
        sys.exit(1)
    
    print("=" * 50)
    print("安装完成！")
    print("=" * 50)
    print("下一步:")
    print("1. 编辑.env文件，配置数据库连接")
    print("2. 运行: python run.py")
    print("3. 访问: http://localhost:5000")
    print("=" * 50)

if __name__ == '__main__':
    main()
