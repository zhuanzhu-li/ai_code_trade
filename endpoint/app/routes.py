from flask import Blueprint, request, jsonify
from models import db, User, Portfolio, Strategy, Trade, MarketData, RiskRule, Symbol, DataSource
# 延迟导入以避免循环导入
from utils.auth import token_required
from utils.response import (
    success_response, error_response, business_error_response, system_error_response,
    ResponseCode, ResponseMessage
)
from services.market_data_service import MarketDataService
import json
from datetime import datetime, date

# API蓝图
api_bp = Blueprint('api', __name__)

# 用户认证相关API
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    if User.query.filter_by(username=data['username']).first():
        return business_error_response(ResponseCode.USERNAME_EXISTS)
    
    if User.query.filter_by(email=data['email']).first():
        return business_error_response(ResponseCode.EMAIL_EXISTS)
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # 生成JWT token
    from utils.auth import generate_token
    token = generate_token(user.id)
    
    return success_response({
        'user': user.to_dict(),
        'token': token
    }, '注册成功')

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return business_error_response(ResponseCode.MISSING_CREDENTIALS)
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return business_error_response(ResponseCode.INVALID_CREDENTIALS)
    
    if not user.is_active:
        return business_error_response(ResponseCode.ACCOUNT_DISABLED)
    
    # 生成JWT token
    from utils.auth import generate_token
    token = generate_token(user.id)
    
    return success_response({
        'user': user.to_dict(),
        'token': token
    }, '登录成功')

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    """获取当前用户信息"""
    user = User.query.get(current_user_id)
    if not user:
        return business_error_response(ResponseCode.NOT_FOUND, '用户不存在')
    return success_response(user.to_dict())

# 用户管理API
@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户（管理员接口）"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    if User.query.filter_by(username=data['username']).first():
        return business_error_response(ResponseCode.USERNAME_EXISTS)
    
    if User.query.filter_by(email=data['email']).first():
        return business_error_response(ResponseCode.EMAIL_EXISTS)
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return success_response(user.to_dict(), '用户创建成功')

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    """获取用户信息"""
    user = User.query.get(user_id)
    if not user:
        return business_error_response(ResponseCode.NOT_FOUND, '用户不存在')
    return success_response(user.to_dict())

# 投资组合相关API
@api_bp.route('/portfolios', methods=['GET'])
@token_required
def get_portfolios(current_user_id):
    """获取投资组合列表"""
    user_id = request.args.get('user_id', type=int) or current_user_id
    portfolios = Portfolio.query.filter_by(user_id=user_id).all()
    return success_response([p.to_dict() for p in portfolios])

@api_bp.route('/portfolios', methods=['POST'])
@token_required
def create_portfolio(current_user_id):
    """创建投资组合"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('user_id'):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    portfolio = Portfolio(
        name=data['name'],
        description=data.get('description', ''),
        user_id=data['user_id'],
        initial_capital=data.get('initial_capital', 0),
        cash_balance=data.get('initial_capital', 0)
    )
    
    db.session.add(portfolio)
    db.session.commit()
    
    return success_response(portfolio.to_dict(), '投资组合创建成功')

@api_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
@token_required
def get_portfolio(current_user_id, portfolio_id):
    """获取投资组合详情"""
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
    return success_response(portfolio.to_dict())

@api_bp.route('/portfolios/<int:portfolio_id>/positions', methods=['GET'])
@token_required
def get_portfolio_positions(current_user_id, portfolio_id):
    """获取投资组合持仓"""
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
    positions = portfolio.positions.all()
    return success_response([p.to_dict() for p in positions])

# 交易相关API
@api_bp.route('/trades', methods=['GET'])
@token_required
def get_trades(current_user_id):
    """获取交易记录"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    symbol = request.args.get('symbol')
    limit = request.args.get('limit', 100, type=int)
    
    query = Trade.query
    if portfolio_id:
        # 验证投资组合属于当前用户
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio or portfolio.user_id != current_user_id:
            return business_error_response(ResponseCode.PORTFOLIO_NOT_FOUND)
        query = query.filter_by(portfolio_id=portfolio_id)
    else:
        # 如果没有指定投资组合，只返回当前用户的交易
        user_portfolios = Portfolio.query.filter_by(user_id=current_user_id).all()
        portfolio_ids = [p.id for p in user_portfolios]
        query = query.filter(Trade.portfolio_id.in_(portfolio_ids))
    
    if symbol:
        query = query.filter_by(symbol=symbol)
    
    trades = query.order_by(Trade.executed_at.desc()).limit(limit).all()
    return success_response([t.to_dict() for t in trades])

