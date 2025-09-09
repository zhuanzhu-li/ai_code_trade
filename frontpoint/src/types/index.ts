// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

// 投资组合相关类型
export interface Portfolio {
  id: number
  user_id: number
  name: string
  description: string
  initial_capital: number
  current_value: number
  cash_balance: number
  total_pnl: number
  total_pnl_percentage: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Position {
  id: number
  portfolio_id: number
  symbol: string
  quantity: number
  average_price: number
  current_price: number
  value: number
  unrealized_pnl: number
  realized_pnl: number
  created_at: string
  updated_at: string
}

export interface CreatePortfolioRequest {
  name: string
  description?: string
  user_id: number
  initial_capital?: number
}

// 交易相关类型
export interface Trade {
  id: number
  portfolio_id: number
  strategy_execution_id?: number
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  amount: number
  fee: number
  net_amount: number
  pnl: number
  status: 'pending' | 'completed' | 'cancelled' | 'failed'
  executed_at: string
  created_at: string
}

export interface CreateTradeRequest {
  portfolio_id: number
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  strategy_execution_id?: number
}

// 策略相关类型
export interface Strategy {
  id: number
  user_id: number
  name: string
  description: string
  strategy_type: 'momentum' | 'mean_reversion'
  parameters: Record<string, any>
  is_active: boolean
  performance: {
    total_trades: number
    winning_trades: number
    win_rate: number
    total_pnl: number
    active_executions: number
  }
  created_at: string
  updated_at: string
}

export interface CreateStrategyRequest {
  name: string
  description?: string
  user_id: number
  strategy_type: 'momentum' | 'mean_reversion'
  parameters?: Record<string, any>
}

export interface StrategyExecution {
  id: number
  strategy_id: number
  portfolio_id: number
  start_time: string
  end_time?: string
  is_active: boolean
  initial_capital: number
  current_value: number
  total_pnl: number
  total_pnl_percentage: number
  created_at: string
  updated_at: string
}

export interface ExecuteStrategyRequest {
  portfolio_id: number
  start_time?: string
  initial_capital?: number
}

// 市场数据相关类型
export interface MarketData {
  id: number
  symbol_id: number
  symbol: string
  timestamp: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
  price_change: number
  price_change_percentage: number
  high_low_spread: number
  created_at: string
}

export interface LatestPrice {
  symbol: string
  price: number
  timestamp: string
}

// 风险管理相关类型
export interface RiskRule {
  id: number
  name: string
  description: string
  rule_type: 'position_size' | 'daily_loss' | 'max_drawdown' | 'trading_frequency'
  parameters: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateRiskRuleRequest {
  name: string
  description?: string
  rule_type: 'position_size' | 'daily_loss' | 'max_drawdown' | 'trading_frequency'
  parameters?: Record<string, any>
}

export interface RiskAlert {
  id: number
  risk_rule_id: number
  portfolio_id: number
  alert_type: 'warning' | 'error' | 'info'
  message: string
  is_resolved: boolean
  resolved_at?: string
  created_at: string
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data?: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// 仪表板统计类型
export interface DashboardStats {
  total_value: number
  total_pnl: number
  total_pnl_percentage: number
  active_portfolios: number
  active_strategies: number
  total_trades: number
  win_rate: number
  risk_alerts: number
}

// 图表数据类型
export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor?: string
    backgroundColor?: string
    fill?: boolean
  }[]
}

// 表格列配置类型
export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any, index: number) => string
}

// 表单验证规则类型
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: 'blur' | 'change'
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}
