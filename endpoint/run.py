#!/usr/bin/env python3
"""
量化交易系统启动脚本
"""

import os
import sys
from app import create_app
from dotenv import load_dotenv

def main():
    """主函数"""
    # 加载环境变量 - 指定.env文件路径
    load_dotenv('.env')
    
    # 获取配置
    config_name = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    # 创建应用
    app = create_app(config_name)
    
    print(f"启动量化交易系统...")
    print(f"环境: {config_name}")
    print(f"地址: http://{host}:{port}")
    print(f"调试模式: {debug}")
    
    # 运行应用
    app.run(
        host=host,
        port=port,
        debug=debug
    )

if __name__ == '__main__':
    main()
