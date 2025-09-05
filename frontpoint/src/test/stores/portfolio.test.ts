import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePortfolioStore } from '@/stores/portfolio'
import { apiClient } from '@/api'
import type { Portfolio, Position, CreatePortfolioRequest } from '@/types'

// Mock API client
vi.mock('@/api', () => ({
  apiClient: {
    getPortfolios: vi.fn(),
    getPortfolio: vi.fn(),
    createPortfolio: vi.fn(),
    getPositions: vi.fn()
  }
}))

const mockedApiClient = vi.mocked(apiClient)

describe('usePortfolioStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const store = usePortfolioStore()
      
      expect(store.portfolios).toEqual([])
      expect(store.currentPortfolio).toBeNull()
      expect(store.positions).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('computed properties', () => {
    it('should calculate totalValue correctly', () => {
      const store = usePortfolioStore()
      
      // No current portfolio
      expect(store.totalValue).toBe(0)
      
      // With current portfolio
      store.currentPortfolio = {
        id: 1,
        user_id: 1,
        name: 'Test Portfolio',
        description: 'Test',
        initial_capital: 10000,
        current_value: 12000,
        cash_balance: 2000,
        total_pnl: 2000,
        total_pnl_percentage: 20,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      expect(store.totalValue).toBe(12000)
    })

    it('should calculate totalPnL correctly', () => {
      const store = usePortfolioStore()
      
      // No current portfolio
      expect(store.totalPnL).toBe(0)
      
      // With current portfolio
      store.currentPortfolio = {
        id: 1,
        user_id: 1,
        name: 'Test Portfolio',
        description: 'Test',
        initial_capital: 10000,
        current_value: 12000,
        cash_balance: 2000,
        total_pnl: 2000,
        total_pnl_percentage: 20,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      expect(store.totalPnL).toBe(2000)
    })

    it('should calculate totalPnLPercentage correctly', () => {
      const store = usePortfolioStore()
      
      // No current portfolio
      expect(store.totalPnLPercentage).toBe(0)
      
      // With current portfolio
      store.currentPortfolio = {
        id: 1,
        user_id: 1,
        name: 'Test Portfolio',
        description: 'Test',
        initial_capital: 10000,
        current_value: 12000,
        cash_balance: 2000,
        total_pnl: 2000,
        total_pnl_percentage: 20,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      expect(store.totalPnLPercentage).toBe(20)
    })

    it('should calculate cashBalance correctly', () => {
      const store = usePortfolioStore()
      
      // No current portfolio
      expect(store.cashBalance).toBe(0)
      
      // With current portfolio
      store.currentPortfolio = {
        id: 1,
        user_id: 1,
        name: 'Test Portfolio',
        description: 'Test',
        initial_capital: 10000,
        current_value: 12000,
        cash_balance: 2000,
        total_pnl: 2000,
        total_pnl_percentage: 20,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      expect(store.cashBalance).toBe(2000)
    })
  })

  describe('fetchPortfolios', () => {
    it('should fetch portfolios successfully', async () => {
      const store = usePortfolioStore()
      const mockPortfolios = [
        { id: 1, name: 'Portfolio 1', user_id: 1 } as Portfolio,
        { id: 2, name: 'Portfolio 2', user_id: 1 } as Portfolio
      ]
      
      mockedApiClient.getPortfolios.mockResolvedValue(mockPortfolios)
      
      await store.fetchPortfolios(1)
      
      expect(mockedApiClient.getPortfolios).toHaveBeenCalledWith(1)
      expect(store.portfolios).toEqual(mockPortfolios)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch error', async () => {
      const store = usePortfolioStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Network error')
      
      mockedApiClient.getPortfolios.mockRejectedValue(error)
      
      await expect(store.fetchPortfolios(1)).rejects.toThrow('Network error')
      expect(consoleSpy).toHaveBeenCalledWith('获取投资组合列表失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('fetchPortfolio', () => {
    it('should fetch portfolio successfully', async () => {
      const store = usePortfolioStore()
      const mockPortfolio = {
        id: 1,
        name: 'Test Portfolio',
        user_id: 1,
        description: 'Test',
        initial_capital: 10000,
        current_value: 12000,
        cash_balance: 2000,
        total_pnl: 2000,
        total_pnl_percentage: 20,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      mockedApiClient.getPortfolio.mockResolvedValue(mockPortfolio)
      
      await store.fetchPortfolio(1)
      
      expect(mockedApiClient.getPortfolio).toHaveBeenCalledWith(1)
      expect(store.currentPortfolio).toEqual(mockPortfolio)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch error', async () => {
      const store = usePortfolioStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Portfolio not found')
      
      mockedApiClient.getPortfolio.mockRejectedValue(error)
      
      await expect(store.fetchPortfolio(1)).rejects.toThrow('Portfolio not found')
      expect(consoleSpy).toHaveBeenCalledWith('获取投资组合详情失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('createPortfolio', () => {
    it('should create portfolio successfully', async () => {
      const store = usePortfolioStore()
      const portfolioData: CreatePortfolioRequest = {
        name: 'New Portfolio',
        description: 'Test portfolio',
        user_id: 1,
        initial_capital: 10000
      }
      
      const mockPortfolio = {
        id: 3,
        ...portfolioData,
        current_value: 10000,
        cash_balance: 10000,
        total_pnl: 0,
        total_pnl_percentage: 0,
        is_active: true,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Portfolio
      
      mockedApiClient.createPortfolio.mockResolvedValue(mockPortfolio)
      
      const result = await store.createPortfolio(portfolioData)
      
      expect(mockedApiClient.createPortfolio).toHaveBeenCalledWith(portfolioData)
      expect(store.portfolios).toContainEqual(mockPortfolio)
      expect(result).toEqual(mockPortfolio)
      expect(store.loading).toBe(false)
    })

    it('should handle create error', async () => {
      const store = usePortfolioStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const portfolioData: CreatePortfolioRequest = {
        name: 'New Portfolio',
        user_id: 1
      }
      const error = new Error('Creation failed')
      
      mockedApiClient.createPortfolio.mockRejectedValue(error)
      
      await expect(store.createPortfolio(portfolioData)).rejects.toThrow('Creation failed')
      expect(consoleSpy).toHaveBeenCalledWith('创建投资组合失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('fetchPositions', () => {
    it('should fetch positions successfully', async () => {
      const store = usePortfolioStore()
      const mockPositions = [
        { id: 1, portfolio_id: 1, symbol: 'AAPL', quantity: 100 } as Position,
        { id: 2, portfolio_id: 1, symbol: 'GOOGL', quantity: 50 } as Position
      ]
      
      mockedApiClient.getPositions.mockResolvedValue(mockPositions)
      
      await store.fetchPositions(1)
      
      expect(mockedApiClient.getPositions).toHaveBeenCalledWith(1)
      expect(store.positions).toEqual(mockPositions)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch error', async () => {
      const store = usePortfolioStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Positions not found')
      
      mockedApiClient.getPositions.mockRejectedValue(error)
      
      await expect(store.fetchPositions(1)).rejects.toThrow('Positions not found')
      expect(consoleSpy).toHaveBeenCalledWith('获取持仓信息失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('updatePortfolio', () => {
    it('should update portfolio in portfolios list', () => {
      const store = usePortfolioStore()
      const originalPortfolio = {
        id: 1,
        name: 'Original Portfolio',
        user_id: 1
      } as Portfolio
      
      const updatedPortfolio = {
        id: 1,
        name: 'Updated Portfolio',
        user_id: 1
      } as Portfolio
      
      store.portfolios = [originalPortfolio]
      
      store.updatePortfolio(updatedPortfolio)
      
      expect(store.portfolios[0]).toEqual(updatedPortfolio)
    })

    it('should update current portfolio if it matches', () => {
      const store = usePortfolioStore()
      const originalPortfolio = {
        id: 1,
        name: 'Original Portfolio',
        user_id: 1
      } as Portfolio
      
      const updatedPortfolio = {
        id: 1,
        name: 'Updated Portfolio',
        user_id: 1
      } as Portfolio
      
      store.currentPortfolio = originalPortfolio
      
      store.updatePortfolio(updatedPortfolio)
      
      expect(store.currentPortfolio).toEqual(updatedPortfolio)
    })

    it('should not update if portfolio not found', () => {
      const store = usePortfolioStore()
      const originalPortfolio = {
        id: 1,
        name: 'Original Portfolio',
        user_id: 1
      } as Portfolio
      
      const updatedPortfolio = {
        id: 2,
        name: 'Updated Portfolio',
        user_id: 1
      } as Portfolio
      
      store.portfolios = [originalPortfolio]
      
      store.updatePortfolio(updatedPortfolio)
      
      expect(store.portfolios[0]).toEqual(originalPortfolio)
    })
  })
})
