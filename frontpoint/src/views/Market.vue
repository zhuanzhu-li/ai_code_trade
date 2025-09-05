<template>
  <div class="market">
    <Layout>
      <div class="market-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">市场数据</h1>
            <p class="page-subtitle">实时市场数据和价格走势</p>
          </div>
          <div class="header-right">
            <el-select v-model="selectedSymbol" placeholder="选择标的" style="width: 150px" @change="handleSymbolChange">
              <el-option label="AAPL" value="AAPL" />
              <el-option label="GOOGL" value="GOOGL" />
              <el-option label="MSFT" value="MSFT" />
              <el-option label="TSLA" value="TSLA" />
              <el-option label="BTCUSDT" value="BTCUSDT" />
            </el-select>
          </div>
        </div>
        
        <!-- 价格概览 -->
        <div v-if="latestPrice" class="price-overview">
          <el-card class="price-card">
            <div class="price-content">
              <div class="price-info">
                <h2 class="symbol">{{ selectedSymbol }}</h2>
                <div class="current-price">${{ latestPrice.price.toFixed(2) }}</div>
                <div class="price-change" :class="priceChange >= 0 ? 'positive' : 'negative'">
                  <el-icon>
                    <ArrowUp v-if="priceChange >= 0" />
                    <ArrowDown v-else />
                  </el-icon>
                  {{ Math.abs(priceChange).toFixed(2) }} ({{ Math.abs(priceChangePercent).toFixed(2) }}%)
                </div>
              </div>
              <div class="price-time">
                <div class="time-label">更新时间</div>
                <div class="time-value">{{ formatTime(latestPrice.timestamp) }}</div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 图表区域 -->
        <div class="charts-section">
          <!-- K线图 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <h3 class="card-title">价格走势</h3>
                <div class="chart-controls">
                  <el-radio-group v-model="chartType" size="small">
                    <el-radio-button label="candlestick">K线</el-radio-button>
                    <el-radio-button label="line">折线</el-radio-button>
                  </el-radio-group>
                  <el-select v-model="timeframe" size="small" style="width: 100px; margin-left: 12px">
                    <el-option label="1分钟" value="1m" />
                    <el-option label="5分钟" value="5m" />
                    <el-option label="15分钟" value="15m" />
                    <el-option label="1小时" value="1h" />
                    <el-option label="1天" value="1d" />
                  </el-select>
                </div>
              </div>
            </template>
            <div class="chart-container large">
              <v-chart :option="priceChartOption" class="chart" />
            </div>
          </el-card>
          
          <!-- 技术指标 -->
          <div class="indicators-grid">
            <!-- RSI指标 -->
            <el-card class="indicator-card">
              <template #header>
                <h3 class="card-title">RSI指标</h3>
              </template>
              <div class="chart-container small">
                <v-chart :option="rsiChartOption" class="chart" />
              </div>
            </el-card>
            
            <!-- 成交量 -->
            <el-card class="indicator-card">
              <template #header>
                <h3 class="card-title">成交量</h3>
              </template>
              <div class="chart-container small">
                <v-chart :option="volumeChartOption" class="chart" />
              </div>
            </el-card>
          </div>
        </div>
        
        <!-- 市场数据表格 -->
        <el-card class="data-table-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">历史数据</h3>
              <div class="table-controls">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="small"
                  @change="handleDateChange"
                />
                <el-button size="small" @click="refreshData">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table
            v-loading="marketStore.loading"
            :data="marketData"
            style="width: 100%"
            max-height="400"
          >
            <el-table-column prop="timestamp" label="时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="open_price" label="开盘价" width="100">
              <template #default="{ row }">
                ${{ row.open_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="high_price" label="最高价" width="100">
              <template #default="{ row }">
                ${{ row.high_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="low_price" label="最低价" width="100">
              <template #default="{ row }">
                ${{ row.low_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="close_price" label="收盘价" width="100">
              <template #default="{ row }">
                ${{ row.close_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="120">
              <template #default="{ row }">
                {{ row.volume.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="price_change" label="涨跌额" width="100">
              <template #default="{ row }">
                <span :class="row.price_change >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ row.price_change.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="price_change_percentage" label="涨跌幅" width="100">
              <template #default="{ row }">
                <span :class="row.price_change_percentage >= 0 ? 'number-positive' : 'number-negative'">
                  {{ row.price_change_percentage.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, CandlestickChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ArrowUp, ArrowDown, Refresh } from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { useMarketStore } from '@/stores/market'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  CandlestickChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

const marketStore = useMarketStore()

const selectedSymbol = ref('AAPL')
const chartType = ref('candlestick')
const timeframe = ref('1d')
const dateRange = ref<[Date, Date]>([
  dayjs().subtract(30, 'day').toDate(),
  dayjs().toDate()
])

// 最新价格
const latestPrice = computed(() => marketStore.latestPrices[selectedSymbol.value])

// 价格变化
const priceChange = computed(() => {
  if (!latestPrice.value) return 0
  // 这里应该计算与前一天的价格变化，简化处理
  return 0
})

const priceChangePercent = computed(() => {
  if (!latestPrice.value) return 0
  // 这里应该计算价格变化百分比，简化处理
  return 0
})

// 市场数据
const marketData = computed(() => marketStore.marketData)

// 价格图表配置
const priceChartOption = computed(() => {
  const data = marketStore.getPriceHistory
  if (data.length === 0) return {}
  
  const dates = data.map(item => item.time)
  const prices = data.map(item => [item.open, item.close, item.low, item.high])
  
  return {
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
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax'
    },
    yAxis: {
      scale: true,
      splitArea: {
        show: true
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        show: true,
        start: 50,
        end: 100,
        handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
        handleSize: '80%',
        handleStyle: {
          color: '#fff',
          shadowBlur: 3,
          shadowColor: 'rgba(0, 0, 0, 0.6)',
          shadowOffsetX: 2,
          shadowOffsetY: 2
        }
      }
    ],
    series: [
      {
        name: '价格',
        type: chartType.value === 'candlestick' ? 'candlestick' : 'line',
        data: chartType.value === 'candlestick' ? prices : data.map(item => item.close),
        itemStyle: {
          color: '#ec0000',
          color0: '#00da3c',
          borderColor: '#8A0000',
          borderColor0: '#008F28'
        }
      }
    ]
  }
})

// RSI图表配置
const rsiChartOption = computed(() => {
  const rsiData = marketStore.calculateRSI(14)
  const dates = marketStore.getPriceHistory.map(item => item.time).slice(14)
  
  return {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: 'RSI',
        type: 'line',
        data: rsiData,
        lineStyle: {
          color: '#409eff'
        },
        markLine: {
          data: [
            { yAxis: 70, name: '超买线' },
            { yAxis: 30, name: '超卖线' }
          ]
        }
      }
    ]
  }
})

// 成交量图表配置
const volumeChartOption = computed(() => {
  const data = marketStore.getVolumeData
  
  return {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.time)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '成交量',
        type: 'bar',
        data: data.map(item => item.volume),
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
})

// 处理标的切换
const handleSymbolChange = async () => {
  try {
    await Promise.all([
      marketStore.fetchLatestPrice(selectedSymbol.value),
      marketStore.fetchMarketData(selectedSymbol.value, {
        start_date: dayjs(dateRange.value[0]).format('YYYY-MM-DD'),
        end_date: dayjs(dateRange.value[1]).format('YYYY-MM-DD')
      })
    ])
  } catch (error) {
    console.error('获取市场数据失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = async () => {
  if (dateRange.value) {
    await marketStore.fetchMarketData(selectedSymbol.value, {
      start_date: dayjs(dateRange.value[0]).format('YYYY-MM-DD'),
      end_date: dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    })
  }
}

// 刷新数据
const refreshData = async () => {
  try {
    await handleSymbolChange()
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 监听图表类型变化
watch(chartType, () => {
  // 图表类型变化时重新渲染
})

// 监听时间框架变化
watch(timeframe, () => {
  // 时间框架变化时重新获取数据
  handleSymbolChange()
})

// 初始化数据
onMounted(async () => {
  try {
    await handleSymbolChange()
  } catch (error) {
    console.error('初始化市场数据失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.market {
  height: 100vh;
  overflow: hidden;
}

.market-content {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.header-left {
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px 0;
  }
  
  .page-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.price-overview {
  margin-bottom: 24px;
}

.price-card {
  .price-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .price-info {
    .symbol {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 8px 0;
    }
    
    .current-price {
      font-size: 32px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 8px;
    }
    
    .price-change {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 16px;
      font-weight: 600;
      
      &.positive {
        color: var(--success-color);
      }
      
      &.negative {
        color: var(--danger-color);
      }
    }
  }
  
  .price-time {
    text-align: right;
    
    .time-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }
    
    .time-value {
      font-size: 14px;
      color: var(--text-primary);
    }
  }
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .chart-controls {
    display: flex;
    align-items: center;
  }
  
  .chart-container {
    &.large {
      height: 500px;
    }
    
    .chart {
      width: 100%;
      height: 100%;
    }
  }
}

.indicators-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.indicator-card {
  .chart-container {
    &.small {
      height: 200px;
    }
    
    .chart {
      width: 100%;
      height: 100%;
    }
  }
}

.data-table-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .table-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

@media (max-width: 1200px) {
  .indicators-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .price-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .price-time {
    text-align: left;
  }
  
  .chart-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .table-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