@api_bp.route('/trades', methods=['POST'])
@token_required
def create_trade(current_user_id):
    """创建交易"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['portfolio_id', 'symbol', 'side', 'quantity', 'price']):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    from services.trading_service import TradingService
    trading_service = TradingService()
    try:
        trade = trading_service.execute_trade(
            portfolio_id=data['portfolio_id'],
            symbol=data['symbol'],
            side=data['side'],
            quantity=data['quantity'],
            price=data['price'],
            strategy_execution_id=data.get('strategy_execution_id')
        )
        return success_response(trade.to_dict(), '交易创建成功')
    except Exception as e:
        return business_error_response(ResponseCode.BAD_REQUEST, str(e))

# 策略相关API
@api_bp.route('/strategies', methods=['GET'])
@token_required
def get_strategies(current_user_id):
    """获取策略列表"""
    user_id = request.args.get('user_id', type=int) or current_user_id
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    return success_response([s.to_dict() for s in strategies])

@api_bp.route('/strategies', methods=['POST'])
@token_required
def create_strategy(current_user_id):
    """创建策略"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'user_id', 'strategy_type']):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    strategy = Strategy(
        name=data['name'],
        description=data.get('description', ''),
        user_id=data['user_id'],
        strategy_type=data['strategy_type']
    )
    
    if data.get('parameters'):
        strategy.set_parameters(data['parameters'])
    
    db.session.add(strategy)
    db.session.commit()
    
    return success_response(strategy.to_dict(), '策略创建成功')

@api_bp.route('/strategies/<int:strategy_id>/execute', methods=['POST'])
@token_required
def execute_strategy(current_user_id, strategy_id):
    """执行策略"""
    data = request.get_json()
    
    if not data or not data.get('portfolio_id'):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    strategy = Strategy.query.get(strategy_id)
    if not strategy:
        return business_error_response(ResponseCode.NOT_FOUND, '策略不存在')
    
    # 创建策略执行记录
    from models.strategy import StrategyExecution
    execution = StrategyExecution(
        strategy_id=strategy_id,
        portfolio_id=data['portfolio_id'],
        start_time=data.get('start_time'),
        initial_capital=data.get('initial_capital', 0),
        current_value=data.get('initial_capital', 0)
    )
    
    db.session.add(execution)
    db.session.commit()
    
    return success_response(execution.to_dict(), '策略执行成功')

# 市场数据相关API - 已移动到文件末尾，避免重复定义

@api_bp.route('/market-data/<symbol>/latest', methods=['GET'])
@token_required
def get_latest_market_data(current_user_id, symbol):
    """获取最新市场数据"""
    from services.data_service import DataService
    data_service = DataService()
    data = data_service.get_latest_price(symbol)
    
    return success_response(data)

# 风险管理相关API
@api_bp.route('/risk-rules', methods=['GET'])
@token_required
def get_risk_rules(current_user_id):
    """获取风险规则列表"""
    rules = RiskRule.query.filter_by(is_active=True).all()
    return success_response([r.to_dict() for r in rules])

@api_bp.route('/risk-rules', methods=['POST'])
@token_required
def create_risk_rule(current_user_id):
    """创建风险规则"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'rule_type']):
        return business_error_response(ResponseCode.MISSING_FIELDS)
    
    rule = RiskRule(
        name=data['name'],
        description=data.get('description', ''),
        rule_type=data['rule_type']
    )
    
    if data.get('parameters'):
        rule.set_parameters(data['parameters'])
    
    db.session.add(rule)
    db.session.commit()
    
    return success_response(rule.to_dict(), '风险规则创建成功')

@api_bp.route('/risk-alerts', methods=['GET'])
@token_required
def get_risk_alerts(current_user_id):
    """获取风险警报"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    is_resolved = request.args.get('is_resolved', type=bool)
    
    query = RiskRule.query.join(RiskRule.alerts)
    if portfolio_id:
        query = query.filter_by(portfolio_id=portfolio_id)
    if is_resolved is not None:
        query = query.filter_by(is_resolved=is_resolved)
    
    alerts = query.all()
    return success_response([a.to_dict() for a in alerts])

