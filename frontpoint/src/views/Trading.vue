<template>
  <div class="trading">
    <Layout>
      <div class="trading-content">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">交易管理</h1>
            <p class="page-subtitle">执行交易和管理交易记录</p>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="showTradeDialog = true">
              <el-icon><Plus /></el-icon>
              执行交易
            </el-button>
          </div>
        </div>
        
        <!-- 交易统计 -->
        <div class="stats-grid">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon primary">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ tradingStore.totalTrades }}</div>
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
                <div class="stat-value">{{ tradingStore.winningTrades }}</div>
                <div class="stat-label">盈利交易</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="tradingStore.winRate >= 50 ? 'success' : 'warning'">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ tradingStore.winRate.toFixed(1) }}%</div>
                <div class="stat-label">胜率</div>
              </div>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :class="tradingStore.totalPnL >= 0 ? 'success' : 'danger'">
                <el-icon size="24"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value" :class="tradingStore.totalPnL >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ tradingStore.totalPnL.toLocaleString() }}
                </div>
                <div class="stat-label">总盈亏</div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 筛选和搜索 -->
        <el-card class="filter-card">
          <div class="filter-content">
            <div class="filter-left">
              <el-select v-model="filters.portfolio_id" placeholder="选择投资组合" clearable style="width: 150px">
                <el-option
                  v-for="portfolio in portfolioStore.portfolios"
                  :key="portfolio.id"
                  :label="portfolio.name"
                  :value="portfolio.id"
                />
              </el-select>
              
              <el-select v-model="filters.symbol" placeholder="选择标的" clearable style="width: 120px">
                <el-option label="AAPL" value="AAPL" />
                <el-option label="GOOGL" value="GOOGL" />
                <el-option label="MSFT" value="MSFT" />
                <el-option label="TSLA" value="TSLA" />
              </el-select>
              
              <el-select v-model="filters.side" placeholder="交易方向" clearable style="width: 120px">
                <el-option label="买入" value="buy" />
                <el-option label="卖出" value="sell" />
              </el-select>
              
              <el-select v-model="filters.status" placeholder="交易状态" clearable style="width: 120px">
                <el-option label="已完成" value="completed" />
                <el-option label="待处理" value="pending" />
                <el-option label="已取消" value="cancelled" />
                <el-option label="失败" value="failed" />
              </el-select>
            </div>
            
            <div class="filter-right">
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="primary" @click="applyFilters">筛选</el-button>
            </div>
          </div>
        </el-card>
        
        <!-- 交易记录表格 -->
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">交易记录</h3>
              <div class="card-actions">
                <el-button size="small" @click="refreshData">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-button size="small" @click="exportData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table
            v-loading="tradingStore.loading"
            :data="filteredTrades"
            style="width: 100%"
            @sort-change="handleSortChange"
          >
            <el-table-column prop="id" label="ID" width="80" sortable="custom" />
            <el-table-column prop="symbol" label="标的" width="100" />
            <el-table-column prop="side" label="方向" width="100">
              <template #default="{ row }">
                <el-tag :type="row.side === 'buy' ? 'success' : 'danger'" size="small">
                  {{ row.side === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" sortable="custom" />
            <el-table-column prop="price" label="价格" width="120" sortable="custom">
              <template #default="{ row }">
                ${{ row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120" sortable="custom">
              <template #default="{ row }">
                ${{ row.amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="fee" label="手续费" width="100">
              <template #default="{ row }">
                ${{ row.fee.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="pnl" label="盈亏" width="120" sortable="custom">
              <template #default="{ row }">
                <span :class="row.pnl >= 0 ? 'number-positive' : 'number-negative'">
                  ${{ row.pnl.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="executed_at" label="执行时间" width="160" sortable="custom">
              <template #default="{ row }">
                {{ formatTime(row.executed_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="text" @click="viewTrade(row)">
                  查看
                </el-button>
                <el-button
                  v-if="row.status === 'pending'"
                  size="small"
                  type="text"
                  @click="cancelTrade(row)"
                >
                  取消
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.size"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </Layout>
    
    <!-- 执行交易对话框 -->
    <el-dialog
      v-model="showTradeDialog"
      title="执行交易"
      width="500px"
      @close="resetTradeForm"
    >
      <el-form
        ref="tradeFormRef"
        :model="tradeForm"
        :rules="tradeFormRules"
        label-width="100px"
      >
        <el-form-item label="投资组合" prop="portfolio_id">
          <el-select v-model="tradeForm.portfolio_id" placeholder="请选择投资组合" style="width: 100%">
            <el-option
              v-for="portfolio in portfolioStore.portfolios"
              :key="portfolio.id"
              :label="portfolio.name"
              :value="portfolio.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="交易标的" prop="symbol">
          <el-input v-model="tradeForm.symbol" placeholder="请输入交易标的，如 AAPL" />
        </el-form-item>
        
        <el-form-item label="交易方向" prop="side">
          <el-radio-group v-model="tradeForm.side">
            <el-radio label="buy">买入</el-radio>
            <el-radio label="sell">卖出</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="交易数量" prop="quantity">
          <el-input-number
            v-model="tradeForm.quantity"
            :min="0"
            :precision="2"
            placeholder="请输入交易数量"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="交易价格" prop="price">
          <el-input-number
            v-model="tradeForm.price"
            :min="0"
            :precision="2"
            placeholder="请输入交易价格"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showTradeDialog = false">取消</el-button>
          <el-button type="primary" :loading="tradeFormLoading" @click="handleTradeSubmit">
            执行交易
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  TrendCharts,
  Check,
  Money,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import Layout from '@/components/Layout/index.vue'
import { useTradingStore } from '@/stores/trading'
import { usePortfolioStore } from '@/stores/portfolio'
import { useAuthStore } from '@/stores/auth'
import type { CreateTradeRequest } from '@/types'
import dayjs from 'dayjs'

const tradingStore = useTradingStore()
const portfolioStore = usePortfolioStore()
const authStore = useAuthStore()

const showTradeDialog = ref(false)
const tradeFormLoading = ref(false)
const tradeFormRef = ref<FormInstance>()

// 筛选条件
const filters = reactive({
  portfolio_id: null as number | null,
  symbol: '',
  side: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 排序
const sortField = ref('')
const sortOrder = ref('')

// 交易表单
const tradeForm = reactive<CreateTradeRequest>({
  portfolio_id: 0,
  symbol: '',
  side: 'buy',
  quantity: 0,
  price: 0
})

const tradeFormRules: FormRules = {
  portfolio_id: [
    { required: true, message: '请选择投资组合', trigger: 'change' }
  ],
  symbol: [
    { required: true, message: '请输入交易标的', trigger: 'blur' },
    { min: 1, max: 10, message: '标的长度在 1 到 10 个字符', trigger: 'blur' }
  ],
  side: [
    { required: true, message: '请选择交易方向', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入交易数量', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '交易数量必须大于0', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入交易价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '交易价格必须大于0', trigger: 'blur' }
  ]
}

// 过滤后的交易记录
const filteredTrades = computed(() => {
  let trades = tradingStore.trades
  
  if (filters.portfolio_id) {
    trades = trades.filter(trade => trade.portfolio_id === filters.portfolio_id)
  }
  
  if (filters.symbol) {
    trades = trades.filter(trade => trade.symbol.includes(filters.symbol))
  }
  
  if (filters.side) {
    trades = trades.filter(trade => trade.side === filters.side)
  }
  
  if (filters.status) {
    trades = trades.filter(trade => trade.status === filters.status)
  }
  
  // 排序
  if (sortField.value) {
    trades.sort((a, b) => {
      const aVal = a[sortField.value as keyof typeof a]
      const bVal = b[sortField.value as keyof typeof b]
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder.value === 'ascending' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder.value === 'ascending' 
          ? aVal - bVal
          : bVal - aVal
      }
      
      return 0
    })
  }
  
  // 分页
  const start = (pagination.page - 1) * pagination.size
  const end = start + pagination.size
  pagination.total = trades.length
  
  return trades.slice(start, end)
})

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

// 重置筛选条件
const resetFilters = () => {
  filters.portfolio_id = null
  filters.symbol = ''
  filters.side = ''
  filters.status = ''
}

// 应用筛选
const applyFilters = () => {
  pagination.page = 1
  // 筛选逻辑在computed中处理
}

// 处理排序
const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortField.value = prop
  sortOrder.value = order
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
}

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
}

// 刷新数据
const refreshData = async () => {
  try {
    await tradingStore.fetchTrades()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中')
}

// 查看交易详情
const viewTrade = (_trade: any) => {
  ElMessage.info('查看交易详情功能开发中')
}

// 取消交易
const cancelTrade = async (_trade: any) => {
  try {
    await ElMessageBox.confirm('确定要取消这笔交易吗？', '确认取消', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 这里应该调用API取消交易
    ElMessage.success('交易已取消')
  } catch (error) {
    // 用户取消
  }
}

// 重置交易表单
const resetTradeForm = () => {
  tradeForm.portfolio_id = 0
  tradeForm.symbol = ''
  tradeForm.side = 'buy'
  tradeForm.quantity = 0
  tradeForm.price = 0
  tradeFormRef.value?.clearValidate()
}

// 提交交易
const handleTradeSubmit = async () => {
  if (!tradeFormRef.value) return
  
  try {
    await tradeFormRef.value.validate()
    tradeFormLoading.value = true
    
    await tradingStore.executeTrade(tradeForm)
    ElMessage.success('交易执行成功')
    showTradeDialog.value = false
    resetTradeForm()
  } catch (error) {
    console.error('执行交易失败:', error)
  } finally {
    tradeFormLoading.value = false
  }
}

// 初始化数据
onMounted(async () => {
  try {
    const userId = authStore.user?.id
    if (userId) {
      await Promise.all([
        portfolioStore.fetchPortfolios(userId),
        tradingStore.fetchTrades()
      ])
    }
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.trading {
  height: 100vh;
  overflow: hidden;
}

.trading-content {
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

.filter-card {
  margin-bottom: 24px;
  
  .filter-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  
  .filter-left {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  
  .filter-right {
    display: flex;
    gap: 8px;
  }
}

.table-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-left {
    justify-content: center;
  }
  
  .filter-right {
    justify-content: center;
  }
}
</style>
