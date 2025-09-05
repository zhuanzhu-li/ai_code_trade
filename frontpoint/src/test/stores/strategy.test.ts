import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useStrategyStore } from '@/stores/strategy'
import { apiClient } from '@/api'
import type { Strategy, StrategyExecution, CreateStrategyRequest, ExecuteStrategyRequest } from '@/types'

// Mock API client
vi.mock('@/api', () => ({
  apiClient: {
    getStrategies: vi.fn(),
    getStrategy: vi.fn(),
    createStrategy: vi.fn(),
    executeStrategy: vi.fn(),
    stopStrategy: vi.fn()
  }
}))

const mockedApiClient = vi.mocked(apiClient)

describe('useStrategyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const store = useStrategyStore()
      
      expect(store.strategies).toEqual([])
      expect(store.currentStrategy).toBeNull()
      expect(store.executions).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('computed properties', () => {
    beforeEach(() => {
      const store = useStrategyStore()
      store.strategies = [
        {
          id: 1,
          user_id: 1,
          name: 'Momentum Strategy',
          description: 'Test momentum strategy',
          strategy_type: 'momentum',
          parameters: { lookback_period: 20 },
          is_active: true,
          performance: {
            total_trades: 100,
            winning_trades: 60,
            win_rate: 60,
            total_pnl: 5000,
            active_executions: 1
          },
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        },
        {
          id: 2,
          user_id: 1,
          name: 'Mean Reversion Strategy',
          description: 'Test mean reversion strategy',
          strategy_type: 'mean_reversion',
          parameters: { lookback_period: 14 },
          is_active: false,
          performance: {
            total_trades: 50,
            winning_trades: 35,
            win_rate: 70,
            total_pnl: 3000,
            active_executions: 0
          },
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        }
      ] as Strategy[]
      
      store.executions = [
        {
          id: 1,
          strategy_id: 1,
          portfolio_id: 1,
          start_time: '2024-01-01T00:00:00Z',
          end_time: null,
          is_active: true,
          initial_capital: 10000,
          current_value: 12000,
          total_pnl: 2000,
          total_pnl_percentage: 20,
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        },
        {
          id: 2,
          strategy_id: 2,
          portfolio_id: 1,
          start_time: '2024-01-01T00:00:00Z',
          end_time: '2024-01-02T00:00:00Z',
          is_active: false,
          initial_capital: 5000,
          current_value: 5500,
          total_pnl: 500,
          total_pnl_percentage: 10,
          created_at: '2024-01-01',
          updated_at: '2024-01-02'
        }
      ] as StrategyExecution[]
    })

    it('should filter active strategies', () => {
      const store = useStrategyStore()
      store.strategies = [
        { id: 1, is_active: true } as Strategy,
        { id: 2, is_active: false } as Strategy,
        { id: 3, is_active: true } as Strategy
      ]
      
      const active = store.activeStrategies
      
      expect(active).toHaveLength(2)
      expect(active[0].id).toBe(1)
      expect(active[1].id).toBe(3)
    })

    it('should group strategies by type', () => {
      const store = useStrategyStore()
      store.strategies = [
        { id: 1, strategy_type: 'momentum' } as Strategy,
        { id: 2, strategy_type: 'mean_reversion' } as Strategy,
        { id: 3, strategy_type: 'momentum' } as Strategy
      ]
      
      const grouped = store.strategiesByType
      
      expect(grouped['momentum']).toHaveLength(2)
      expect(grouped['mean_reversion']).toHaveLength(1)
    })

    it('should filter active executions', () => {
      const store = useStrategyStore()
      store.executions = [
        { id: 1, is_active: true } as StrategyExecution,
        { id: 2, is_active: false } as StrategyExecution,
        { id: 3, is_active: true } as StrategyExecution
      ]
      
      const active = store.activeExecutions
      
      expect(active).toHaveLength(2)
      expect(active[0].id).toBe(1)
      expect(active[1].id).toBe(3)
    })

    it('should calculate total strategies', () => {
      const store = useStrategyStore()
      store.strategies = [
        { id: 1 } as Strategy,
        { id: 2 } as Strategy,
        { id: 3 } as Strategy
      ]
      
      expect(store.totalStrategies).toBe(3)
    })

    it('should calculate active strategies count', () => {
      const store = useStrategyStore()
      store.strategies = [
        { id: 1, is_active: true } as Strategy,
        { id: 2, is_active: false } as Strategy,
        { id: 3, is_active: true } as Strategy
      ]
      
      expect(store.activeStrategiesCount).toBe(2)
    })

    it('should calculate total executions', () => {
      const store = useStrategyStore()
      store.executions = [
        { id: 1 } as StrategyExecution,
        { id: 2 } as StrategyExecution
      ]
      
      expect(store.totalExecutions).toBe(2)
    })

    it('should calculate active executions count', () => {
      const store = useStrategyStore()
      store.executions = [
        { id: 1, is_active: true } as StrategyExecution,
        { id: 2, is_active: false } as StrategyExecution,
        { id: 3, is_active: true } as StrategyExecution
      ]
      
      expect(store.activeExecutionsCount).toBe(2)
    })

    it('should calculate average win rate', () => {
      const store = useStrategyStore()
      store.strategies = [
        { performance: { win_rate: 60 } } as Strategy,
        { performance: { win_rate: 80 } } as Strategy
      ]
      
      expect(store.averageWinRate).toBe(70)
    })

    it('should return 0 average win rate when no strategies', () => {
      const store = useStrategyStore()
      store.strategies = []
      
      expect(store.averageWinRate).toBe(0)
    })

    it('should calculate total strategy PnL', () => {
      const store = useStrategyStore()
      store.strategies = [
        { performance: { total_pnl: 1000 } } as Strategy,
        { performance: { total_pnl: 2000 } } as Strategy
      ]
      
      expect(store.totalStrategyPnL).toBe(3000)
    })
  })

  describe('fetchStrategies', () => {
    it('should fetch strategies successfully', async () => {
      const store = useStrategyStore()
      const mockStrategies = [
        { id: 1, name: 'Strategy 1' } as Strategy,
        { id: 2, name: 'Strategy 2' } as Strategy
      ]
      
      mockedApiClient.getStrategies.mockResolvedValue(mockStrategies)
      
      await store.fetchStrategies(1)
      
      expect(mockedApiClient.getStrategies).toHaveBeenCalledWith(1)
      expect(store.strategies).toEqual(mockStrategies)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch error', async () => {
      const store = useStrategyStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Network error')
      
      mockedApiClient.getStrategies.mockRejectedValue(error)
      
      await expect(store.fetchStrategies(1)).rejects.toThrow('Network error')
      expect(consoleSpy).toHaveBeenCalledWith('获取策略列表失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('fetchStrategy', () => {
    it('should fetch strategy successfully', async () => {
      const store = useStrategyStore()
      const mockStrategy = {
        id: 1,
        name: 'Test Strategy',
        user_id: 1
      } as Strategy
      
      mockedApiClient.getStrategy.mockResolvedValue(mockStrategy)
      
      await store.fetchStrategy(1)
      
      expect(mockedApiClient.getStrategy).toHaveBeenCalledWith(1)
      expect(store.currentStrategy).toEqual(mockStrategy)
      expect(store.loading).toBe(false)
    })

    it('should handle fetch error', async () => {
      const store = useStrategyStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Strategy not found')
      
      mockedApiClient.getStrategy.mockRejectedValue(error)
      
      await expect(store.fetchStrategy(1)).rejects.toThrow('Strategy not found')
      expect(consoleSpy).toHaveBeenCalledWith('获取策略详情失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('createStrategy', () => {
    it('should create strategy successfully', async () => {
      const store = useStrategyStore()
      const strategyData: CreateStrategyRequest = {
        name: 'New Strategy',
        description: 'Test strategy',
        user_id: 1,
        strategy_type: 'momentum',
        parameters: { lookback_period: 20 }
      }
      
      const mockStrategy = {
        id: 3,
        ...strategyData,
        is_active: true,
        performance: {
          total_trades: 0,
          winning_trades: 0,
          win_rate: 0,
          total_pnl: 0,
          active_executions: 0
        },
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as Strategy
      
      mockedApiClient.createStrategy.mockResolvedValue(mockStrategy)
      
      const result = await store.createStrategy(strategyData)
      
      expect(mockedApiClient.createStrategy).toHaveBeenCalledWith(strategyData)
      expect(store.strategies).toContainEqual(mockStrategy)
      expect(result).toEqual(mockStrategy)
      expect(store.loading).toBe(false)
    })

    it('should handle create error', async () => {
      const store = useStrategyStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const strategyData: CreateStrategyRequest = {
        name: 'New Strategy',
        user_id: 1,
        strategy_type: 'momentum'
      }
      const error = new Error('Creation failed')
      
      mockedApiClient.createStrategy.mockRejectedValue(error)
      
      await expect(store.createStrategy(strategyData)).rejects.toThrow('Creation failed')
      expect(consoleSpy).toHaveBeenCalledWith('创建策略失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('executeStrategy', () => {
    it('should execute strategy successfully', async () => {
      const store = useStrategyStore()
      const executionData: ExecuteStrategyRequest = {
        portfolio_id: 1,
        start_time: '2024-01-01T00:00:00Z',
        initial_capital: 10000
      }
      
      const mockExecution = {
        id: 1,
        strategy_id: 1,
        ...executionData,
        is_active: true,
        current_value: 10000,
        total_pnl: 0,
        total_pnl_percentage: 0,
        created_at: '2024-01-01',
        updated_at: '2024-01-01'
      } as StrategyExecution
      
      mockedApiClient.executeStrategy.mockResolvedValue(mockExecution)
      
      const result = await store.executeStrategy(1, executionData)
      
      expect(mockedApiClient.executeStrategy).toHaveBeenCalledWith(1, executionData)
      expect(store.executions).toContainEqual(mockExecution)
      expect(result).toEqual(mockExecution)
      expect(store.loading).toBe(false)
    })

    it('should handle execute error', async () => {
      const store = useStrategyStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const executionData: ExecuteStrategyRequest = {
        portfolio_id: 1,
        initial_capital: 10000
      }
      const error = new Error('Execution failed')
      
      mockedApiClient.executeStrategy.mockRejectedValue(error)
      
      await expect(store.executeStrategy(1, executionData)).rejects.toThrow('Execution failed')
      expect(consoleSpy).toHaveBeenCalledWith('执行策略失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('stopStrategy', () => {
    it('should stop strategy successfully', async () => {
      const store = useStrategyStore()
      store.strategies = [
        { id: 1, is_active: true } as Strategy,
        { id: 2, is_active: false } as Strategy
      ]
      
      mockedApiClient.stopStrategy.mockResolvedValue(undefined)
      
      await store.stopStrategy(1)
      
      expect(mockedApiClient.stopStrategy).toHaveBeenCalledWith(1)
      expect(store.strategies[0].is_active).toBe(false)
      expect(store.loading).toBe(false)
    })

    it('should handle stop error', async () => {
      const store = useStrategyStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Stop failed')
      
      mockedApiClient.stopStrategy.mockRejectedValue(error)
      
      await expect(store.stopStrategy(1)).rejects.toThrow('Stop failed')
      expect(consoleSpy).toHaveBeenCalledWith('停止策略失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('updateStrategy', () => {
    it('should update strategy in strategies list', () => {
      const store = useStrategyStore()
      const originalStrategy = {
        id: 1,
        name: 'Original Strategy',
        user_id: 1
      } as Strategy
      
      const updatedStrategy = {
        id: 1,
        name: 'Updated Strategy',
        user_id: 1
      } as Strategy
      
      store.strategies = [originalStrategy]
      
      store.updateStrategy(updatedStrategy)
      
      expect(store.strategies[0]).toEqual(updatedStrategy)
    })

    it('should update current strategy if it matches', () => {
      const store = useStrategyStore()
      const originalStrategy = {
        id: 1,
        name: 'Original Strategy',
        user_id: 1
      } as Strategy
      
      const updatedStrategy = {
        id: 1,
        name: 'Updated Strategy',
        user_id: 1
      } as Strategy
      
      store.currentStrategy = originalStrategy
      
      store.updateStrategy(updatedStrategy)
      
      expect(store.currentStrategy).toEqual(updatedStrategy)
    })

    it('should not update if strategy not found', () => {
      const store = useStrategyStore()
      const originalStrategy = {
        id: 1,
        name: 'Original Strategy',
        user_id: 1
      } as Strategy
      
      const updatedStrategy = {
        id: 2,
        name: 'Updated Strategy',
        user_id: 1
      } as Strategy
      
      store.strategies = [originalStrategy]
      
      store.updateStrategy(updatedStrategy)
      
      expect(store.strategies[0]).toEqual(originalStrategy)
    })
  })
})
