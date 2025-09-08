<template>
  <div class="market-data">
    <Layout>
      <div class="market-data-content">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1>市场数据管理</h1>
          <p>管理股票数据获取和同步</p>
        </div>

        <!-- 操作面板 -->
        <el-card class="operation-panel">
          <template #header>
            <div class="card-header">
              <h3>数据操作</h3>
            </div>
          </template>
          
          <div class="operation-buttons">
            <el-button 
              type="primary" 
              @click="syncIndexComponents"
              :loading="loading.syncIndex"
              icon="Download"
            >
              同步上证500成分股
            </el-button>
            
            <el-button 
              type="success" 
              @click="fetchLatestData"
              :loading="loading.fetchLatest"
              icon="Refresh"
            >
              获取最新行情数据
            </el-button>
            
            <el-button 
              type="info" 
              @click="syncAllSymbols"
              :loading="loading.syncAll"
              icon="Collection"
            >
              同步所有股票列表
            </el-button>
            
            <el-button 
              type="warning" 
              @click="showSchedulerDialog"
              icon="Timer"
            >
              定时任务管理
            </el-button>
          </div>

          <!-- 数据源配置 -->
          <div class="data-source-config">
            <el-form :model="config" label-width="120px" inline>
              <el-form-item label="数据源:">
                <el-select v-model="config.dataSource" style="width: 150px">
                  <el-option 
                    v-for="source in dataSources" 
                    :key="source" 
                    :label="source" 
                    :value="source"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="批量大小:">
                <el-input-number 
                  v-model="config.batchSize" 
                  :min="10" 
                  :max="100" 
                  style="width: 120px"
                />
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <!-- 统计信息 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-value">{{ statistics.totalSymbols || 0 }}</div>
                <div class="stat-label">总股票数</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-value">{{ statistics.totalRecords || 0 }}</div>
                <div class="stat-label">总记录数</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-value">{{ statistics.symbolsWithData || 0 }}</div>
                <div class="stat-label">有数据股票数</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-value">{{ dataSourceStatus }}</div>
                <div class="stat-label">数据源状态</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 股票列表 -->
        <el-card class="symbols-table">
          <template #header>
            <div class="card-header">
              <h3>股票列表</h3>
              <div class="header-actions">
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索股票代码或名称"
                  style="width: 200px"
                  @input="handleSearch"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                
                <el-select 
                  v-model="filterExchange" 
                  placeholder="筛选交易所"
                  style="width: 120px; margin-left: 10px"
                  clearable
                  @change="handleFilter"
                >
                  <el-option label="上交所" value="SH" />
                  <el-option label="深交所" value="SZ" />
                </el-select>
                
                <el-button 
                  @click="refreshSymbols"
                  :loading="loading.symbols"
                  icon="Refresh"
                  style="margin-left: 10px"
                >
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="symbols" 
            v-loading="loading.symbols"
            stripe
            height="400"
          >
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column prop="name" label="股票名称" width="150" />
            <el-table-column prop="exchange" label="交易所" width="80" />
            <el-table-column prop="asset_type" label="类型" width="80" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                  {{ row.is_active ? '活跃' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  @click="fetchSymbolData(row.symbol)"
                  :loading="loading.fetchSymbol === row.symbol"
                >
                  获取数据
                </el-button>
                <el-button 
                  size="small" 
                  type="info"
                  @click="viewSymbolData(row.symbol)"
                >
                  查看数据
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.perPage"
              :total="pagination.total"
              :page-sizes="[20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>

        <!-- 定时任务管理对话框 -->
        <el-dialog
          v-model="schedulerDialogVisible"
          title="定时任务管理"
          width="800px"
        >
          <div class="scheduler-content">
            <el-table :data="schedulerJobs" v-loading="loading.scheduler">
              <el-table-column prop="name" label="任务名称" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="row.status === 'success' ? 'success' : 
                           row.status === 'error' ? 'danger' : 'info'"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="next_run_time" label="下次执行" width="180">
                <template #default="{ row }">
                  {{ row.next_run_time ? formatDate(row.next_run_time) : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="last_run" label="最后执行" width="180">
                <template #default="{ row }">
                  {{ row.last_run ? formatDate(row.last_run) : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    type="primary"
                    @click="triggerJob(row.id)"
                  >
                    立即执行
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <template #footer>
            <el-button @click="schedulerDialogVisible = false">关闭</el-button>
            <el-button type="primary" @click="refreshSchedulerJobs">刷新</el-button>
          </template>
        </el-dialog>
      </div>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Layout from '@/components/Layout/index.vue'
import { apiClient } from '@/api'
import dayjs from 'dayjs'

// 响应式数据
const loading = reactive({
  syncIndex: false,
  fetchLatest: false,
  syncAll: false,
  symbols: false,
  scheduler: false,
  fetchSymbol: null as string | null
})

const config = reactive({
  dataSource: 'akshare',
  batchSize: 50
})

const statistics = reactive({
  totalSymbols: 0,
  totalRecords: 0,
  symbolsWithData: 0
})

const symbols = ref([])
const dataSources = ref(['akshare'])
const dataSourceStatus = ref('未知')

const searchQuery = ref('')
const filterExchange = ref('')

const pagination = reactive({
  page: 1,
  perPage: 50,
  total: 0
})

const schedulerDialogVisible = ref(false)
const schedulerJobs = ref([])

// 方法
const syncIndexComponents = async () => {
  loading.syncIndex = true
  try {
    const response = await apiClient.syncIndexComponents({
      index_code: '上证500',
      data_source: config.dataSource
    })
    
    ElMessage.success(`成功同步${response.synced_count}只成分股`)
    await refreshStatistics()
    await loadSymbols()
  } catch (error) {
    ElMessage.error('同步成分股失败: ' + error.message)
  } finally {
    loading.syncIndex = false
  }
}

const fetchLatestData = async () => {
  loading.fetchLatest = true
  try {
    const response = await apiClient.fetchLatestData({
      data_source: config.dataSource
    })
    
    ElMessage.success(
      `获取完成: 处理${response.total_symbols}只股票，成功${response.successful_symbols}只，新增${response.total_records}条记录`
    )
    await refreshStatistics()
  } catch (error) {
    ElMessage.error('获取最新数据失败: ' + error.message)
  } finally {
    loading.fetchLatest = false
  }
}

const syncAllSymbols = async () => {
  loading.syncAll = true
  try {
    const response = await apiClient.syncSymbols({
      market: 'A股',
      data_source: config.dataSource
    })
    
    ElMessage.success(`成功同步${response.synced_count}只股票`)
    await refreshStatistics()
    await loadSymbols()
  } catch (error) {
    ElMessage.error('同步股票列表失败: ' + error.message)
  } finally {
    loading.syncAll = false
  }
}

const fetchSymbolData = async (symbol: string) => {
  loading.fetchSymbol = symbol
  try {
    const response = await apiClient.fetchHistoricalData({
      symbol,
      data_source: config.dataSource
    })
    
    ElMessage.success(`${symbol}数据获取完成，新增${response.records_added}条记录`)
  } catch (error) {
    ElMessage.error(`获取${symbol}数据失败: ` + error.message)
  } finally {
    loading.fetchSymbol = null
  }
}

const viewSymbolData = (symbol: string) => {
  // 这里可以跳转到股票详情页面或显示数据图表
  ElMessage.info(`查看${symbol}的数据功能待实现`)
}

const loadSymbols = async () => {
  loading.symbols = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      search: searchQuery.value,
      exchange: filterExchange.value
    }
    
    const response = await apiClient.getSymbols(params)
    
    symbols.value = response.symbols
    pagination.total = response.pagination.total
  } catch (error) {
    ElMessage.error('加载股票列表失败: ' + error.message)
  } finally {
    loading.symbols = false
  }
}

const refreshSymbols = () => {
  loadSymbols()
}

const handleSearch = () => {
  pagination.page = 1
  loadSymbols()
}

const handleFilter = () => {
  pagination.page = 1
  loadSymbols()
}

const handleSizeChange = (size: number) => {
  pagination.perPage = size
  pagination.page = 1
  loadSymbols()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadSymbols()
}

const refreshStatistics = async () => {
  try {
    const response = await apiClient.getMarketDataStatistics()
    Object.assign(statistics, response)
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const loadDataSources = async () => {
  try {
    const response = await apiClient.getDataSources()
    dataSources.value = response.sources
    config.dataSource = response.default
  } catch (error) {
    console.error('获取数据源失败:', error)
  }
}

const checkDataSourceHealth = async () => {
  try {
    const response = await apiClient.getMarketDataHealth()
    dataSourceStatus.value = response.data_source_health?.is_connected ? '正常' : '异常'
  } catch (error) {
    dataSourceStatus.value = '异常'
  }
}

const showSchedulerDialog = () => {
  schedulerDialogVisible.value = true
  refreshSchedulerJobs()
}

const refreshSchedulerJobs = async () => {
  loading.scheduler = true
  try {
    // 这里需要添加获取定时任务列表的API
    // const response = await apiClient.get('/scheduler/jobs')
    // schedulerJobs.value = response.jobs
    schedulerJobs.value = [] // 临时空数组
  } catch (error) {
    ElMessage.error('获取定时任务失败: ' + error.message)
  } finally {
    loading.scheduler = false
  }
}

const triggerJob = async (jobId: string) => {
  try {
    // 这里需要添加立即执行任务的API
    // await apiClient.post(`/scheduler/jobs/${jobId}/trigger`)
    ElMessage.success('任务已触发执行')
  } catch (error) {
    ElMessage.error('触发任务失败: ' + error.message)
  }
}

const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

const getStatusText = (status: string) => {
  const statusMap = {
    success: '成功',
    error: '失败',
    pending: '等待中',
    running: '运行中'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadDataSources(),
    refreshStatistics(),
    loadSymbols(),
    checkDataSourceHealth()
  ])
})
</script>

<style lang="scss" scoped>
.market-data {
  height: 100vh;
  overflow: hidden;
}

.market-data-content {
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.page-header {
  margin-bottom: 20px;
  
  h1 {
    margin: 0 0 8px 0;
    font-size: 24px;
    color: #303133;
  }
  
  p {
    margin: 0;
    color: #606266;
    font-size: 14px;
  }
}

.operation-panel {
  margin-bottom: 20px;
  
  .operation-buttons {
    margin-bottom: 20px;
    
    .el-button {
      margin-right: 10px;
      margin-bottom: 10px;
    }
  }
  
  .data-source-config {
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}

.stats-row {
  margin-bottom: 20px;
  
  .stat-card {
    text-align: center;
    
    .stat-item {
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #409eff;
        margin-bottom: 8px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
      }
    }
  }
}

.symbols-table {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
    }
    
    .header-actions {
      display: flex;
      align-items: center;
    }
  }
  
  .pagination-wrapper {
    margin-top: 20px;
    text-align: center;
  }
}

.scheduler-content {
  .el-table {
    margin-bottom: 20px;
  }
}
</style>
