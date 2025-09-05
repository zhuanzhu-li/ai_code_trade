from models import db, Portfolio, Position, Trade, Order
from services.risk_service import RiskService
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TradingService:
    """交易服务类"""
    
    def __init__(self):
        self.risk_service = RiskService()
    
    def execute_trade(self, portfolio_id, symbol, side, quantity, price, strategy_execution_id=None):
        """执行交易"""
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        
        # 风险检查
        trade_data = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price
        }
        
        risk_violations = self.risk_service.check_trade_risk(portfolio, trade_data)
        if risk_violations:
            raise Exception(f"风险检查失败: {', '.join(risk_violations)}")
        
        # 计算交易金额和手续费
        amount = Decimal(str(quantity)) * Decimal(str(price))
        fee = self._calculate_fee(amount)
        net_amount = amount - fee
        
        # 检查资金是否充足
        if side == 'buy':
            if portfolio.cash_balance < net_amount:
                raise Exception("资金不足")
        elif side == 'sell':
            position = portfolio.positions.filter_by(symbol=symbol).first()
            if not position or position.quantity < quantity:
                raise Exception("持仓不足")
        
        # 创建交易记录
        trade = Trade(
            portfolio_id=portfolio_id,
            strategy_execution_id=strategy_execution_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            amount=amount,
            fee=fee,
            status='completed'
        )
        
        db.session.add(trade)
        
        # 更新投资组合
        self._update_portfolio(portfolio, trade)
        
        # 更新或创建持仓
        self._update_position(portfolio, trade)
        
        db.session.commit()
        
        logger.info(f"交易执行成功: {symbol} {side} {quantity}@{price}")
        
        return trade
    
    def create_order(self, portfolio_id, symbol, side, order_type, quantity, price=None, stop_price=None, strategy_execution_id=None):
        """创建订单"""
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        
        order = Order(
            portfolio_id=portfolio_id,
            strategy_execution_id=strategy_execution_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 如果是市价单，立即执行
        if order_type == 'market':
            self._execute_market_order(order)
        
        return order
    
    def cancel_order(self, order_id):
        """取消订单"""
        order = Order.query.get_or_404(order_id)
        
        if order.status != 'pending':
            raise Exception("只能取消待处理的订单")
        
        order.cancel_order()
        db.session.commit()
        
        return order
    
    def _calculate_fee(self, amount):
        """计算手续费"""
        # 简化实现，实际应该根据交易所规则计算
        fee_rate = Decimal('0.001')  # 0.1%
        return amount * fee_rate
    
    def _update_portfolio(self, portfolio, trade):
        """更新投资组合"""
        if trade.side == 'buy':
            portfolio.cash_balance -= trade.get_net_amount()
        else:  # sell
            portfolio.cash_balance += trade.get_net_amount()
        
        # 更新当前价值
        portfolio.current_value = portfolio.get_total_value()
    
    def _update_position(self, portfolio, trade):
        """更新持仓"""
        position = portfolio.positions.filter_by(symbol=trade.symbol).first()
        
        if trade.side == 'buy':
            if position:
                position.add_quantity(trade.quantity, trade.price)
            else:
                position = Position(
                    portfolio_id=portfolio.id,
                    symbol=trade.symbol,
                    quantity=trade.quantity,
                    average_price=trade.price,
                    current_price=trade.price
                )
                db.session.add(position)
        else:  # sell
            if position:
                # 计算已实现盈亏
                cost_basis = position.average_price * trade.quantity
                realized_pnl = (trade.price - position.average_price) * trade.quantity
                position.realized_pnl += realized_pnl
                
                position.reduce_quantity(trade.quantity)
                
                # 如果持仓为0，删除持仓记录
                if position.quantity == 0:
                    db.session.delete(position)
    
    def _execute_market_order(self, order):
        """执行市价单"""
        try:
            # 获取当前市场价格
            from services.data_service import DataService
            data_service = DataService()
            current_price = data_service.get_latest_price(order.symbol)
            
            if not current_price:
                raise Exception("无法获取当前价格")
            
            # 执行交易
            trade = self.execute_trade(
                portfolio_id=order.portfolio_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=current_price['price'],
                strategy_execution_id=order.strategy_execution_id
            )
            
            # 更新订单状态
            order.fill_order(order.quantity, current_price['price'])
            db.session.commit()
            
        except Exception as e:
            logger.error(f"市价单执行失败: {e}")
            order.status = 'rejected'
            db.session.commit()
            raise e
    
    def get_portfolio_performance(self, portfolio_id, start_date=None, end_date=None):
        """获取投资组合表现"""
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        
        # 获取交易记录
        trades_query = portfolio.trades
        if start_date:
            trades_query = trades_query.filter(Trade.executed_at >= start_date)
        if end_date:
            trades_query = trades_query.filter(Trade.executed_at <= end_date)
        
        trades = trades_query.all()
        
        # 计算表现指标
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        total_pnl = sum(t.pnl for t in trades)
        total_fees = sum(t.fee for t in trades)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_pnl': float(total_pnl),
            'total_fees': float(total_fees),
            'net_pnl': float(total_pnl - total_fees)
        }
