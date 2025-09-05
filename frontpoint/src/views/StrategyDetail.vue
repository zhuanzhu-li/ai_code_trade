<template>
  <div class="strategy-detail">
    <Layout>
      <div class="strategy-detail-content">
        <!-- 策略头部信息 -->
        <div v-if="strategyStore.currentStrategy" class="strategy-header">
          <div class="header-left">
            <el-button type="text" class="back-btn" @click="$router.back()">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="strategy-info">
              <h1 class="strategy-name">{{ strategyStore.currentStrategy.name }}</h1>
              <p class="strategy-description">{{ strategyStore.currentStrategy.description || '暂无描述' }}</p>
              <div class="strategy-meta">
                <el-tag :type="getStrategyTypeColor(strategyStore.currentStrategy.strategy_type)" size="large">
                  {{ getStrategyTypeName(strategyStore.currentStrategy.strategy_type) }}
                </el-tag>
                <el-tag :type="strategyStore.currentStrategy.is_active ? 'success' : 'info'" size="large">
                  {{ strategyStore.currentStrategy.is_active ? '活跃' : '暂停' }}
                </el-tag>
              </div>
            </div>
          </div>
          <div class="header-right">
            <el-button-group>
              <el-button 
                v-if="strategyStore.currentStrategy.is_active"
                type="warning" 
                @click="stopStrategy"
              >
                <el-icon><VideoPause /></el-icon>
                停止策略
              </el-button>
              <el-button 
                v-else
                type="success" 
                @click="startStrategy"
              >
                <el-icon><VideoPlay /></el-icon>
                启动策略
              </el-button>
              <el-button type="primary" @click="showExecuteDialog = true">
                <el-icon><Setting /></el-icon>
                执行策略
              </el-button>
            </el-button-group>
          </div>
        </div>
        
        <!-- 策略统计 -->
        <div class="stats-grid">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon primary">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyStore.currentStrategy?.performance.total_trades || 0 }}</div>
                <div class="stat-label">总交易次数</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon success">
                <el-icon size="24"><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyStore.currentStrategy?.performance.winning_trades || 0 }}</div>
                <div class="stat-label">盈利交易</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="(strategyStore.currentStrategy?.performance.win_rate || 0) >= 50 ? 'success' : 'warning'">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ (strategyStore.currentStrategy?.performance.win_rate || 0).toFixed(1) }}%</div>
                <div class="stat-label">胜率</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="(strategyStore.currentStrategy?.performance.total_pnl || 0) >= 0 ? 'success' : 'danger'">
                <el-icon size="24"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" :class="(strategyStore.currentStrategy?.performance.total_pnl || 0) >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ (strategyStore.currentStrategy?.performance.total_pnl || 0).toLocaleString() }}
                </div>
                <div class="stat-label">总盈亏</div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 策略参数和图表 -->
        <div class="content-grid">
          <!-- 策略参数 -->
          <el-card class="parameters-card">
            <template #header>
              <h3 class="card-title">策略参数</h3>
            </template>
            <div class="parameters-list">
              <div 
                v-for="(value, key) in strategyStore.currentStrategy?.parameters" 
                :key="key"
                class="parameter-item"
              >
                <div class="parameter-key">{{ getParameterLabel(key) }}</div>
                <div class="parameter-value">{{ value }}</div>
              </div>
            </div>
          </el-card>
          
          <!-- 策略表现图表 -->
          <el-card class="chart-card">
            <template #header>
              <h3 class="card-title">策略表现</h3>
            </template>
            <div class="chart-container">
              <v-chart :option="performanceChartOption" class="chart" />
            </div>
          </el-card>
        </div>
        
        <!-- 策略执行记录 -->
        <el-card class="executions-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">执行记录</h3>
              <el-button type="primary" size="small" @click="showExecuteDialog = true">
                新建执行
              </el-button>
            </div>
          </template>
          <el-table :data="strategyExecutions" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="portfolio_id" label="投资组合" width="120">
              <template #default="{ row }">
                {{ getPortfolioName(row.portfolio_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="end_time" label="结束时间" width="160">
              <template #default="{ row }">
                {{ row.end_time ? formatTime(row.end_time) : '进行中' }}
              </template>
            </el-table-column>
            <el-table-column prop="initial_capital" label="初始资金" width="120">
              <template #default="{ row }">
                ${{ row.initial_capital.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="current_value" label="当前价值" width="120">
              <template #default="{ row }">
                ${{ row.current_value.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="total_pnl" label="总盈亏" width="120">
              <template #default="{ row }">
                <span :class="row.total_pnl >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ row.total_pnl.toLocaleString() }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="total_pnl_percentage" label="盈亏率" width="100">
              <template #default="{ row }">
                <span :class="row.total_pnl_percentage >= 0 ? 'number-positive' : 'number-negative'">
                  {{ row.total_pnl_percentage.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '活跃' : '已停止' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button 
                  v-if="row.is_active"
                  size="small" 
                  type="warning" 
                  @click="stopExecution(row)"
                >
                  停止
                </el-button>
                <el-button 
                  v-else
                  size="small" 
                  type="success" 
                  @click="startExecution(row)"
                >
                  启动
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </Layout>
    
    <!-- 执行策略对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行策略"
      width="400px"
    >
      <el-form
        ref="executeFormRef"
        :model="executeForm"
        :rules="executeFormRules"
        label-width="100px"
      >
        <el-form-item label="投资组合" prop="portfolio_id">
          <el-select v-model="executeForm.portfolio_id" placeholder="请选择投资组合" style="width: 100%">
            <el-option
              v-for="portfolio in portfolioStore.portfolios"
              :key="portfolio.id"
              :label="portfolio.name"
              :value="portfolio.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="初始资金" prop="initial_capital">
          <el-input-number
            v-model="executeForm.initial_capital"
            :min="1000"
            :precision="2"
            placeholder="请输入初始资金"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showExecuteDialog = false">取消</el-button>
          <el-button type="primary" :loading="executeLoading" @click="handleExecute">
            开始执行
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  ArrowLeft,
  VideoPause,
  VideoPlay,
  Setting,
  TrendCharts,
  Check,
  Money
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { useStrategyStore } from '@/stores/strategy'
import { usePortfolioStore } from '@/stores/portfolio'
import { useAuthStore } from '@/stores/auth'
import type { ExecuteStrategyRequest, StrategyExecution } from '@/types'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const route = useRoute()
const strategyStore = useStrategyStore()
const portfolioStore = usePortfolioStore()
const authStore = useAuthStore()

const showExecuteDialog = ref(false)
const executeLoading = ref(false)
const executeFormRef = ref<FormInstance>()

// 策略执行记录（模拟数据）
const strategyExecutions = ref<StrategyExecution[]>([
  {
    id: 1,
    strategy_id: 1,
    portfolio_id: 1,
    start_time: '2024-01-01T00:00:00Z',
    end_time: undefined,
    is_active: true,
    initial_capital: 10000,
    current_value: 10500,
    total_pnl: 500,
    total_pnl_percentage: 5.0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }
])

const executeForm = reactive<ExecuteStrategyRequest>({
  portfolio_id: 0,
  initial_capital: 10000
})

const executeFormRules: FormRules = {
  portfolio_id: [
    { required: true, message: '请选择投资组合', trigger: 'change' }
  ],
  initial_capital: [
    { required: true, message: '请输入初始资金', trigger: 'blur' },
    { type: 'number', min: 1000, message: '初始资金不能少于1000', trigger: 'blur' }
  ]
}

// 策略表现图表配置
const performanceChartOption = computed(() => ({
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
      name: '策略价值',
      type: 'line',
      data: generatePerformanceData(),
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
  const labels = []
  for (let i = 29; i >= 0; i--) {
    labels.push(dayjs().subtract(i, 'day').format('MM-DD'))
  }
  return labels
}

// 生成表现数据
const generatePerformanceData = () => {
  const data = []
  let baseValue = 10000
  for (let i = 0; i < 30; i++) {
    baseValue += (Math.random() - 0.5) * baseValue * 0.02
    data.push(Math.round(baseValue))
  }
  return data
}

// 获取策略类型颜色
const getStrategyTypeColor = (type: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const colorMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'momentum': 'primary',
    'mean_reversion': 'success'
  }
  return colorMap[type] || 'info'
}

// 获取策略类型名称
const getStrategyTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    'momentum': '动量策略',
    'mean_reversion': '均值回归策略'
  }
  return nameMap[type] || type
}

// 获取参数标签
const getParameterLabel = (key: string) => {
  const labelMap: Record<string, string> = {
    'lookback_period': '回望周期',
    'rsi_period': 'RSI周期',
    'position_size_percentage': '仓位比例',
    'bb_period': '布林带周期',
    'bb_std': '布林带标准差'
  }
  return labelMap[key] || key
}

// 获取投资组合名称
const getPortfolioName = (portfolioId: number) => {
  const portfolio = portfolioStore.portfolios.find(p => p.id === portfolioId)
  return portfolio?.name || `投资组合 ${portfolioId}`
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 启动策略
const startStrategy = async () => {
  try {
    if (strategyStore.currentStrategy) {
      strategyStore.currentStrategy.is_active = true
      ElMessage.success('策略已启动')
    }
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

// 停止策略
const stopStrategy = async () => {
  try {
    if (strategyStore.currentStrategy) {
      await strategyStore.stopStrategy(strategyStore.currentStrategy.id)
      ElMessage.success('策略已停止')
    }
  } catch (error) {
    ElMessage.error('停止失败')
  }
}

// 启动执行
const startExecution = (execution: StrategyExecution) => {
  execution.is_active = true
  ElMessage.success('执行已启动')
}

// 停止执行
const stopExecution = (execution: StrategyExecution) => {
  execution.is_active = false
  execution.end_time = new Date().toISOString()
  ElMessage.success('执行已停止')
}

// 执行策略
const handleExecute = async () => {
  if (!executeFormRef.value || !strategyStore.currentStrategy) return
  
  try {
    await executeFormRef.value.validate()
    executeLoading.value = true
    
    await strategyStore.executeStrategy(strategyStore.currentStrategy.id, executeForm)
    ElMessage.success('策略开始执行')
    showExecuteDialog.value = false
  } catch (error) {
    console.error('执行策略失败:', error)
  } finally {
    executeLoading.value = false
  }
}

// 初始化数据
onMounted(async () => {
  try {
    const strategyId = Number(route.params.id)
    const userId = authStore.user?.id
    
    if (userId) {
      await Promise.all([
        strategyStore.fetchStrategy(strategyId),
        portfolioStore.fetchPortfolios(userId)
      ])
    }
  } catch (error) {
    console.error('获取策略详情失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.strategy-detail {
  height: 100vh;
  overflow: hidden;
}

.strategy-detail-content {
  height: 100%;
  overflow-y: auto;
}

.strategy-header {
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

.strategy-info {
  .strategy-name {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px 0;
  }
  
  .strategy-description {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0 0 8px 0;
  }
  
  .strategy-meta {
    display: flex;
    gap: 8px;
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
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 24px;
}

.parameters-card {
  .parameters-list {
    .parameter-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--border-light);
      
      &:last-child {
        border-bottom: none;
      }
      
      .parameter-key {
        font-size: 14px;
        color: var(--text-secondary);
      }
      
      .parameter-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }
  }
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

.executions-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
  
  .strategy-header {
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
