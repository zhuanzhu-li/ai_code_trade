#!/usr/bin/env python3
"""
量化交易系统API客户端示例
"""

import requests
import json
from datetime import datetime, timedelta

class QuantTradingAPIClient:
    """量化交易系统API客户端"""
    
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return None
    
    def register(self, username, email, password):
        """用户注册"""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        result = self._make_request("POST", "/auth/register", data)
        if result and "token" in result:
            self.token = result["token"]
        return result
    
    def login(self, username, password):
        """用户登录"""
        data = {
            "username": username,
            "password": password
        }
        result = self._make_request("POST", "/auth/login", data)
        if result and "token" in result:
            self.token = result["token"]
        return result
    
    def get_current_user(self):
        """获取当前用户信息"""
        return self._make_request("GET", "/auth/me")
    
    def get_system_info(self):
        """获取系统信息"""
        return self._make_request("GET", "/info")
    
    def health_check(self):
        """健康检查"""
        return self._make_request("GET", "/health")
    
    # 投资组合管理
    def create_portfolio(self, name, description="", initial_capital=10000):
        """创建投资组合"""
        data = {
            "name": name,
            "description": description,
            "initial_capital": initial_capital
        }
        return self._make_request("POST", "/portfolios", data)
    
    def get_portfolios(self):
        """获取投资组合列表"""
        return self._make_request("GET", "/portfolios")
    
    def get_portfolio(self, portfolio_id):
        """获取投资组合详情"""
        return self._make_request("GET", f"/portfolios/{portfolio_id}")
    
    def get_portfolio_positions(self, portfolio_id):
        """获取投资组合持仓"""
        return self._make_request("GET", f"/portfolios/{portfolio_id}/positions")
    
    # 交易管理
    def execute_trade(self, portfolio_id, symbol, side, quantity, price, strategy_execution_id=None):
        """执行交易"""
        data = {
            "portfolio_id": portfolio_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price
        }
        if strategy_execution_id:
            data["strategy_execution_id"] = strategy_execution_id
        
        return self._make_request("POST", "/trades", data)
    
    def get_trades(self, portfolio_id=None, symbol=None, limit=100):
        """获取交易记录"""
        params = {"limit": limit}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        if symbol:
            params["symbol"] = symbol
        
        return self._make_request("GET", "/trades", params=params)
    
    # 策略管理
    def create_strategy(self, name, strategy_type, description="", parameters=None):
        """创建策略"""
        data = {
            "name": name,
            "strategy_type": strategy_type,
            "description": description,
            "parameters": parameters or {}
        }
        return self._make_request("POST", "/strategies", data)
    
    def get_strategies(self):
        """获取策略列表"""
        return self._make_request("GET", "/strategies")
    
    def execute_strategy(self, strategy_id, portfolio_id, initial_capital=10000):
        """执行策略"""
        data = {
            "portfolio_id": portfolio_id,
            "initial_capital": initial_capital
        }
        return self._make_request("POST", f"/strategies/{strategy_id}/execute", data)
    
    # 市场数据
    def get_market_data(self, symbol, start_date=None, end_date=None, limit=1000):
        """获取市场数据"""
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._make_request("GET", f"/market-data/{symbol}", params=params)
    
    def get_latest_price(self, symbol):
        """获取最新价格"""
        return self._make_request("GET", f"/market-data/{symbol}/latest")
    
    # 风险管理
    def create_risk_rule(self, name, rule_type, description="", parameters=None):
        """创建风险规则"""
        data = {
            "name": name,
            "rule_type": rule_type,
            "description": description,
            "parameters": parameters or {}
        }
        return self._make_request("POST", "/risk-rules", data)
    
    def get_risk_rules(self):
        """获取风险规则列表"""
        return self._make_request("GET", "/risk-rules")
    
    def get_risk_alerts(self, portfolio_id=None, is_resolved=None):
        """获取风险警报"""
        params = {}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        if is_resolved is not None:
            params["is_resolved"] = is_resolved
        
        return self._make_request("GET", "/risk-alerts", params=params)
    
    # 仪表板数据
    def get_dashboard_stats(self):
        """获取仪表板统计数据"""
        return self._make_request("GET", "/dashboard/stats")
    
    def get_performance_data(self, portfolio_id=None, days=30):
        """获取表现数据"""
        params = {"days": days}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        
        return self._make_request("GET", "/dashboard/performance", params=params)
    
    def get_positions_summary(self, portfolio_id=None):
        """获取持仓汇总"""
        params = {}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        
        return self._make_request("GET", "/dashboard/positions", params=params)
    
    def get_recent_trades(self, portfolio_id=None, limit=10):
        """获取最近交易"""
        params = {"limit": limit}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        
        return self._make_request("GET", "/dashboard/recent-trades", params=params)


