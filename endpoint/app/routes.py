from flask import Blueprint, request, jsonify
from models import db, User, Portfolio, Strategy, Trade, MarketData, RiskRule
# 延迟导入以避免循环导入
from utils.auth import token_required
import json

# API蓝图
api_bp = Blueprint('api', __name__)

# 用户认证相关API
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少必要字段', 'code': 'MISSING_FIELDS'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在', 'code': 'USERNAME_EXISTS'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在', 'code': 'EMAIL_EXISTS'}), 400
    
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
    
    return jsonify({
        'user': user.to_dict(),
        'token': token,
        'message': '注册成功'
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '缺少用户名或密码', 'code': 'MISSING_CREDENTIALS'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误', 'code': 'INVALID_CREDENTIALS'}), 401
    
    if not user.is_active:
        return jsonify({'error': '账户已被禁用', 'code': 'ACCOUNT_DISABLED'}), 401
    
    # 生成JWT token
    from utils.auth import generate_token
    token = generate_token(user.id)
    
    return jsonify({
        'user': user.to_dict(),
        'token': token,
        'message': '登录成功'
    })

@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    """获取当前用户信息"""
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict())

# 用户管理API
@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户（管理员接口）"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少必要字段', 'code': 'MISSING_FIELDS'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在', 'code': 'USERNAME_EXISTS'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在', 'code': 'EMAIL_EXISTS'}), 400
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """获取用户信息"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# 投资组合相关API
@api_bp.route('/portfolios', methods=['GET'])
@token_required
def get_portfolios():
    """获取投资组合列表"""
    user_id = request.args.get('user_id', type=int)
    portfolios = Portfolio.query.filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in portfolios])

@api_bp.route('/portfolios', methods=['POST'])
@token_required
def create_portfolio():
    """创建投资组合"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('user_id'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    portfolio = Portfolio(
        name=data['name'],
        description=data.get('description', ''),
        user_id=data['user_id'],
        initial_capital=data.get('initial_capital', 0),
        cash_balance=data.get('initial_capital', 0)
    )
    
    db.session.add(portfolio)
    db.session.commit()
    
    return jsonify(portfolio.to_dict()), 201

@api_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
@token_required
def get_portfolio(portfolio_id):
    """获取投资组合详情"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return jsonify(portfolio.to_dict())

@api_bp.route('/portfolios/<int:portfolio_id>/positions', methods=['GET'])
@token_required
def get_portfolio_positions(portfolio_id):
    """获取投资组合持仓"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    positions = portfolio.positions.all()
    return jsonify([p.to_dict() for p in positions])

# 交易相关API
@api_bp.route('/trades', methods=['GET'])
@token_required
def get_trades():
    """获取交易记录"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    symbol = request.args.get('symbol')
    limit = request.args.get('limit', 100, type=int)
    
    query = Trade.query
    if portfolio_id:
        query = query.filter_by(portfolio_id=portfolio_id)
    if symbol:
        query = query.filter_by(symbol=symbol)
    
    trades = query.order_by(Trade.executed_at.desc()).limit(limit).all()
    return jsonify([t.to_dict() for t in trades])

@api_bp.route('/trades', methods=['POST'])
@token_required
def create_trade():
    """创建交易"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['portfolio_id', 'symbol', 'side', 'quantity', 'price']):
        return jsonify({'error': '缺少必要字段'}), 400
    
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
        return jsonify(trade.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 策略相关API
@api_bp.route('/strategies', methods=['GET'])
@token_required
def get_strategies():
    """获取策略列表"""
    user_id = request.args.get('user_id', type=int)
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    return jsonify([s.to_dict() for s in strategies])

@api_bp.route('/strategies', methods=['POST'])
@token_required
def create_strategy():
    """创建策略"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'user_id', 'strategy_type']):
        return jsonify({'error': '缺少必要字段'}), 400
    
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
    
    return jsonify(strategy.to_dict()), 201

@api_bp.route('/strategies/<int:strategy_id>/execute', methods=['POST'])
@token_required
def execute_strategy(strategy_id):
    """执行策略"""
    data = request.get_json()
    
    if not data or not data.get('portfolio_id'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    strategy = Strategy.query.get_or_404(strategy_id)
    
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
    
    return jsonify(execution.to_dict()), 201

# 市场数据相关API
@api_bp.route('/market-data/<symbol>', methods=['GET'])
@token_required
def get_market_data(symbol):
    """获取市场数据"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 1000, type=int)
    
    from services.data_service import DataService
    data_service = DataService()
    data = data_service.get_market_data(symbol, start_date, end_date, limit)
    
    return jsonify(data)

@api_bp.route('/market-data/<symbol>/latest', methods=['GET'])
@token_required
def get_latest_market_data(symbol):
    """获取最新市场数据"""
    from services.data_service import DataService
    data_service = DataService()
    data = data_service.get_latest_price(symbol)
    
    return jsonify(data)

# 风险管理相关API
@api_bp.route('/risk-rules', methods=['GET'])
@token_required
def get_risk_rules():
    """获取风险规则列表"""
    rules = RiskRule.query.filter_by(is_active=True).all()
    return jsonify([r.to_dict() for r in rules])

@api_bp.route('/risk-rules', methods=['POST'])
@token_required
def create_risk_rule():
    """创建风险规则"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'rule_type']):
        return jsonify({'error': '缺少必要字段'}), 400
    
    rule = RiskRule(
        name=data['name'],
        description=data.get('description', ''),
        rule_type=data['rule_type']
    )
    
    if data.get('parameters'):
        rule.set_parameters(data['parameters'])
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify(rule.to_dict()), 201

@api_bp.route('/risk-alerts', methods=['GET'])
@token_required
def get_risk_alerts():
    """获取风险警报"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    is_resolved = request.args.get('is_resolved', type=bool)
    
    query = RiskRule.query.join(RiskRule.alerts)
    if portfolio_id:
        query = query.filter_by(portfolio_id=portfolio_id)
    if is_resolved is not None:
        query = query.filter_by(is_resolved=is_resolved)
    
    alerts = query.all()
    return jsonify([a.to_dict() for a in alerts])

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
    
    return jsonify({
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
        portfolios = [Portfolio.query.get_or_404(portfolio_id)]
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
    
    return jsonify(performance_data)

@api_bp.route('/dashboard/positions', methods=['GET'])
@token_required
def get_positions_summary(current_user_id):
    """获取持仓汇总"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    
    if portfolio_id:
        portfolios = [Portfolio.query.get_or_404(portfolio_id)]
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
    
    return jsonify(positions_summary)

@api_bp.route('/dashboard/recent-trades', methods=['GET'])
@token_required
def get_recent_trades(current_user_id):
    """获取最近交易"""
    portfolio_id = request.args.get('portfolio_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if portfolio_id:
        portfolios = [Portfolio.query.get_or_404(portfolio_id)]
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
    return jsonify(all_trades[:limit])

# 健康检查
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '量化交易系统API服务正常运行',
        'version': '1.0.0'
    })

# 系统信息
@api_bp.route('/info', methods=['GET'])
def system_info():
    """系统信息接口"""
    return jsonify({
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
    return jsonify({'error': '资源未找到', 'code': 'NOT_FOUND'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': '内部服务器错误', 'code': 'INTERNAL_ERROR'}), 500

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': '请求参数错误', 'code': 'BAD_REQUEST'}), 400

@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': '未授权访问', 'code': 'UNAUTHORIZED'}), 401
