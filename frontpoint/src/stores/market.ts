import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'
import type { MarketData, LatestPrice } from '@/types'

export const useMarketStore = defineStore('market', () => {
  const marketData = ref<MarketData[]>([])
  const latestPrices = ref<Record<string, LatestPrice>>({})
  const loading = ref(false)

  // 获取市场数据
  const fetchMarketData = async (
    symbol: string,
    params?: {
      start_date?: string
      end_date?: string
      limit?: number
    }
  ) => {
    loading.value = true
    try {
      const data = await apiClient.getMarketData(symbol, params)
      marketData.value = data
      return data
    } catch (error) {
      console.error('获取市场数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取最新价格
  const fetchLatestPrice = async (symbol: string) => {
    try {
      const price = await apiClient.getLatestPrice(symbol)
      latestPrices.value[symbol] = price
      return price
    } catch (error) {
      console.error('获取最新价格失败:', error)
      throw error
    }
  }

  // 批量获取最新价格
  const fetchLatestPrices = async (symbols: string[]) => {
    const promises = symbols.map(symbol => fetchLatestPrice(symbol))
    try {
      await Promise.all(promises)
    } catch (error) {
      console.error('批量获取最新价格失败:', error)
      throw error
    }
  }

  // 获取价格历史数据（用于图表）
  const getPriceHistory = computed(() => {
    if (marketData.value.length === 0) return []
    
    return marketData.value.map(data => ({
      time: data.timestamp,
      open: data.open_price,
      high: data.high_price,
      low: data.low_price,
      close: data.close_price,
      volume: data.volume
    }))
  })

  // 获取价格变化数据
  const getPriceChanges = computed(() => {
    if (marketData.value.length === 0) return []
    
    return marketData.value.map(data => ({
      time: data.timestamp,
      price: data.close_price,
      change: data.price_change,
      changePercent: data.price_change_percentage
    }))
  })

  // 获取成交量数据
  const getVolumeData = computed(() => {
    if (marketData.value.length === 0) return []
    
    return marketData.value.map(data => ({
      time: data.timestamp,
      volume: data.volume
    }))
  })

  // 计算技术指标
  const calculateRSI = (period: number = 14) => {
    if (marketData.value.length < period) return []
    
    const prices = marketData.value.map(d => d.close_price)
    const rsi: number[] = []
    
    for (let i = period; i < prices.length; i++) {
      const gains: number[] = []
      const losses: number[] = []
      
      for (let j = i - period + 1; j <= i; j++) {
        const change = prices[j] - prices[j - 1]
        if (change > 0) {
          gains.push(change)
          losses.push(0)
        } else {
          gains.push(0)
          losses.push(-change)
        }
      }
      
      const avgGain = gains.reduce((sum, gain) => sum + gain, 0) / period
      const avgLoss = losses.reduce((sum, loss) => sum + loss, 0) / period
      
      if (avgLoss === 0) {
        rsi.push(100)
      } else {
        const rs = avgGain / avgLoss
        const rsiValue = 100 - (100 / (1 + rs))
        rsi.push(rsiValue)
      }
    }
    
    return rsi
  }

  // 计算移动平均线
  const calculateMA = (period: number) => {
    if (marketData.value.length < period) return []
    
    const prices = marketData.value.map(d => d.close_price)
    const ma: number[] = []
    
    for (let i = period - 1; i < prices.length; i++) {
      const sum = prices.slice(i - period + 1, i + 1).reduce((s, p) => s + p, 0)
      ma.push(sum / period)
    }
    
    return ma
  }

  // 获取当前价格
  const getCurrentPrice = (symbol: string) => {
    return latestPrices.value[symbol]?.price || 0
  }

  // 获取价格变化
  const getPriceChange = (symbol: string) => {
    const latest = latestPrices.value[symbol]
    if (!latest) return { change: 0, changePercent: 0 }
    
    // 这里需要计算与前一天的价格变化
    // 简化处理，实际应该从历史数据中获取
    return { change: 0, changePercent: 0 }
  }

  // 清除数据
  const clearData = () => {
    marketData.value = []
    latestPrices.value = {}
  }

  return {
    marketData,
    latestPrices,
    loading,
    getPriceHistory,
    getPriceChanges,
    getVolumeData,
    calculateRSI,
    calculateMA,
    getCurrentPrice,
    getPriceChange,
    fetchMarketData,
    fetchLatestPrice,
    fetchLatestPrices,
    clearData
  }
})
