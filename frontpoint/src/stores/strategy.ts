import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api'
import type { Strategy, StrategyExecution, CreateStrategyRequest, ExecuteStrategyRequest } from '@/types'

export const useStrategyStore = defineStore('strategy', () => {
  const strategies = ref<Strategy[]>([])
  const currentStrategy = ref<Strategy | null>(null)
  const executions = ref<StrategyExecution[]>([])
  const loading = ref(false)

  // 获取策略列表
  const fetchStrategies = async (userId: number) => {
    loading.value = true
    try {
      strategies.value = await apiClient.getStrategies(userId)
    } catch (error) {
      console.error('获取策略列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取策略详情
  const fetchStrategy = async (strategyId: number) => {
    loading.value = true
    try {
      currentStrategy.value = await apiClient.getStrategy(strategyId)
    } catch (error) {
      console.error('获取策略详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建策略
  const createStrategy = async (data: CreateStrategyRequest) => {
    loading.value = true
    try {
      const newStrategy = await apiClient.createStrategy(data)
      strategies.value.push(newStrategy)
      return newStrategy
    } catch (error) {
      console.error('创建策略失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 执行策略
  const executeStrategy = async (strategyId: number, data: ExecuteStrategyRequest) => {
    loading.value = true
    try {
      const execution = await apiClient.executeStrategy(strategyId, data)
      executions.value.push(execution)
      return execution
    } catch (error) {
      console.error('执行策略失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 停止策略
  const stopStrategy = async (strategyId: number) => {
    loading.value = true
    try {
      await apiClient.stopStrategy(strategyId)
      // 更新策略状态
      const strategy = strategies.value.find(s => s.id === strategyId)
      if (strategy) {
        strategy.is_active = false
      }
    } catch (error) {
      console.error('停止策略失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新策略
  const updateStrategy = (strategy: Strategy) => {
    const index = strategies.value.findIndex(s => s.id === strategy.id)
    if (index !== -1) {
      strategies.value[index] = strategy
    }
    if (currentStrategy.value?.id === strategy.id) {
      currentStrategy.value = strategy
    }
  }

  // 活跃策略
  const activeStrategies = computed(() => 
    strategies.value.filter(s => s.is_active)
  )

  // 按类型分组策略
  const strategiesByType = computed(() => {
    const grouped: Record<string, Strategy[]> = {}
    strategies.value.forEach(strategy => {
      if (!grouped[strategy.strategy_type]) {
        grouped[strategy.strategy_type] = []
      }
      grouped[strategy.strategy_type].push(strategy)
    })
    return grouped
  })

  // 活跃执行
  const activeExecutions = computed(() => 
    executions.value.filter(e => e.is_active)
  )

  // 总策略数
  const totalStrategies = computed(() => strategies.value.length)

  // 活跃策略数
  const activeStrategiesCount = computed(() => activeStrategies.value.length)

  // 总执行次数
  const totalExecutions = computed(() => executions.value.length)

  // 活跃执行次数
  const activeExecutionsCount = computed(() => activeExecutions.value.length)

  // 平均胜率
  const averageWinRate = computed(() => {
    if (strategies.value.length === 0) return 0
    const totalWinRate = strategies.value.reduce((sum, s) => sum + s.performance.win_rate, 0)
    return totalWinRate / strategies.value.length
  })

  // 总策略盈亏
  const totalStrategyPnL = computed(() => 
    strategies.value.reduce((sum, s) => sum + s.performance.total_pnl, 0)
  )

  return {
    strategies,
    currentStrategy,
    executions,
    loading,
    activeStrategies,
    strategiesByType,
    activeExecutions,
    totalStrategies,
    activeStrategiesCount,
    totalExecutions,
    activeExecutionsCount,
    averageWinRate,
    totalStrategyPnL,
    fetchStrategies,
    fetchStrategy,
    createStrategy,
    executeStrategy,
    stopStrategy,
    updateStrategy
  }
})
