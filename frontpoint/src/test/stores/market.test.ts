import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMarketStore } from '@/stores/market'
import { apiClient } from '@/api'
import type { MarketData, LatestPrice } from '@/types'

// Mock API client
vi.mock('@/api', () => ({
  apiClient: {
    getMarketData: vi.fn(),
    getLatestPrice: vi.fn()
  }
}))

const mockedApiClient = vi.mocked(apiClient)

describe('useMarketStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const store = useMarketStore()
      
      expect(store.marketData).toEqual([])
      expect(store.latestPrices).toEqual({})
      expect(store.loading).toBe(false)
    })
  })

  describe('computed properties', () => {
    beforeEach(() => {
      const store = useMarketStore()
      store.marketData = [
        {
          id: 1,
          symbol_id: 1,
          symbol: 'AAPL',
          timestamp: '2024-01-01T10:00:00Z',
          open_price: 150.0,
          high_price: 155.0,
          low_price: 148.0,
          close_price: 152.0,
          volume: 1000000,
          price_change: 2.0,
          price_change_percentage: 1.33,
          high_low_spread: 7.0,
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: 2,
          symbol_id: 1,
          symbol: 'AAPL',
          timestamp: '2024-01-01T11:00:00Z',
          open_price: 152.0,
          high_price: 158.0,
          low_price: 151.0,
          close_price: 156.0,
          volume: 1200000,
          price_change: 4.0,
          price_change_percentage: 2.63,
          high_low_spread: 7.0,
          created_at: '2024-01-01T11:00:00Z'
        }
      ] as MarketData[]
    })

    it('should get price history', () => {
      const store = useMarketStore()
      store.marketData = [
        {
          id: 1,
          symbol: 'AAPL',
          timestamp: '2024-01-01T10:00:00Z',
          open_price: 150.0,
          high_price: 155.0,
          low_price: 148.0,
          close_price: 152.0,
          volume: 1000000,
          price_change: 2.0,
          price_change_percentage: 1.33,
          high_low_spread: 7.0,
          symbol_id: 1,
          created_at: '2024-01-01T10:00:00Z'
        }
      ] as MarketData[]
      
      const history = store.getPriceHistory
      
      expect(history).toHaveLength(1)
      expect(history[0]).toEqual({
        time: '2024-01-01T10:00:00Z',
        open: 150.0,
        high: 155.0,
        low: 148.0,
        close: 152.0,
        volume: 1000000
      })
    })

    it('should return empty array when no market data', () => {
      const store = useMarketStore()
      store.marketData = []
      
      expect(store.getPriceHistory).toEqual([])
    })

    it('should get price changes', () => {
      const store = useMarketStore()
      store.marketData = [
        {
          id: 1,
          symbol: 'AAPL',
          timestamp: '2024-01-01T10:00:00Z',
          open_price: 150.0,
          high_price: 155.0,
          low_price: 148.0,
          close_price: 152.0,
          volume: 1000000,
          price_change: 2.0,
          price_change_percentage: 1.33,
          high_low_spread: 7.0,
          symbol_id: 1,
          created_at: '2024-01-01T10:00:00Z'
        }
      ] as MarketData[]
      
      const changes = store.getPriceChanges
      
      expect(changes).toHaveLength(1)
      expect(changes[0]).toEqual({
        time: '2024-01-01T10:00:00Z',
        price: 152.0,
        change: 2.0,
        changePercent: 1.33
      })
    })

    it('should get volume data', () => {
      const store = useMarketStore()
      store.marketData = [
        {
          id: 1,
          symbol: 'AAPL',
          timestamp: '2024-01-01T10:00:00Z',
          open_price: 150.0,
          high_price: 155.0,
          low_price: 148.0,
          close_price: 152.0,
          volume: 1000000,
          price_change: 2.0,
          price_change_percentage: 1.33,
          high_low_spread: 7.0,
          symbol_id: 1,
          created_at: '2024-01-01T10:00:00Z'
        }
      ] as MarketData[]
      
      const volume = store.getVolumeData
      
      expect(volume).toHaveLength(1)
      expect(volume[0]).toEqual({
        time: '2024-01-01T10:00:00Z',
        volume: 1000000
      })
    })
  })

  describe('fetchMarketData', () => {
    it('should fetch market data successfully', async () => {
      const store = useMarketStore()
      const mockData = [
        { symbol: 'AAPL', timestamp: '2024-01-01', close_price: 150.0 } as MarketData
      ]
      
      mockedApiClient.getMarketData.mockResolvedValue(mockData)
      
      const result = await store.fetchMarketData('AAPL', { 
        start_date: '2024-01-01', 
        end_date: '2024-01-02' 
      })
      
      expect(mockedApiClient.getMarketData).toHaveBeenCalledWith('AAPL', { 
        start_date: '2024-01-01', 
        end_date: '2024-01-02' 
      })
      expect(store.marketData).toEqual(mockData)
      expect(result).toEqual(mockData)
      expect(store.loading).toBe(false)
    })

    it('should fetch market data without params', async () => {
      const store = useMarketStore()
      const mockData = [
        { symbol: 'AAPL', timestamp: '2024-01-01', close_price: 150.0 } as MarketData
      ]
      
      mockedApiClient.getMarketData.mockResolvedValue(mockData)
      
      await store.fetchMarketData('AAPL')
      
      expect(mockedApiClient.getMarketData).toHaveBeenCalledWith('AAPL', undefined)
      expect(store.marketData).toEqual(mockData)
    })

    it('should handle fetch error', async () => {
      const store = useMarketStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Network error')
      
      mockedApiClient.getMarketData.mockRejectedValue(error)
      
      await expect(store.fetchMarketData('AAPL')).rejects.toThrow('Network error')
      expect(consoleSpy).toHaveBeenCalledWith('获取市场数据失败:', error)
      expect(store.loading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('fetchLatestPrice', () => {
    it('should fetch latest price successfully', async () => {
      const store = useMarketStore()
      const mockPrice = {
        symbol: 'AAPL',
        price: 150.0,
        timestamp: '2024-01-01T10:00:00Z'
      } as LatestPrice
      
      mockedApiClient.getLatestPrice.mockResolvedValue(mockPrice)
      
      const result = await store.fetchLatestPrice('AAPL')
      
      expect(mockedApiClient.getLatestPrice).toHaveBeenCalledWith('AAPL')
      expect(store.latestPrices['AAPL']).toEqual(mockPrice)
      expect(result).toEqual(mockPrice)
    })

    it('should handle fetch error', async () => {
      const store = useMarketStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Price not found')
      
      mockedApiClient.getLatestPrice.mockRejectedValue(error)
      
      await expect(store.fetchLatestPrice('AAPL')).rejects.toThrow('Price not found')
      expect(consoleSpy).toHaveBeenCalledWith('获取最新价格失败:', error)
      
      consoleSpy.mockRestore()
    })
  })

  describe('fetchLatestPrices', () => {
    it('should fetch multiple latest prices successfully', async () => {
      const store = useMarketStore()
      const mockPrices = [
        { symbol: 'AAPL', price: 150.0, timestamp: '2024-01-01T10:00:00Z' } as LatestPrice,
        { symbol: 'GOOGL', price: 200.0, timestamp: '2024-01-01T10:00:00Z' } as LatestPrice
      ]
      
      mockedApiClient.getLatestPrice
        .mockResolvedValueOnce(mockPrices[0])
        .mockResolvedValueOnce(mockPrices[1])
      
      await store.fetchLatestPrices(['AAPL', 'GOOGL'])
      
      expect(mockedApiClient.getLatestPrice).toHaveBeenCalledWith('AAPL')
      expect(mockedApiClient.getLatestPrice).toHaveBeenCalledWith('GOOGL')
      expect(store.latestPrices['AAPL']).toEqual(mockPrices[0])
      expect(store.latestPrices['GOOGL']).toEqual(mockPrices[1])
    })

    it('should handle fetch error', async () => {
      const store = useMarketStore()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const error = new Error('Price fetch failed')
      
      mockedApiClient.getLatestPrice.mockRejectedValue(error)
      
      await expect(store.fetchLatestPrices(['AAPL'])).rejects.toThrow('Price fetch failed')
      expect(consoleSpy).toHaveBeenCalledWith('批量获取最新价格失败:', error)
      
      consoleSpy.mockRestore()
    })
  })

  describe('calculateRSI', () => {
    it('should calculate RSI correctly', () => {
      const store = useMarketStore()
      store.marketData = [
        { close_price: 100 } as MarketData,
        { close_price: 101 } as MarketData,
        { close_price: 102 } as MarketData,
        { close_price: 103 } as MarketData,
        { close_price: 104 } as MarketData,
        { close_price: 105 } as MarketData,
        { close_price: 106 } as MarketData,
        { close_price: 107 } as MarketData,
        { close_price: 108 } as MarketData,
        { close_price: 109 } as MarketData,
        { close_price: 110 } as MarketData,
        { close_price: 111 } as MarketData,
        { close_price: 112 } as MarketData,
        { close_price: 113 } as MarketData,
        { close_price: 114 } as MarketData,
        { close_price: 115 } as MarketData,
        { close_price: 116 } as MarketData,
        { close_price: 117 } as MarketData,
        { close_price: 118 } as MarketData,
        { close_price: 119 } as MarketData,
        { close_price: 120 } as MarketData
      ]
      
      const rsi = store.calculateRSI(14)
      
      expect(rsi).toHaveLength(7) // 21 - 14 = 7 (实际计算长度)
      expect(rsi[0]).toBeCloseTo(100, 0) // All gains, no losses
    })

    it('should return empty array when insufficient data', () => {
      const store = useMarketStore()
      store.marketData = [
        { close_price: 100 } as MarketData,
        { close_price: 102 } as MarketData
      ]
      
      const rsi = store.calculateRSI(14)
      
      expect(rsi).toEqual([])
    })
  })

  describe('calculateMA', () => {
    it('should calculate moving average correctly', () => {
      const store = useMarketStore()
      store.marketData = [
        { close_price: 100 } as MarketData,
        { close_price: 102 } as MarketData,
        { close_price: 101 } as MarketData,
        { close_price: 103 } as MarketData,
        { close_price: 105 } as MarketData
      ]
      
      const ma = store.calculateMA(3)
      
      expect(ma).toHaveLength(3) // 5 - 3 + 1
      expect(ma[0]).toBe(101) // (100 + 102 + 101) / 3
      expect(ma[1]).toBe(102) // (102 + 101 + 103) / 3
      expect(ma[2]).toBe(103) // (101 + 103 + 105) / 3
    })

    it('should return empty array when insufficient data', () => {
      const store = useMarketStore()
      store.marketData = [
        { close_price: 100 } as MarketData,
        { close_price: 102 } as MarketData
      ]
      
      const ma = store.calculateMA(3)
      
      expect(ma).toEqual([])
    })
  })

  describe('getCurrentPrice', () => {
    it('should return current price for symbol', () => {
      const store = useMarketStore()
      store.latestPrices = {
        'AAPL': { symbol: 'AAPL', price: 150.0, timestamp: '2024-01-01T10:00:00Z' }
      }
      
      expect(store.getCurrentPrice('AAPL')).toBe(150.0)
    })

    it('should return 0 for unknown symbol', () => {
      const store = useMarketStore()
      
      expect(store.getCurrentPrice('UNKNOWN')).toBe(0)
    })
  })

  describe('getPriceChange', () => {
    it('should return price change for symbol', () => {
      const store = useMarketStore()
      store.latestPrices = {
        'AAPL': { symbol: 'AAPL', price: 150.0, timestamp: '2024-01-01T10:00:00Z' }
      }
      
      const change = store.getPriceChange('AAPL')
      
      expect(change).toEqual({ change: 0, changePercent: 0 })
    })

    it('should return zero change for unknown symbol', () => {
      const store = useMarketStore()
      
      const change = store.getPriceChange('UNKNOWN')
      
      expect(change).toEqual({ change: 0, changePercent: 0 })
    })
  })

  describe('clearData', () => {
    it('should clear all data', () => {
      const store = useMarketStore()
      store.marketData = [
        { symbol: 'AAPL' } as MarketData
      ]
      store.latestPrices = {
        'AAPL': { symbol: 'AAPL', price: 150.0, timestamp: '2024-01-01T10:00:00Z' }
      }
      
      store.clearData()
      
      expect(store.marketData).toEqual([])
      expect(store.latestPrices).toEqual({})
    })
  })
})