def main():
    """示例用法"""
    # 创建API客户端
    client = QuantTradingAPIClient()
    
    print("=== 量化交易系统API客户端示例 ===\n")
    
    # 1. 健康检查
    print("1. 健康检查")
    health = client.health_check()
    print(f"系统状态: {health}")
    print()
    
    # 2. 获取系统信息
    print("2. 系统信息")
    info = client.get_system_info()
    print(f"系统信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
    print()
    
    # 3. 用户注册
    print("3. 用户注册")
    register_result = client.register("testuser", "test@example.com", "password123")
    if register_result:
        print(f"注册成功: {register_result['message']}")
        print(f"用户ID: {register_result['user']['id']}")
    else:
        print("注册失败，尝试登录...")
        # 如果注册失败，尝试登录
        login_result = client.login("testuser", "password123")
        if login_result:
            print(f"登录成功: {login_result['message']}")
        else:
            print("登录失败")
            return
    print()
    
    # 4. 获取当前用户信息
    print("4. 当前用户信息")
    user_info = client.get_current_user()
    print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
    print()
    
    # 5. 创建投资组合
    print("5. 创建投资组合")
    portfolio = client.create_portfolio("我的投资组合", "测试投资组合", 10000)
    if portfolio:
        portfolio_id = portfolio['id']
        print(f"投资组合创建成功: {portfolio['name']} (ID: {portfolio_id})")
    else:
        print("投资组合创建失败")
        return
    print()
    
    # 6. 执行交易
    print("6. 执行交易")
    trade = client.execute_trade(portfolio_id, "AAPL", "buy", 10, 150.0)
    if trade:
        print(f"交易执行成功: {trade['symbol']} {trade['side']} {trade['quantity']}@{trade['price']}")
    else:
        print("交易执行失败")
    print()
    
    # 7. 获取市场数据
    print("7. 获取市场数据")
    market_data = client.get_market_data("AAPL", limit=5)
    if market_data:
        print(f"获取到 {len(market_data)} 条市场数据")
        for data in market_data[:2]:  # 只显示前2条
            print(f"  {data['timestamp']}: 收盘价 ${data['close_price']}")
    else:
        print("获取市场数据失败")
    print()
    
    # 8. 获取仪表板统计
    print("8. 仪表板统计")
    stats = client.get_dashboard_stats()
    if stats:
        print(f"总资产价值: ${stats['total_value']:.2f}")
        print(f"总盈亏: ${stats['total_pnl']:.2f}")
        print(f"总盈亏百分比: {stats['total_pnl_percentage']:.2f}%")
        print(f"总交易数: {stats['total_trades']}")
        print(f"胜率: {stats['win_rate']:.2f}%")
    else:
        print("获取仪表板统计失败")
    print()
    
    # 9. 获取持仓汇总
    print("9. 持仓汇总")
    positions = client.get_positions_summary(portfolio_id)
    if positions:
        print(f"持仓数量: {len(positions)}")
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['quantity']} 股, 价值 ${pos['value']:.2f}")
    else:
        print("获取持仓汇总失败")
    print()
    
    print("=== API客户端示例完成 ===")


if __name__ == "__main__":
    main()
