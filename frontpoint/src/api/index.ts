import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  Portfolio,
  Position,
  CreatePortfolioRequest,
  Trade,
  CreateTradeRequest,
  Strategy,
  CreateStrategyRequest,
  StrategyExecution,
  ExecuteStrategyRequest,
  MarketData,
  LatestPrice,
  RiskRule,
  CreateRiskRuleRequest,
  RiskAlert,
  ApiResponse,
  DashboardStats
} from '@/types'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        
        const message = error.response?.data?.error || error.message || '请求失败'
        ElMessage.error(message)
        
        return Promise.reject(error)
      }
    )
  }

  // 通用请求方法
  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.request<ApiResponse<T>>(config)
      return response.data.data as T
    } catch (error) {
      throw error
    }
  }

  // 用户认证相关
  async login(data: LoginRequest): Promise<{ user: User; token: string }> {
    return this.request({
      method: 'POST',
      url: '/auth/login',
      data
    })
  }

  async register(data: RegisterRequest): Promise<User> {
    return this.request({
      method: 'POST',
      url: '/users',
      data
    })
  }

  async getUserInfo(userId: number): Promise<User> {
    return this.request({
      method: 'GET',
      url: `/users/${userId}`
    })
  }

  // 投资组合相关
  async getPortfolios(userId: number): Promise<Portfolio[]> {
    return this.request({
      method: 'GET',
      url: '/portfolios',
      params: { user_id: userId }
    })
  }

  async getPortfolio(portfolioId: number): Promise<Portfolio> {
    return this.request({
      method: 'GET',
      url: `/portfolios/${portfolioId}`
    })
  }

  async createPortfolio(data: CreatePortfolioRequest): Promise<Portfolio> {
    return this.request({
      method: 'POST',
      url: '/portfolios',
      data
    })
  }

  async getPositions(portfolioId: number): Promise<Position[]> {
    return this.request({
      method: 'GET',
      url: `/portfolios/${portfolioId}/positions`
    })
  }

  // 交易相关
  async getTrades(params?: {
    portfolio_id?: number
    symbol?: string
    limit?: number
  }): Promise<Trade[]> {
    return this.request({
      method: 'GET',
      url: '/trades',
      params
    })
  }

  async createTrade(data: CreateTradeRequest): Promise<Trade> {
    return this.request({
      method: 'POST',
      url: '/trades',
      data
    })
  }

  // 策略相关
  async getStrategies(userId: number): Promise<Strategy[]> {
    return this.request({
      method: 'GET',
      url: '/strategies',
      params: { user_id: userId }
    })
  }

  async getStrategy(strategyId: number): Promise<Strategy> {
    return this.request({
      method: 'GET',
      url: `/strategies/${strategyId}`
    })
  }

  async createStrategy(data: CreateStrategyRequest): Promise<Strategy> {
    return this.request({
      method: 'POST',
      url: '/strategies',
      data
    })
  }

  async executeStrategy(strategyId: number, data: ExecuteStrategyRequest): Promise<StrategyExecution> {
    return this.request({
      method: 'POST',
      url: `/strategies/${strategyId}/execute`,
      data
    })
  }

  async stopStrategy(strategyId: number): Promise<void> {
    return this.request({
      method: 'POST',
      url: `/strategies/${strategyId}/stop`
    })
  }

  // 市场数据相关
  async getMarketData(
    symbol: string,
    params?: {
      start_date?: string
      end_date?: string
      limit?: number
    }
  ): Promise<MarketData[]> {
    return this.request({
      method: 'GET',
      url: `/market-data/${symbol}`,
      params
    })
  }

  async getLatestPrice(symbol: string): Promise<LatestPrice> {
    return this.request({
      method: 'GET',
      url: `/market-data/${symbol}/latest`
    })
  }

  // 风险管理相关
  async getRiskRules(): Promise<RiskRule[]> {
    return this.request({
      method: 'GET',
      url: '/risk-rules'
    })
  }

  async createRiskRule(data: CreateRiskRuleRequest): Promise<RiskRule> {
    return this.request({
      method: 'POST',
      url: '/risk-rules',
      data
    })
  }

  async getRiskAlerts(params?: {
    portfolio_id?: number
    is_resolved?: boolean
  }): Promise<RiskAlert[]> {
    return this.request({
      method: 'GET',
      url: '/risk-alerts',
      params
    })
  }

  // 仪表板相关
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request({
      method: 'GET',
      url: '/dashboard/stats'
    })
  }

  // 市场数据相关
  async getDataSources(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/market-data/sources'
    })
  }

  async syncSymbols(data: any): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/market-data/sync/symbols',
      data
    })
  }

  async syncIndexComponents(data: any): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/market-data/sync/index-components',
      data
    })
  }

  async fetchLatestData(data?: any): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/market-data/fetch/latest',
      data
    })
  }

  async fetchHistoricalData(data: any): Promise<any> {
    return this.request({
      method: 'POST',
      url: '/market-data/fetch/historical',
      data
    })
  }

  async getMarketData(symbol: string, params?: any): Promise<any> {
    return this.request({
      method: 'GET',
      url: `/market-data/${symbol}`,
      params
    })
  }

  async getSymbols(params?: any): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/market-data/symbols',
      params
    })
  }

  async getMarketDataStatistics(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/market-data/statistics'
    })
  }

  async getMarketDataHealth(): Promise<any> {
    return this.request({
      method: 'GET',
      url: '/market-data/health'
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient
