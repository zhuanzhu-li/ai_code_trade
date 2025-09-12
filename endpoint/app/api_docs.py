"""
API文档自动生成模块
使用Flask-RESTX自动生成Swagger/OpenAPI文档
"""

from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint
from functools import wraps
import inspect
import datetime
import json

# 创建API文档蓝图
api_docs_bp = Blueprint('api_docs', __name__)

# 创建API实例
api = Api(
    api_docs_bp,
    version='1.0.0',
    title='量化交易系统 API',
    description='基于Flask的个人量化交易系统API文档',
    doc='/docs/',  # Swagger UI路径
    prefix='/',
    # 配置JSON处理
    default='json',
    default_label='JSON',
    # 添加自定义JSON编码器
    catch_all_404s=True
)

# 定义通用响应模型
success_response_model = api.model('SuccessResponse', {
    'code': fields.Integer(description='状态码，200为成功', example=200),
    'msg': fields.String(description='返回信息', example='成功！'),
    'data': fields.Raw(description='返回的具体数据')
})

error_response_model = api.model('ErrorResponse', {
    'code': fields.Integer(description='错误码', example=10001),
    'msg': fields.String(description='错误信息', example='缺少必要字段'),
    'data': fields.Raw(description='错误详情', example=None)
})

# 定义用户相关模型
user_model = api.model('User', {
    'id': fields.Integer(description='用户ID', example=1),
    'username': fields.String(description='用户名', example='testuser'),
    'email': fields.String(description='邮箱', example='test@example.com'),
    'is_active': fields.Boolean(description='是否激活', example=True),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

user_register_model = api.model('UserRegister', {
    'username': fields.String(required=True, description='用户名', example='testuser'),
    'email': fields.String(required=True, description='邮箱', example='test@example.com'),
    'password': fields.String(required=True, description='密码', example='password123')
})

user_login_model = api.model('UserLogin', {
    'username': fields.String(required=True, description='用户名', example='testuser'),
    'password': fields.String(required=True, description='密码', example='password123')
})

# 定义投资组合相关模型
portfolio_model = api.model('Portfolio', {
    'id': fields.Integer(description='投资组合ID', example=1),
    'user_id': fields.Integer(description='用户ID', example=1),
    'name': fields.String(description='投资组合名称', example='我的投资组合'),
    'description': fields.String(description='描述', example='主要投资组合'),
    'initial_capital': fields.Float(description='初始资金', example=10000.0),
    'current_value': fields.Float(description='当前价值', example=10500.0),
    'cash_balance': fields.Float(description='现金余额', example=500.0),
    'total_pnl': fields.Float(description='总盈亏', example=500.0),
    'total_pnl_percentage': fields.Float(description='总盈亏百分比', example=5.0),
    'is_active': fields.Boolean(description='是否激活', example=True),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

portfolio_create_model = api.model('PortfolioCreate', {
    'name': fields.String(required=True, description='投资组合名称', example='我的投资组合'),
    'description': fields.String(description='描述', example='主要投资组合'),
    'user_id': fields.Integer(required=True, description='用户ID', example=1),
    'initial_capital': fields.Float(description='初始资金', example=10000.0)
})

# 定义交易相关模型
trade_model = api.model('Trade', {
    'id': fields.Integer(description='交易ID', example=1),
    'portfolio_id': fields.Integer(description='投资组合ID', example=1),
    'strategy_execution_id': fields.Integer(description='策略执行ID', example=1),
    'symbol': fields.String(description='交易标的', example='AAPL'),
    'side': fields.String(description='交易方向', example='buy', enum=['buy', 'sell']),
    'quantity': fields.Integer(description='数量', example=100),
    'price': fields.Float(description='价格', example=150.0),
    'amount': fields.Float(description='金额', example=15000.0),
    'fee': fields.Float(description='手续费', example=15.0),
    'net_amount': fields.Float(description='净金额', example=14985.0),
    'pnl': fields.Float(description='盈亏', example=0.0),
    'status': fields.String(description='状态', example='completed'),
    'executed_at': fields.DateTime(description='执行时间'),
    'created_at': fields.DateTime(description='创建时间')
})

trade_create_model = api.model('TradeCreate', {
    'portfolio_id': fields.Integer(required=True, description='投资组合ID', example=1),
    'symbol': fields.String(required=True, description='交易标的', example='AAPL'),
    'side': fields.String(required=True, description='交易方向', example='buy', enum=['buy', 'sell']),
    'quantity': fields.Integer(required=True, description='数量', example=100),
    'price': fields.Float(required=True, description='价格', example=150.0),
    'strategy_execution_id': fields.Integer(description='策略执行ID', example=1)
})

# 定义策略相关模型
strategy_model = api.model('Strategy', {
    'id': fields.Integer(description='策略ID', example=1),
    'user_id': fields.Integer(description='用户ID', example=1),
    'name': fields.String(description='策略名称', example='动量策略'),
    'description': fields.String(description='策略描述', example='基于动量的交易策略'),
    'strategy_type': fields.String(description='策略类型', example='momentum', enum=['momentum', 'mean_reversion']),
    'parameters': fields.Raw(description='策略参数'),
    'is_active': fields.Boolean(description='是否激活', example=True),
    'performance': fields.Raw(description='表现数据'),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

strategy_create_model = api.model('StrategyCreate', {
    'name': fields.String(required=True, description='策略名称', example='动量策略'),
    'description': fields.String(description='策略描述', example='基于动量的交易策略'),
    'user_id': fields.Integer(required=True, description='用户ID', example=1),
    'strategy_type': fields.String(required=True, description='策略类型', example='momentum', enum=['momentum', 'mean_reversion']),
    'parameters': fields.Raw(description='策略参数')
})

strategy_execute_model = api.model('StrategyExecute', {
    'portfolio_id': fields.Integer(required=True, description='投资组合ID', example=1),
    'start_time': fields.DateTime(description='开始时间'),
    'initial_capital': fields.Float(description='初始资金', example=10000.0)
})

# 定义市场数据相关模型
market_data_model = api.model('MarketData', {
    'id': fields.Integer(description='数据ID', example=1),
    'symbol_id': fields.Integer(description='标的ID', example=1),
    'symbol': fields.String(description='标的代码', example='AAPL'),
    'symbol_name': fields.String(description='标的名称', example='苹果公司'),
    'timestamp': fields.DateTime(description='时间戳'),
    'open_price': fields.Float(description='开盘价', example=150.0),
    'high_price': fields.Float(description='最高价', example=155.0),
    'low_price': fields.Float(description='最低价', example=149.0),
    'close_price': fields.Float(description='收盘价', example=154.0),
    'volume': fields.Integer(description='成交量', example=1000000),
    'price_change': fields.Float(description='价格变化', example=4.0),
    'price_change_percentage': fields.Float(description='价格变化百分比', example=2.67),
    'high_low_spread': fields.Float(description='高低价差', example=6.0),
    'created_at': fields.DateTime(description='创建时间')
})

symbol_model = api.model('Symbol', {
    'id': fields.Integer(description='标的ID', example=1),
    'symbol': fields.String(description='标的代码', example='AAPL'),
    'name': fields.String(description='标的名称', example='苹果公司'),
    'market': fields.String(description='市场', example='NASDAQ'),
    'sector': fields.String(description='行业', example='科技'),
    'is_active': fields.Boolean(description='是否激活', example=True),
    'created_at': fields.DateTime(description='创建时间')
})

# 定义风险规则相关模型
risk_rule_model = api.model('RiskRule', {
    'id': fields.Integer(description='规则ID', example=1),
    'name': fields.String(description='规则名称', example='持仓大小限制'),
    'description': fields.String(description='规则描述', example='限制单个持仓的最大金额'),
    'rule_type': fields.String(description='规则类型', example='position_size'),
    'parameters': fields.Raw(description='规则参数'),
    'is_active': fields.Boolean(description='是否激活', example=True),
    'created_at': fields.DateTime(description='创建时间'),
    'updated_at': fields.DateTime(description='更新时间')
})

risk_rule_create_model = api.model('RiskRuleCreate', {
    'name': fields.String(required=True, description='规则名称', example='持仓大小限制'),
    'description': fields.String(description='规则描述', example='限制单个持仓的最大金额'),
    'rule_type': fields.String(required=True, description='规则类型', example='position_size'),
    'parameters': fields.Raw(description='规则参数')
})

# 定义仪表板相关模型
dashboard_stats_model = api.model('DashboardStats', {
    'total_value': fields.Float(description='总资产价值', example=100000.0),
    'total_pnl': fields.Float(description='总盈亏', example=5000.0),
    'total_pnl_percentage': fields.Float(description='总盈亏百分比', example=5.0),
    'active_portfolios': fields.Integer(description='活跃投资组合数', example=3),
    'active_strategies': fields.Integer(description='活跃策略数', example=2),
    'total_trades': fields.Integer(description='总交易数', example=100),
    'win_rate': fields.Float(description='胜率', example=65.0),
    'risk_alerts': fields.Integer(description='风险警报数', example=2)
})

# 定义分页模型
pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='当前页码', example=1),
    'per_page': fields.Integer(description='每页记录数', example=50),
    'total': fields.Integer(description='总记录数', example=100),
    'pages': fields.Integer(description='总页数', example=2),
    'has_next': fields.Boolean(description='是否有下一页', example=True),
    'has_prev': fields.Boolean(description='是否有上一页', example=False)
})

# 创建命名空间
auth_ns = api.namespace('auth', description='用户认证相关API')
users_ns = api.namespace('users', description='用户管理API')
portfolios_ns = api.namespace('portfolios', description='投资组合管理API')
trades_ns = api.namespace('trades', description='交易管理API')
strategies_ns = api.namespace('strategies', description='策略管理API')
market_data_ns = api.namespace('market-data', description='市场数据API')
risk_ns = api.namespace('risk', description='风险管理API')
dashboard_ns = api.namespace('dashboard', description='仪表板API')
system_ns = api.namespace('system', description='系统API')

def api_doc_decorator(description, responses=None, params=None):
    """
    API文档装饰器
    用于为现有路由添加Swagger文档
    """
    def decorator(func):
        # 添加文档字符串
        func.__doc__ = description
        
        # 添加响应模型
        if responses:
            func.responses = responses
        
        # 添加参数模型
        if params:
            func.params = params
            
        return func
    return decorator

def register_legacy_routes():
    """
    注册现有的API路由到Flask-RESTX
    这里可以逐步迁移现有的路由
    """
    pass

# 导出API实例供其他模块使用
__all__ = ['api', 'api_docs_bp', 'api_doc_decorator', 'register_legacy_routes']
