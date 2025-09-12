"""
使用Flask-RESTX重构的API路由
提供自动生成的Swagger文档
"""

from flask import request
from flask_restx import Resource
from models import db, User, Portfolio, Strategy, Trade, MarketData, RiskRule, Symbol, DataSource
from utils.auth import token_required
from utils.response import (
    success_response, error_response, business_error_response, system_error_response,
    ResponseCode, ResponseMessage
)
from services.market_data_service import MarketDataService
from services.trading_service import TradingService
from app.api_docs import (
    api, auth_ns, users_ns, portfolios_ns, trades_ns, strategies_ns, 
    market_data_ns, risk_ns, dashboard_ns, system_ns,
    user_model, user_register_model, user_login_model,
    portfolio_model, portfolio_create_model,
    trade_model, trade_create_model,
    strategy_model, strategy_create_model, strategy_execute_model,
    market_data_model, symbol_model,
    risk_rule_model, risk_rule_create_model,
    dashboard_stats_model, success_response_model, error_response_model
)

# ==================== 用户认证API ====================

@auth_ns.route('/register')
class UserRegister(Resource):
    @auth_ns.expect(user_register_model)
    @auth_ns.marshal_with(success_response_model, code=200, description='注册成功')
    @auth_ns.marshal_with(error_response_model, code=400, description='注册失败')
    def post(self):
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
        
        # 确保所有数据都是JSON可序列化的
        user_data = user.to_dict()
        response_data = {
            'user': user_data,
            'token': str(token)  # 确保token是字符串
        }
        
        return success_response(response_data, '注册成功')

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(user_login_model)
    @auth_ns.marshal_with(success_response_model, code=200, description='登录成功')
    @auth_ns.marshal_with(error_response_model, code=400, description='登录失败')
    def post(self):
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
        
        # 确保所有数据都是JSON可序列化的
        user_data = user.to_dict()
        response_data = {
            'user': user_data,
            'token': str(token)  # 确保token是字符串
        }
        
        return success_response(response_data, '登录成功')

@auth_ns.route('/me')
class CurrentUser(Resource):
    @auth_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @auth_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
        """获取当前用户信息"""
        user = User.query.get(current_user_id)
        if not user:
            return business_error_response(ResponseCode.NOT_FOUND, '用户不存在')
        return success_response(user.to_dict())

# ==================== 用户管理API ====================

@users_ns.route('')
class UserList(Resource):
    @users_ns.expect(user_register_model)
    @users_ns.marshal_with(success_response_model, code=200, description='创建成功')
    @users_ns.marshal_with(error_response_model, code=400, description='创建失败')
    def post(self):
        """创建用户（管理员功能）"""
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

@users_ns.route('/<int:user_id>')
class UserDetail(Resource):
    @users_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @users_ns.marshal_with(error_response_model, code=404, description='用户不存在')
    @token_required
    def get(self, current_user_id, user_id):
        """获取用户信息"""
        user = User.query.get(user_id)
        if not user:
            return business_error_response(ResponseCode.NOT_FOUND, '用户不存在')
        return success_response(user.to_dict())

# ==================== 投资组合管理API ====================

@portfolios_ns.route('')
class PortfolioList(Resource):
    @portfolios_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @portfolios_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
        """获取投资组合列表"""
        user_id = request.args.get('user_id', type=int) or current_user_id
        portfolios = Portfolio.query.filter_by(user_id=user_id).all()
        return success_response([p.to_dict() for p in portfolios])

    @portfolios_ns.expect(portfolio_create_model)
    @portfolios_ns.marshal_with(success_response_model, code=200, description='创建成功')
    @portfolios_ns.marshal_with(error_response_model, code=400, description='创建失败')
    @token_required
    def post(self, current_user_id):
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

@portfolios_ns.route('/<int:portfolio_id>')
class PortfolioDetail(Resource):
    @portfolios_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @portfolios_ns.marshal_with(error_response_model, code=404, description='投资组合不存在')
    @token_required
    def get(self, current_user_id, portfolio_id):
        """获取投资组合详情"""
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
        return success_response(portfolio.to_dict())

@portfolios_ns.route('/<int:portfolio_id>/positions')
class PortfolioPositions(Resource):
    @portfolios_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @portfolios_ns.marshal_with(error_response_model, code=404, description='投资组合不存在')
    @token_required
    def get(self, current_user_id, portfolio_id):
        """获取投资组合持仓"""
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            return business_error_response(ResponseCode.NOT_FOUND, '投资组合不存在')
        positions = portfolio.positions.all()
        return success_response([p.to_dict() for p in positions])

