import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'
import type { Portfolio, Position, CreatePortfolioRequest } from '@/types'

export const usePortfolioStore = defineStore('portfolio', () => {
  const portfolios = ref<Portfolio[]>([])
  const currentPortfolio = ref<Portfolio | null>(null)
  const positions = ref<Position[]>([])
  const loading = ref(false)

  // 获取投资组合列表
  const fetchPortfolios = async (userId: number) => {
    loading.value = true
    try {
      portfolios.value = await apiClient.getPortfolios(userId)
    } catch (error) {
      console.error('获取投资组合列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取投资组合详情
  const fetchPortfolio = async (portfolioId: number) => {
    loading.value = true
    try {
      currentPortfolio.value = await apiClient.getPortfolio(portfolioId)
    } catch (error) {
      console.error('获取投资组合详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建投资组合
  const createPortfolio = async (data: CreatePortfolioRequest) => {
    loading.value = true
    try {
      const newPortfolio = await apiClient.createPortfolio(data)
      portfolios.value.push(newPortfolio)
      return newPortfolio
    } catch (error) {
      console.error('创建投资组合失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取持仓信息
  const fetchPositions = async (portfolioId: number) => {
    loading.value = true
    try {
      positions.value = await apiClient.getPositions(portfolioId)
    } catch (error) {
      console.error('获取持仓信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新投资组合信息
  const updatePortfolio = (portfolio: Portfolio) => {
    const index = portfolios.value.findIndex(p => p.id === portfolio.id)
    if (index !== -1) {
      portfolios.value[index] = portfolio
    }
    if (currentPortfolio.value?.id === portfolio.id) {
      currentPortfolio.value = portfolio
    }
  }

  // 计算总价值
  const totalValue = computed(() => {
    if (!currentPortfolio.value) return 0
    return currentPortfolio.value.current_value
  })

  // 计算总盈亏
  const totalPnL = computed(() => {
    if (!currentPortfolio.value) return 0
    return currentPortfolio.value.total_pnl
  })

  // 计算总盈亏百分比
  const totalPnLPercentage = computed(() => {
    if (!currentPortfolio.value) return 0
    return currentPortfolio.value.total_pnl_percentage
  })

  // 计算现金余额
  const cashBalance = computed(() => {
    if (!currentPortfolio.value) return 0
    return currentPortfolio.value.cash_balance
  })

  return {
    portfolios,
    currentPortfolio,
    positions,
    loading,
    totalValue,
    totalPnL,
    totalPnLPercentage,
    cashBalance,
    fetchPortfolios,
    fetchPortfolio,
    createPortfolio,
    fetchPositions,
    updatePortfolio
  }
})
