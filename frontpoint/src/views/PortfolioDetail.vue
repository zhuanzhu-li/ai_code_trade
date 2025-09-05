<template>
  <div class="portfolio-detail">
    <Layout>
      <div class="portfolio-detail-content">
        <!-- 投资组合头部信息 -->
        <div v-if="portfolioStore.currentPortfolio" class="portfolio-header">
          <div class="header-left">
            <el-button type="text" class="back-btn" @click="$router.back()">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="portfolio-info">
              <h1 class="portfolio-name">{{ portfolioStore.currentPortfolio.name }}</h1>
              <p class="portfolio-description">{{ portfolioStore.currentPortfolio.description || '暂无描述' }}</p>
            </div>
          </div>
          <div class="header-right">
            <el-tag :type="portfolioStore.currentPortfolio.is_active ? 'success' : 'info'" size="large">
              {{ portfolioStore.currentPortfolio.is_active ? '活跃' : '暂停' }}
            </el-tag>
          </div>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon primary">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">${{ portfolioStore.totalValue.toLocaleString() }}</div>
                <div class="stat-label">总资产价值</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="portfolioStore.totalPnL >= 0 ? 'success' : 'danger'">
                <el-icon size="24"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" :class="portfolioStore.totalPnL >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ portfolioStore.totalPnL.toLocaleString() }}
                </div>
                <div class="stat-label">总盈亏</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warning">
                <el-icon size="24"><Wallet /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">${{ portfolioStore.cashBalance.toLocaleString() }}</div>
                <div class="stat-label">现金余额</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="portfolioStore.totalPnLPercentage >= 0 ? 'success' : 'danger'">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" :class="portfolioStore.totalPnLPercentage >= 0 ? 'number-positive' : 'number-negative'">
                  {{ portfolioStore.totalPnLPercentage.toFixed(2) }}%
                </div>
                <div class="stat-label">盈亏率</div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 图表和持仓 -->
        <div class="content-grid">
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
          
          <!-- 持仓信息 -->
          <el-card class="positions-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">持仓信息</h3>
                <el-button type="primary" size="small" @click="$router.push('/trading')">
                  执行交易
                </el-button>
              </div>
            </template>
            <div v-if="portfolioStore.positions.length === 0" class="empty-container">
              <el-icon size="48" color="#c0c4cc">
                <Box />
              </el-icon>
              <p>暂无持仓</p>
            </div>
            <el-table v-else :data="portfolioStore.positions" style="width: 100%">
              <el-table-column prop="symbol" label="标的" width="80" />
              <el-table-column prop="quantity" label="数量" width="100" />
              <el-table-column prop="average_price" label="均价" width="100">
                <template #default="{ row }">
                  ${{ row.average_price.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="current_price" label="现价" width="100">
                <template #default="{ row }">
                  ${{ row.current_price.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="value" label="市值" width="100">
                <template #default="{ row }">
                  ${{ row.value.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="unrealized_pnl" label="浮动盈亏" width="120">
                <template #default="{ row }">
                  <span :class="row.unrealized_pnl >= 0 ? 'number-positive' : 'number-negative'">
                    ${{ row.unrealized_pnl.toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="unrealized_pnl_percentage" label="盈亏率" width="100">
                <template #default="{ row }">
                  <span :class="(row.unrealized_pnl / row.value * 100) >= 0 ? 'number-positive' : 'number-negative'">
                    {{ ((row.unrealized_pnl / row.value) * 100).toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        
        <!-- 最近交易记录 -->
        <el-card class="trades-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">最近交易记录</h3>
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
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                ${{ row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="{ row }">
                ${{ row.amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="fee" label="手续费" width="100">
              <template #default="{ row }">
                ${{ row.fee.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="executed_at" label="执行时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.executed_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  ArrowLeft,
  TrendCharts,
  Money,
  Wallet,
  Box
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useTradingStore } from '@/stores/trading'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const route = useRoute()
const portfolioStore = usePortfolioStore()
const tradingStore = useTradingStore()

const chartPeriod = ref('30d')

// 最近交易记录
const recentTrades = computed(() => 
  tradingStore.trades.filter(trade => 
    trade.portfolio_id === portfolioStore.currentPortfolio?.id
  ).slice(0, 10)
)

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

// 获取状态类型
const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'danger' => {
  const statusMap: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
    'completed': 'success',
    'pending': 'warning',
    'cancelled': 'info',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'completed': '已完成',
    'pending': '待处理',
    'cancelled': '已取消',
    'failed': '失败'
  }
  return statusMap[status] || status
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 初始化数据
onMounted(async () => {
  try {
    const portfolioId = Number(route.params.id)
    await Promise.all([
      portfolioStore.fetchPortfolio(portfolioId),
      portfolioStore.fetchPositions(portfolioId),
      tradingStore.fetchTrades({ portfolio_id: portfolioId, limit: 10 })
    ])
  } catch (error) {
    console.error('获取投资组合详情失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.portfolio-detail {
  height: 100vh;
  overflow: hidden;
}

.portfolio-detail-content {
  height: 100%;
  overflow-y: auto;
}

.portfolio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-base);
  border-radius: 8px;
  box-shadow: var(--shadow-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  font-size: 16px;
  color: var(--text-secondary);
  
  &:hover {
    color: var(--primary-color);
  }
}

.portfolio-info {
  .portfolio-name {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px 0;
  }
  
  .portfolio-description {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
    width: 48px;
    height: 48px;
    border-radius: 8px;
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
    
    &.danger {
      background: #fff2f0;
      color: #f56c6c;
    }
  }
  
  .stat-info {
    flex: 1;
  }
  
  .stat-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.content-grid {
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

.positions-card {
  .empty-container {
    text-align: center;
    padding: 40px;
    color: var(--text-secondary);
  }
}

.trades-card {
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .portfolio-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
