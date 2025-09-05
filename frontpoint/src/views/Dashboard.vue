<template>
  <div class="dashboard">
    <Layout>
      <div class="dashboard-content">
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <el-card v-for="stat in stats" :key="stat.title" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="stat.type">
                <el-icon :size="32">
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-title">{{ stat.title }}</div>
                <div class="stat-change" :class="stat.changeType">
                  <el-icon v-if="stat.changeType === 'positive'">
                    <ArrowUp />
                  </el-icon>
                  <el-icon v-else-if="stat.changeType === 'negative'">
                    <ArrowDown />
                  </el-icon>
                  {{ stat.change }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 图表区域 -->
        <div class="charts-grid">
          <!-- 资产价值趋势图 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">资产价值趋势</h3>
                <el-select v-model="chartPeriod" size="small" style="width: 120px">
                  <el-option label="7天" value="7d" />
                  <el-option label="30天" value="30d" />
                  <el-option label="90天" value="90d" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <v-chart :option="valueChartOption" class="chart" />
            </div>
          </el-card>
          
          <!-- 盈亏分布图 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">盈亏分布</h3>
              </div>
            </template>
            <div class="chart-container">
              <v-chart :option="pnlChartOption" class="chart" />
            </div>
          </el-card>
        </div>
        
        <!-- 最近交易和风险警报 -->
        <div class="bottom-grid">
          <!-- 最近交易 -->
          <el-card class="table-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">最近交易</h3>
                <el-button type="primary" size="small" @click="$router.push('/trading')">
                  查看全部
                </el-button>
              </div>
            </template>
            <el-table :data="recentTrades" style="width: 100%">
              <el-table-column prop="symbol" label="标的" width="80" />
              <el-table-column prop="side" label="方向" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.side === 'buy' ? 'success' : 'danger'" size="small">
                    {{ row.side === 'buy' ? '买入' : '卖出' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="80" />
              <el-table-column prop="price" label="价格" width="100">
                <template #default="{ row }">
                  ${{ row.price.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="100">
                <template #default="{ row }">
                  ${{ row.amount.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="pnl" label="盈亏" width="100">
                <template #default="{ row }">
                  <span :class="row.pnl >= 0 ? 'number-positive' : 'number-negative'">
                    ${{ row.pnl.toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="executed_at" label="时间" width="120">
                <template #default="{ row }">
                  {{ formatTime(row.executed_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
          
          <!-- 风险警报 -->
          <el-card class="table-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">风险警报</h3>
                <el-button type="primary" size="small" @click="$router.push('/risk')">
                  查看全部
                </el-button>
              </div>
            </template>
            <div v-if="riskAlerts.length === 0" class="empty-container">
              <el-icon size="48" color="#c0c4cc">
                <Check />
              </el-icon>
              <p>暂无风险警报</p>
            </div>
            <div v-else class="alert-list">
              <div
                v-for="alert in riskAlerts"
                :key="alert.id"
                class="alert-item"
                :class="alert.alert_type"
              >
                <el-icon>
                  <Warning v-if="alert.alert_type === 'warning'" />
                  <CircleClose v-else-if="alert.alert_type === 'error'" />
                  <InfoFilled v-else />
                </el-icon>
                <div class="alert-content">
                  <div class="alert-message">{{ alert.message }}</div>
                  <div class="alert-time">{{ formatTime(alert.created_at) }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  ArrowUp,
  ArrowDown,
  Warning,
  Check,
  CircleClose,
  InfoFilled
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useTradingStore } from '@/stores/trading'
import { useStrategyStore } from '@/stores/strategy'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const portfolioStore = usePortfolioStore()
const tradingStore = useTradingStore()
const strategyStore = useStrategyStore()

const chartPeriod = ref('30d')

// 统计数据
const stats = computed(() => [
  {
    title: '总资产价值',
    value: `$${portfolioStore.totalValue.toLocaleString()}`,
    change: '+5.2%',
    changeType: 'positive',
    icon: 'TrendCharts',
    type: 'primary'
  },
  {
    title: '总盈亏',
    value: `$${portfolioStore.totalPnL.toLocaleString()}`,
    change: `+${portfolioStore.totalPnLPercentage.toFixed(2)}%`,
    changeType: portfolioStore.totalPnL >= 0 ? 'positive' : 'negative',
    icon: 'Money',
    type: portfolioStore.totalPnL >= 0 ? 'success' : 'danger'
  },
  {
    title: '活跃策略',
    value: strategyStore.activeStrategiesCount.toString(),
    change: `${strategyStore.totalStrategies} 个策略`,
    changeType: 'neutral',
    icon: 'Setting',
    type: 'info'
  },
  {
    title: '现金余额',
    value: `$${portfolioStore.cashBalance.toLocaleString()}`,
    change: '可用资金',
    changeType: 'neutral',
    icon: 'Wallet',
    type: 'warning'
  }
])

// 最近交易
const recentTrades = computed(() => tradingStore.recentTrades)

// 风险警报（模拟数据）
const riskAlerts = ref([
  {
    id: 1,
    alert_type: 'warning',
    message: 'AAPL持仓超过20%限制',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    alert_type: 'info',
    message: '策略执行完成',
    created_at: '2024-01-15T09:15:00Z'
  }
])

// 资产价值趋势图配置
const valueChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: generateTimeLabels()
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '${value}'
    }
  },
  series: [
    {
      name: '资产价值',
      type: 'line',
      data: generateValueData(),
      smooth: true,
      lineStyle: {
        color: '#409eff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ]
        }
      }
    }
  ]
}))

// 盈亏分布图配置
const pnlChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '盈亏分布',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 35, name: '盈利交易' },
        { value: 15, name: '亏损交易' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

// 生成时间标签
const generateTimeLabels = () => {
  const days = chartPeriod.value === '7d' ? 7 : chartPeriod.value === '30d' ? 30 : 90
  const labels = []
  for (let i = days - 1; i >= 0; i--) {
    labels.push(dayjs().subtract(i, 'day').format('MM-DD'))
  }
  return labels
}

// 生成价值数据
const generateValueData = () => {
  const days = chartPeriod.value === '7d' ? 7 : chartPeriod.value === '30d' ? 30 : 90
  const data = []
  let baseValue = portfolioStore.totalValue * 0.9
  for (let i = 0; i < days; i++) {
    baseValue += (Math.random() - 0.5) * baseValue * 0.02
    data.push(Math.round(baseValue))
  }
  return data
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 初始化数据
onMounted(async () => {
  try {
    // 这里需要根据实际用户ID获取数据
    const userId = 1
    await Promise.all([
      portfolioStore.fetchPortfolios(userId),
      tradingStore.fetchTrades({ limit: 10 }),
      strategyStore.fetchStrategies(userId)
    ])
  } catch (error) {
    console.error('初始化仪表板数据失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  height: 100vh;
  overflow: hidden;
}

.dashboard-content {
  height: 100%;
  overflow-y: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.primary {
      background: #e6f7ff;
      color: #409eff;
    }
    
    &.success {
      background: #f6ffed;
      color: #67c23a;
    }
    
    &.warning {
      background: #fffbe6;
      color: #e6a23c;
    }
    
    &.info {
      background: #f4f4f5;
      color: #909399;
    }
    
    &.danger {
      background: #fff2f0;
      color: #f56c6c;
    }
  }
  
  .stat-info {
    flex: 1;
  }
  
  .stat-value {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .stat-title {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }
  
  .stat-change {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
    
    &.positive {
      color: var(--success-color);
    }
    
    &.negative {
      color: var(--danger-color);
    }
    
    &.neutral {
      color: var(--text-secondary);
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  .chart-container {
    height: 300px;
  }
  
  .chart {
    width: 100%;
    height: 100%;
  }
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.table-card {
  .empty-container {
    text-align: center;
    padding: 40px;
    color: var(--text-secondary);
  }
}

.alert-list {
  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 8px;
    
    &.warning {
      background: #fff7e6;
      border-left: 4px solid #e6a23c;
    }
    
    &.error {
      background: #fff2f0;
      border-left: 4px solid #f56c6c;
    }
    
    &.info {
      background: #f0f9ff;
      border-left: 4px solid #409eff;
    }
    
    .alert-content {
      flex: 1;
    }
    
    .alert-message {
      font-size: 14px;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    .alert-time {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
