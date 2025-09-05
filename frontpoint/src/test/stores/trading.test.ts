import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTradingStore } from '@/stores/trading'
import { apiClient } from '@/api'
import type { Trade, CreateTradeRequest } from '@/types'

// Mock API client
vi.mock('@/api', () => ({
  apiClient: {
    getTrades: vi.fn(),
    createTrade: vi.fn()
  }
}))

const mockedApiClient = vi.mocked(apiClient)

describe('useTradingStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const store = useTradingStore()
      
      expect(store.trades).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('computed properties', () => {
    beforeEach(() => {
      const store = useTradingStore()
      store.trades = [
        {
          id: 1,
          portfolio_id: 1,
          symbol: 'AAPL',
          side: 'buy',
          quantity: 100,
          price: 150.0,
          amount: 15000,
          fee: 15,
          net_amount: 14985,
          pnl: 500,
          status: 'completed',
          executed_at: '2024-01-01T10:00:00Z',
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: 2,
          portfolio_id: 1,
          symbol: 'GOOGL',
          side: 'sell',
          quantity: 50,
          price: 200.0,
          amount: 10000,
          fee: 10,
          net_amount: 9990,
          pnl: -200,
          status: 'completed',
          executed_at: '2024-01-01T11:00:00Z',
          created_at: '2024-01-01T11:00:00Z'
        },
        {
          id: 3,
          portfolio_id: 2,
          symbol: 'MSFT',
          side: 'buy',
          quantity: 75,
          price: 300.0,
          amount: 22500,
          fee: 22.5,
          net_amount: 22477.5,
          pnl: 300,
          status: 'completed',
          executed_at: '2024-01-01T12:00:00Z',
          created_at: '2024-01-01T12:00:00Z'
        }
      ] as Trade[]
    })

    it('should group trades by portfolio', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, portfolio_id: 1, symbol: 'AAPL' } as Trade,
        { id: 2, portfolio_id: 1, symbol: 'GOOGL' } as Trade,
        { id: 3, portfolio_id: 2, symbol: 'MSFT' } as Trade
      ]
      
      const grouped = store.tradesByPortfolio
      
      expect(grouped[1]).toHaveLength(2)
      expect(grouped[2]).toHaveLength(1)
      expect(grouped[1][0].symbol).toBe('AAPL')
      expect(grouped[1][1].symbol).toBe('GOOGL')
      expect(grouped[2][0].symbol).toBe('MSFT')
    })

    it('should group trades by symbol', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, portfolio_id: 1, symbol: 'AAPL' } as Trade,
        { id: 2, portfolio_id: 1, symbol: 'GOOGL' } as Trade,
        { id: 3, portfolio_id: 2, symbol: 'AAPL' } as Trade
      ]
      
      const grouped = store.tradesBySymbol
      
      expect(grouped['AAPL']).toHaveLength(2)
      expect(grouped['GOOGL']).toHaveLength(1)
    })

    it('should calculate total trades', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1 } as Trade,
        { id: 2 } as Trade,
        { id: 3 } as Trade
      ]
      
      expect(store.totalTrades).toBe(3)
    })

    it('should calculate winning trades', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, pnl: 100 } as Trade,
        { id: 2, pnl: -50 } as Trade,
        { id: 3, pnl: 200 } as Trade
      ]
      
      expect(store.winningTrades).toBe(2)
    })

    it('should calculate win rate', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, pnl: 100 } as Trade,
        { id: 2, pnl: -50 } as Trade,
        { id: 3, pnl: 200 } as Trade
      ]
      
      expect(store.winRate).toBe((2 / 3) * 100)
    })

    it('should return 0 win rate when no trades', () => {
      const store = useTradingStore()
      store.trades = []
      
      expect(store.winRate).toBe(0)
    })

    it('should calculate total PnL', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, pnl: 100 } as Trade,
        { id: 2, pnl: -50 } as Trade,
        { id: 3, pnl: 200 } as Trade
      ]
      
      expect(store.totalPnL).toBe(250)
    })

    it('should calculate total amount', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, amount: 1000 } as Trade,
        { id: 2, amount: 2000 } as Trade,
        { id: 3, amount: 1500 } as Trade
      ]
      
      expect(store.totalAmount).toBe(4500)
    })

    it('should calculate total fees', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, fee: 10 } as Trade,
        { id: 2, fee: 20 } as Trade,
        { id: 3, fee: 15 } as Trade
      ]
      
      expect(store.totalFees).toBe(45)
    })

    it('should get recent trades', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, symbol: 'AAPL' } as Trade,
        { id: 2, symbol: 'GOOGL' } as Trade,
        { id: 3, symbol: 'MSFT' } as Trade,
        { id: 4, symbol: 'TSLA' } as Trade,
        { id: 5, symbol: 'AMZN' } as Trade,
        { id: 6, symbol: 'NVDA' } as Trade,
        { id: 7, symbol: 'META' } as Trade,
        { id: 8, symbol: 'NFLX' } as Trade,
        { id: 9, symbol: 'ADBE' } as Trade,
        { id: 10, symbol: 'CRM' } as Trade,
        { id: 11, symbol: 'ORCL' } as Trade
      ]
      
      const recent = store.recentTrades
      
      expect(recent).toHaveLength(10)
      expect(recent[0].id).toBe(1)
      expect(recent[9].id).toBe(10)
    })

    it('should group trades by status', () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, status: 'completed' } as Trade,
        { id: 2, status: 'pending' } as Trade,
        { id: 3, status: 'completed' } as Trade,
        { id: 4, status: 'cancelled' } as Trade
      ]
      
      const grouped = store.tradesByStatus
      
      expect(grouped['completed']).toHaveLength(2)
      expect(grouped['pending']).toHaveLength(1)
      expect(grouped['cancelled']).toHaveLength(1)
    })
  })

  describe('fetchTrades', () => {
    it('should fetch trades successfully', async () => {
      const store = useTradingStore()
      const mockTrades = [
        { id: 1, portfolio_id: 1, symbol: 'AAPL' } as Trade,
        { id: 2, portfolio_id: 1, symbol: 'GOOGL' } as Trade
      ]
      
      mockedApiClient.getTrades.mockResolvedValue(mockTrades)
      
      await store.fetchTrades({ portfolio_id: 1, limit: 10 })
      
      expect(mockedApiClient.getTrades).toHaveBeenCalledWith({ portfolio_id: 1, limit: 10 })
      expect(store.trades).toEqual(mockTrades)
      expect(store.loading).toBe(false)
    })

    it('should fetch trades without params', async () => {
      const store = useTradingStore()
      const mockTrades = [
        { id: 1, portfolio_id: 1, symbol: 'AAPL' } as Trade
      ]
      
      mockedApiClient.getTrades.mockResolvedValue(mockTrades)
      
      await store.fetchTrades()
      
      expect(mockedApiClient.getTrades).toHaveBeenCalledWith(undefined)
      expect(store.trades).toEqual(mockTrades)
    })

    it('should handle fetch error', async () => {
      const store = useTradingStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Network error')
      
      mockedApiClient.getTrades.mockRejectedValue(error)
      
      await expect(store.fetchTrades()).rejects.toThrow('Network error')
      expect(consoleSpy).toHaveBeenCalledWith('获取交易记录失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('executeTrade', () => {
    it('should execute trade successfully', async () => {
      const store = useTradingStore()
      const tradeData: CreateTradeRequest = {
        portfolio_id: 1,
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150.0
      }
      
      const mockTrade = {
        id: 3,
        ...tradeData,
        amount: 15000,
        fee: 15,
        net_amount: 14985,
        pnl: 0,
        status: 'completed',
        executed_at: '2024-01-01T10:00:00Z',
        created_at: '2024-01-01T10:00:00Z'
      } as Trade
      
      mockedApiClient.createTrade.mockResolvedValue(mockTrade)
      
      const result = await store.executeTrade(tradeData)
      
      expect(mockedApiClient.createTrade).toHaveBeenCalledWith(tradeData)
      expect(store.trades[0]).toEqual(mockTrade)
      expect(result).toEqual(mockTrade)
      expect(store.loading).toBe(false)
    })

    it('should add trade to beginning of list', async () => {
      const store = useTradingStore()
      store.trades = [
        { id: 1, symbol: 'GOOGL' } as Trade,
        { id: 2, symbol: 'MSFT' } as Trade
      ]
      
      const tradeData: CreateTradeRequest = {
        portfolio_id: 1,
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150.0
      }
      
      const mockTrade = { id: 3, symbol: 'AAPL' } as Trade
      mockedApiClient.createTrade.mockResolvedValue(mockTrade)
      
      await store.executeTrade(tradeData)
      
      expect(store.trades[0]).toEqual(mockTrade)
      expect(store.trades).toHaveLength(3)
    })

    it('should handle execute error', async () => {
      const store = useTradingStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const tradeData: CreateTradeRequest = {
        portfolio_id: 1,
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150.0
      }
      const error = new Error('Insufficient funds')
      
      mockedApiClient.createTrade.mockRejectedValue(error)
      
      await expect(store.executeTrade(tradeData)).rejects.toThrow('Insufficient funds')
      expect(consoleSpy).toHaveBeenCalledWith('执行交易失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })
})
