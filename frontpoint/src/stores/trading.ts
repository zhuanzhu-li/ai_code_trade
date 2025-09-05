import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'
import type { Trade, CreateTradeRequest } from '@/types'

export const useTradingStore = defineStore('trading', () => {
  const trades = ref<Trade[]>([])
  const loading = ref(false)

  // 获取交易记录
  const fetchTrades = async (params?: {
    portfolio_id?: number
    symbol?: string
    limit?: number
  }) => {
    loading.value = true
    try {
      trades.value = await apiClient.getTrades(params)
    } catch (error) {
      console.error('获取交易记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 执行交易
  const executeTrade = async (data: CreateTradeRequest) => {
    loading.value = true
    try {
      const newTrade = await apiClient.createTrade(data)
      trades.value.unshift(newTrade)
      return newTrade
    } catch (error) {
      console.error('执行交易失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 按投资组合分组交易
  const tradesByPortfolio = computed(() => {
    const grouped: Record<number, Trade[]> = {}
    trades.value.forEach(trade => {
      if (!grouped[trade.portfolio_id]) {
        grouped[trade.portfolio_id] = []
      }
      grouped[trade.portfolio_id].push(trade)
    })
    return grouped
  })

  // 按标的分组交易
  const tradesBySymbol = computed(() => {
    const grouped: Record<string, Trade[]> = {}
    trades.value.forEach(trade => {
      if (!grouped[trade.symbol]) {
        grouped[trade.symbol] = []
      }
      grouped[trade.symbol].push(trade)
    })
    return grouped
  })

  // 计算总交易次数
  const totalTrades = computed(() => trades.value.length)

  // 计算盈利交易次数
  const winningTrades = computed(() => 
    trades.value.filter(trade => trade.pnl > 0).length
  )

  // 计算胜率
  const winRate = computed(() => {
    if (totalTrades.value === 0) return 0
    return (winningTrades.value / totalTrades.value) * 100
  })

  // 计算总盈亏
  const totalPnL = computed(() => 
    trades.value.reduce((sum, trade) => sum + trade.pnl, 0)
  )

  // 计算总交易金额
  const totalAmount = computed(() => 
    trades.value.reduce((sum, trade) => sum + trade.amount, 0)
  )

  // 计算总手续费
  const totalFees = computed(() => 
    trades.value.reduce((sum, trade) => sum + trade.fee, 0)
  )

  // 获取最近交易
  const recentTrades = computed(() => 
    trades.value.slice(0, 10)
  )

  // 按状态分组
  const tradesByStatus = computed(() => {
    const grouped: Record<string, Trade[]> = {}
    trades.value.forEach(trade => {
      if (!grouped[trade.status]) {
        grouped[trade.status] = []
      }
      grouped[trade.status].push(trade)
    })
    return grouped
  })

  return {
    trades,
    loading,
    tradesByPortfolio,
    tradesBySymbol,
    totalTrades,
    winningTrades,
    winRate,
    totalPnL,
    totalAmount,
    totalFees,
    recentTrades,
    tradesByStatus,
    fetchTrades,
    executeTrade
  }
})