# ==================== 交易管理API ====================

@trades_ns.route('')
class TradeList(Resource):
    @trades_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @trades_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
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

    @trades_ns.expect(trade_create_model)
    @trades_ns.marshal_with(success_response_model, code=200, description='创建成功')
    @trades_ns.marshal_with(error_response_model, code=400, description='创建失败')
    @token_required
    def post(self, current_user_id):
        """创建交易"""
        data = request.get_json()
        
        if not data or not all(k in data for k in ['portfolio_id', 'symbol', 'side', 'quantity', 'price']):
            return business_error_response(ResponseCode.MISSING_FIELDS)
        
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

# ==================== 策略管理API ====================

@strategies_ns.route('')
class StrategyList(Resource):
    @strategies_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @strategies_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
        """获取策略列表"""
        user_id = request.args.get('user_id', type=int) or current_user_id
        strategies = Strategy.query.filter_by(user_id=user_id).all()
        return success_response([s.to_dict() for s in strategies])

    @strategies_ns.expect(strategy_create_model)
    @strategies_ns.marshal_with(success_response_model, code=200, description='创建成功')
    @strategies_ns.marshal_with(error_response_model, code=400, description='创建失败')
    @token_required
    def post(self, current_user_id):
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

@strategies_ns.route('/<int:strategy_id>/execute')
class StrategyExecute(Resource):
    @strategies_ns.expect(strategy_execute_model)
    @strategies_ns.marshal_with(success_response_model, code=200, description='执行成功')
    @strategies_ns.marshal_with(error_response_model, code=400, description='执行失败')
    @token_required
    def post(self, current_user_id, strategy_id):
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

# ==================== 市场数据API ====================

@market_data_ns.route('/<symbol>/latest')
class LatestMarketData(Resource):
    @market_data_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @market_data_ns.marshal_with(error_response_model, code=500, description='获取失败')
    @token_required
    def get(self, current_user_id, symbol):
        """获取最新市场数据"""
        from services.data_service import DataService
        data_service = DataService()
        data = data_service.get_latest_price(symbol)
        
        return success_response(data)

@market_data_ns.route('/<symbol>')
class MarketData(Resource):
    @market_data_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @market_data_ns.marshal_with(error_response_model, code=500, description='获取失败')
    @token_required
    def get(self, current_user_id, symbol):
        """获取股票的市场数据"""
        try:
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', type=int)
            
            # 转换日期格式
            if start_date:
                from datetime import datetime
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                from datetime import datetime
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

@market_data_ns.route('/symbols')
class SymbolList(Resource):
    @market_data_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @market_data_ns.marshal_with(error_response_model, code=500, description='获取失败')
    @token_required
    def get(self, current_user_id):
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

# ==================== 风险管理API ====================

@risk_ns.route('/rules')
class RiskRuleList(Resource):
    @risk_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @risk_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
        """获取风险规则列表"""
        rules = RiskRule.query.filter_by(is_active=True).all()
        return success_response([r.to_dict() for r in rules])

    @risk_ns.expect(risk_rule_create_model)
    @risk_ns.marshal_with(success_response_model, code=200, description='创建成功')
    @risk_ns.marshal_with(error_response_model, code=400, description='创建失败')
    @token_required
    def post(self, current_user_id):
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

# ==================== 仪表板API ====================

@dashboard_ns.route('/stats')
class DashboardStats(Resource):
    @dashboard_ns.marshal_with(success_response_model, code=200, description='获取成功')
    @dashboard_ns.marshal_with(error_response_model, code=401, description='未授权')
    @token_required
    def get(self, current_user_id):
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

# ==================== 系统API ====================

@system_ns.route('/health')
class HealthCheck(Resource):
    @system_ns.marshal_with(success_response_model, code=200, description='系统健康')
    def get(self):
        """健康检查接口"""
        return success_response({
            'status': 'healthy',
            'message': '量化交易系统API服务正常运行',
            'version': '1.0.0'
        })

@system_ns.route('/info')
class SystemInfo(Resource):
    @system_ns.marshal_with(success_response_model, code=200, description='获取成功')
    def get(self):
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
