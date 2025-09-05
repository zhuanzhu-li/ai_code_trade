import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/quant_trading'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 交易配置
    TRADING_ENABLED = os.environ.get('TRADING_ENABLED', 'False').lower() == 'true'
    MAX_POSITION_SIZE = float(os.environ.get('MAX_POSITION_SIZE', '10000'))
    MAX_DAILY_LOSS = float(os.environ.get('MAX_DAILY_LOSS', '1000'))
    
    # API配置
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '1000')
    
    # 数据源配置
    YAHOO_FINANCE_ENABLED = True
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY')
    
    # 调度器配置
    SCHEDULER_API_ENABLED = True
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/trading.log')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:password@localhost/quant_trading_dev'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/quant_trading'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
