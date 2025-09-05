import unittest
from app import create_app
from models import db, User, Portfolio, Position, Trade
from datetime import datetime

class TestModels(unittest.TestCase):
    """模型测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_portfolio_creation(self):
        """测试投资组合创建"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        portfolio = Portfolio(
            name='Test Portfolio',
            user_id=user.id,
            initial_capital=10000,
            cash_balance=10000
        )
        
        db.session.add(portfolio)
        db.session.commit()
        
        self.assertEqual(portfolio.name, 'Test Portfolio')
        self.assertEqual(portfolio.initial_capital, 10000)
        self.assertEqual(portfolio.get_total_value(), 10000)
    
    def test_position_management(self):
        """测试持仓管理"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        portfolio = Portfolio(
            name='Test Portfolio',
            user_id=user.id,
            initial_capital=10000,
            cash_balance=10000
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # 创建持仓
        position = Position(
            portfolio_id=portfolio.id,
            symbol='AAPL',
            quantity=10,
            average_price=150.0,
            current_price=155.0
        )
        db.session.add(position)
        db.session.commit()
        
        self.assertEqual(position.get_value(), 1550.0)
        self.assertEqual(position.get_unrealized_pnl(), 50.0)
        
        # 更新价格
        position.update_price(160.0)
        self.assertEqual(position.get_unrealized_pnl(), 100.0)
    
    def test_trade_execution(self):
        """测试交易执行"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        portfolio = Portfolio(
            name='Test Portfolio',
            user_id=user.id,
            initial_capital=10000,
            cash_balance=10000
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # 执行买入交易
        trade = Trade(
            portfolio_id=portfolio.id,
            symbol='AAPL',
            side='buy',
            quantity=10,
            price=150.0,
            amount=1500.0,
            fee=1.5
        )
        db.session.add(trade)
        db.session.commit()
        
        self.assertEqual(trade.get_net_amount(), 1498.5)
        self.assertEqual(trade.symbol, 'AAPL')

if __name__ == '__main__':
    unittest.main()