# 统计和仪表板API
@api_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user_id):
    """获取仪表板统计数据"""
    # 获取用户的所有投资组合
    portfolios = Portfolio.query.filter_by(user_id=current_user_id).all()
    
    # 计算总资产价值
    total_value = sum(p.get_total_value() for p in portfolios)
    total_pnl = sum(p.get_total_pnl() for p in portfolios)
    total_pnl_percentage = (total_pnl / sum(p.initial_capital for p in portfolios) * 100) if portfolios else 0
    
    # 获取交易统计
    total_trades = sum(len(p.trades) for p in portfolios)
    winning_trades = sum(len([t for t in p.trades if t.pnl > 0]) for p in portfolios)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # 获取活跃策略数量
    active_strategies = Strategy.query.filter_by(user_id=current_user_id, is_active=True).count()
    
    # 获取风险警报数量
    from models.risk_management import RiskAlert
    active_alerts = RiskAlert.query.filter_by(is_resolved=False).count()
    
    return success_response({
        'total_value': total_value,
        'total_pnl': total_pnl,
        'total_pnl_percentage': total_pnl_percentage,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate': win_rate,
        'active_strategies': active_strategies,
        'active_alerts': active_alerts,
        'portfolios_count': len(portfolios)
    })

@api_bp.route('/dashboard/performance', methods=['GET'])
@token_required
def get_performance_data(current_user_id):
    """获取表现数据"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    from datetime import datetime, timedelta
    from services.trading_service import TradingService
    
    if portfolio_id:
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
        portfolios = [portfolio]
    else:
        portfolios = Portfolio.query.filter_by(user_id=current_user_id).all()
    
    trading_service = TradingService()
    performance_data = []
    
    for portfolio in portfolios:
        perf = trading_service.get_portfolio_performance(
            portfolio.id,
            start_date=datetime.now() - timedelta(days=days)
        )
        performance_data.append({
            'portfolio_id': portfolio.id,
            'portfolio_name': portfolio.name,
            **perf
        })
    
    return success_response(performance_data)

@api_bp.route('/dashboard/positions', methods=['GET'])
@token_required
def get_positions_summary(current_user_id):
    """获取持仓汇总"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    
    if portfolio_id:
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
        portfolios = [portfolio]
    else:
        portfolios = Portfolio.query.filter_by(user_id=current_user_id).all()
    
    positions_summary = []
    for portfolio in portfolios:
        positions = portfolio.positions.all()
        for position in positions:
            positions_summary.append({
                'portfolio_id': portfolio.id,
                'portfolio_name': portfolio.name,
                'symbol': position.symbol,
                'quantity': float(position.quantity),
                'average_price': float(position.average_price),
                'current_price': float(position.current_price),
                'value': position.get_value(),
                'unrealized_pnl': position.get_unrealized_pnl(),
                'unrealized_pnl_percentage': (position.get_unrealized_pnl() / (float(position.quantity) * float(position.average_price)) * 100) if position.quantity > 0 else 0
            })
    
    return success_response(positions_summary)

@api_bp.route('/dashboard/recent-trades', methods=['GET'])
@token_required
def get_recent_trades(current_user_id):
    """获取最近交易"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if portfolio_id:
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
        portfolios = [portfolio]
    else:
        portfolios = Portfolio.query.filter_by(user_id=current_user_id).all()
    
    all_trades = []
    for portfolio in portfolios:
        trades = portfolio.trades.order_by(Trade.executed_at.desc()).limit(limit).all()
        for trade in trades:
            all_trades.append({
                'portfolio_id': portfolio.id,
                'portfolio_name': portfolio.name,
                **trade.to_dict()
            })
    
    # 按时间排序并限制数量
    all_trades.sort(key=lambda x: x['executed_at'], reverse=True)
    return success_response(all_trades[:limit])

# 健康检查
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return success_response({
        'status': 'healthy',
        'message': '量化交易系统API服务正常运行',
        'version': '1.0.0'
    })

# 系统信息
@api_bp.route('/info', methods=['GET'])
def system_info():
    """系统信息接口"""
    return success_response({
        'name': '量化交易系统',
        'version': '1.0.0',
        'description': '基于Flask的个人量化交易系统API',
        'features': [
            '用户管理',
            '投资组合管理',
            '交易执行',
            '策略管理',
            '市场数据获取',
            '风险管理'
        ],
        'endpoints': {
            'users': '/api/users',
            'portfolios': '/api/portfolios',
            'trades': '/api/trades',
            'strategies': '/api/strategies',
            'market_data': '/api/market-data',
            'risk': '/api/risk-rules'
        }
    })

# 错误处理
@api_bp.errorhandler(404)
def not_found(error):
    return business_error_response(ResponseCode.NOT_FOUND)

@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return system_error_response(ResponseCode.INTERNAL_ERROR)

@api_bp.errorhandler(400)
def bad_request(error):
    return business_error_response(ResponseCode.BAD_REQUEST)

@api_bp.errorhandler(401)
def unauthorized(error):
    return business_error_response(ResponseCode.UNAUTHORIZED)

# =====================================================
# 数据来源管理API
# =====================================================

@api_bp.route('/data-sources', methods=['GET'])
@token_required
def get_data_sources(current_user_id):
    """获取数据来源列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        provider_type = request.args.get('provider_type', '')
        is_active = request.args.get('is_active', type=bool)
        
        # 构建查询
        query = DataSource.query
        
        if provider_type:
            query = query.filter_by(provider_type=provider_type)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        data_sources = [ds.to_dict() for ds in pagination.items]
        
        return success_response({
            'data_sources': data_sources,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_DATA_ERROR, f'获取数据来源列表失败: {str(e)}')

@api_bp.route('/data-sources', methods=['POST'])
@token_required
def create_data_source(current_user_id):
    """创建数据来源"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['name', 'uri', 'provider_type']):
            return business_error_response(ResponseCode.MISSING_FIELDS)
        
        # 检查名称是否已存在
        if DataSource.query.filter_by(name=data['name']).first():
            return business_error_response(ResponseCode.DATA_SOURCE_EXISTS)
        
        data_source = DataSource(
            name=data['name'],
            uri=data['uri'],
            description=data.get('description', ''),
            provider_type=data['provider_type'],
            is_active=data.get('is_active', True),
            priority=data.get('priority', 1),
            config=data.get('config', {})
        )
        
        if data.get('config'):
            data_source.set_config(data['config'])
        
        db.session.add(data_source)
        db.session.commit()
        
        return success_response(data_source.to_dict(), '数据来源创建成功')
        
    except Exception as e:
        return system_error_response(ResponseCode.CREATE_ERROR, f'创建数据来源失败: {str(e)}')

@api_bp.route('/data-sources/<int:data_source_id>', methods=['GET'])
@token_required
def get_data_source(current_user_id, data_source_id):
    """获取数据来源详情"""
    try:
        data_source = DataSource.query.get(data_source_id)
        if not data_source:
            return business_error_response(ResponseCode.NOT_FOUND, '数据来源不存在')
        return success_response(data_source.to_dict())
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_DATA_ERROR, f'获取数据来源详情失败: {str(e)}')

@api_bp.route('/data-sources/<int:data_source_id>', methods=['PUT'])
@token_required
def update_data_source(current_user_id, data_source_id):
    """更新数据来源"""
    try:
        data_source = DataSource.query.get(data_source_id)
        if not data_source:
            return business_error_response(ResponseCode.NOT_FOUND, '数据来源不存在')
        data = request.get_json()
        
        if not data:
            return business_error_response(ResponseCode.MISSING_FIELDS)
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否与其他数据来源冲突
            existing = DataSource.query.filter_by(name=data['name']).first()
            if existing and existing.id != data_source_id:
                return business_error_response(ResponseCode.DATA_SOURCE_EXISTS)
            data_source.name = data['name']
        
        if 'uri' in data:
            data_source.uri = data['uri']
        
        if 'description' in data:
            data_source.description = data['description']
        
        if 'provider_type' in data:
            data_source.provider_type = data['provider_type']
        
        if 'is_active' in data:
            data_source.is_active = data['is_active']
        
        if 'priority' in data:
            data_source.priority = data['priority']
        
        if 'config' in data:
            data_source.set_config(data['config'])
        
        db.session.commit()
        
        return success_response(data_source.to_dict(), '数据来源更新成功')
        
    except Exception as e:
        return system_error_response(ResponseCode.UPDATE_ERROR, f'更新数据来源失败: {str(e)}')

@api_bp.route('/data-sources/<int:data_source_id>', methods=['DELETE'])
@token_required
def delete_data_source(current_user_id, data_source_id):
    """删除数据来源"""
    try:
        data_source = DataSource.query.get(data_source_id)
        if not data_source:
            return business_error_response(ResponseCode.NOT_FOUND, '数据来源不存在')
        
        # 检查是否有关联的symbols或market_data
        symbol_count = Symbol.query.filter_by(data_source_id=data_source_id).count()
        market_data_count = MarketData.query.filter_by(data_source_id=data_source_id).count()
        
        if symbol_count > 0 or market_data_count > 0:
            return business_error_response(ResponseCode.DATA_SOURCE_IN_USE, 
                f'数据来源正在使用中，无法删除。关联的symbols: {symbol_count}, market_data: {market_data_count}')
        
        db.session.delete(data_source)
        db.session.commit()
        
        return success_response(None, '数据来源删除成功')
        
    except Exception as e:
        return system_error_response(ResponseCode.DELETE_ERROR, f'删除数据来源失败: {str(e)}')

@api_bp.route('/data-sources/<int:data_source_id>/statistics', methods=['GET'])
@token_required
def get_data_source_statistics(current_user_id, data_source_id):
    """获取数据来源统计信息"""
    try:
        data_source = DataSource.query.get(data_source_id)
        if not data_source:
            return business_error_response(ResponseCode.NOT_FOUND, '数据来源不存在')
        
        # 统计关联的symbols和market_data
        symbol_count = Symbol.query.filter_by(data_source_id=data_source_id).count()
        market_data_count = MarketData.query.filter_by(data_source_id=data_source_id).count()
        
        # 获取最新的市场数据时间
        latest_data = MarketData.query.filter_by(data_source_id=data_source_id)\
            .order_by(MarketData.timestamp.desc()).first()
        
        # 获取数据来源性能统计
        from sqlalchemy import func
        stats = db.session.query(
            func.count(MarketData.id).label('total_records'),
            func.count(func.distinct(MarketData.symbol_id)).label('unique_symbols'),
            func.min(MarketData.timestamp).label('earliest_data'),
            func.max(MarketData.timestamp).label('latest_data')
        ).filter_by(data_source_id=data_source_id).first()
        
        return success_response({
            'data_source': data_source.to_dict(),
            'symbol_count': symbol_count,
            'market_data_count': market_data_count,
            'latest_data_time': latest_data.timestamp.isoformat() if latest_data else None,
            'statistics': {
                'total_records': stats.total_records or 0,
                'unique_symbols': stats.unique_symbols or 0,
                'earliest_data': stats.earliest_data.isoformat() if stats.earliest_data else None,
                'latest_data': stats.latest_data.isoformat() if stats.latest_data else None
            }
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_STATS_ERROR, f'获取数据来源统计失败: {str(e)}')

@api_bp.route('/data-sources/test/<int:data_source_id>', methods=['POST'])
@token_required
def test_data_source(current_user_id, data_source_id):
    """测试数据来源连接"""
    try:
        data_source = DataSource.query.get(data_source_id)
        if not data_source:
            return business_error_response(ResponseCode.NOT_FOUND, '数据来源不存在')
        
        # 根据provider_type测试连接
        if data_source.provider_type == 'akshare':
            from services.data_sources.akshare_data_source import AkshareDataSource
            test_source = AkshareDataSource()
            result = test_source.test_connection()
        elif data_source.provider_type == 'yahoo':
            from services.data_sources.yahoo_data_source import YahooDataSource
            test_source = YahooDataSource()
            result = test_source.test_connection()
        elif data_source.provider_type == 'alpha_vantage':
            from services.data_sources.alpha_vantage_data_source import AlphaVantageDataSource
            test_source = AlphaVantageDataSource()
            result = test_source.test_connection()
        else:
            # 尝试使用通用方法
            try:
                from services.data_sources import create_data_source
                test_source = create_data_source(data_source.provider_type)
                result = test_source.test_connection()
            except Exception as e:
                result = {'status': 'error', 'message': f'无法创建 {data_source.provider_type} 数据源: {str(e)}'}
        
        return success_response({
            'data_source_id': data_source_id,
            'provider_type': data_source.provider_type,
            'test_result': result
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.TEST_ERROR, f'测试数据来源失败: {str(e)}')

@api_bp.route('/data-sources/auto-create', methods=['POST'])
@token_required
def auto_create_data_sources(current_user_id):
    """自动创建所有支持的数据来源"""
    try:
        data = request.get_json() or {}
        provider_types = data.get('provider_types', ['akshare', 'yahoo', 'alpha_vantage', 'tushare', 'eastmoney'])
        
        results = []
        
        for provider_type in provider_types:
            try:
                # 检查是否已存在
                existing = DataSource.query.filter_by(provider_type=provider_type).first()
                if existing:
                    results.append({
                        'provider_type': provider_type,
                        'status': 'exists',
                        'data_source_id': existing.id,
                        'message': f'{provider_type} 数据来源已存在'
                    })
                    continue
                
                # 尝试创建数据源并自动创建记录
                from services.data_sources import create_data_source
                data_source = create_data_source(provider_type)
                
                if data_source:
                    # 创建数据来源记录
                    data_source_info = data_source.create_data_source_record()
                    if data_source_info:
                        results.append({
                            'provider_type': provider_type,
                            'status': 'created',
                            'data_source_id': data_source_info['id'],
                            'message': f'{provider_type} 数据来源创建成功'
                        })
                    else:
                        results.append({
                            'provider_type': provider_type,
                            'status': 'failed',
                            'message': f'{provider_type} 数据来源记录创建失败'
                        })
                else:
                    results.append({
                        'provider_type': provider_type,
                        'status': 'unsupported',
                        'message': f'{provider_type} 数据源不支持'
                    })
                    
            except Exception as e:
                results.append({
                    'provider_type': provider_type,
                    'status': 'error',
                    'message': f'{provider_type} 创建失败: {str(e)}'
                })
        
        return success_response({
            'results': results,
            'total': len(provider_types),
            'success_count': len([r for r in results if r['status'] in ['created', 'exists']])
        }, '数据来源自动创建完成')
        
    except Exception as e:
        return system_error_response(ResponseCode.CREATE_ERROR, f'自动创建数据来源失败: {str(e)}')

# =====================================================
# 市场数据相关API
# =====================================================

@api_bp.route('/market-data/sources', methods=['GET'])
@token_required
def get_market_data_sources(current_user_id):
    """获取可用的数据源列表"""
    try:
        from services.data_sources import list_available_sources
        
        sources = list_available_sources()
        return success_response({
            'sources': sources,
            'default': 'akshare'
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.DATA_SOURCE_ERROR, f'获取数据源失败: {str(e)}')

@api_bp.route('/market-data/sync/symbols', methods=['POST'])
@token_required
def sync_symbols(current_user_id):
    """同步股票列表"""
    try:
        data = request.get_json() or {}
        market = data.get('market', 'A股')
        data_source = data.get('data_source', 'akshare')
        
        # 初始化市场数据服务
        market_service = MarketDataService(data_source)
        
        if not market_service.initialize_data_source():
            return system_error_response(ResponseCode.DATA_SOURCE_INIT_ERROR)
        
        # 同步股票列表
        synced_count = market_service.sync_symbols(market)
        
        return success_response({
            'synced_count': synced_count,
            'market': market,
            'data_source': data_source
        }, f'股票列表同步完成')
        
    except Exception as e:
        return system_error_response(ResponseCode.SYNC_ERROR, f'同步股票列表失败: {str(e)}')

@api_bp.route('/market-data/sync/index-components', methods=['POST'])
@token_required
def sync_index_components(current_user_id):
    """同步指数成分股"""
    try:
        data = request.get_json()
        
        if not data or 'index_code' not in data:
            return business_error_response(ResponseCode.MISSING_INDEX_CODE)
        
        index_code = data['index_code']
        data_source = data.get('data_source', 'akshare')
        
        # 初始化市场数据服务
        market_service = MarketDataService(data_source)
        
        if not market_service.initialize_data_source():
            return system_error_response(ResponseCode.DATA_SOURCE_INIT_ERROR)
        
        # 同步指数成分股
        synced_count = market_service.sync_index_components(index_code)
        
        return success_response({
            'synced_count': synced_count,
            'index_code': index_code,
            'data_source': data_source
        }, f'{index_code}成分股同步完成')
        
    except Exception as e:
        return system_error_response(ResponseCode.SYNC_ERROR, f'同步指数成分股失败: {str(e)}')

@api_bp.route('/market-data/fetch/latest', methods=['POST'])
@token_required
def fetch_latest_data(current_user_id):
    """手动获取最新行情数据"""
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', [])
        data_source = data.get('data_source', 'akshare')
        
        # 如果没有指定股票，获取所有活跃股票
        if not symbols:
            active_symbols = Symbol.query.filter_by(is_active=True).all()
            symbols = [s.symbol for s in active_symbols]
        
        if not symbols:
            return business_error_response(ResponseCode.NO_SYMBOLS)
        
        # 初始化市场数据服务
        market_service = MarketDataService(data_source)
        
        if not market_service.initialize_data_source():
            return system_error_response(ResponseCode.DATA_SOURCE_INIT_ERROR)
        
        # 批量获取最新数据
        results = market_service.batch_fetch_latest_data(symbols)
        
        total_updated = sum(results.values())
        successful_symbols = len([k for k, v in results.items() if v > 0])
        
        return success_response({
            'total_symbols': len(symbols),
            'successful_symbols': successful_symbols,
            'total_records': total_updated,
            'results': results,
            'data_source': data_source
        }, '最新行情数据获取完成')
        
    except Exception as e:
        return system_error_response(ResponseCode.FETCH_ERROR, f'获取最新行情数据失败: {str(e)}')

@api_bp.route('/market-data/fetch/historical', methods=['POST'])
@token_required
def fetch_historical_data(current_user_id):
    """获取指定股票的历史数据"""
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return business_error_response(ResponseCode.MISSING_SYMBOL)
        
        symbol = data['symbol']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        force_update = data.get('force_update', False)
        data_source = data.get('data_source', 'akshare')
        
        # 转换日期格式
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 初始化市场数据服务
        market_service = MarketDataService(data_source)
        
        if not market_service.initialize_data_source():
            return system_error_response(ResponseCode.DATA_SOURCE_INIT_ERROR)
        
        # 获取历史数据
        count = market_service.fetch_historical_data(
            symbol, start_date, end_date, force_update
        )
        
        return success_response({
            'symbol': symbol,
            'records_added': count,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'force_update': force_update,
            'data_source': data_source
        }, f'{symbol}历史数据获取完成')
        
    except Exception as e:
        return system_error_response(ResponseCode.FETCH_ERROR, f'获取历史数据失败: {str(e)}')

@api_bp.route('/market-data/<symbol>', methods=['GET'])
@token_required
def get_market_data(current_user_id, symbol):
    """获取股票的市场数据"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # 转换日期格式
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 初始化市场数据服务
        market_service = MarketDataService()
        
        # 获取市场数据
        data = market_service.get_market_data(symbol, start_date, end_date, limit)
        
        return success_response({
            'symbol': symbol,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_DATA_ERROR, f'获取市场数据失败: {str(e)}')

@api_bp.route('/market-data/symbols', methods=['GET'])
@token_required
def get_symbols(current_user_id):
    """获取股票列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        exchange = request.args.get('exchange', '')
        
        # 构建查询
        query = Symbol.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(
                db.or_(
                    Symbol.symbol.contains(search),
                    Symbol.name.contains(search)
                )
            )
        
        if exchange:
            query = query.filter_by(exchange=exchange)
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        symbols = [symbol.to_dict() for symbol in pagination.items]
        
        return success_response({
            'symbols': symbols,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_SYMBOLS_ERROR, f'获取股票列表失败: {str(e)}')

@api_bp.route('/market-data/statistics', methods=['GET'])
@token_required
def get_market_data_statistics(current_user_id):
    """获取市场数据统计信息"""
    try:
        market_service = MarketDataService()
        stats = market_service.get_data_statistics()
        
        return success_response(stats)
        
    except Exception as e:
        return system_error_response(ResponseCode.GET_STATS_ERROR, f'获取统计信息失败: {str(e)}')

@api_bp.route('/market-data/health', methods=['GET'])
@token_required
def market_data_health_check(current_user_id):
    """市场数据服务健康检查"""
    try:
        market_service = MarketDataService()
        health_info = market_service.health_check()
        
        return success_response(health_info)
        
    except Exception as e:
        return system_error_response(ResponseCode.HEALTH_CHECK_ERROR, f'健康检查失败: {str(e)}')
